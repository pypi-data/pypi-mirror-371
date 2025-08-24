import click
from click.shell_completion import CompletionItem
from src.util.config_util import load_config
import os

def get_host_aliases(ctx, param, incomplete):
    """Provide completion for host aliases."""
    config = load_config()
    hosts = config.get('hosts', [])
    return [
        CompletionItem(h['alias'], help=f"Host: {h['address']}")
        for h in hosts
        if h['alias'].startswith(incomplete)
    ]

def get_port_aliases(ctx, param, incomplete):
    """Provide completion for port aliases."""
    config = load_config()
    ports = config.get('ports', [])
    completions = [
        CompletionItem(str(p['alias']), help=f"Port: {p['value']}")
        for p in ports
        if str(p['alias']).startswith(incomplete)
    ]
    # Add common ports if no custom ports match
    if not completions:
        common_ports = ['22', '80', '443', '3306', '5432', '6379', '8080', '8443']
        completions.extend([
            CompletionItem(p, help=f"Common port")
            for p in common_ports
            if p.startswith(incomplete)
        ])
    return completions

def get_username_aliases(ctx, param, incomplete):
    """Provide completion for username aliases."""
    config = load_config()
    usernames = config.get('usernames', [])
    return [
        CompletionItem(u['alias'], help=f"Username: {u['value']}")
        for u in usernames
        if u['alias'].startswith(incomplete)
    ]

def get_password_aliases(ctx, param, incomplete):
    """Provide completion for password aliases."""
    config = load_config()
    passwords = config.get('passwords', [])
    return [
        CompletionItem(p['alias'], help="Password: ****")
        for p in passwords
        if p['alias'].startswith(incomplete)
    ]

def get_keypair_aliases(ctx, param, incomplete):
    """Provide completion for keypair aliases."""
    config = load_config()
    keypairs = config.get('keypairs', [])
    return [
        CompletionItem(k['alias'], help=f"Keypair: {os.path.basename(k['path'])}")
        for k in keypairs
        if k['alias'].startswith(incomplete)
    ]

def get_environment_aliases(ctx, param, incomplete):
    """Provide completion for environment aliases."""
    config = load_config()
    environments = config.get('environments', [])
    completions = []
    for env in environments:
        if env['alias'].startswith(incomplete):
            host_alias = env.get('host_alias', 'N/A')
            port_alias = env.get('port_alias', '22')
            username_alias = env.get('username_alias', 'N/A')
            help_text = f"Env: {host_alias}:{port_alias} (user: {username_alias})"
            completions.append(CompletionItem(env['alias'], help=help_text))
    return completions

def get_proxy_aliases(ctx, param, incomplete):
    """Provide completion for proxy aliases (environments that can be used as jump hosts)."""
    config = load_config()
    environments = config.get('environments', [])
    completions = []
    for env in environments:
        # Only show environments with keypair authentication (required for proxy)
        if env.get('keypair_alias') and env['alias'].startswith(incomplete):
            host_alias = env.get('host_alias', 'N/A')
            help_text = f"Proxy: {host_alias} (key auth)"
            completions.append(CompletionItem(env['alias'], help=help_text))
    return completions

def get_all_aliases(ctx, param, incomplete):
    """Provide completion for all types of aliases."""
    config = load_config()
    completions = []
    
    # Add hosts
    for h in config.get('hosts', []):
        if h['alias'].startswith(incomplete):
            completions.append(CompletionItem(h['alias'], help=f"Host: {h['address']}"))
    
    # Add ports
    for p in config.get('ports', []):
        if str(p['alias']).startswith(incomplete):
            completions.append(CompletionItem(str(p['alias']), help=f"Port: {p['value']}"))
    
    # Add usernames
    for u in config.get('usernames', []):
        if u['alias'].startswith(incomplete):
            completions.append(CompletionItem(u['alias'], help=f"Username: {u['value']}"))
    
    # Add passwords
    for p in config.get('passwords', []):
        if p['alias'].startswith(incomplete):
            completions.append(CompletionItem(p['alias'], help="Password: ****"))
    
    # Add keypairs
    for k in config.get('keypairs', []):
        if k['alias'].startswith(incomplete):
            completions.append(CompletionItem(k['alias'], help=f"Keypair"))
    
    # Add environments
    for e in config.get('environments', []):
        if e['alias'].startswith(incomplete):
            completions.append(CompletionItem(e['alias'], help=f"Environment"))
    
    return completions

def get_component_type_completion(ctx, param, incomplete):
    """Provide completion for component types in list/remove commands."""
    types = ['host', 'port', 'username', 'user', 'password', 'pwd', 'keypair', 'kp', 'environment', 'env']
    return [
        CompletionItem(t)
        for t in types
        if t.startswith(incomplete)
    ]

def get_alias_for_remove(ctx, param, incomplete):
    """Smart completion for remove command based on the component type."""
    # Try to get the component type from context
    if ctx.parent and hasattr(ctx.parent, 'params'):
        component_type = ctx.parent.params.get('component')
        if component_type:
            config = load_config()
            
            # Map short names to full names
            type_map = {
                'host': 'hosts',
                'port': 'ports',
                'username': 'usernames',
                'user': 'usernames',
                'password': 'passwords',
                'pwd': 'passwords',
                'keypair': 'keypairs',
                'kp': 'keypairs',
                'environment': 'environments',
                'env': 'environments'
            }
            
            component_key = type_map.get(component_type, component_type + 's')
            components = config.get(component_key, [])
            
            completions = []
            for comp in components:
                alias = comp.get('alias', '')
                if alias.startswith(incomplete):
                    if component_key == 'hosts':
                        help_text = f"Host: {comp.get('address', 'N/A')}"
                    elif component_key == 'ports':
                        help_text = f"Port: {comp.get('value', 'N/A')}"
                    elif component_key == 'usernames':
                        help_text = f"Username: {comp.get('value', 'N/A')}"
                    elif component_key == 'passwords':
                        help_text = "Password: ****"
                    elif component_key == 'keypairs':
                        help_text = "Keypair"
                    elif component_key == 'environments':
                        help_text = f"Environment: {comp.get('host_alias', 'N/A')}"
                    else:
                        help_text = component_type.capitalize()
                    
                    completions.append(CompletionItem(alias, help=help_text))
            
            return completions
    
    # Fallback to all aliases
    return get_all_aliases(ctx, param, incomplete)