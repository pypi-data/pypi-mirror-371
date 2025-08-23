import copy
import warnings

warnings.filterwarnings("ignore", message="Valid config keys have changed in V2:*")

import base64
import inspect
import json
import logging
import re
from functools import wraps
from textwrap import dedent
from typing import Any, Callable, Dict, List, Optional, Union
import asyncio
from enum import Enum

import litellm
from jsonschema import validate as validate_json_schema
from litellm import completion as litellm_completion
from litellm import acompletion as litellm_acompletion
from pydantic import BaseModel
from stamina import retry
from litellm.exceptions import RateLimitError, InternalServerError, APIError, Timeout
from fix_busted_json import repair_json, is_json
from json_repair import repair_json as repair_json2
from pathlib import Path
import subprocess
import os

# Import Django support utilities
from .django_support import (
    is_django_model,
    django_model_to_json_schema,
    create_django_model_instance,
    get_django_model_instructions,
    DJANGO_AVAILABLE
)

# Import fastmcp for MCP support
try:
    import fastmcp
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    logging.warning("fastmcp not found - MCP tools will be unavailable. Install with: pip install fastmcp")

__version__ = "5.5.6"

def with_fallback(
    models: Optional[List[str]] = None,
    temperature: Optional[float] = None
):
    '''
    Decorator that provides model fallback capability for LLM methods.
    Can be used in conjunction with the @llm decorator.
    
    Args:
        models: List of models to try in order. If None, uses default list
        temperature: Temperature to use for all models. If None, uses each model's default
        
    Example:
        ```python
        @with_fallback(models=['model2', 'model3'])
        @llm(model='model1', temperature=0.5)
        async def my_llm_method(self, arg1, arg2):
            """Method docstring"""
            pass
        ```
    '''
    def decorator(func: Callable):
        # Get the original llm decorator if it exists
        original_model = None
        original_temp = None
        
        # Look for the llm decorator in the function's metadata
        if hasattr(func, '__llm_params__'):
            original_model = func.__llm_params__.get('model')
            original_temp = func.__llm_params__.get('temperature')
        
        # Set up fallback models list
        fallback_models = [] if models is None else models.copy()
        if original_model and original_model not in fallback_models:
            fallback_models.insert(0, original_model)  # Try original model first
        elif not fallback_models:
            fallback_models = [
                "groq/meta-llama/llama-4-scout-17b-16e-instruct",
                "groq/meta-llama/llama-4-maverick-17b-128e-instruct",
                "openai/gpt-4o-mini",
                "openai/gpt-4o"
            ]
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            
            for model in fallback_models:
                try:
                    # Create a new llm decorator with the current model
                    model_kwargs = {"model": model}
                    
                    # Use temperature in this priority:
                    # 1. Temperature passed to with_fallback
                    # 2. Original temperature from @llm
                    # 3. No temperature (let llm use its default)
                    if temperature is not None:
                        model_kwargs["temperature"] = temperature
                    elif original_temp is not None:
                        model_kwargs["temperature"] = original_temp
                    
                    decorated_func = llm(**model_kwargs)(func)
                    return await decorated_func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    continue
            
            raise Exception(f"All models failed. Last error: {str(last_error)}")
            
        return wrapper
    return decorator

def extend_enum(base_enum: type[Enum], **new_members) -> type[Enum]:
    """
    Extend an existing Enum with new members.
    
    Args:
        base_enum: The original Enum class to extend
        **new_members: New enum members as keyword arguments (name=value)
    
    Returns:
        A new Enum class with all original members plus the new ones
        
    Example:
        class Priority(str, Enum):
            LOW = "low"
            HIGH = "high"
            
        ExtendedPriority = extend_enum(Priority, EMERGENCY="emergency", MAINTENANCE="maintenance")
        # ExtendedPriority now has: LOW, HIGH, EMERGENCY, MAINTENANCE
    """
    if not (inspect.isclass(base_enum) and issubclass(base_enum, Enum)):
        raise ValueError("base_enum must be an Enum class")
    
    # Get existing members
    existing_members = {member.name: member.value for member in base_enum}
    
    # Combine with new members (convert keys to uppercase for consistency)
    all_members = {**existing_members, **{k.upper(): v for k, v in new_members.items()}}
    
    # Determine the enum type (str, int, etc.) from the base enum
    enum_bases = [cls for cls in base_enum.__mro__ if cls != Enum and cls != object]
    if enum_bases:
        enum_type = enum_bases[0]  # First non-Enum base class (e.g., str, int)
    else:
        enum_type = None
    
    # Create new enum with same type
    if enum_type:
        return Enum(f'Extended{base_enum.__name__}', all_members, type=enum_type)
    else:
        return Enum(f'Extended{base_enum.__name__}', all_members)


SystemPrompt = Optional[Union[str, List[str], List[Dict[str, str]]]]

ImageBytes = bytes

# Define common errors that should be retried
LITELLM_ERRORS = (RateLimitError, InternalServerError, APIError, Timeout)


class State:
    """Base state class for managing conversation memory"""

    def __init__(self):
        self._messages: List[Dict[str, str]] = []

    def add_message(self, message: Dict[str, str]) -> None:
        """Add a message to the conversation history"""
        self._messages.append(message)

    def get_messages(
        self, prompt: str = None, limit: int = None
    ) -> List[Dict[str, str]]:
        """Retrieve messages from the conversation history
        Args:
            prompt: Optional prompt to filter messages by
            limit: Optional number of most recent messages to return
        """
        if limit is None:
            return self._messages
        return self._messages[-limit:]

    def clear(self) -> None:
        """Clear all messages from memory"""
        self._messages = []


class MCPServer:
    """Configuration for an MCP server"""
    
    def __init__(self, name: str, command: str, args: List[str] = None, env: Dict[str, str] = None):
        self.name = name
        self.command = command
        self.args = args or []
        self.env = env or {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary format"""
        return {
            "name": self.name,
            "command": self.command,
            "args": self.args,
            "env": self.env
        }


class MCPConfig:
    """Global MCP configuration manager"""
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None, auto_start: bool = True):
        """Initialize MCP configuration
        
        Args:
            config_file: Path to MCP config JSON file (default: ~/.cursor/mcp.json)
            auto_start: Whether to automatically start servers when needed
        """
        if config_file:
            self.config_file = Path(config_file).expanduser()
        else:
            self.config_file = Path.home() / ".cursor" / "mcp.json"
        
        self.auto_start = auto_start
        self.servers = {}
        self._load_config()
    
    def _load_config(self):
        """Load MCP server configurations from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    config = json.load(f)
                    self.servers = config.get("mcpServers", {})
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"Failed to load MCP config from {self.config_file}: {e}")
    
    def get_server(self, name: str) -> dict:
        """Get server configuration by name
        
        Args:
            name: Server name
            
        Returns:
            Server configuration dict
            
        Raises:
            ValueError: If server not found in config
        """
        if name not in self.servers:
            raise ValueError(f"MCP server '{name}' not found in config")
        return {"name": name, **self.servers[name]}
    
    def list_servers(self) -> List[str]:
        """List available server names"""
        return list(self.servers.keys())


# Global MCP configuration instance
_mcp_config: Optional[MCPConfig] = None


def configure_mcp(config_file: Optional[Union[str, Path]] = None, auto_start: bool = True) -> MCPConfig:
    """Configure global MCP settings
    
    Args:
        config_file: Path to MCP config JSON file
        auto_start: Whether to automatically start servers when needed
        
    Returns:
        MCPConfig instance
    """
    global _mcp_config
    _mcp_config = MCPConfig(config_file, auto_start)
    return _mcp_config


class MCPServerManager:
    """Manages MCP server lifecycle and connections"""
    
    def __init__(self):
        self.running_servers = {}  # name -> client mapping
        self.server_processes = {}  # name -> process mapping
    
    async def ensure_server_running(self, server_config: dict) -> Any:
        """Start server if not running, or connect if already running
        
        Args:
            server_config: Server configuration dict
            
        Returns:
            MCP client connected to the server
        """
        if not FASTMCP_AVAILABLE:
            raise ImportError("fastmcp is required for MCP support. Install with: pip install fastmcp")
        
        server_name = server_config["name"]
        
        if server_name not in self.running_servers:
            # Start and connect to server
            try:
                # Create transport configuration for the server
                transport_config = {
                    "command": server_config["command"],
                    "args": server_config.get("args", []),
                    "env": {**os.environ, **server_config.get("env", {})}
                }
                
                # Create client for the server
                from fastmcp import Client
                client = Client(transport=transport_config)
                
                # Connect to the server
                await client.connect()
                
                self.running_servers[server_name] = client
            except Exception as e:
                raise RuntimeError(f"Failed to start MCP server '{server_name}': {e}")
        
        return self.running_servers[server_name]
    
    async def shutdown_server(self, server_name: str):
        """Shutdown a running MCP server
        
        Args:
            server_name: Name of the server to shutdown
        """
        if server_name in self.running_servers:
            client = self.running_servers[server_name]
            try:
                await client.disconnect()
            except:
                pass
            del self.running_servers[server_name]
    
    async def shutdown_all(self):
        """Shutdown all running MCP servers"""
        for server_name in list(self.running_servers.keys()):
            await self.shutdown_server(server_name)


