import click
from click.shell_completion import CompletionItem
from src.util.config_util import load_config
import os
import re

def smart_match(text, incomplete):
    """
    Smart matching with scoring:
    - Exact match: score 100
    - Prefix match (case-insensitive): score 90
    - Word boundary match: score 70
    - Substring match: score 50
    - No match: score 0
    """
    if not incomplete:
        return 100  # Show all when no input
    
    # Handle None or non-string values
    if text is None:
        return 0
    if not isinstance(text, str):
        text = str(text)
    
    text_lower = text.lower()
    incomplete_lower = incomplete.lower()
    
    # Exact match
    if text_lower == incomplete_lower:
        return 100
    
    # Prefix match
    if text_lower.startswith(incomplete_lower):
        return 90
    
    # Word boundary match (e.g., "dev-server" matches "server")
    words = re.split(r'[-_\s]+', text_lower)
    for word in words:
        if word.startswith(incomplete_lower):
            return 70
    
    # Substring match
    if incomplete_lower in text_lower:
        return 50
    
    return 0

def get_host_aliases(ctx, param, incomplete):
    """Provide completion for host aliases with smart matching."""
    config = load_config()
    hosts = config.get('hosts', [])
    
    # Score and filter hosts
    scored_hosts = []
    for h in hosts:
        score = smart_match(h.get('alias', ''), incomplete)
        if score > 0:
            scored_hosts.append((score, h))
    
    # Sort by score (highest first) and then by alias
    scored_hosts.sort(key=lambda x: (-x[0], x[1].get('alias', '')))
    
    return [
        CompletionItem(h.get('alias', ''), help=f"Host: {h.get('address', 'N/A')}")
        for score, h in scored_hosts
    ]

def get_port_aliases(ctx, param, incomplete):
    """Provide completion for port aliases with smart matching."""
    config = load_config()
    ports = config.get('ports', [])
    
    # Score and filter ports
    scored_ports = []
    for p in ports:
        score = smart_match(str(p['alias']), incomplete)
        if score > 0:
            scored_ports.append((score, p))
    
    # Sort by score
    scored_ports.sort(key=lambda x: (-x[0], str(x[1].get('alias', ''))))
    
    completions = [
        CompletionItem(str(p.get('alias', '')), help=f"Port: {p.get('value', 'N/A')}")
        for score, p in scored_ports
    ]
    
    # Add common ports if they match
    if not completions or len(completions) < 5:
        common_ports = ['22', '80', '443', '3306', '5432', '6379', '8080', '8443']
        for port in common_ports:
            score = smart_match(port, incomplete)
            if score > 0 and port not in [str(p['alias']) for p in ports]:
                completions.append(CompletionItem(port, help=f"Common port"))
    
    return completions

def get_username_aliases(ctx, param, incomplete):
    """Provide completion for username aliases with smart matching."""
    config = load_config()
    usernames = config.get('usernames', [])
    
    # Score and filter usernames
    scored_users = []
    for u in usernames:
        alias_score = smart_match(u.get('alias', ''), incomplete)
        value_score = smart_match(u.get('value', ''), incomplete)
        score = max(alias_score, value_score)
        if score > 0:
            scored_users.append((score, u))
    
    # Sort by score
    scored_users.sort(key=lambda x: (-x[0], x[1].get('alias', '')))
    
    return [
        CompletionItem(u.get('alias', ''), help=f"Username: {u.get('value', 'N/A')}")
        for score, u in scored_users
    ]

def get_password_aliases(ctx, param, incomplete):
    """Provide completion for password aliases with smart matching."""
    config = load_config()
    passwords = config.get('passwords', [])
    
    # Score and filter passwords
    scored_passwords = []
    for p in passwords:
        score = smart_match(p.get('alias', ''), incomplete)
        if score > 0:
            scored_passwords.append((score, p))
    
    # Sort by score
    scored_passwords.sort(key=lambda x: (-x[0], x[1].get('alias', '')))
    
    return [
        CompletionItem(p.get('alias', ''), help="Password: ****")
        for score, p in scored_passwords
    ]

def get_keypair_aliases(ctx, param, incomplete):
    """Provide completion for keypair aliases with smart matching."""
    config = load_config()
    keypairs = config.get('keypairs', [])
    
    # Score and filter keypairs
    scored_keypairs = []
    for k in keypairs:
        score = smart_match(k.get('alias', ''), incomplete)
        if score > 0:
            scored_keypairs.append((score, k))
    
    # Sort by score
    scored_keypairs.sort(key=lambda x: (-x[0], x[1].get('alias', '')))
    
    return [
        CompletionItem(k.get('alias', ''), help=f"Keypair: {os.path.basename(k.get('path', ''))}")
        for score, k in scored_keypairs
    ]

