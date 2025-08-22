from typing import Annotated

import rich
from typer import Option

from spiral.api.text_indexes import SyncIndexRequest
from spiral.cli import AsyncTyper, state
from spiral.cli.indexes.args import get_text_index_id
from spiral.cli.types import ProjectArg

from ...api.workers import ResourceClass
from . import workers

app = AsyncTyper(short_help="Indexes.")
app.add_typer(workers.app, name="workers")


@app.command(help="List indexes.")
def ls(
    project: ProjectArg,
):
    """List indexes."""
    indexes = state.spiral.project(project).indexes.list_indexes()

    rich_table = rich.table.Table("id", "name", title="Indexes")
    for index in indexes:
        rich_table.add_row(index.id, index.name)
    rich.print(rich_table)


@app.command(help="Trigger a sync job for the index.")
def sync(
    project: ProjectArg,
    name: Annotated[str | None, Option(help="Index name.")] = None,
    resources: Annotated[ResourceClass, Option(help="Resources to use for the sync job.")] = ResourceClass.SMALL,
):
    """Trigger a sync job for the index."""
    index_id = get_text_index_id(project, name)
    response = state.spiral.api.text_indexes.sync_index(index_id, SyncIndexRequest(resources=resources))
    rich.print(f"Triggered sync job {response.worker_id} for index {index_id}.")
