import os
import typer
import pyotp
import datetime
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated


TOTP_FILE = os.path.expanduser('~/.ssh/tfa.txt')

console = Console(emoji=False)
app = typer.Typer()

def _generate_totp(totp_key):
    try:
        totp = pyotp.TOTP(totp_key)
        code = totp.now()
        time_remaining = str(round(
            totp.interval - datetime.datetime.now().timestamp() % totp.interval))
        return code, time_remaining + " s"
    except Exception as e:
        typer.secho(f"Error generating a TOTP: {str(e)}. "
                      f"Are you sure to use a valid secret for {host}?", fg=typer.colors.RED)

@app.callback(
    invoke_without_command=True,
    help="""Print an actual TOTP code based on the entries in ~/.ssh/tfa.txt"""
)
def ls(host: Annotated[str, typer.Argument()] = ''):

    hosts = {}
    keys = Table(title="TOTP")
    keys.add_column("Hosts", style="cyan")
    keys.add_column("TOTP", style="green")
    keys.add_column("Expires in ...", style="red", justify="right")

    try:
        with open(TOTP_FILE, 'r') as f:
            for line in f:
                server, key = line.strip().split(':')
                hosts[server] = key

    except Exception as e:
        typer.secho(f"Error: {str(e)}. Be sure to check your ~/.ssh/tfa.txt. "
                      f"It should contain lines like keyname:secret "
                      f"for each TOTP you want to use.", fg=typer.colors.RED)

    if host:
        if host in hosts:
            code, time_remaining = _generate_totp(hosts[host])
            keys.add_row(host, code, time_remaining)
            console.print(keys)
        else:
            typer.secho(f"Host {host} not found", fg=(215,135,0))
    else:
        for host,key in hosts.items():
            code, time_remaining = _generate_totp(key)
            keys.add_row(host, code, time_remaining)
        console.print(keys)

