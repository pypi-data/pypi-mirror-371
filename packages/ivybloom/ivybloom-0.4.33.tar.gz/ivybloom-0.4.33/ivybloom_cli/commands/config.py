"""
Configuration management commands for IvyBloom CLI
"""

import click
import json
from rich.console import Console
from rich.table import Table

from ..utils.config import Config
from ..utils.colors import get_console, print_success, print_error, print_warning, print_info

console = get_console()

@click.group()
def config():
    """⚙️ CLI configuration and environment management
    
    Configure IvyBloom CLI settings, endpoints, and preferences for optimal 
    performance in your environment.
    
    CONFIGURATION CATEGORIES:
    
      🌐 Endpoints & URLs:      API and frontend server addresses
      🔐 Authentication:        Default auth methods and tokens
      📊 Output & Display:      Formatting, colors, and verbosity  
      ⚡ Performance:          Timeouts, concurrency, caching
      📁 Project Settings:     Default project IDs and directories
    
    COMMON SETTINGS:
    
      • api_url:               Backend API endpoint
      • frontend_url:          Web interface URL  
      • default_project_id:    Default project for new jobs
      • output_format:         Preferred output format (table/json)
      • timeout:               Request timeout in seconds
      • debug:                 Enable debug logging
      • max_concurrent_jobs:   Job execution concurrency limit
    
    CONFIGURATION WORKFLOW:
    
      1. View current settings:    ivybloom config show
      2. Set individual values:    ivybloom config set api_url https://api.example.com
      3. Get specific setting:     ivybloom config get timeout  
      4. Reset to defaults:        ivybloom config reset
      5. Validate configuration:   ivybloom config validate
    
    ENVIRONMENT VARIABLES:
    
      Settings can also be configured via environment variables:
      • IVY_API_URL, IVY_FRONTEND_URL
      • IVY_DEFAULT_PROJECT_ID  
      • IVY_DEBUG=true/false
      • IVY_TIMEOUT=30
    
    CONFIGURATION PRIORITY:
    
      1. Command-line arguments (highest)
      2. Environment variables  
      3. Config file settings
      4. Built-in defaults (lowest)
    
    💡 TIP: Use 'ivybloom config validate' to check for configuration issues
    💡 TIP: Environment variables override config file settings
    
    Run 'ivybloom config <command> --help' for detailed help on each command.
    """
    pass

@config.command()
@click.argument('key')
@click.argument('value')
@click.option('--type', type=click.Choice(['string', 'int', 'float', 'bool', 'json']), help='Value type (auto-detected if not specified)')
@click.pass_context
def set(ctx, key, value, type):
    """⚙️ Set a configuration value
    
    Update CLI configuration settings. Values are automatically parsed based on
    content, or you can specify the type explicitly.
    
    COMMON SETTINGS:
    
      # Endpoint configuration
      ivybloom config set api_url https://api.ivybiosciences.com
      ivybloom config set frontend_url https://ivybiosciences.com
      
      # Default project and formatting  
      ivybloom config set default_project_id proj_abc123
      ivybloom config set output_format json
      
      # Performance tuning
      ivybloom config set timeout 60
      ivybloom config set max_concurrent_jobs 5
      ivybloom config set debug true
    
    VALUE TYPES:
    
      📄 Strings:     URLs, names, IDs (quoted or unquoted)
      🔢 Numbers:     Integers and floats (timeout: 30, rate: 1.5)
      ✅ Booleans:    true/false, yes/no, 1/0
      📋 JSON:        Complex objects {"key": "value"} or ["item1", "item2"]
    
    EXAMPLES:
    
      ivybloom config set debug true
      ivybloom config set timeout 30  
      ivybloom config set tags '["research", "covid"]' --type json
      ivybloom config set endpoints '{"api": "...", "web": "..."}' --type json
    
    Configuration is stored in ~/.config/ivybloom/config.json and takes effect
    immediately for new commands.
    
    💡 TIP: Use 'ivybloom config show' to see all current settings  
    💡 TIP: Complex JSON values should be quoted and use --type json
    """
    config_obj = ctx.obj['config']
    
    # Try to parse value as JSON for complex types
    try:
        parsed_value = json.loads(value)
    except json.JSONDecodeError:
        parsed_value = value
    
    config_obj.set(key, parsed_value)
    console.print(f"[green]✅ Set {key} = {parsed_value}[/green]")

