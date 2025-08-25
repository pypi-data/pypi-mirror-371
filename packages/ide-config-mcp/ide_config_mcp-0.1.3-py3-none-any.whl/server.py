import os
import json
import commentjson
import platform
from fastmcp import FastMCP
from typing import Dict, Any, Optional
from typing import Annotated


# Initialize MCP server
mcp = FastMCP("IDE config MCP Server")

# Define VS Code settings file path constants for different operating systems
WINDOWS_VSCODE_SETTINGS_PATH = os.path.expanduser("~\AppData\\Roaming\\Code\\User\\settings.json")
MACOS_VSCODE_SETTINGS_PATH = os.path.expanduser("~/Library/Application Support/Code/User/settings.json")
LINUX_VSCODE_SETTINGS_PATH = os.path.expanduser("~/.config/Code/User/settings.json")

# Set default VS Code settings file path based on operating system
if platform.system() == "Windows":
    DEFAULT_VSCODE_SETTINGS_PATH = WINDOWS_VSCODE_SETTINGS_PATH
elif platform.system() == "Darwin":  # macOS
    DEFAULT_VSCODE_SETTINGS_PATH = MACOS_VSCODE_SETTINGS_PATH
elif platform.system() == "Linux":
    DEFAULT_VSCODE_SETTINGS_PATH = LINUX_VSCODE_SETTINGS_PATH
else:
    # Default to standard path for current operating system
    if os.name == "nt":  # Windows
        DEFAULT_VSCODE_SETTINGS_PATH = WINDOWS_VSCODE_SETTINGS_PATH
    else:  # Non-Windows systems default to Linux path
        DEFAULT_VSCODE_SETTINGS_PATH = LINUX_VSCODE_SETTINGS_PATH

# Ensure path format is correct
DEFAULT_VSCODE_SETTINGS_PATH = os.path.normpath(DEFAULT_VSCODE_SETTINGS_PATH)


def _get_vscode_settings() -> Dict[str, Any]:
    """Get VS Code user settings

    Returns:
        JSON content of the settings file
    """
    path = DEFAULT_VSCODE_SETTINGS_PATH
    try:
        if not os.path.exists(path):
            # If file doesn't exist, return empty dictionary
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            try:
                # Try to load commented JSON using commentjson
                return commentjson.load(f)
            except Exception as e:
                # If failed, try to load with standard json
                f.seek(0)
                try:
                    return json.load(f)
                except Exception:
                    return {'error': f'解析JSON文件失败: {str(e)}'}
    except Exception as e:
        return {"error": f"读取VS Code配置失败: {str(e)}"}

@mcp.tool(name = "get_vscode_settings")
def get_vscode_settings() -> Dict[str, Any]:
    """get all vs code user settings

    Args:

    Returns:
        vs code user settings
    """
    return _get_vscode_settings()


@mcp.tool()
def update_vscode_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """update VS Code user settings

    Args:
        settings: Settings to update

    Returns:
        Updated settings file content
    """
    path = DEFAULT_VSCODE_SETTINGS_PATH
    try:
        # Read existing settings
        current_settings = get_vscode_settings()
        # Update settings
        current_settings.update(settings)
        # Write to file
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(current_settings, f, indent=2, ensure_ascii=False)
        return current_settings
    except Exception as e:
        return {"error": f"更新VS Code配置失败: {str(e)}"}



@mcp.tool()
def get_vscode_setting_by_key(key: str) -> Dict[str, Any]:
    """Get VS Code user setting by key, if not found in user settings, will return default value

    Args:
        key: Setting key name

    Returns:
        Dictionary containing setting value, or error message if key doesn't exist
    """
    path = DEFAULT_VSCODE_SETTINGS_PATH
    try:
        # Get current settings
        current_settings = _get_vscode_settings()
        # Check if key exists
        if key in current_settings:
            return {key: current_settings[key]}
        else:
            # If key not found in user settings, try to get default value from defaultSettings.json
            try:
                default_settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'defaultSettings.json')
                if os.path.exists(default_settings_path):
                    with open(default_settings_path, 'r', encoding='utf-8') as f:
                        default_settings = commentjson.load(f)
                        if key in default_settings:
                            return {key: default_settings[key]}
                return {"error": f"配置项 '{key}' 不存在"}
            except Exception:
                return {"error": f"配置项 '{key}' 不存在"}
    except Exception as e:
        return {"error": f"获取配置项失败: {str(e)}"}


@mcp.tool()
def set_vscode_setting_by_key(
        key: Annotated[str, "the key of the setting"], 
        value: Annotated[Any, "the value of the setting"]
    ) -> Dict[str, Any]:
    """Set VS Code user setting by key, if you're not sure about the setting key, you can get all available settings via get_default_settings tool or fetch https://vscode.github.net.cn/docs/getstarted/settings

    Args:
        key: Setting key name
        value: New value for the setting

    Returns:
        Updated setting value, or error message if update failed
    """
    path = DEFAULT_VSCODE_SETTINGS_PATH
    try:
        # Get current settings
        current_settings = _get_vscode_settings()
        # Update specified key's value
        current_settings[key] = value
        # Write to file
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(current_settings, f, indent=2, ensure_ascii=False)
        return {key: value}
    except Exception as e:
        return {"error": f"设置配置项失败: {str(e)}"}


@mcp.tool(
    name="get_default_settings",
    description="Get all available VS Code settings and default value",
)
def get_default_settings() -> str:
    """Get all available VS Code settings and default value
    
    Returns:
        vs code's default settings in json format with comments preserved
    """
    try:
        default_settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'defaultSettings.json')
        if not os.path.exists(default_settings_path):
            return json.dumps({"error": "Default configuration file does not exist"})
        with open(default_settings_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return json.dumps({"error": f"读取默认配置文件失败: {str(e)}"})

def main():
    """Main entry point for the MCP server"""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

    # for debug only
    # mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")