# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from tabulate import tabulate
from termcolor import colored

from .. import pullyfile
from ..constants import BASE_DIR


def ls_command(args):
    base_dir = Path(args.directory) if args.directory else BASE_DIR
    table = []
    with pullyfile.project_context(base_dir, search=not args.directory) as context:
        config_dir, projects, groups = context
        for project_id, project in projects.items():
            git_dir = config_dir / project.local_path / ".git"

            if git_dir.exists():
                status = colored("cloned", "green")
            else:
                status = "-"

            table.append([status, colored(project.project_id), project.local_path])
    print(tabulate(table, tablefmt="plain", colalign=["left", "left", "left"]))


def ls_command_parser(subparsers):
    parser = subparsers.add_parser("ls")
    parser.set_defaults(func=ls_command)
