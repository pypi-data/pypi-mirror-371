import shutil
from pathlib import Path

import typer

from qcdb.core import process_all
from qcdb.vault import Vault

app = typer.Typer()


@app.command()
def scrape(
    root: Path = Path("."), vault_dir: Path = Path("vault"), reset: bool = False
):
    """
    1) Find and parse all .out files under `root`
    2) Add new notes into your Obsidian vault at `vault_dir`
    3) Lint the vault for dupes / missing fields
    """
    if reset:
        shutil.rmtree(vault_dir)
    items = process_all(root)
    vault = Vault(vault_dir)
    vault.add(items)
    vault.lint()


if __name__ == "__main__":
    app()
