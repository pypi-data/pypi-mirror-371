"""
Windows Terminal configuration utilities
"""

import os
import json
import platform
from pathlib import Path

def get_windows_terminal_settings_path():
    """Get the path to Windows Terminal settings file"""
    if platform.system() != "Windows":
        return None
        
    local_appdata = os.getenv('LOCALAPPDATA')
    if not local_appdata:
        return None
        
    return Path(local_appdata) / "Packages" / "Microsoft.WindowsTerminal_8wekyb3d8bbwe" / "LocalState" / "settings.json"

def apply_windows_terminal_theme(theme):
    """Apply a theme to Windows Terminal"""
    settings_path = get_windows_terminal_settings_path()
    if not settings_path or not settings_path.exists():
        print("Windows Terminal settings not found!")
        return False
    
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        # Add or update the theme in schemes
        if "schemes" not in settings:
            settings["schemes"] = []
        
        # Check if theme already exists
        theme_exists = False
        for i, existing_theme in enumerate(settings["schemes"]):
            if existing_theme.get("name") == theme["name"]:
                settings["schemes"][i] = theme
                theme_exists = True
                break
        
        if not theme_exists:
            settings["schemes"].append(theme)
        
        # Set as default theme
        if "profiles" in settings and "defaults" in settings["profiles"]:
            settings["profiles"]["defaults"]["colorScheme"] = theme["name"]
        
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)
        
        return True
        
    except Exception as e:
        print(f"Error applying theme: {e}")
        return False

def apply_prompt_configuration(profile_config):
    """Apply prompt configuration"""
    # This would create PowerShell profile scripts or modify them
    # to achieve the Kali Linux prompt look
    
    powershell_profile_path = Path.home() / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
    
    prompt_config = profile_config.get("promptConfig", {})
    
    prompt_function = f"""
function Global:Prompt {{
    $user = [Environment]::UserName
    $hostname = [Environment]::MachineName
    $location = Get-Location
    
    # Colors
    ${prompt_config.get('userColor', 'green')} = "`e[32m"
    ${prompt_config.get('hostColor', 'green')} = "`e[32m"
    ${prompt_config.get('pathColor', 'blue')} = "`e[34m"
    ${prompt_config.get('suffixColor', 'white')} = "`e[37m"
    $reset = "`e[0m"
    
    # Build prompt
    $prompt = "{prompt_config.get('prefix', '┌─[')}"
    $prompt += "$green$user$reset"
    $prompt += "{prompt_config.get('userSeparator', '@')}"
    $prompt += "$green$hostname$reset"
    $prompt += "{prompt_config.get('hostSuffix', ']')}"
    $prompt += "{prompt_config.get('pathPrefix', '─[')}"
    $prompt += "$blue$($location.Path)$reset"
    $prompt += "{prompt_config.get('pathSuffix', ']')}"
    $prompt += "{prompt_config.get('suffix', '\n└──╼ ')}"
    
    $prompt
}}
"""
    
    try:
        with open(powershell_profile_path, 'w') as f:
            f.write(prompt_function)
        return True
    except Exception as e:
        print(f"Error creating PowerShell profile: {e}")
        return False