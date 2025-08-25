# Echo SDK

A bridge library for developing plugins for the Echo multi-agent system.

## 🎯 Purpose

- **Clean Interfaces**: Well-defined contracts for plugin development
- **Zero Core Dependencies**: Plugins only depend on the SDK, not the core system
- **Independent Distribution**: Plugins can be distributed as standalone packages
- **Version Management**: SDK versioning with compatibility checks
- **Testing Isolation**: Test plugins without running the core system
- **Auto-Registration**: Automatic plugin discovery through global registry
- **Hybrid Discovery**: Support for both pip-installable and directory-based plugins

## 📚 Core Concepts

### Plugin Interface (`BasePlugin`)

Every plugin must implement the `BasePlugin` interface:

- `get_metadata()`: Returns `PluginMetadata` with name, version, capabilities, and LLM requirements
- `create_agent()`: Factory method for creating agent instances
- `validate_dependencies()`: Optional dependency validation
- `get_config_schema()`: Optional configuration schema
- `health_check()`: Optional health check implementation

### Agent Interface (`BasePluginAgent`)

Every agent must implement the `BasePluginAgent` interface:

- `get_tools()`: Returns list of LangChain tools
- `get_system_prompt()`: Returns the system prompt for the agent
- `bind_model()`: Binds tools to an LLM model (inherited from base class)
- `initialize()`: Initializes the agent
- `cleanup()`: Cleans up agent resources
- `create_agent_node()`: Creates LangGraph node function (inherited from base class)
- `should_continue()`: Decides whether to call tools or return to coordinator (inherited from base class)

### Plugin Registry

The SDK provides a global registry for plugin discovery:

- `register_plugin(plugin_class)`: Register a plugin class with the global registry
- `discover_plugins()`: Discover all registered plugins (used by core system)
- `get_plugin_registry()`: Access the global registry instance

### Plugin Contracts (`PluginContract`)

The bridge between core system and plugins:

- Wraps plugin classes for standardized interaction
- Provides validation and health check interfaces
- Enables communication without direct imports

## 🔧 Advanced Features

### Plugin Discovery

The SDK provides comprehensive plugin discovery capabilities:

```python
from echo_sdk import auto_discover_plugins, auto_discover_all_plugins

# Discover pip-installable plugins only
pip_count = auto_discover_plugins()

# Discover all plugins (pip + directory-based)
results = auto_discover_all_plugins()
```

### Discovery Functions

```python
from echo_sdk.utils import (
    # Pip discovery
    auto_discover_plugins,
    get_plugin_discovery_stats,
    list_installed_plugin_packages,
    reset_discovery_manager,

    # Hybrid discovery
    auto_discover_all_plugins,
    get_hybrid_discovery_stats,
    is_directory_discovery_enabled,
    get_configured_plugin_directories,
    reset_hybrid_discovery,
)
```

### Directory-Based Plugin Discovery

Enable directory-based plugin loading via environment variables:

```bash
# Enable directory discovery
export ECHO_ENABLE_DIRECTORY_PLUGINS=true

# Configure plugin directories
export ECHO_PLUGIN_DIRS="/path/to/plugins,/another/path"
export ECHO_PLUGIN_DIR="./plugins"
```

### Plugin Validation

The SDK includes comprehensive validation:

```python
from echo_sdk.utils import validate_plugin_structure

errors = validate_plugin_structure(MyPlugin)
if errors:
    print("Plugin validation failed:", errors)
```

### Model Configuration

The SDK provides flexible model configuration through `ModelConfig`:

```python
from echo_sdk.base.metadata import ModelConfig

config = ModelConfig(
    provider="openai",
    model_name="gpt-4o",
    temperature=0.1,
    max_tokens=1024,
    additional_params={"top_p": 0.9}
)
```

### Version Compatibility

Check SDK compatibility:

```python
from echo_sdk.utils import check_compatibility

is_compatible = check_compatibility(">=0.1.0,<0.1.0", "1.2.0")
```

### Health Checks

Implement custom health checks:

```python
class MyPlugin(BasePlugin):
    @staticmethod
    def health_check():
        return {
            "healthy": True,
            "details": "All systems operational"
        }
```

## 📦 Package Structure

