#!/usr/bin/env python3
"""
SpyronX - Main executable
"""

import argparse
import sys
import os
from pathlib import Path

# Add the package directory to the path
package_dir = Path(__file__).parent
sys.path.insert(0, str(package_dir))

import spyronx
from spyronx.utils import terminal_config, color_schemes
from spyronx.plugins import command_suggestions, auto_complete

def main():
    parser = argparse.ArgumentParser(description="SpyronX - Kali Linux Terminal for Windows")
    
    parser.add_argument("--theme", "-t", default="kali_dark", 
                       help="Theme to apply (kali_dark, kali_light, custom)")
    
    parser.add_argument("--profile", "-p", default="kali_zsh", 
                       help="Prompt profile to apply (kali_zsh, kali_bash, powershell_kali)")
    
    parser.add_argument("--reset", "-r", action="store_true",
                       help="Reset to default terminal settings")
    
    parser.add_argument("--list-themes", "-l", action="store_true",
                       help="List all available themes")
    
    parser.add_argument("--list-profiles", "-L", action="store_true",
                       help="List all available profiles")
    
    args = parser.parse_args()
    
    if args.list_themes:
        list_themes()
        return
        
    if args.list_profiles:
        list_profiles()
        return
        
    if args.reset:
        reset_terminal()
        return
    
    # Apply the selected theme and profile
    try:
        success = spyronx.apply_kali_theme(args.theme)
        if success:
            print(f"Applied theme: {args.theme}")
            
        success = spyronx.apply_kali_prompt(args.profile)
        if success:
            print(f"Applied profile: {args.profile}")
            
        print("SpyronX configuration complete! Restart your terminal to see changes.")
        
    except Exception as e:
        print(f"Error applying configuration: {e}")
        sys.exit(1)

def list_themes():
    """List all available themes"""
    themes_dir = Path(__file__).parent / "spyronx" / "themes"
    print("Available themes:")
    for theme_file in themes_dir.glob("*.json"):
        print(f"  - {theme_file.stem}")

def list_profiles():
    """List all available profiles"""
    profiles_dir = Path(__file__).parent / "spyronx" / "profiles"
    print("Available profiles:")
    for profile_file in profiles_dir.glob("*.json"):
        print(f"  - {profile_file.stem}")

def reset_terminal():
    """Reset terminal to default settings"""
    print("Resetting terminal to default settings...")
    # Implementation would reset Windows Terminal settings
    print("Reset complete! Restart your terminal.")

if __name__ == "__main__":
    main()