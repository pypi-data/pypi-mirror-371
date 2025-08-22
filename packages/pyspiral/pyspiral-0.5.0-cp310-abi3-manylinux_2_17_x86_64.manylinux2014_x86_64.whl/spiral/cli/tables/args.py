from typing import Annotated

import questionary
import rich
import typer
from questionary import Choice
from typer import Option

from spiral.api.projects import TableResource
from spiral.cli import state
from spiral.cli.types import ProjectArg
from spiral.tables import Table


def ask_table(project_id, title="Select a table"):
    tables: list[TableResource] = list(state.spiral.project(project_id).tables.list_tables())

    if not tables:
        rich.print("[red]No tables found[/red]")
        raise typer.Exit(1)

    return questionary.select(
        title,
        choices=[
            Choice(title=f"{table.dataset}.{table.table}", value=f"{table.project_id}.{table.dataset}.{table.table}")
            for table in sorted(tables, key=lambda t: (t.dataset, t.table))
        ],
    ).ask()


def get_table(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
) -> (str, Table):
    if table is None:
        identifier = ask_table(project)
    else:
        identifier = table
        if dataset is not None:
            identifier = f"{dataset}.{table}"
    return identifier, state.spiral.project(project).tables.table(identifier)
