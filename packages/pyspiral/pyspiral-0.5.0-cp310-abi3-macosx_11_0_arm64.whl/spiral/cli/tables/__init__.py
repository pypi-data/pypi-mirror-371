from typing import Annotated

import rich
from typer import Argument, Option

from spiral import Spiral
from spiral.cli import AsyncTyper
from spiral.cli.tables.args import get_table
from spiral.cli.types import ProjectArg

app = AsyncTyper(short_help="Spiral Tables.")


@app.command(help="List tables.")
def ls(
    project: ProjectArg,
):
    tables = Spiral().project(project).tables.list_tables()

    rich_table = rich.table.Table("id", "dataset", "name", title="Spiral tables")
    for table in tables:
        rich_table.add_row(table.id, table.dataset, table.table)
    rich.print(rich_table)


@app.command(help="Show the table key schema.")
def key_schema(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
):
    _, table = get_table(project, table, dataset)
    rich.print(table.key_schema)


@app.command(help="Compute the full table schema.")
def schema(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
):
    _, table = get_table(project, table, dataset)
    rich.print(table.schema)


@app.command(help="Flush Write-Ahead-Log.")
def flush(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
):
    identifier, table = get_table(project, table, dataset)
    table.maintenance().flush_wal()
    print(f"Flushed WAL for table {identifier} in project {project}.")


@app.command(help="Display scan.")
def debug(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
    column_group: Annotated[str, Argument(help="Dot-separated column group path.")] = ".",
):
    _, table = get_table(project, table, dataset)
    if column_group != ".":
        projection = table[column_group]
    else:
        projection = table
    scan = table.scan(projection)

    scan._debug()


@app.command(help="Display manifests.")
def manifests(
    project: ProjectArg,
    table: Annotated[str | None, Option(help="Table name.")] = None,
    dataset: Annotated[str | None, Option(help="Dataset name.")] = None,
    column_group: Annotated[str, Argument(help="Dot-separated column group path.")] = ".",
):
    _, table = get_table(project, table, dataset)
    if column_group != ".":
        projection = table[column_group]
    else:
        projection = table
    scan = projection.scan()

    scan._dump_manifests()