```
sdk/
├── src/echo_sdk/           # SDK source code
│   ├── __init__.py         # Main SDK exports
│   ├── base/               # Core interfaces
│   │   ├── __init__.py
│   │   ├── agent.py        # BasePluginAgent interface
│   │   ├── plugin.py       # BasePlugin interface
│   │   ├── metadata.py     # PluginMetadata, ModelConfig
│   │   └── loggable.py     # Loggable base class
│   ├── tools/              # Tool utilities
│   │   ├── __init__.py
│   │   ├── decorators.py   # @tool decorator (LangChain tool wrapper)
│   │   └── registry.py     # Tool registry
│   ├── registry/           # Plugin registry system
│   │   ├── __init__.py
│   │   ├── contracts.py    # PluginContract wrapper
│   │   └── plugin_registry.py # Global registry
│   ├── types/              # Type definitions
│   │   ├── __init__.py
│   │   ├── state.py        # AgentState TypedDict
│   │   └── messages.py     # LangChain message types
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   ├── validation.py   # Plugin validation
│   │   ├── helpers.py      # Version compatibility
│   │   ├── plugin_discovery.py # Pip plugin discovery
│   │   └── hybrid_discovery.py # Combined discovery
│   └── examples/           # Template examples
│       ├── __init__.py
│       └── template_plugin/ # Complete plugin template
├── pyproject.toml          # Package configuration
├── README.md               # This documentation
└── LICENSE                 # MIT license
```

## 🔧 Key Features

### Core Dependencies

- **LangChain Core**: For tool definitions and model binding
- **LangGraph**: For multi-agent orchestration
- **Pydantic**: For data validation and serialization
- **Python 3.13+**: Modern Python features and type hints

### Version Information

- **Current Version**: 0.1.0
- **Python Support**: 3.13+
- **LangChain Core**: >=0.3.74,<0.4.0
- **LangGraph**: >=0.6.5,<0.7.0
- **Pydantic**: >=2.11.7,<3.0.0

### Agent State Management

The SDK provides comprehensive state management for multi-agent workflows:

```python
from echo_sdk.types.state import AgentState

# State includes:
# - messages: LangChain message sequence
# - current_agent: Active agent identifier
# - hops: Hop counter for loop prevention
# - tool_hops: Tool call counter
# - agent_hops: Agent transition counter
# - plugin_context: Plugin-specific context
# - routing_history: Agent routing history
```

## 🔍 Plugin Discovery System

### Automatic Discovery

The SDK automatically discovers plugins through multiple mechanisms:

1. **Pip-Installable Plugins**: Automatically detects and imports plugins installed via pip
2. **Directory-Based Plugins**: Scans configured directories for plugin modules
3. **Hybrid Discovery**: Combines both methods for comprehensive plugin coverage

### Discovery Functions

```python
from echo_sdk.utils import (
    # Pip discovery
    auto_discover_plugins,
    get_plugin_discovery_stats,
    list_installed_plugin_packages,
    reset_discovery_manager,

    # Hybrid discovery
    auto_discover_all_plugins,
    get_hybrid_discovery_stats,
    is_directory_discovery_enabled,
    get_configured_plugin_directories,
    reset_hybrid_discovery,
)
```

### Discovery Statistics

Get comprehensive discovery information:

```python
from echo_sdk import get_hybrid_discovery_stats

stats = get_hybrid_discovery_stats()
print(f"Total plugins: {stats['total_plugins']}")
print(f"Pip plugins: {stats['pip_plugins']}")
print(f"Directory plugins: {stats['directory_plugins']}")
print(f"Discovery sources: {stats['discovery_sources']}")
```

### Environment Configuration

The SDK supports environment-based configuration for plugin discovery:

```bash
# Enable directory-based plugin discovery
export ECHO_ENABLE_DIRECTORY_PLUGINS=true

# Configure plugin directories (comma-separated)
export ECHO_PLUGIN_DIRS="/path/to/plugins,/another/path"

# Set default plugin directory
export ECHO_PLUGIN_DIR="./plugins"

# Configure agent behavior
export ECHO_MAX_AGENT_HOPS=5
export ECHO_MAX_TOOL_HOPS=25
```

## 🧪 Testing

Test your plugins in isolation using SDK contracts:

