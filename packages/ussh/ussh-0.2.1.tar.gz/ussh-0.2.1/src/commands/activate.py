import click
import os
import subprocess
import sys
from pathlib import Path

@click.group()
def activate():
    """Activate ussh features and integrations."""
    pass

@click.command()
@click.option('--shell', '-s', type=click.Choice(['bash', 'zsh', 'fish', 'auto']), default='auto', 
              help='Target shell for completion (default: auto-detect)')
@click.option('--force', '-f', is_flag=True, help='Force reinstall completion even if already configured')
def completion(shell, force):
    """Activate shell tab completion for ussh."""
    
    # Auto-detect shell if not specified
    if shell == 'auto':
        shell_path = os.environ.get('SHELL', '/bin/bash')
        shell = os.path.basename(shell_path)
        if shell not in ['bash', 'zsh', 'fish']:
            # Try to detect from parent process
            try:
                parent = subprocess.check_output(['ps', '-p', str(os.getppid()), '-o', 'comm=']).decode().strip()
                if 'zsh' in parent:
                    shell = 'zsh'
                elif 'bash' in parent:
                    shell = 'bash'
                elif 'fish' in parent:
                    shell = 'fish'
                else:
                    shell = 'bash'  # Default fallback
            except:
                shell = 'bash'  # Default fallback
    
    click.echo(f"🐚 Detected shell: {shell}")
    click.echo("Setting up tab completion for ussh...")
    
    home = Path.home()
    
    try:
        if shell == 'bash':
            setup_bash_completion(home, force)
        elif shell == 'zsh':
            setup_zsh_completion(home, force)
        elif shell == 'fish':
            setup_fish_completion(home, force)
        
        click.secho("\n✅ Tab completion successfully activated!", fg='green', bold=True)
        click.echo("\n📝 Next steps:")
        
        if shell in ['bash', 'zsh']:
            click.echo("   1. Restart your terminal, OR")
            click.echo("   2. Run the following command to activate immediately:")
            if shell == 'bash':
                click.echo(f"      source ~/.ussh-complete.bash")
            else:
                click.echo(f"      source ~/.zshrc")
        else:
            click.echo("   Completion is now active in Fish shell!")
        
        click.echo("\n🎯 Try it out:")
        click.echo("   Type 'ussh ' and press Tab to see available commands")
        click.echo("   Type 'ussh connect ' and press Tab to see your environments")
        
    except Exception as e:
        click.secho(f"\n❌ Error setting up completion: {e}", fg='red')
        sys.exit(1)

