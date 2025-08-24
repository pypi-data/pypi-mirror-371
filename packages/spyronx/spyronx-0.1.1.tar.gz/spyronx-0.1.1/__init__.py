"""
SpyronX - Kali Linux Terminal Experience for Windows
"""

__version__ = "1.0.0"
__author__ = "Ken"

import os
import sys
import json
from pathlib import Path

def apply_kali_theme(theme_name="kali_dark"):
    """Apply Kali Linux theme to the terminal"""
    theme_path = Path(__file__).parent / "themes" / f"{theme_name}.json"
    
    if not theme_path.exists():
        print(f"Theme {theme_name} not found!")
        return False
    
    with open(theme_path, 'r') as f:
        theme = json.load(f)
    
    # Apply theme to Windows Terminal
    apply_windows_terminal_theme(theme)
    return True

def apply_kali_prompt(profile_name="kali_zsh"):
    """Apply Kali Linux prompt style"""
    profile_path = Path(__file__).parent / "profiles" / f"{profile_name}.json"
    
    if not profile_path.exists():
        print(f"Profile {profile_name} not found!")
        return False
    
    with open(profile_path, 'r') as f:
        profile = json.load(f)
    
    # Apply prompt configuration
    apply_prompt_configuration(profile)
    return True

def setup_kali_environment():
    """Setup complete Kali Linux terminal environment"""
    apply_kali_theme()
    apply_kali_prompt()
    print("SpyronX: Kali Linux terminal environment applied!")