```python
import pytest
from echo_sdk import PluginContract, discover_plugins
from echo_sdk.utils import validate_plugin_structure


def test_my_plugin():
    # Test plugin structure
    errors = validate_plugin_structure(MyPlugin)
    assert not errors, f"Plugin validation failed: {errors}"

    # Test plugin contract
    contract = PluginContract(MyPlugin)
    assert contract.is_valid()

    # Test metadata
    metadata = contract.get_metadata()
    assert metadata.name == "my_plugin"
    assert metadata.version

    # Test agent creation
    agent = contract.create_agent()
    tools = agent.get_tools()
    assert len(tools) > 0

    # Test health check
    health = contract.health_check()
    assert health.get("healthy", False)


def test_plugin_discovery():
    # Test that plugin is discoverable via SDK
    plugins = discover_plugins()
    plugin_names = [p.name for p in plugins]
    assert "my_plugin" in plugin_names


def test_discovery_reset():
    # Test discovery state management
    from echo_sdk import reset_hybrid_discovery

    # Reset discovery state
    reset_hybrid_discovery()

    # Rediscover plugins
    results = auto_discover_all_plugins()
    assert results['total_plugins'] >= 0


def test_agent_interface():
    """Test that agent implements required interface."""
    agent = MyAgent(MyPlugin.get_metadata())
    
    # Test required methods
    assert hasattr(agent, 'get_tools')
    assert hasattr(agent, 'get_system_prompt')
    assert hasattr(agent, 'initialize')
    assert hasattr(agent, 'cleanup')
    
    # Test tool binding
    tools = agent.get_tools()
    assert isinstance(tools, list)
    assert all(hasattr(tool, 'name') for tool in tools)

## 📋 Plugin Template

The SDK includes a complete plugin template at `examples/template_plugin/` with:

- **Proper Project Structure**: Standard plugin package layout
- **Complete Implementation**: All required methods and interfaces
- **Documentation**: Comprehensive docstrings and examples
- **Validation Examples**: Dependency and health check implementations
- **Tool Examples**: Multiple tool types and patterns

### Template Features

The template plugin demonstrates:

```python
# Complete metadata with all fields
PluginMetadata(
    name="template_plugin",
    version="0.1.0",
    description="Template plugin demonstrating Echo SDK usage",
    capabilities=["example_capability", "template_operation", "sdk_demonstration"],
    llm_requirements={
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.1,
        "max_tokens": 1024,
    },
    agent_type="specialized",
    system_prompt="You are a template agent for demonstration purposes.",
    dependencies=["echo-sdk>=0.1.0,<1.0.0"],
    sdk_version=">=0.1.0,<1.0.0",
)

# Dependency validation
@staticmethod
def validate_dependencies() -> list[str]:
    errors = []
    try:
        import echo_sdk
    except ImportError:
        errors.append("echo-sdk is required")
    return errors

# Configuration schema
@staticmethod
def get_config_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "api_key": {"type": "string", "description": "API key for service"},
            "timeout": {"type": "integer", "default": 30},
        },
        "required": ["api_key"],
    }

# Health check implementation
@staticmethod
def health_check() -> dict:
    return {
        "healthy": True,
        "details": "Template plugin is operational",
        "checks": {"dependencies": "OK", "configuration": "OK"},
    }
```

Study this template to understand best practices for SDK-based plugin development.

## 🔒 Security Features

The SDK provides security boundaries and validation:

- **Plugin Structure Validation**: Comprehensive validation of plugin interfaces and implementations
- **Dependency Checking**: Validates plugin dependencies and SDK version compatibility
- **Safe Tool Execution**: Tool validation and type checking for safe execution
- **Version Compatibility**: Semantic version checking and compatibility enforcement
- **Health Monitoring**: Plugin health checks and failure detection
- **Contract Isolation**: Clean boundaries between core system and plugins
- **Discovery Isolation**: Separate discovery managers prevent cross-contamination

## 📈 Version Compatibility

The SDK uses semantic versioning and provides compatibility checking:

```python
from echo_sdk.utils import check_compatibility, get_sdk_version

# Check if plugin's SDK requirement is compatible
is_compatible = check_compatibility(">=0.0.1", get_sdk_version())

# Plugin metadata should specify SDK requirements
PluginMetadata(
    name="my_plugin",
    sdk_version=">=0.1.0",  # SDK version requirement
    langchain_version=">=0.1.0",  # LangChain requirement
    # ...
)
```

## 🔗 Related Components

- **[Echo Core](https://github.com/jonaskahn/echo)**: Core multi-agent orchestration system
- **[Echo Plugins](https://github.com/jonaskahn/echo-plugins)**: Example plugins and templates using this SDK

## 🚀 Code Quality

The SDK follows modern Python best practices:

- **KISS Principle**: Keep It Simple, Stupid - clean, focused methods
- **DRY Principle**: Don't Repeat Yourself - reusable components
- **Self-Documenting Code**: Meaningful names, no redundant comments
- **Consistent Formatting**: Black formatter for consistent style
- **Type Hints**: Full type annotations for better IDE support
- **Comprehensive Testing**: Thorough test coverage for all functionality

### Contribution Process

When contributing to the SDK:

1. **Fork and Branch**: Create a feature branch from main
2. **Setup Environment**: Use shared environment (recommended) or individual setup
3. **Follow Standards**: Use existing code style and patterns
4. **Add Tests**: Include tests for new features or bug fixes
5. **Quality Checks**: Run `pytest`, `black`, `mypy`, etc.
6. **Update Documentation**: Keep README and docstrings current
7. **Test Compatibility**: Ensure existing plugins still work
8. **Submit PR**: Create a pull request with clear description

### Development Commands

```bash
# With shared environment active
pytest              # Run tests
black src/          # Format code
mypy src/           # Type checking
ruff check src/     # Linting

# Test plugin compatibility
pytest examples/template_plugin/

# Test discovery functionality
python -c "from echo_sdk import auto_discover_all_plugins; print(auto_discover_all_plugins())"
```

## 📄 License

MIT License - see main project LICENSE file for details.