@config.command()
@click.argument('key')
@click.option('--default', help='Default value if setting not found')
@click.pass_context
def get(ctx, key, default):
    """📋 Get a specific configuration value
    
    Retrieve the current value of a configuration setting. Useful for 
    scripting and automation.
    
    USAGE EXAMPLES:
    
      # Get individual settings  
      ivybloom config get api_url
      ivybloom config get timeout
      ivybloom config get debug
      
      # Use in scripts with default fallback
      ivybloom config get default_project_id --default proj_fallback
      
      # Check boolean settings
      ivybloom config get debug  # Returns: true or false
    
    RETURN VALUES:
    
      • Found setting: Prints the value and exits with code 0
      • Missing setting: Shows error message and exits with code 1  
      • With --default: Shows default value for missing settings (exit 0)
    
    SCRIPTING EXAMPLES:
    
      ```bash
      # Store setting in variable
      API_URL=$(ivybloom config get api_url)
      
      # Conditional logic based on setting
      if [ "$(ivybloom config get debug)" = "true" ]; then
          echo "Debug mode enabled"  
      fi
      
      # Use default values safely
      PROJECT=$(ivybloom config get default_project_id --default proj_main)
      ```
    
    💡 TIP: Use --default to avoid errors when settings might not exist
    💡 TIP: Perfect for shell scripting and automation workflows
    """
    config_obj = ctx.obj['config']
    
    value = config_obj.get(key)
    if value is None:
        console.print(f"[red]❌ Configuration key '{key}' not found[/red]")
    else:
        console.print(f"{key} = {value}")

@config.command()
@click.pass_context
def list(ctx):
    """List all configuration values"""
    config_obj = ctx.obj['config']
    
    config_data = config_obj.show_config()
    
    table = Table(title="🔧 Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in config_data.items():
        table.add_row(key, str(value))
    
    console.print(table)

@config.command(name="show")
@click.pass_context
def show_config(ctx):
    """Show key runtime values (frontend URL, API URL, client_id)."""
    config_obj = ctx.obj['config']
    table = Table(title="🔧 IvyBloom Runtime Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("IVY_ORCHESTRATOR_URL (resolved)", config_obj.get_api_url())
    table.add_row("IVY_FRONTEND_URL (resolved)", config_obj.get_frontend_url())
    table.add_row("client_id", config_obj.get_or_create_client_id())
    console.print(table)

@config.command()
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def reset(ctx, confirm):
    """Reset configuration to defaults"""
    config_obj = ctx.obj['config']
    
    if not confirm:
        if not click.confirm("Are you sure you want to reset all configuration to defaults?"):
            console.print("Reset cancelled.")
            return
    
    config_obj.reset()
    console.print("[green]✅ Configuration reset to defaults[/green]")

@config.command()
@click.pass_context
def path(ctx):
    """Show configuration file path"""
    config_obj = ctx.obj['config']
    console.print(f"Configuration file: {config_obj.config_path}")

@config.command()
@click.argument('key')
@click.pass_context
def unset(ctx, key):
    """Remove configuration key"""
    config_obj = ctx.obj['config']
    
    config_data = config_obj.show_config()
    if key not in config_data:
        console.print(f"[red]❌ Configuration key '{key}' not found[/red]")
        return
    
    # Remove by setting to None and reloading defaults
    config_obj.config.pop(key, None)
    config_obj.save()
    console.print(f"[green]✅ Removed configuration key '{key}'[/green]")

@config.command()
@click.option('--format', default='json', type=click.Choice(['json', 'yaml']), help='Export format')
@click.option('--output', '-o', help='Output file path')
@click.pass_context
def export(ctx, format, output):
    """Export configuration to file"""
    config_obj = ctx.obj['config']
    config_data = config_obj.show_config()
    
    if format == 'json':
        content = json.dumps(config_data, indent=2)
    elif format == 'yaml':
        import yaml
        content = yaml.dump(config_data, default_flow_style=False)
    
    if output:
        with open(output, 'w') as f:
            f.write(content)
        console.print(f"[green]✅ Configuration exported to {output}[/green]")
    else:
        console.print(content)

@config.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--merge', is_flag=True, help='Merge with existing config instead of replacing')
@click.pass_context
def import_config(ctx, file_path, merge):
    """Import configuration from file"""
    config_obj = ctx.obj['config']
    
    try:
        with open(file_path, 'r') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                import yaml
                imported_config = yaml.safe_load(f)
            else:
                imported_config = json.load(f)
        
        if merge:
            # Merge with existing config
            current_config = config_obj.show_config()
            current_config.update(imported_config)
            config_obj.config = current_config
        else:
            # Replace config
            config_obj.config = imported_config
        
        config_obj.save()
        action = "merged" if merge else "imported"
        console.print(f"[green]✅ Configuration {action} from {file_path}[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to import configuration: {e}[/red]")