def setup_bash_completion(home: Path, force: bool):
    """Setup Bash completion."""
    completion_file = home / '.ussh-complete.bash'
    bashrc = home / '.bashrc'
    bash_profile = home / '.bash_profile'
    
    # Generate completion script
    click.echo("  Generating Bash completion script...")
    result = subprocess.run(
        ['ussh'],
        env={**os.environ, '_USSH_COMPLETE': 'bash_source'},
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Failed to generate completion script: {result.stderr}")
    
    # Write completion file
    completion_file.write_text(result.stdout)
    click.echo(f"  ✓ Created {completion_file}")
    
    # Add to bashrc
    source_line = "source ~/.ussh-complete.bash"
    comment_line = "# ussh tab completion"
    
    if bashrc.exists():
        bashrc_content = bashrc.read_text()
        if source_line not in bashrc_content or force:
            if source_line in bashrc_content and force:
                # Remove old entries
                lines = bashrc_content.split('\n')
                new_lines = [l for l in lines if not (source_line in l or (comment_line in l and 'ussh' in l))]
                bashrc_content = '\n'.join(new_lines)
                bashrc.write_text(bashrc_content)
            
            # Add new entry
            with bashrc.open('a') as f:
                f.write(f"\n{comment_line}\n{source_line}\n")
            click.echo(f"  ✓ Added completion to {bashrc}")
        else:
            click.echo(f"  ✓ Completion already configured in {bashrc}")
    else:
        with bashrc.open('w') as f:
            f.write(f"{comment_line}\n{source_line}\n")
        click.echo(f"  ✓ Created {bashrc} with completion")
    
    # For macOS, also update bash_profile
    if sys.platform == 'darwin' and bash_profile.exists():
        profile_content = bash_profile.read_text()
        if source_line not in profile_content:
            with bash_profile.open('a') as f:
                f.write(f"\n{comment_line}\n{source_line}\n")
            click.echo(f"  ✓ Added completion to {bash_profile} (macOS)")

def setup_zsh_completion(home: Path, force: bool):
    """Setup Zsh completion."""
    completion_dir = home / '.zsh' / 'completion'
    completion_file = completion_dir / '_ussh'
    zshrc = home / '.zshrc'
    
    # Create completion directory
    completion_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate completion script
    click.echo("  Generating Zsh completion script...")
    result = subprocess.run(
        ['ussh'],
        env={**os.environ, '_USSH_COMPLETE': 'zsh_source'},
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Failed to generate completion script: {result.stderr}")
    
    # Write completion file
    completion_file.write_text(result.stdout)
    click.echo(f"  ✓ Created {completion_file}")
    
    # Add to zshrc
    fpath_line = "fpath+=~/.zsh/completion"
    autoload_line = "autoload -Uz compinit && compinit"
    comment_line = "# ussh tab completion"
    
    if zshrc.exists():
        zshrc_content = zshrc.read_text()
        
        # Check if fpath is configured
        if fpath_line not in zshrc_content or force:
            if fpath_line in zshrc_content and force:
                # Remove old entries
                lines = zshrc_content.split('\n')
                new_lines = []
                skip_next = False
                for i, line in enumerate(lines):
                    if skip_next:
                        skip_next = False
                        continue
                    if comment_line in line and 'ussh' in line:
                        skip_next = True
                        continue
                    if fpath_line not in line and autoload_line not in line:
                        new_lines.append(line)
                zshrc_content = '\n'.join(new_lines)
                zshrc.write_text(zshrc_content)
            
            # Add new entries
            with zshrc.open('a') as f:
                f.write(f"\n{comment_line}\n{fpath_line}\n{autoload_line}\n")
            click.echo(f"  ✓ Added completion to {zshrc}")
        else:
            click.echo(f"  ✓ Completion already configured in {zshrc}")
    else:
        with zshrc.open('w') as f:
            f.write(f"{comment_line}\n{fpath_line}\n{autoload_line}\n")
        click.echo(f"  ✓ Created {zshrc} with completion")

def setup_fish_completion(home: Path, force: bool):
    """Setup Fish completion."""
    completion_dir = home / '.config' / 'fish' / 'completions'
    completion_file = completion_dir / 'ussh.fish'
    
    # Create completion directory
    completion_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate completion script
    click.echo("  Generating Fish completion script...")
    result = subprocess.run(
        ['ussh'],
        env={**os.environ, '_USSH_COMPLETE': 'fish_source'},
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Failed to generate completion script: {result.stderr}")
    
    # Write completion file
    completion_file.write_text(result.stdout)
    click.echo(f"  ✓ Created {completion_file}")
    click.echo("  ✓ Fish completion is now active!")

@click.command()
def status():
    """Check the status of ussh features and integrations."""
    home = Path.home()
    
    click.echo("🔍 Checking ussh activation status...\n")
    
    # Check shell completions
    click.echo("📋 Shell Completions:")
    
    # Check Bash
    bash_complete = home / '.ussh-complete.bash'
    bashrc = home / '.bashrc'
    if bash_complete.exists():
        bashrc_configured = False
        if bashrc.exists() and 'source ~/.ussh-complete.bash' in bashrc.read_text():
            bashrc_configured = True
        
        if bashrc_configured:
            click.echo(f"  ✅ Bash: Fully configured")
        else:
            click.echo(f"  ⚠️  Bash: Completion file exists but not sourced in .bashrc")
    else:
        click.echo(f"  ❌ Bash: Not configured")
    
    # Check Zsh
    zsh_complete = home / '.zsh' / 'completion' / '_ussh'
    zshrc = home / '.zshrc'
    if zsh_complete.exists():
        zshrc_configured = False
        if zshrc.exists() and 'fpath+=~/.zsh/completion' in zshrc.read_text():
            zshrc_configured = True
        
        if zshrc_configured:
            click.echo(f"  ✅ Zsh: Fully configured")
        else:
            click.echo(f"  ⚠️  Zsh: Completion file exists but not configured in .zshrc")
    else:
        click.echo(f"  ❌ Zsh: Not configured")
    
    # Check Fish
    fish_complete = home / '.config' / 'fish' / 'completions' / 'ussh.fish'
    if fish_complete.exists():
        click.echo(f"  ✅ Fish: Fully configured")
    else:
        click.echo(f"  ❌ Fish: Not configured")
    
    # Check current shell
    current_shell = os.path.basename(os.environ.get('SHELL', 'unknown'))
    click.echo(f"\n🐚 Current shell: {current_shell}")
    
    # Check if ussh is in PATH
    click.echo(f"\n🔧 Installation:")
    try:
        result = subprocess.run(['which', 'ussh'], capture_output=True, text=True)
        if result.returncode == 0:
            click.echo(f"  ✅ ussh is in PATH: {result.stdout.strip()}")
        else:
            click.echo(f"  ❌ ussh is not in PATH")
    except:
        click.echo(f"  ⚠️  Could not determine if ussh is in PATH")
    
    # Check configuration
    from src.util.config_util import CONFIG_PATH
    if Path(CONFIG_PATH).exists():
        import json
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        
        click.echo(f"\n📊 Configuration:")
        click.echo(f"  Hosts:        {len(config.get('hosts', []))}")
        click.echo(f"  Ports:        {len(config.get('ports', []))}")
        click.echo(f"  Usernames:    {len(config.get('usernames', []))}")
        click.echo(f"  Passwords:    {len(config.get('passwords', []))}")
        click.echo(f"  Keypairs:     {len(config.get('keypairs', []))}")
        click.echo(f"  Environments: {len(config.get('environments', []))}")
    else:
        click.echo(f"\n📊 Configuration: No configuration file found")
    
    click.echo("\n💡 Tips:")
    click.echo("  • Run 'ussh activate completion' to set up tab completion")
    click.echo("  • Run 'ussh list' to see all stored configurations")
    click.echo("  • Run 'ussh --help' to see all available commands")

activate.add_command(completion)
activate.add_command(status)