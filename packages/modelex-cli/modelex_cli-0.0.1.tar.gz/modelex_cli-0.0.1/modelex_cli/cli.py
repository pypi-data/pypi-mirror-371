# modelex_cli/cli.py
import sys
from pathlib import Path

def app():
    # Very barebones argv parser: modelex init <name>
    argv = sys.argv[1:]
    if len(argv) < 2 or argv[0] != "init":
        print("Usage: modelex init <name>")
        sys.exit(1)

    name = argv[1]
    dest = Path(name)

    try:
        dest.mkdir(parents=False, exist_ok=False)
        print(f"✅ Created directory: {dest.resolve()}")
    except FileExistsError:
        print(f"⚠️  Directory '{name}' already exists.")
        sys.exit(1)