class Promptic:
    def __init__(
        self,
        model="gpt-4o-mini",
        system: SystemPrompt = None,
        dry_run: bool = False,
        debug: bool = False,
        memory: bool = False,
        state: Optional[State] = None,
        json_schema: Optional[Dict] = None,
        cache: bool = True,
        create_completion_fn=None,
        openai_client=None,
        weave_client=None,
        tool_timeout: int = 120,
        mcp: Optional[Union[List, Dict]] = None,
        mcp_config: Optional[MCPConfig] = None,
        **completion_kwargs,
    ):
        """Initialize a new Promptic instance.

        Args:
            model (str, optional): The LLM model to use. Defaults to "gpt-4o-mini".
            system (SystemPrompt, optional): System prompt(s) to prepend to all conversations.
                Can be a string, list of strings, or list of message dictionaries. Defaults to None.
            dry_run (bool, optional): If True, tools will not be executed. Defaults to False.
            debug (bool, optional): Enable debug logging. Defaults to False.
            memory (bool, optional): Enable conversation memory. Defaults to False.
            state (State, optional): Custom state instance for memory management. Defaults to None.
            json_schema (Dict, optional): JSON schema for response validation. Defaults to None.
            cache (bool, optional): Enable response caching for Anthropic models. Defaults to True.
            openai_client (OpenAI, optional): The OpenAI client to use for API calls. Defaults to None.
            create_completion_fn (Callable, optional): The function to use for API calls. Defaults to None.
            weave_client (WeaveClient, optional): The Weights & Biases client used to trace calls. Defaults to None.
            tool_timeout (int, optional): Timeout in seconds for tool execution. Defaults to 120.
            **client_kwargs: Additional keyword arguments passed to the create_completion_fn.
        """
        assert not (openai_client and create_completion_fn), (
            "openai_client and create_completion_fn are mutually exclusive"
        )

        self.model = model
        self.system = system
        self.dry_run = dry_run
        self.completion_kwargs = completion_kwargs
        self.tools: Dict[str, Callable] = {}
        self.tool_timeouts: Dict[str, int] = {}
        self.tool_timeout = tool_timeout
        self.json_schema = json_schema
        
        # MCP configuration
        self.mcp_servers = mcp or []
        self.mcp_config = mcp_config or _mcp_config  # Use global if not specified
        self.mcp_clients = {}  # Cache for MCP client connections
        self.mcp_tools = {}  # Map tool names to MCP clients
        self.mcp_manager = MCPServerManager()
        self.openai_client = openai_client
        self.weave_client = weave_client
        if self.openai_client:
            self.create_completion_fn = self.openai_client.chat.completions.create
        elif create_completion_fn:
            self.create_completion_fn = create_completion_fn
        else:
            self.create_completion_fn = litellm_completion

        self.logger = logging.getLogger("promptic")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.debug = debug

        if debug:
            self.logger.setLevel(logging.DEBUG)
            if self.create_completion_fn == litellm:
                litellm.set_verbose = True
        else:
            self.logger.setLevel(logging.WARNING)

        self.result_regex = re.compile(r"```(?:json)?(.*?)```", re.DOTALL)

        self.memory = memory or state is not None

        if memory and state is None:
            self.state = State()
        else:
            self.state = state

        self.anthropic = self.model.startswith(("claude", "anthropic"))
        self.gemini = self.model.startswith(("gemini", "vertex"))

        self.cache = cache
        self.anthropic_cached_block_limit = 4
        self.cached_count = 0

        self.tool_definitions = None

    @property
    def system_messages(self):
        result = []

        if not self.system:
            return result
        if isinstance(self.system, str):
            result = [{"content": self.system, "role": "system"}]
        elif isinstance(self.system, list) and isinstance(self.system[0], dict):
            result = self.system
        elif isinstance(self.system, list) and isinstance(self.system[0], str):
            result = [{"content": msg, "role": "system"} for msg in self.system]
        else:
            raise ValueError("Invalid system prompt")

        result = self._set_anthropic_cache(result)

        if self.state and not self.state.get_messages():
            for msg in result:
                self.state.add_message(msg)

        return result

    def _completion(self, messages: list[dict], **kwargs):
        """Internal method to handle completion requests with retry support"""
        new_messages = self._set_anthropic_cache(messages)
        previous_messages = self.state.get_messages() if self.state else []
        completion_messages = self.system_messages + previous_messages + new_messages

        self.logger.debug(f"{self.model = }")
        self.logger.debug(f"{completion_messages = }")
        self.logger.debug(f"{self.tool_definitions = }")
        self.logger.debug(f"{self.completion_kwargs = }")
        self.logger.debug(f"{kwargs = }")

        # Apply default cache behavior for Anthropic models
        self._set_anthropic_cache(completion_messages)
        
        # Filter out internal parameters that shouldn't be passed to litellm
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['retry', 'retry_enabled', 'retry_max_attempts']}
        filtered_completion_kwargs = {k: v for k, v in self.completion_kwargs.items() if k not in ['retry', 'retry_enabled', 'retry_max_attempts']}

        completion = self.create_completion_fn(
            model=self.model,
            messages=completion_messages,
            tools=self.tool_definitions,
            tool_choice="auto" if self.tool_definitions else None,
            **(filtered_completion_kwargs | filtered_kwargs),
        )

        if self.state:
            for msg in new_messages:
                self.state.add_message(msg)

        return completion_messages, completion

    async def _async_completion(self, messages: list[dict], **kwargs):
        """Async version of _completion for use with async functions with retry support."""
        new_messages = self._set_anthropic_cache(messages)
        previous_messages = self.state.get_messages() if self.state else []
        completion_messages = self.system_messages + previous_messages + new_messages

        self.logger.debug(f"{self.model = }")
        self.logger.debug(f"{completion_messages = }")
        self.logger.debug(f"{self.tool_definitions = }")
        self.logger.debug(f"{self.completion_kwargs = }")
        self.logger.debug(f"{kwargs = }")

        # Apply Anthropic caching behavior
        self._set_anthropic_cache(completion_messages)
        
        # Filter out internal parameters that shouldn't be passed to litellm
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['retry', 'retry_enabled', 'retry_max_attempts']}
        filtered_completion_kwargs = {k: v for k, v in self.completion_kwargs.items() if k not in ['retry', 'retry_enabled', 'retry_max_attempts']}

        # Check if create_completion_fn is an async function
        if inspect.iscoroutinefunction(self.create_completion_fn):
            completion = await self.create_completion_fn(
                model=self.model,
                messages=completion_messages,
                tools=self.tool_definitions,
                tool_choice="auto" if self.tool_definitions else None,
                **(filtered_completion_kwargs | filtered_kwargs),
            )
        else:
            # For async contexts, use litellm's acompletion function
            completion = await litellm_acompletion(
                model=self.model,
                messages=completion_messages,
                tools=self.tool_definitions,
                tool_choice="auto" if self.tool_definitions else None,
                **(filtered_completion_kwargs | filtered_kwargs),
            )

        if self.state:
            for msg in new_messages:
                self.state.add_message(msg)

        return completion_messages, completion

    def completion(self, messages: list[dict], **kwargs):
        """Return the raw completion response from the LLM for a list of messages.

        This method provides direct access to the underlying LLM completion API, allowing
        more control over the conversation flow. Unlike the message method, it accepts
        a list of messages and returns the raw completion response.

        Args:
            messages (list[dict]): A list of message dictionaries, each with 'role' and 'content' keys.
                Example: [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]
            **kwargs: Additional arguments passed to the completion function.

        Returns:
            The raw completion response from the LLM.

        Warning:
            If state/memory is enabled, this method will warn that it's being called directly
            as it may lead to unexpected behavior with conversation history.
        """
        if self.state:
            warnings.warn(
                "State is enabled, but completion is being called directly. This can cause unexpected behavior.",
                UserWarning,
            )
        return self._completion(messages, **kwargs)[1]

    async def async_completion(self, messages: list[dict], **kwargs):
        """Async version of completion for use with async functions."""
        if self.state:
            warnings.warn(
                "State is enabled, but completion is being called directly. This can cause unexpected behavior.",
                UserWarning,
            )
        return (await self._async_completion(messages, **kwargs))[1]

    def message(self, message: str, **kwargs):
        messages = [{"content": message, "role": "user"}]
        completion_messages, response = self._completion(messages, **kwargs)

        call = None

        if self.weave_client:
            call = self.weave_client.create_call(
                op="Promptic.message",
                inputs={
                    "messages": completion_messages,
                },
                attributes={
                    "model": self.model,
                    "system": self.system,
                    "tools": self.tool_definitions,
                    "tool_choice": "auto" if self.tool_definitions else None,
                },
                display_name="promptic_message",
            )

        if (self.completion_kwargs | kwargs).get("stream"):
            return self._stream_response(response, call)
        else:
            content = response.choices[0].message.content
            result = self._parse_and_validate_response(content)

            if call and self.weave_client:
                self.weave_client.finish_call(call, output=result)

            return result

    async def async_message(self, message: str, **kwargs):
        messages = [{"content": message, "role": "user"}]
        completion_messages, response = await self._async_completion(messages, **kwargs)

        call = None

        if self.weave_client:
            call = self.weave_client.create_call(
                op="Promptic.message",
                inputs={
                    "messages": completion_messages,
                },
                attributes={
                    "model": self.model,
                    "system": self.system,
                    "tools": self.tool_definitions,
                    "tool_choice": "auto" if self.tool_definitions else None,
                },
                display_name="promptic_message",
            )

        if (self.completion_kwargs | kwargs).get("stream"):
            return await self._async_stream_response(response, call)
        else:
            content = response.choices[0].message.content
            result = self._parse_and_validate_response(content)

            if call and self.weave_client:
                self.weave_client.finish_call(call, output=result)

            return result

    def _set_anthropic_cache(self, messages: List[dict]):
        """Set the cache control for the message if it is an Anthropic message"""
        if not (self.cache and self.anthropic):
            return messages

        for msg in messages:
            if len(str(msg.get("content"))) * 4 > 1024:
                msg["cache_control"] = {"type": "ephemeral"}

        return messages

    def __call__(self, fn=None):
        return self._decorator(fn) if fn else self._decorator

    def tool(self, fn: Callable = None, timeout: int = None) -> Callable:
        """Register a function as a tool that can be used by the LLM
        
        Args:
            fn (Callable, optional): Function to register as a tool. Defaults to None.
            timeout (int, optional): Timeout in seconds for tool execution. 
                If not specified, uses the global tool_timeout setting. Defaults to None.
        """
        def decorator(fn):
            # Store the function in the tools dictionary with its metadata
            # Store as a tuple (fn, is_class_method) to track if it's a class method
            is_class_method = inspect.ismethod(fn) or (hasattr(fn, "__qualname__") and "." in fn.__qualname__)
            self.tools[fn.__name__] = (fn, is_class_method)
            
            # Store the timeout for this tool if specified
            if timeout is not None:
                self.tool_timeouts[fn.__name__] = timeout
                
            return fn
            
        # Handle both @tool and @tool() decorators
        if fn is None:
            return decorator
        return decorator(fn)

    def _generate_tool_definition(self, fn: Callable) -> dict:
        """Generate a tool definition from a function's metadata"""
        # If fn is a tuple (fn, is_class_method), extract just the function
        if isinstance(fn, tuple):
            fn = fn[0]
            
        sig = inspect.signature(fn)
        doc = dedent(fn.__doc__ or "")

        parameters = {"type": "object", "properties": {}, "required": []}

        for name, param in sig.parameters.items():
            # Skip 'self' parameter if present in class methods
            if name == 'self':
                continue
                
            param_type = param.annotation if param.annotation != inspect._empty else Any
            param_default = None if param.default == inspect._empty else param.default

            if param_default is None and param.default == inspect._empty:
                parameters["required"].append(name)

            param_info = {"type": "string"}  # Default to string if no type hint
            if param_type == int:
                param_info["type"] = "integer"
            elif param_type == float:
                param_info["type"] = "number"
            elif param_type == bool:
                param_info["type"] = "boolean"
            elif inspect.isclass(param_type) and issubclass(param_type, BaseModel):
                param_info = param_type.model_json_schema()

            parameters["properties"][name] = param_info

        # Add dummy parameter for Gemini models if the function doesn't take any arguments
        if self.gemini and not parameters.get("required"):
            parameters["properties"]["llm_invocation"] = {
                "type": "boolean",
                "description": "True if the function was invoked by an LLM",
            }
            parameters["required"].append("llm_invocation")

        return {
            "type": "function",
            "function": {
                "name": fn.__name__,
                "description": doc,
                "parameters": parameters,
            },
        }

    async def _setup_mcp_tools(self) -> List[dict]:
        """Initialize MCP tools from configured servers
        
        Returns:
            List of tool definitions in OpenAI format
        """
        if not self.mcp_servers:
            return []
        
        if not FASTMCP_AVAILABLE:
            self.logger.warning("fastmcp is not installed. MCP tools will be unavailable.")
            return []
        
        tool_definitions = []
        
        for server_spec in self.mcp_servers:
            try:
                server_config = self._parse_mcp_server_spec(server_spec)
                
                # Connect to server
                client = await self.mcp_manager.ensure_server_running(server_config)
                
                # Get available tools
                tools_response = await client.list_tools()
                # Extract tools from response (tools might be in a 'tools' field)
                tools = tools_response.tools if hasattr(tools_response, 'tools') else tools_response
                
                # Process tools based on filtering
                tools_to_add = self._filter_mcp_tools(tools, server_spec, server_config["name"])
                
                for tool_name, original_tool in tools_to_add:
                    # Convert to OpenAI format
                    tool_def = self._convert_mcp_tool_to_openai(original_tool, server_config["name"], tool_name)
                    tool_definitions.append(tool_def)
                    
                    # Cache for execution
                    self.mcp_tools[tool_def["function"]["name"]] = {
                        "client": client,
                        "original_name": original_tool.name,
                        "server": server_config["name"]
                    }
                    
            except Exception as e:
                self.logger.error(f"Failed to setup MCP server: {e}")
                continue
        
        return tool_definitions
    
    def _parse_mcp_server_spec(self, server_spec) -> dict:
        """Parse various MCP server specification formats
        
        Args:
            server_spec: Server specification (string, dict, or MCPServer)
            
        Returns:
            Server configuration dict
        """
        if isinstance(server_spec, str):
            # Reference to config file
            if not self.mcp_config:
                raise ValueError(f"No MCP config available for server '{server_spec}'")
            return self.mcp_config.get_server(server_spec)
        elif isinstance(server_spec, dict):
            if "command" in server_spec:
                # Inline configuration
                return server_spec
            else:
                # Dict with server name as key (for filtering)
                # This is handled in _filter_mcp_tools
                server_name = list(server_spec.keys())[0]
                if not self.mcp_config:
                    raise ValueError(f"No MCP config available for server '{server_name}'")
                return self.mcp_config.get_server(server_name)
        elif isinstance(server_spec, MCPServer):
            # MCPServer object
            return server_spec.to_dict()
        else:
            raise ValueError(f"Invalid MCP server specification: {server_spec}")
    
    def _filter_mcp_tools(self, tools: List, server_spec, server_name: str) -> List[tuple]:
        """Filter MCP tools based on specification
        
        Args:
            tools: List of tools from MCP server
            server_spec: Original server specification
            server_name: Name of the server
            
        Returns:
            List of (tool_name, tool) tuples to add
        """
        result = []
        
        # Handle different specification formats for filtering
        if isinstance(server_spec, dict) and "command" not in server_spec:
            # Dict format for filtering
            filter_spec = server_spec.get(server_name, True)
            
            if filter_spec is True:
                # Use all tools
                for tool in tools:
                    result.append((f"mcp_{server_name}_{tool.name}", tool))
            elif isinstance(filter_spec, list):
                # Use only specified tools
                tool_names = {t.name for t in tools}
                for tool_name in filter_spec:
                    matching_tool = next((t for t in tools if t.name == tool_name), None)
                    if matching_tool:
                        result.append((f"mcp_{server_name}_{tool_name}", matching_tool))
                    else:
                        self.logger.warning(f"Tool '{tool_name}' not found in server '{server_name}'")
            elif isinstance(filter_spec, dict):
                # Advanced filtering with options
                selected_tools = filter_spec.get("tools", [t.name for t in tools])
                prefix = filter_spec.get("prefix", f"mcp_{server_name}_")
                
                for tool in tools:
                    if tool.name in selected_tools:
                        tool_name = f"{prefix}{tool.name}"
                        result.append((tool_name, tool))
        else:
            # Default: use all tools with standard prefix
            for tool in tools:
                result.append((f"mcp_{server_name}_{tool.name}", tool))
        
        return result
    
    def _convert_mcp_tool_to_openai(self, mcp_tool, server_name: str, tool_name: str) -> dict:
        """Convert MCP tool definition to OpenAI format
        
        Args:
            mcp_tool: MCP tool object
            server_name: Name of the MCP server
            tool_name: Name to use for the tool
            
        Returns:
            Tool definition in OpenAI format
        """
        # MCP tools might have different attribute names depending on the response format
        # Try to get the input schema from various possible attributes
        parameters = None
        if hasattr(mcp_tool, 'inputSchema'):
            parameters = mcp_tool.inputSchema
        elif hasattr(mcp_tool, 'input_schema'):
            parameters = mcp_tool.input_schema
        elif hasattr(mcp_tool, 'parameters'):
            parameters = mcp_tool.parameters
        
        if parameters is None:
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }
        
        # Get description from various possible attributes
        description = None
        if hasattr(mcp_tool, 'description'):
            description = mcp_tool.description
        elif hasattr(mcp_tool, 'desc'):
            description = mcp_tool.desc
        
        if not description:
            description = f"MCP tool from {server_name}"
        
        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": description,
                "parameters": parameters,
            },
        }

    def _parse_and_validate_response(
        self, generated_text: str, return_type=None, json_schema=None, dynamic_schema=None
    ):
        """Parse and validate the response according to the return type"""

        # Handle dynamic Pydantic model (highest priority)
        if dynamic_schema and inspect.isclass(dynamic_schema) and issubclass(dynamic_schema, BaseModel):
            match = self.result_regex.search(generated_text)
            if match:
                json_result = match.group(1)
                if self.state:
                    self.state.add_message(
                        {"content": json_result, "role": "assistant"}
                    )
                try:
                    return dynamic_schema.model_validate(json.loads(repair_json(json_result)))
                except Exception as e:
                    return dynamic_schema.model_validate(json.loads(repair_json2(json_result)))

            raise ValueError("Failed to extract JSON result from the generated text.")

        # Handle dynamic Django model
        if dynamic_schema and is_django_model(dynamic_schema):
            match = self.result_regex.search(generated_text)
            if match:
                json_result = match.group(1)
                if self.state:
                    self.state.add_message(
                        {"content": json_result, "role": "assistant"}
                    )
                try:
                    data = json.loads(repair_json(json_result))
                except Exception as e:
                    data = json.loads(repair_json2(json_result))
                
                return create_django_model_instance(dynamic_schema, data)

            raise ValueError("Failed to extract JSON result from the generated text.")

        # Handle Pydantic model return types
        if return_type and issubclass(return_type, BaseModel):
            match = self.result_regex.search(generated_text)
            if match:
                json_result = match.group(1)
                if self.state:
                    self.state.add_message(
                        {"content": json_result, "role": "assistant"}
                    )
                try:
                    return return_type.model_validate(json.loads(repair_json(json_result)))
                except Exception as e:
                    return return_type.model_validate(json.loads(repair_json2(json_result)))

            raise ValueError("Failed to extract JSON result from the generated text.")

        # Handle Django model return types
        if return_type and is_django_model(return_type):
            match = self.result_regex.search(generated_text)
            if match:
                json_result = match.group(1)
                if self.state:
                    self.state.add_message(
                        {"content": json_result, "role": "assistant"}
                    )
                try:
                    data = json.loads(repair_json(json_result))
                except Exception as e:
                    data = json.loads(repair_json2(json_result))
                
                return create_django_model_instance(return_type, data)

            raise ValueError("Failed to extract JSON result from the generated text.")

        # Handle json_schema if provided
        elif json_schema:
            match = self.result_regex.search(generated_text)
            if not match:
                raise ValueError(
                    "Failed to extract JSON result from the generated text."
                )

            try:
                json_result = match.group(1)
                try:
                    parsed_result = json.loads(repair_json(json_result))
                except Exception as e:
                    parsed_result = json.loads(repair_json2(json_result))
                # Validate against the schema
                validate_json_schema(instance=parsed_result, schema=self.json_schema)
                if self.state:
                    self.state.add_message(
                        {"content": json_result, "role": "assistant"}
                    )
                return parsed_result
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in response: {e}")
            except Exception as e:
                raise ValueError(f"Schema validation failed: {str(e)}")

        # Handle plain text responses
        else:
            if self.state:
                self.state.add_message({"content": generated_text, "role": "assistant"})
            return generated_text

    @classmethod
    def decorate(cls, func: Callable = None, **kwargs):
        """See Promptic.__init__ for valid kwargs."""
        instance = cls(**kwargs)
        return instance._decorator(func) if func else instance._decorator

    def _clear_tools(self):
        self.tools = {}
        self.tool_definitions = None
        self.mcp_tools = {}
        self.mcp_clients = {}

    def _disable_state(self):
        self.state = None

    def llm(self, func: Callable = None, **kwargs):
        """Decorate a function with the Promptic instance.
        
        Args:
            func (Callable, optional): Function to decorate. Defaults to None.
            retry (bool or int, optional): If True, enables retry with default settings.
                If an integer, specifies the number of retry attempts.
                If False, disables retry functionality. Defaults to True.
            tool_timeout (int, optional): Default timeout in seconds for all tools. Defaults to 120.
            mcp (list or dict, optional): MCP server configuration. Can be:
                - List of server names (from config file)
                - List of inline server configs (dicts with command, args, env)
                - Dict mapping server names to tool filters
            mcp_config (MCPConfig, optional): MCP configuration instance.
            **kwargs: Additional arguments passed to Promptic.
        
        Returns:
            Callable: Decorated function.
        """
        new_instance = copy.copy(self)
        new_instance._clear_tools()
        new_instance._disable_state()

        # Handle the retry parameter
        retry_setting = kwargs.pop('retry', True)
        new_instance.retry_enabled = bool(retry_setting)
        
        # If retry is an integer, use it as max_attempts
        if isinstance(retry_setting, int) and retry_setting > 0:
            new_instance.retry_max_attempts = retry_setting
        else:
            new_instance.retry_max_attempts = 3  # Default to 3 attempts
            
        # Set tool timeout if provided
        if 'tool_timeout' in kwargs:
            new_instance.tool_timeout = kwargs.pop('tool_timeout')

        for key, value in kwargs.items():
            setattr(new_instance, key, value)

        return new_instance._decorator(func) if func else new_instance._decorator

    def _deserialize_pydantic_args(self, fn: Callable, function_args: dict) -> dict:
        """Deserialize any Pydantic model parameters in the function arguments.

        Args:
            fn: The function whose parameters to check
            function_args: The arguments to deserialize

        Returns:
            The function arguments with any Pydantic models deserialized
        """
        sig = inspect.signature(fn)
        for param_name, param in sig.parameters.items():
            param_type = param.annotation if param.annotation != inspect._empty else Any
            if (
                inspect.isclass(param_type)
                and issubclass(param_type, BaseModel)
                and param_name in function_args
                and isinstance(function_args[param_name], dict)
            ):
                function_args[param_name] = param_type(**function_args[param_name])
        return function_args

    def _decorator(self, func: Callable):
        if func is None:
            return self
        
        # Create the proper retry-decorated version of completion methods
        # if retry is enabled (default)
        if hasattr(self, 'retry_enabled') and self.retry_enabled:
            max_attempts = getattr(self, 'retry_max_attempts', 3)
            
            # Define retry decorator for completion methods
            completion_retry = retry(
                on=LITELLM_ERRORS,
                attempts=max_attempts
            )
            
            # Create retry-decorated versions of the completion methods
            self._completion_with_retry = completion_retry(self._completion)
            self._async_completion_with_retry = completion_retry(self._async_completion)
        else:
            # If retry is disabled, use the original methods
            self._completion_with_retry = self._completion
            self._async_completion_with_retry = self._async_completion
        
        # Check if the function is async
        is_async = inspect.iscoroutinefunction(func)
        # Check if the function is a method of a class
        is_method = inspect.ismethod(func) or (hasattr(func, "__qualname__") and "." in func.__qualname__)

        return_type = func.__annotations__.get("return")

        if (
            return_type
            and inspect.isclass(return_type)
            and issubclass(return_type, BaseModel)
            and self.json_schema
        ):
            raise ValueError(
                "Cannot use both Pydantic return type hints and json_schema validation together"
            )

        # Check if the function is async
        is_async = inspect.iscoroutinefunction(func)
        # Check if the function is a method of a class
        is_method = inspect.ismethod(func) or (hasattr(func, "__qualname__") and "." in func.__qualname__)

        if is_async:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                self.logger.debug(f"{self.model = }")
                self.logger.debug(f"{self.system = }")
                self.logger.debug(f"{self.dry_run = }")
                self.logger.debug(f"{self.completion_kwargs = }")
                self.logger.debug(f"{self.tools = }")
                self.logger.debug(f"{func = }")
                self.logger.debug(f"{args = }")
                self.logger.debug(f"{kwargs = }")
                self.logger.debug(f"{self.cache = }")
                self.logger.debug(f"{self.create_completion_fn = }")
                self.logger.debug(f"{self.openai_client = }")

                if (
                    self.tools and not self.openai_client
                ):  # assume oai clients support tools
                    assert litellm.supports_function_calling(self.model), (
                        f"Model {self.model} does not support function calling"
                    )

                # Generate tool definitions from regular tools
                self.tool_definitions = []
                if self.tools:
                    self.tool_definitions.extend([
                        self._generate_tool_definition(tool_fn)
                        for tool_fn in self.tools.values()
                    ])
                
                # Add MCP tools if configured
                if self.mcp_servers:
                    mcp_tool_defs = await self._setup_mcp_tools()
                    self.tool_definitions.extend(mcp_tool_defs)
                
                # Set to None if no tools
                if not self.tool_definitions:
                    self.tool_definitions = None

                # Get the function's docstring as the prompt
                prompt_template = dedent(func.__doc__)

                # Get the argument names, default values and values using inspect
                sig = inspect.signature(func)
                arg_names = list(sig.parameters.keys())
                
                # Handle 'self' parameter for class methods
                instance = None
                if is_method and args and len(args) > 0:
                    instance = args[0]  # The first argument is 'self' for instance methods
                    args = args[1:]  # Remove 'self' from args for later processing
                    if arg_names and arg_names[0] == 'self':
                        arg_names = arg_names[1:]  # Remove 'self' from arg_names
                
                arg_values = {
                    name: (
                        sig.parameters[name].default
                        if sig.parameters[name].default is not inspect.Parameter.empty
                        else None
                    )
                    for name in arg_names
                }
                arg_values.update(zip(arg_names, args))
                arg_values.update(kwargs)

                # Extract image arguments
                image_args = {}
                for name, param in sig.parameters.items():
                    if param.annotation == ImageBytes and name in arg_values:
                        image_args[name] = arg_values.pop(name)

                self.logger.debug(f"{arg_values = }")

                # Replace {name} placeholders with argument values
                prompt_text = prompt_template.format(**arg_values)

                # Create the user message with text and images
                content = [{"type": "text", "text": prompt_text}]

                # Add image content
                for img_bytes in image_args.values():
                    img_b64_str = base64.b64encode(img_bytes).decode("utf-8")

                    if self.anthropic:
                        # Check for PNG signature
                        if img_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
                            img_type = "image/png"
                        # Check for JPEG signature
                        elif img_bytes.startswith(b"\xff\xd8"):
                            img_type = "image/jpeg"
                        else:
                            img_type = "image/jpeg"  # fallback
                    else:
                        img_type = "image/jpeg"  # default for non-Anthropic models

                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{img_type};base64,{img_b64_str}"},
                        }
                    )

                user_message = {"content": content, "role": "user"}
                messages = [user_message]

                # Check if the function has a return type hint of a Pydantic model
                return_type = func.__annotations__.get("return")
                
                # Check for dynamic schema first (takes priority)
                dynamic_schema = getattr(async_wrapper if 'async_wrapper' in locals() else wrapper, '_dynamic_schema', None)

                self.logger.debug(f"{return_type = }")
                self.logger.debug(f"{dynamic_schema = }")

                # Add schema instructions before any LLM call if return type requires it
                # Dynamic schema takes priority over return type annotation
                if dynamic_schema and inspect.isclass(dynamic_schema) and issubclass(dynamic_schema, BaseModel):
                    schema = dynamic_schema.model_json_schema()
                    json_schema = json.dumps(schema, indent=2)
                    msg = {
                        "role": "user",
                        "content": (
                            "Format your response according to this JSON schema:\n"
                            f"```json\n{json_schema}\n```\n\n"
                            "Provide the result enclosed in triple backticks with 'json' "
                            "on the first line. Don't put control characters in the wrong "
                            "place or the JSON will be invalid."
                        ),
                    }
                    messages.append(msg)
                elif dynamic_schema and is_django_model(dynamic_schema):
                    # Handle dynamic Django model
                    schema = django_model_to_json_schema(dynamic_schema)
                    json_schema = json.dumps(schema, indent=2)
                    msg = {
                        "role": "user",
                        "content": (
                            "Format your response according to this Django model JSON schema:\n"
                            f"```json\n{json_schema}\n```\n\n"
                            "Provide the result enclosed in triple backticks with 'json' "
                            "on the first line. Don't put control characters in the wrong "
                            "place or the JSON will be invalid."
                        ),
                    }
                    messages.append(msg)
                # Original schema instructions below
                elif (
                    return_type
                    and inspect.isclass(return_type)
                    and issubclass(return_type, BaseModel)
                ):
                    schema = return_type.model_json_schema()
                    json_schema = json.dumps(schema, indent=2)
                    msg = {
                        "role": "user",
                        "content": (
                            "Format your response according to this JSON schema:\n"
                            f"```json\n{json_schema}\n```\n\n"
                            "Provide the result enclosed in triple backticks with 'json' "
                            "on the first line. Don't put control characters in the wrong "
                            "place or the JSON will be invalid."
                        ),
                    }
                    messages.append(msg)
                elif return_type and is_django_model(return_type):
                    # Handle Django model return type
                    schema = django_model_to_json_schema(return_type)
                    json_schema = json.dumps(schema, indent=2)
                    msg = {
                        "role": "user",
                        "content": (
                            "Format your response according to this Django model JSON schema:\n"
                            f"```json\n{json_schema}\n```\n\n"
                            "Provide the result enclosed in triple backticks with 'json' "
                            "on the first line. Don't put control characters in the wrong "
                            "place or the JSON will be invalid."
                        ),
                    }
                    messages.append(msg)
                elif self.json_schema:
                    json_schema = json.dumps(self.json_schema, indent=2)
                    msg = {
                        "role": "user",
                        "content": (
                            "Format your response according to this JSON schema:\n"
                            f"```json\n{json_schema}\n```\n\n"
                            "Provide the result enclosed in triple backticks with 'json' "
                            "on the first line. Don't put control characters in the wrong "
                            "place or the JSON will be invalid."
                        ),
                    }
                    messages.append(msg)

                # Add check for Gemini streaming with tools
                if self.gemini and self.completion_kwargs.get("stream") and self.tools:
                    raise ValueError("Gemini models do not support streaming with tools")

                self.logger.debug("Chat History:")
                for i, msg in enumerate(messages):
                    self.logger.debug(f"Message {i}:")
                    self.logger.debug(f"  Role: {msg.get('role', 'unknown')}")
                    self.logger.debug(f"  Content: {msg.get('content')}")
                    if "tool_calls" in msg:
                        self.logger.debug("  Tool Calls:")
                        for tool_call in msg["tool_calls"]:
                            self.logger.debug(f"    Name: {tool_call.function.name}")
                            self.logger.debug(
                                f"    Arguments: {tool_call.function.arguments}"
                            )
                    if "tool_call_id" in msg:
                        self.logger.debug(f"  Tool Call ID: {msg['tool_call_id']}")
                        self.logger.debug(f"  Tool Name: {msg.get('name')}")

                if self.tool_definitions:
                    self.logger.debug("\nAvailable Tools:")
                    for tool in self.tool_definitions:
                        self.logger.debug(
                            f"  {tool['function']['name']}: {tool['function']['description']}"
                        )

                call = None

                if self.weave_client:
                    call = self.weave_client.create_call(
                        op="Promptic._decorator",
                        inputs={"messages": messages},
                        attributes={
                            "model": self.model,
                            "system": self.system,
                            "tools": self.tool_definitions,
                            "tool_choice": "auto" if self.tool_definitions else None,
                        },
                        display_name="promptic_decorator",
                    )

                try:
                    # Call the LLM with the prompt and tools
                    completion_messages, response = await self._async_completion_with_retry(messages)

                    if call:
                        call.inputs["messages"] = completion_messages

                    if self.completion_kwargs.get("stream"):
                        return await self._async_stream_response(response, call)
                    else:
                        for choice in response.choices:
                            # Handle tool calls if present
                            if (
                                hasattr(choice.message, "tool_calls")
                                and choice.message.tool_calls
                            ):
                                tool_calls = choice.message.tool_calls
                                messages.append(choice.message)

                                for tool_call in tool_calls:
                                    function_name = tool_call.function.name
                                    if function_name in self.tools:
                                        fn_info = self.tools[function_name]
                                        # Check if fn_info is a tuple (new format) or just a function (old format)
                                        if isinstance(fn_info, tuple):
                                            fn, is_class_method = fn_info
                                        else:
                                            fn, is_class_method = fn_info, False
                                        
                                        function_args = json.loads(tool_call.function.arguments)
                                        if self.gemini and "llm_invocation" in function_args:
                                            function_args.pop("llm_invocation")
                                        if self.dry_run:
                                            self.logger.warning(
                                                f"[DRY RUN]: {function_name = } {function_args = }"
                                            )
                                            function_response = f"[DRY RUN] Would have called {function_name = } {function_args = }"
                                        else:
                                            try:
                                                self.logger.debug(
                                                    f"Calling tool {function_name}({function_args}) using {self.model = }"
                                                )
                                                function_args = self._deserialize_pydantic_args(
                                                    fn, function_args
                                                )
                                                
                                                # Store the instance reference for class methods in tool execution
                                                if is_class_method and instance is not None:
                                                    # Handle both async and sync tools for class methods
                                                    tool_timeout = self.tool_timeouts.get(function_name, self.tool_timeout)
                                                    
                                                    if inspect.iscoroutinefunction(fn):
                                                        try:
                                                            function_response = await asyncio.wait_for(
                                                                fn(instance, **function_args), 
                                                                timeout=tool_timeout
                                                            )
                                                        except asyncio.TimeoutError:
                                                            self.logger.error(
                                                                f"Tool {function_name} timed out after {tool_timeout} seconds"
                                                            )
                                                            function_response = f"Error: Tool {function_name} timed out after {tool_timeout} seconds"
                                                    else:
                                                        # For synchronous functions, we need to run in a thread to apply timeout
                                                        loop = asyncio.get_event_loop()
                                                        try:
                                                            function_response = await asyncio.wait_for(
                                                                loop.run_in_executor(
                                                                    None, lambda: fn(instance, **function_args)
                                                                ),
                                                                timeout=tool_timeout
                                                            )
                                                        except asyncio.TimeoutError:
                                                            self.logger.error(
                                                                f"Tool {function_name} timed out after {tool_timeout} seconds"
                                                            )
                                                            function_response = f"Error: Tool {function_name} timed out after {tool_timeout} seconds"
                                                else:
                                                    # Handle both async and sync tools for regular functions
                                                    tool_timeout = self.tool_timeouts.get(function_name, self.tool_timeout)
                                                    
                                                    if inspect.iscoroutinefunction(fn):
                                                        try:
                                                            function_response = await asyncio.wait_for(
                                                                fn(**function_args), 
                                                                timeout=tool_timeout
                                                            )
                                                        except asyncio.TimeoutError:
                                                            self.logger.error(
                                                                f"Tool {function_name} timed out after {tool_timeout} seconds"
                                                            )
                                                            function_response = f"Error: Tool {function_name} timed out after {tool_timeout} seconds"
                                                    else:
                                                        # For synchronous functions, we need to run in a thread to apply timeout
                                                        loop = asyncio.get_event_loop()
                                                        try:
                                                            function_response = await asyncio.wait_for(
                                                                loop.run_in_executor(
                                                                    None, lambda: fn(**function_args)
                                                                ),
                                                                timeout=tool_timeout
                                                            )
                                                        except asyncio.TimeoutError:
                                                            self.logger.error(
                                                                f"Tool {function_name} timed out after {tool_timeout} seconds"
                                                            )
                                                            function_response = f"Error: Tool {function_name} timed out after {tool_timeout} seconds"
                                            except Exception as e:
                                                self.logger.error(
                                                    f"Error calling tool {function_name}({function_args}): {e}"
                                                )
                                                function_response = f"Error calling tool {function_name}({function_args}): {e}"
                                        msg = {
                                            "tool_call_id": tool_call.id,
                                            "role": "tool",
                                            "name": function_name,
                                            "content": to_json(function_response),
                                        }
                                        messages.append(msg)
                                
                                # After all tool calls are processed, get a final response with the tool results
                                completion_messages, response = await self._async_completion_with_retry(messages)
                                
                                if call:
                                    call.inputs["messages"] = completion_messages
                                
                                if self.completion_kwargs.get("stream"):
                                    return await self._async_stream_response(response, call)
                                else:
                                    # Process the final response from the LLM after tools have been used
                                    generated_text = response.choices[0].message.content
                                    result = self._parse_and_validate_response(
                                        generated_text=generated_text,
                                        return_type=return_type,
                                        json_schema=self.json_schema,
                                        dynamic_schema=getattr(wrapper, '_dynamic_schema', None),
                                    )

                                    if call and self.weave_client:
                                        self.weave_client.finish_call(call, output=result)

                                    # For class methods, if the original function is also decorated to process LLM results,
                                    # we need to call it with the instance and the result
                                    if is_method and instance is not None:
                                        # Add logging to debug class method invocation
                                        self.logger.debug(f"Calling class method {func.__name__} with instance: {instance}")
                                        
                                        # Check if the function has a '_result' parameter
                                        sig = inspect.signature(func)
                                        updated_args = arg_values.copy()
                                        
                                        # Only add result parameter if it exists in the function signature
                                        if '_result' in sig.parameters:
                                            updated_args['_result'] = result
                                            return await func(instance, **updated_args)
                                        else:
                                            # If no _result parameter, just return the result directly
                                            # This allows class methods to work like standalone functions
                                            return result
                                    
                                    return result
                                continue

                            # GPT and Claude have `stop` when conversation is complete
                            # Gemini has `stop` as a finish reason when tools are used
                            elif choice.finish_reason in ["stop", "max_tokens", "length"]:
                                generated_text = choice.message.content
                                result = self._parse_and_validate_response(
                                    generated_text=generated_text,
                                    return_type=return_type,
                                    json_schema=self.json_schema,
                                )

                                if call and self.weave_client:
                                    self.weave_client.finish_call(call, output=result)
                                
                                # For class methods, if the original function is also decorated to process LLM results,
                                # we need to call it with the instance and the result
                                if is_method and instance is not None:
                                    # Add logging to debug class method invocation
                                    self.logger.debug(f"Calling class method {func.__name__} with instance: {instance}")
                                    
                                    # Check if the function has a '_result' parameter
                                    sig = inspect.signature(func)
                                    updated_args = arg_values.copy()
                                    
                                    # Only add result parameter if it exists in the function signature
                                    if '_result' in sig.parameters:
                                        updated_args['_result'] = result
                                        return await func(instance, **updated_args)
                                    else:
                                        # If no _result parameter, just return the result directly
                                        # This allows class methods to work like standalone functions
                                        return result
                                
                                return result

                except LITELLM_ERRORS as e:
                    self.logger.warning(f"Error: {e}")
                    raise

            # Add methods explicitly
            async_wrapper.tool = self.tool
            async_wrapper.clear = self.clear
            async_wrapper.message = self.message
            async_wrapper.instance = self
            
            # Always add dynamic schema support
            async_wrapper._dynamic_schema = None
            
            def setSchema(schema_model):
                """Set the dynamic Pydantic or Django model schema for this function"""
                if not (
                    (inspect.isclass(schema_model) and issubclass(schema_model, BaseModel))
                    or is_django_model(schema_model)
                ):
                    raise ValueError("schema_model must be a Pydantic BaseModel or Django Model class")
                async_wrapper._dynamic_schema = schema_model
            
            async_wrapper.setSchema = setSchema

            # Automatically expose all other attributes from self
            for attr_name, attr_value in self.__dict__.items():
                if not attr_name.startswith("_"):  # Skip private attributes
                    setattr(async_wrapper, attr_name, attr_value)

            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                self.logger.debug(f"{self.model = }")
                self.logger.debug(f"{self.system = }")
                self.logger.debug(f"{self.dry_run = }")
                self.logger.debug(f"{self.completion_kwargs = }")
                self.logger.debug(f"{self.tools = }")
                self.logger.debug(f"{func = }")
                self.logger.debug(f"{args = }")
                self.logger.debug(f"{kwargs = }")
                self.logger.debug(f"{self.cache = }")
                self.logger.debug(f"{self.create_completion_fn = }")
                self.logger.debug(f"{self.openai_client = }")

                if (
                    self.tools and not self.openai_client
                ):  # assume oai clients support tools
                    assert litellm.supports_function_calling(self.model), (
                        f"Model {self.model} does not support function calling"
                    )

                # Generate tool definitions from regular tools
                self.tool_definitions = []
                if self.tools:
                    self.tool_definitions.extend([
                        self._generate_tool_definition(tool_fn)
                        for tool_fn in self.tools.values()
                    ])
                
                # Add MCP tools if configured (sync wrapper - run async code)
                if self.mcp_servers:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    try:
                        mcp_tool_defs = loop.run_until_complete(self._setup_mcp_tools())
                        self.tool_definitions.extend(mcp_tool_defs)
                    finally:
                        loop.close()
                
                # Set to None if no tools
                if not self.tool_definitions:
                    self.tool_definitions = None

                # Get the function's docstring as the prompt
                prompt_template = dedent(func.__doc__)

                # Get the argument names, default values and values using inspect
                sig = inspect.signature(func)
                arg_names = list(sig.parameters.keys())
                
                # Handle 'self' parameter for class methods
                instance = None
                if is_method and args and len(args) > 0:
                    instance = args[0]  # The first argument is 'self' for instance methods
                    args = args[1:]  # Remove 'self' from args for later processing
                    if arg_names and arg_names[0] == 'self':
                        arg_names = arg_names[1:]  # Remove 'self' from arg_names
                
                arg_values = {
                    name: (
                        sig.parameters[name].default
                        if sig.parameters[name].default is not inspect.Parameter.empty
                        else None
                    )
                    for name in arg_names
                }
                arg_values.update(zip(arg_names, args))
                arg_values.update(kwargs)

                # Extract image arguments
                image_args = {}
                for name, param in sig.parameters.items():
                    if param.annotation == ImageBytes and name in arg_values:
                        image_args[name] = arg_values.pop(name)

                self.logger.debug(f"{arg_values = }")

                # Replace {name} placeholders with argument values
                prompt_text = prompt_template.format(**arg_values)

                # Create the user message with text and images
                content = [{"type": "text", "text": prompt_text}]

                # Add image content
                for img_bytes in image_args.values():
                    img_b64_str = base64.b64encode(img_bytes).decode("utf-8")

                    if self.anthropic:
                        # Check for PNG signature
                        if img_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
                            img_type = "image/png"
                        # Check for JPEG signature
                        elif img_bytes.startswith(b"\xff\xd8"):
                            img_type = "image/jpeg"
                        else:
                            img_type = "image/jpeg"  # fallback
                    else:
                        img_type = "image/jpeg"  # default for non-Anthropic models

                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{img_type};base64,{img_b64_str}"},
                        }
                    )

                user_message = {"content": content, "role": "user"}
                messages = [user_message]

                # Check if the function has a return type hint of a Pydantic model
                return_type = func.__annotations__.get("return")
                
                # Check for dynamic schema first (takes priority)
                dynamic_schema = getattr(async_wrapper if 'async_wrapper' in locals() else wrapper, '_dynamic_schema', None)

                self.logger.debug(f"{return_type = }")
                self.logger.debug(f"{dynamic_schema = }")

                # Add schema instructions before any LLM call if return type requires it
                # Dynamic schema takes priority over return type annotation
                if dynamic_schema and inspect.isclass(dynamic_schema) and issubclass(dynamic_schema, BaseModel):
                    schema = dynamic_schema.model_json_schema()
                    json_schema = json.dumps(schema, indent=2)
                    msg = {
                        "role": "user",
                        "content": (
                            "Format your response according to this JSON schema:\n"
                            f"```json\n{json_schema}\n```\n\n"
                            "Provide the result enclosed in triple backticks with 'json' "
                            "on the first line. Don't put control characters in the wrong "
                            "place or the JSON will be invalid."
                        ),
                    }
                    messages.append(msg)
                elif dynamic_schema and is_django_model(dynamic_schema):
                    # Handle dynamic Django model
                    schema = django_model_to_json_schema(dynamic_schema)
                    json_schema = json.dumps(schema, indent=2)
                    msg = {
                        "role": "user",
                        "content": (
                            "Format your response according to this Django model JSON schema:\n"
                            f"```json\n{json_schema}\n```\n\n"
                            "Provide the result enclosed in triple backticks with 'json' "
                            "on the first line. Don't put control characters in the wrong "
                            "place or the JSON will be invalid."
                        ),
                    }
                    messages.append(msg)
                # Original schema instructions below
                elif (
                    return_type
                    and inspect.isclass(return_type)
                    and issubclass(return_type, BaseModel)
                ):
                    schema = return_type.model_json_schema()
                    json_schema = json.dumps(schema, indent=2)
                    msg = {
                        "role": "user",
                        "content": (
                            "Format your response according to this JSON schema:\n"
                            f"```json\n{json_schema}\n```\n\n"
                            "Provide the result enclosed in triple backticks with 'json' "
                            "on the first line. Don't put control characters in the wrong "
                            "place or the JSON will be invalid."
                        ),
                    }
                    messages.append(msg)
                elif return_type and is_django_model(return_type):
                    # Handle Django model return type
                    schema = django_model_to_json_schema(return_type)
                    json_schema = json.dumps(schema, indent=2)
                    msg = {
                        "role": "user",
                        "content": (
                            "Format your response according to this Django model JSON schema:\n"
                            f"```json\n{json_schema}\n```\n\n"
                            "Provide the result enclosed in triple backticks with 'json' "
                            "on the first line. Don't put control characters in the wrong "
                            "place or the JSON will be invalid."
                        ),
                    }
                    messages.append(msg)
                elif self.json_schema:
                    json_schema = json.dumps(self.json_schema, indent=2)
                    msg = {
                        "role": "user",
                        "content": (
                            "Format your response according to this JSON schema:\n"
                            f"```json\n{json_schema}\n```\n\n"
                            "Provide the result enclosed in triple backticks with 'json' "
                            "on the first line. Don't put control characters in the wrong "
                            "place or the JSON will be invalid."
                        ),
                    }
                    messages.append(msg)

                # Add check for Gemini streaming with tools
                if self.gemini and self.completion_kwargs.get("stream") and self.tools:
                    raise ValueError("Gemini models do not support streaming with tools")

                self.logger.debug("Chat History:")
                for i, msg in enumerate(messages):
                    self.logger.debug(f"Message {i}:")
                    self.logger.debug(f"  Role: {msg.get('role', 'unknown')}")
                    self.logger.debug(f"  Content: {msg.get('content')}")
                    if "tool_calls" in msg:
                        self.logger.debug("  Tool Calls:")
                        for tool_call in msg["tool_calls"]:
                            self.logger.debug(f"    Name: {tool_call.function.name}")
                            self.logger.debug(
                                f"    Arguments: {tool_call.function.arguments}"
                            )
                    if "tool_call_id" in msg:
                        self.logger.debug(f"  Tool Call ID: {msg['tool_call_id']}")
                        self.logger.debug(f"  Tool Name: {msg.get('name')}")

                if self.tool_definitions:
                    self.logger.debug("\nAvailable Tools:")
                    for tool in self.tool_definitions:
                        self.logger.debug(
                            f"  {tool['function']['name']}: {tool['function']['description']}"
                        )

                call = None

                if self.weave_client:
                    call = self.weave_client.create_call(
                        op="Promptic._decorator",
                        inputs={"messages": messages},
                        attributes={
                            "model": self.model,
                            "system": self.system,
                            "tools": self.tool_definitions,
                            "tool_choice": "auto" if self.tool_definitions else None,
                        },
                        display_name="promptic_decorator",
                    )

                try:
                    # Call the LLM with the prompt and tools
                    completion_messages, response = self._completion_with_retry(messages)

                    if call:
                        call.inputs["messages"] = completion_messages

                    if self.completion_kwargs.get("stream"):
                        return self._stream_response(response, call)
                    else:
                        for choice in response.choices:
                            # Handle tool calls if present
                            if (
                                hasattr(choice.message, "tool_calls")
                                and choice.message.tool_calls
                            ):
                                tool_calls = choice.message.tool_calls
                                messages.append(choice.message)

                                for tool_call in tool_calls:
                                    function_name = tool_call.function.name
                                    if function_name in self.tools:
                                        fn_info = self.tools[function_name]
                                        # Check if fn_info is a tuple (new format) or just a function (old format)
                                        if isinstance(fn_info, tuple):
                                            fn, is_class_method = fn_info
                                        else:
                                            fn, is_class_method = fn_info, False
                                        
                                        function_args = json.loads(tool_call.function.arguments)
                                        if self.gemini and "llm_invocation" in function_args:
                                            function_args.pop("llm_invocation")
                                        if self.dry_run:
                                            self.logger.warning(
                                                f"[DRY RUN]: {function_name = } {function_args = }"
                                            )
                                            function_response = f"[DRY RUN] Would have called {function_name = } {function_args = }"
                                        else:
                                            try:
                                                self.logger.debug(
                                                    f"Calling tool {function_name}({function_args}) using {self.model = }"
                                                )
                                                function_args = self._deserialize_pydantic_args(
                                                    fn, function_args
                                                )
                                                
                                                # Store the instance reference for class methods in tool execution
                                                if is_class_method and instance is not None:
                                                    # Handle both async and sync tools for class methods
                                                    tool_timeout = self.tool_timeouts.get(function_name, self.tool_timeout)
                                                    
                                                    if inspect.iscoroutinefunction(fn):
                                                        raise ValueError(
                                                            f"Cannot call async tool function {function_name} from sync context. "
                                                            f"Either make the decorated function async or make the tool function sync."
                                                        )
                                                    function_response = fn(instance, **function_args)
                                                else:
                                                    # Handle both async and sync tools for regular functions
                                                    tool_timeout = self.tool_timeouts.get(function_name, self.tool_timeout)
                                                    
                                                    if inspect.iscoroutinefunction(fn):
                                                        raise ValueError(
                                                            f"Cannot call async tool function {function_name} from sync context. "
                                                            f"Either make the decorated function async or make the tool function sync."
                                                        )
                                                    function_response = fn(**function_args)
                                            except Exception as e:
                                                self.logger.error(
                                                    f"Error calling tool {function_name}({function_args}): {e}"
                                                )
                                                function_response = f"Error calling tool {function_name}({function_args}): {e}"
                                        msg = {
                                            "tool_call_id": tool_call.id,
                                            "role": "tool",
                                            "name": function_name,
                                            "content": to_json(function_response),
                                        }
                                        messages.append(msg)
                                
                                # After all tool calls are processed, get a final response with the tool results
                                completion_messages, response = self._completion_with_retry(messages)
                                
                                if call:
                                    call.inputs["messages"] = completion_messages
                                
                                if self.completion_kwargs.get("stream"):
                                    return self._stream_response(response, call)
                                else:
                                    # Process the final response from the LLM after tools have been used
                                    generated_text = response.choices[0].message.content
                                    result = self._parse_and_validate_response(
                                        generated_text=generated_text,
                                        return_type=return_type,
                                        json_schema=self.json_schema,
                                        dynamic_schema=getattr(wrapper, '_dynamic_schema', None),
                                    )

                                    if call and self.weave_client:
                                        self.weave_client.finish_call(call, output=result)
                                    
                                    # For class methods, if the original function is also decorated to process LLM results,
                                    # we need to call it with the instance and the result
                                    if is_method and instance is not None:
                                        # Add logging to debug class method invocation
                                        self.logger.debug(f"Calling class method {func.__name__} with instance: {instance}")
                                        
                                        # Check if the function has a '_result' parameter
                                        sig = inspect.signature(func)
                                        updated_args = arg_values.copy()
                                        
                                        # Only add result parameter if it exists in the function signature
                                        if '_result' in sig.parameters:
                                            updated_args['_result'] = result
                                            return func(instance, **updated_args)
                                        else:
                                            # If no _result parameter, just return the result directly
                                            # This allows class methods to work like standalone functions
                                            return result
                                    
                                    return result
                                continue

                            # GPT and Claude have `stop` when conversation is complete
                            # Gemini has `stop` as a finish reason when tools are used
                            elif choice.finish_reason in ["stop", "max_tokens", "length"]:
                                generated_text = choice.message.content
                                result = self._parse_and_validate_response(
                                    generated_text,
                                    return_type=return_type,
                                    json_schema=self.json_schema,
                                    dynamic_schema=getattr(async_wrapper, '_dynamic_schema', None),
                                )

                                if call and self.weave_client:
                                    self.weave_client.finish_call(call, output=result)
                                
                                # For class methods, if the original function is also decorated to process LLM results,
                                # we need to call it with the instance and the result
                                if is_method and instance is not None:
                                    # Add logging to debug class method invocation
                                    self.logger.debug(f"Calling class method {func.__name__} with instance: {instance}")
                                    
                                    # Check if the function has a '_result' parameter
                                    sig = inspect.signature(func)
                                    updated_args = arg_values.copy()
                                    
                                    # Only add result parameter if it exists in the function signature
                                    if '_result' in sig.parameters:
                                        updated_args['_result'] = result
                                        return func(instance, **updated_args)
                                    else:
                                        # If no _result parameter, just return the result directly
                                        # This allows class methods to work like standalone functions
                                        return result
                                
                                return result

                except LITELLM_ERRORS as e:
                    self.logger.warning(f"Error: {e}")
                    raise

            # Add methods explicitly
            wrapper.tool = self.tool
            wrapper.clear = self.clear
            wrapper.message = self.message
            wrapper.instance = self
            
            # Always add dynamic schema support
            wrapper._dynamic_schema = None
            
            def setSchema(schema_model):
                """Set the dynamic Pydantic or Django model schema for this function"""
                if not (
                    (inspect.isclass(schema_model) and issubclass(schema_model, BaseModel))
                    or is_django_model(schema_model)
                ):
                    raise ValueError("schema_model must be a Pydantic BaseModel or Django Model class")
                wrapper._dynamic_schema = schema_model
            
            wrapper.setSchema = setSchema

            # Automatically expose all other attributes from self
            for attr_name, attr_value in self.__dict__.items():
                if not attr_name.startswith("_"):  # Skip private attributes
                    setattr(wrapper, attr_name, attr_value)

            return wrapper

    def _stream_response(self, response, call=None):
        current_tool_calls = {}
        current_index = None
        accumulated_response = ""

        for part in response:
            # Handle tool calls in streaming mode
            if (
                hasattr(part.choices[0].delta, "tool_calls")
                and part.choices[0].delta.tool_calls
            ):
                tool_calls = part.choices[0].delta.tool_calls

                for tool_call in tool_calls:
                    # If we have an ID and name, this is the start of a new tool call
                    if tool_call.id:
                        current_index = tool_call.index
                        current_tool_calls[current_index] = {
                            "id": tool_call.id,
                            "name": tool_call.function.name,
                            "arguments": "",
                        }

                    # If we don't have an ID but have arguments, append to current tool call
                    elif tool_call.function.arguments and current_index is not None:
                        current_tool_calls[current_index]["arguments"] += (
                            tool_call.function.arguments
                        )

                        # Try to execute if arguments look complete
                        tool_info = current_tool_calls[current_index]
                        try:
                            args_str = tool_info["arguments"]
                            if (
                                args_str.strip() and args_str[-1] == "}"
                            ):  # Check if arguments look complete
                                try:
                                    function_args = json.loads(args_str)
                                    if (
                                        self.gemini
                                        and "llm_invocation" in function_args
                                    ):
                                        function_args.pop("llm_invocation")

                                    if tool_info["name"] in self.tools:
                                        fn_info = self.tools[tool_info["name"]]
                                        # Check if fn_info is a tuple (new format) or just a function (old format)
                                        if isinstance(fn_info, tuple):
                                            fn, is_class_method = fn_info
                                        else:
                                            fn, is_class_method = fn_info, False
                                        
                                        function_args = self._deserialize_pydantic_args(
                                            fn, function_args
                                        )
                                        
                                        # Store the instance reference for class methods in tool execution
                                        if is_class_method and instance is not None:
                                            # Handle both async and sync tools for class methods
                                            if inspect.iscoroutinefunction(fn):
                                                raise ValueError(
                                                    f"Cannot call async tool function {tool_info['name']} from sync context. "
                                                    f"Either make the decorated function async or make the tool function sync."
                                                )
                                            function_response = fn(instance, **function_args)
                                        else:
                                            # Handle both async and sync tools for regular functions
                                            if inspect.iscoroutinefunction(fn):
                                                raise ValueError(
                                                    f"Cannot call async tool function {tool_info['name']} from sync context. "
                                                    f"Either make the decorated function async or make the tool function sync."
                                                )
                                            function_response = fn(**function_args)
                                    elif tool_info["name"] in self.mcp_tools:
                                        # MCP tool execution (sync context)
                                        mcp_info = self.mcp_tools[tool_info["name"]]
                                        client = mcp_info["client"]
                                        original_name = mcp_info["original_name"]
                                        
                                        # Run async MCP call in sync context
                                        import asyncio
                                        loop = asyncio.new_event_loop()
                                        try:
                                            function_response = loop.run_until_complete(
                                                client.call_tool(original_name, function_args)
                                            )
                                        finally:
                                            loop.close()
                                    else:
                                        self.logger.warning(f"Tool {tool_info['name']} not found")
                                        function_response = f"Error: Tool {tool_info['name']} not found"
                                except json.JSONDecodeError:
                                    # Arguments not complete yet, continue accumulating
                                    continue
                        except Exception as e:
                            self.logger.error(f"Error executing tool: {e}")
                            self.logger.exception(e)
                            continue

            # Stream regular content and accumulate
            if (
                hasattr(part.choices[0].delta, "content")
                and part.choices[0].delta.content
            ):
                content = part.choices[0].delta.content
                accumulated_response += content
                yield content

        # After streaming is complete, add to state if memory is enabled
        if self.state:
            self.state.add_message(
                {"content": accumulated_response, "role": "assistant"}
            )

        if call and self.weave_client:
            self.weave_client.finish_call(call, output=accumulated_response)

    async def _async_stream_response(self, response, call=None):
        """Async version of _stream_response for use with async functions."""
        current_tool_calls = {}
        current_index = None
        accumulated_response = ""

        async for part in response:
            # Handle tool calls in streaming mode
            if (
                hasattr(part.choices[0].delta, "tool_calls")
                and part.choices[0].delta.tool_calls
            ):
                tool_calls = part.choices[0].delta.tool_calls

                for tool_call in tool_calls:
                    # If we have an ID and name, this is the start of a new tool call
                    if tool_call.id:
                        current_index = tool_call.index
                        current_tool_calls[current_index] = {
                            "id": tool_call.id,
                            "name": tool_call.function.name,
                            "arguments": "",
                        }

                    # If we don't have an ID but have arguments, append to current tool call
                    elif tool_call.function.arguments and current_index is not None:
                        current_tool_calls[current_index]["arguments"] += (
                            tool_call.function.arguments
                        )

                        # Try to execute if arguments look complete
                        tool_info = current_tool_calls[current_index]
                        try:
                            args_str = tool_info["arguments"]
                            if (
                                args_str.strip() and args_str[-1] == "}"
                            ):  # Check if arguments look complete
                                try:
                                    function_args = json.loads(args_str)
                                    if (
                                        self.gemini
                                        and "llm_invocation" in function_args
                                    ):
                                        function_args.pop("llm_invocation")

                                    if tool_info["name"] in self.tools:
                                        fn_info = self.tools[tool_info["name"]]
                                        # Check if fn_info is a tuple (new format) or just a function (old format)
                                        if isinstance(fn_info, tuple):
                                            fn, is_class_method = fn_info
                                        else:
                                            fn, is_class_method = fn_info, False
                                        
                                        function_args = self._deserialize_pydantic_args(
                                            fn, function_args
                                        )
                                        
                                        # Store the instance reference for class methods in tool execution
                                        if is_class_method and instance is not None:
                                            # Handle both async and sync tools for class methods
                                            if inspect.iscoroutinefunction(fn):
                                                function_response = await fn(instance, **function_args)
                                            else:
                                                function_response = fn(instance, **function_args)
                                        else:
                                            # Handle both async and sync tools for regular functions
                                            if inspect.iscoroutinefunction(fn):
                                                function_response = await fn(**function_args)
                                            else:
                                                function_response = fn(**function_args)
                                    elif tool_info["name"] in self.mcp_tools:
                                        # MCP tool execution (async context)
                                        mcp_info = self.mcp_tools[tool_info["name"]]
                                        client = mcp_info["client"]
                                        original_name = mcp_info["original_name"]
                                        
                                        # Call MCP tool with timeout
                                        tool_timeout = self.tool_timeouts.get(tool_info["name"], self.tool_timeout)
                                        try:
                                            function_response = await asyncio.wait_for(
                                                client.call_tool(original_name, function_args),
                                                timeout=tool_timeout
                                            )
                                        except asyncio.TimeoutError:
                                            self.logger.error(
                                                f"MCP tool {tool_info['name']} timed out after {tool_timeout} seconds"
                                            )
                                            function_response = f"Error: MCP tool {tool_info['name']} timed out after {tool_timeout} seconds"
                                    else:
                                        self.logger.warning(f"Tool {tool_info['name']} not found")
                                        function_response = f"Error: Tool {tool_info['name']} not found"
                                except json.JSONDecodeError:
                                    # Arguments not complete yet, continue accumulating
                                    continue
                        except Exception as e:
                            self.logger.error(f"Error executing tool: {e}")
                            self.logger.exception(e)
                            continue

            # Stream regular content and accumulate
            if (
                hasattr(part.choices[0].delta, "content")
                and part.choices[0].delta.content
            ):
                content = part.choices[0].delta.content
                accumulated_response += content
                yield content

        # After streaming is complete, add to state if memory is enabled
        if self.state:
            self.state.add_message(
                {"content": accumulated_response, "role": "assistant"}
            )

        if call and self.weave_client:
            self.weave_client.finish_call(call, output=accumulated_response)

    def clear(self) -> None:
        """Clear all messages from the state if it exists.

        Raises:
            ValueError: If memory/state is not enabled
        """
        if not self.memory or not self.state:
            raise ValueError("Cannot clear state: memory/state is not enabled")
        self.state.clear()


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)


def to_json(obj: Any) -> str:
    return json.dumps(obj, cls=CustomJSONEncoder, ensure_ascii=False)


llm = Promptic.decorate
