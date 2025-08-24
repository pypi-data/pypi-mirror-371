import click
from src.commands.add import add
from src.commands.list import list
from src.commands.remove import remove
from src.commands.connect import connect
from src.commands.find import find
from src.commands.change import change
from src.commands.update import update
from src.commands.tunnel import tunnel
from src.commands.activate import activate

@click.group()
@click.version_option(version='0.2.3', prog_name='ussh')
def cli():
    """
    ussh - Smart SSH Connection Manager
    
    \b
    Manage your SSH connections with ease using stored configurations.
    
    \b
    QUICK START:
      ussh activate completion    # Enable tab completion
      ussh add host -v IP -l NAME # Add a new host
      ussh add env -h HOST -l ENV # Create an environment
      ussh connect ENV            # Connect to environment
    
    \b
    COMMON COMMANDS:
      ussh list                   # Show all configurations
      ussh connect prod           # Connect to production
      ussh find -q server         # Search for 'server'
      ussh tunnel local -e dev    # Create SSH tunnel
    
    \b
    💡 Enable tab completion for the best experience!
       ussh activate completion    
       → Smart substring matching & auto-suggestions
    
    \b
    Need help? ussh COMMAND --help
    """
    pass

cli.add_command(add)
cli.add_command(list)
cli.add_command(remove)
cli.add_command(remove, name='rm')
cli.add_command(connect)
cli.add_command(connect, name='con')
cli.add_command(find)
cli.add_command(change)
cli.add_command(update)
cli.add_command(tunnel)
cli.add_command(activate)

if __name__ == "__main__":
    cli()