import os
import typer
import glob
from rich.console import Console
from rich.table import Table
from cryptography.hazmat.primitives.serialization import load_ssh_public_key

console = Console(emoji=False)
app = typer.Typer()

@app.callback(
    invoke_without_command=True,
    help="""List all ssh keys in ~/.ssh and their length / type."""
)
def ls():

    ssh_keys = Table(title=f"SSH Keys")
    ssh_keys.add_column("Path", style="cyan")
    ssh_keys.add_column("Type", style="yellow")
    ssh_keys.add_column("Length", style="green")

    pattern = os.path.expanduser("~/.ssh/") + '**/*.pub'
    for key_path in glob.glob(pattern, recursive=True):
        with open(key_path, 'rb') as f:
            key_content = f.read()

        key_type = key_content.decode().split(' ')[0]
        key = load_ssh_public_key(key_content)

        key_size = getattr(key, 'key_size', None)
        if key_size is None:
            key_size = len(key.public_bytes_raw())*8
        ssh_keys.add_row(key_path, key_type, str(key_size))


    console.print(ssh_keys)