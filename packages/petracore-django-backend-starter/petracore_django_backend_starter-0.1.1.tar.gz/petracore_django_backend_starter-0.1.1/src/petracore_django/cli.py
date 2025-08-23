import argparse
import subprocess
import sys
from pathlib import Path

from .scaffold import create_project_with_core_and_user


def main():
    parser = argparse.ArgumentParser(prog="djsp", description="Django starter plus")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("new", help="Create a new Django project with core (incl. startapp_plus) and user apps")
    p_new.add_argument("project_name", help="Django project name (package-safe)")
    p_new.add_argument("--django", default="django-admin", help="django-admin executable (default: django-admin)")

    args = parser.parse_args()

    if args.cmd == "new":
        subprocess.run([args.django, "startproject", args.project_name, "."], check=True)

        project_dir = Path(".").resolve()
        create_project_with_core_and_user(project_dir)
        print(f"✅ Created Django project '{args.project_name}' in the current directory with core + user scaffolding.")
    else:
        parser.print_help()
        sys.exit(1)