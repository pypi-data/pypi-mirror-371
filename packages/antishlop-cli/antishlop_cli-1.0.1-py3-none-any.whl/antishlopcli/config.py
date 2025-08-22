#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from dotenv import load_dotenv, set_key
import openai

console = Console()

def get_config_path():
    """Get path to config file"""
    return Path.home() / '.antishlop' / '.env'

def ensure_config_dir():
    """Ensure config directory exists"""
    config_dir = Path.home() / '.antishlop'
    config_dir.mkdir(exist_ok=True)
    return config_dir

def load_api_key():
    """Load API key from environment or config file"""
    # Try environment first
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        # Try config file
        config_path = get_config_path()
        if config_path.exists():
            load_dotenv(config_path)
            api_key = os.getenv('OPENAI_API_KEY')
    
    return api_key

def validate_api_key(api_key):
    """Validate API key by making a test call"""
    if not api_key or len(api_key) < 20:
        return False
    
    try:
        client = openai.OpenAI(api_key=api_key)
        # Test with minimal request
        client.models.list()
        return True
    except Exception:
        return False

def setup_api_key():
    """Interactive API key setup"""
    console.print(Panel.fit(
        "[bold cyan]AntiShlop Configuration[/bold cyan]\n\n"
        "[yellow]OpenAI API key required for security analysis[/yellow]\n\n"
        "Get your API key from: [link]https://platform.openai.com/api-keys[/link]",
        border_style="cyan",
        title="Setup Required"
    ))
    
    while True:
        api_key = Prompt.ask(
            "\n[cyan]Enter your OpenAI API key[/cyan]",
            password=True
        )
        
        if not api_key:
            console.print("[red]API key cannot be empty[/red]")
            continue
        
        console.print("\n[yellow]Validating API key...[/yellow]")
        
        if validate_api_key(api_key):
            # Save to config file
            ensure_config_dir()
            config_path = get_config_path()
            set_key(str(config_path), 'OPENAI_API_KEY', api_key)
            
            console.print("[green]API key validated and saved![/green]")
            return api_key
        else:
            console.print("[red]Invalid API key. Please try again.[/red]")

def get_validated_api_key():
    """Get and validate API key, prompt for setup if needed"""
    api_key = load_api_key()
    
    if not api_key:
        console.print("[yellow]No OpenAI API key found[/yellow]")
        return setup_api_key()
    
    if not validate_api_key(api_key):
        console.print("[red]Invalid API key found[/red]")
        return setup_api_key()
    
    return api_key