def get_environment_aliases(ctx, param, incomplete):
    """Provide completion for environment aliases with smart matching."""
    config = load_config()
    environments = config.get('environments', [])
    
    # Score and filter environments
    scored_envs = []
    for env in environments:
        # Check multiple fields for matching
        alias_score = smart_match(env.get('alias', ''), incomplete)
        host_score = smart_match(env.get('host_alias') or '', incomplete) * 0.7  # Lower weight for indirect matches
        username_score = smart_match(env.get('username_alias') or '', incomplete) * 0.5
        
        # Get host address for additional matching
        host_address = ''
        if env.get('host_alias'):
            for h in config.get('hosts', []):
                if h.get('alias') == env.get('host_alias'):
                    host_address = h.get('address', '')
                    break
        address_score = smart_match(host_address, incomplete) * 0.6
        
        # Take the highest score
        score = max(alias_score, host_score, username_score, address_score)
        
        if score > 0:
            scored_envs.append((score, env))
    
    # Sort by score
    scored_envs.sort(key=lambda x: (-x[0], x[1].get('alias', '')))
    
    completions = []
    for score, env in scored_envs:
        host_alias = env.get('host_alias') or 'N/A'
        port_alias = env.get('port_alias') or '22'
        username_alias = env.get('username_alias') or 'N/A'
        help_text = f"Env: {host_alias}:{port_alias} (user: {username_alias})"
        completions.append(CompletionItem(env.get('alias', ''), help=help_text))
    
    return completions

def get_proxy_aliases(ctx, param, incomplete):
    """Provide completion for proxy aliases with smart matching."""
    config = load_config()
    environments = config.get('environments', [])
    
    # Score and filter proxy-capable environments
    scored_proxies = []
    for env in environments:
        # Only show environments with keypair authentication (required for proxy)
        if env.get('keypair_alias'):
            score = smart_match(env.get('alias', ''), incomplete)
            
            # Also check host alias for matching
            if env.get('host_alias'):
                host_score = smart_match(env.get('host_alias') or '', incomplete) * 0.7
                score = max(score, host_score)
            
            if score > 0:
                scored_proxies.append((score, env))
    
    # Sort by score
    scored_proxies.sort(key=lambda x: (-x[0], x[1].get('alias', '')))
    
    completions = []
    for score, env in scored_proxies:
        host_alias = env.get('host_alias') or 'N/A'
        help_text = f"Proxy: {host_alias} (key auth)"
        completions.append(CompletionItem(env.get('alias', ''), help=help_text))
    
    return completions

def get_all_aliases(ctx, param, incomplete):
    """Provide completion for all types of aliases with smart matching."""
    config = load_config()
    completions = []
    
    # Score all items
    scored_items = []
    
    # Add hosts
    for h in config.get('hosts', []):
        score = smart_match(h.get('alias', ''), incomplete)
        if score > 0:
            scored_items.append((score, 'host', h.get('alias', ''), f"Host: {h.get('address', 'N/A')}"))
    
    # Add ports
    for p in config.get('ports', []):
        score = smart_match(str(p['alias']), incomplete)
        if score > 0:
            scored_items.append((score, 'port', str(p['alias']), f"Port: {p['value']}"))
    
    # Add usernames
    for u in config.get('usernames', []):
        alias_score = smart_match(u.get('alias', ''), incomplete)
        value_score = smart_match(u.get('value', ''), incomplete)
        score = max(alias_score, value_score)
        if score > 0:
            scored_items.append((score, 'username', u.get('alias', ''), f"Username: {u.get('value', 'N/A')}"))
    
    # Add passwords
    for p in config.get('passwords', []):
        score = smart_match(p.get('alias', ''), incomplete)
        if score > 0:
            scored_items.append((score, 'password', p.get('alias', ''), "Password: ****"))
    
    # Add keypairs
    for k in config.get('keypairs', []):
        score = smart_match(k.get('alias', ''), incomplete)
        if score > 0:
            scored_items.append((score, 'keypair', k.get('alias', ''), "Keypair"))
    
    # Add environments
    for e in config.get('environments', []):
        score = smart_match(e.get('alias', ''), incomplete)
        if score > 0:
            scored_items.append((score, 'environment', e.get('alias', ''), "Environment"))
    
    # Sort by score (highest first), then by type, then by alias
    scored_items.sort(key=lambda x: (-x[0], x[1], x[2]))
    
    # Convert to CompletionItems
    for score, item_type, alias, help_text in scored_items:
        completions.append(CompletionItem(alias, help=help_text))
    
    return completions

def get_component_type_completion(ctx, param, incomplete):
    """Provide completion for component types with smart matching."""
    types = ['host', 'port', 'username', 'user', 'password', 'pwd', 'keypair', 'kp', 'environment', 'env']
    
    # Score and filter types
    scored_types = []
    for t in types:
        score = smart_match(t, incomplete)
        if score > 0:
            scored_types.append((score, t))
    
    # Sort by score
    scored_types.sort(key=lambda x: (-x[0], x[1]))
    
    return [
        CompletionItem(t)
        for score, t in scored_types
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
            
            # Score and filter components
            scored_components = []
            for comp in components:
                alias = comp.get('alias', '')
                score = smart_match(alias, incomplete)
                
                if score > 0:
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
                    
                    scored_components.append((score, alias, help_text))
            
            # Sort by score
            scored_components.sort(key=lambda x: (-x[0], x[1]))
            
            return [
                CompletionItem(alias, help=help_text)
                for score, alias, help_text in scored_components
            ]
    
    # Fallback to all aliases
    return get_all_aliases(ctx, param, incomplete)