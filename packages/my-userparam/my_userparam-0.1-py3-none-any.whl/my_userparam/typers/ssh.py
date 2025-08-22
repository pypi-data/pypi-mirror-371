import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.table import Table
from ssh_config import SSHConfig


console = Console(emoji=False)
app = typer.Typer()

@app.callback(
    invoke_without_command=True,
    help="""List all ssh config in ~/.ssh/config. Use FILTER to filter them."""
)
def ls(filter_str: Annotated[str, typer.Argument()] = ''):

    config = SSHConfig()
    base_header = ["HostName", "User", "Port", "IdentityFile", "LocalForward"]

    ssh = Table(title=f"SSH Configuration")
    ssh.add_column("Hosts", style="cyan")
    ssh.add_column("User", style="cyan")
    ssh.add_column("Port", style="yellow")
    ssh.add_column("IdentityFile", style="green")
    ssh.add_column("LocalForward", style="green")
    ssh.add_column("Others", style="green")

    for host in config.hosts:
        user = host._Host__attrs.get('User', '')
        port = str(host._Host__attrs.get('Port', ''))
        idfile = host._Host__attrs.get('IdentityFile', '')
        locforw = host._Host__attrs.get('LocalForward', '')
        other = ','.join([f"{k}:{v}" for k,v in host._Host__attrs.items() if k not in base_header])

        if host._Host__name == ['*']:
            ssh.add_row('Global options', user, port, idfile, locforw, other)
        else:
            hostname = host._Host__name
            hostname.append(host._Host__attrs.get('HostName', ''))
            hostname = ' '.join(hostname)
            if filter_str in hostname:
                ssh.add_row( hostname, user, port, idfile, locforw, other)

    console.print(ssh)