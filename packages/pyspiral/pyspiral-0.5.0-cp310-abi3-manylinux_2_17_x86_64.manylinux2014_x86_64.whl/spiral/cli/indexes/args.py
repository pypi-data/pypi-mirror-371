from typing import Annotated

import questionary
import rich
import typer
from questionary import Choice
from typer import Option

from spiral.api.projects import TextIndexResource
from spiral.api.types import IndexId
from spiral.cli import state
from spiral.cli.types import ProjectArg


def ask_index(project_id, title="Select an index"):
    indexes: list[TextIndexResource] = list(state.spiral.project(project_id).indexes.list_indexes())

    if not indexes:
        rich.print("[red]No indexes found[/red]")
        raise typer.Exit(1)

    return questionary.select(
        title,
        choices=[Choice(title=index.name, value=index.id) for index in sorted(indexes, key=lambda t: (t.name, t.id))],
    ).ask()


def get_text_index_id(
    project: ProjectArg,
    name: Annotated[str | None, Option(help="Index name.")] = None,
) -> IndexId:
    if name is None:
        return ask_index(project)

    indexes: list[TextIndexResource] = list(state.spiral.project(project).indexes.list_indexes())
    for index in indexes:
        if index.name == name:
            return index.id
    raise ValueError(f"Index not found: {name}")
