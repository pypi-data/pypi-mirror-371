# IDE Config MCP Server

A Python-based MCP Server that provides tools for modifying IDE configuration files (currently supports VS Code only). MCP allows Large Language Models (LLMs) to directly call these tools to manipulate IDE settings.

## Features

- Get IDE configuration file content
- Update IDE configuration files
- Get configuration item by key
- Set configuration item by key
- Compliant with MCP standard, can be directly called by LLMs

## Installation

### install uv

uv is a fast Python package manager and runner. It is used to install and run the ide-config-mcp server.

https://uv.doczh.com/getting-started/installation/

### config ide-config-mcp

- Cursor

```json
{
  "mcpServers": {
    "ide-config-mcp": {
      "command": "uvx",
      "args": [
        "ide-config-mcp",
        "Cursor"
      ]
    }
  }
}
```

- VS Code

```json
{
  "mcpServers": {
    "ide-config-mcp": {
      "command": "uvx",
      "args": [
        "ide-config-mcp",
        "Code"
      ]
    }
  }
}
```

- Trae CN

```json
{
  "mcpServers": {
    "ide-config-mcp": {
      "command": "uvx",
      "args": [
        "ide-config-mcp",
        "TraeCN"
      ]
    }
  }
}
```

- Trae

```json
{
  "mcpServers": {
    "ide-config-mcp": {
      "command": "uvx",
      "args": [
        "ide-config-mcp",
        "Trae"
      ]
    }
  }
}
```

## Available Tools

### get_ide_settings
Get VS Code configuration file content.

**Returns**: JSON content of the configuration file

### update_ide_settings
Update VS Code configuration file.

**Parameters**:
- `settings`: Settings to update (dictionary format)

**Returns**: Updated configuration file content

### get_ide_setting_by_key
Get VS Code configuration item by key.

**Parameters**:
- `key`: Configuration item key name

**Returns**: Dictionary containing the configuration value, or error message if key doesn't exist. If the key is not found in user settings, it will return the default value from default settings.

### set_ide_setting_by_key
Set VS Code configuration item by key.

**Parameters**:
- `key`: Configuration item key name
- `value`: New value for the configuration item

**Returns**: Updated configuration value, or error message if update fails

### get_default_settings
Get VS Code default configuration items.

**Parameters**:

**Returns**: All default configurations in JSON format, including comments

## Notes

1. The server automatically accesses the corresponding VS Code configuration file based on the operating system:
   - Windows: `%APPDATA%\Code\User\settings.json`
   - macOS: `~/Library/Application Support/Code/User/settings.json`
   - Linux: `~/.config/Code/User/settings.json`

2. Ensure your LLM supports MCP protocol for automatic tool discovery and invocation.