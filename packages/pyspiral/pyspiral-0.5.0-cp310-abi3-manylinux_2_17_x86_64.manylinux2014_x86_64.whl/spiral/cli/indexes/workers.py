from typing import Annotated

import rich
from typer import Option

from spiral.api.text_indexes import CreateWorkerRequest
from spiral.api.workers import CPU, GcpRegion, Memory
from spiral.cli import AsyncTyper, state
from spiral.cli.indexes.args import get_text_index_id
from spiral.cli.types import ProjectArg

app = AsyncTyper(short_help="Text Search Workers.")


@app.command(name="serve", help="Create a search worker.")
def serve(
    project: ProjectArg,
    index: Annotated[str | None, Option(help="Index name.")] = None,
    region: Annotated[GcpRegion, Option(help="GCP region for the worker.")] = GcpRegion.US_EAST4,
    cpu: Annotated[CPU, Option(help="CPU resources for the worker.")] = CPU.ONE,
    memory: Annotated[Memory, Option(help="Memory resources for the worker in MB.")] = Memory.MB_512,
):
    """Create a new text search worker."""
    index_id = get_text_index_id(project, index)
    request = CreateWorkerRequest(cpu=cpu, memory=memory, region=region)
    response = state.spiral.api.text_indexes.create_worker(index_id, request)
    rich.print(f"Created worker {response.worker_id} for {index_id}.")


@app.command(name="shutdown", help="Shutdown a search worker.")
def shutdown(worker_id: str):
    """Shutdown a worker."""
    state.spiral.api.text_indexes.shutdown_worker(worker_id)
    rich.print(f"Requested worker {worker_id} to shutdown.")


@app.command(name="ls", help="List search workers.")
def ls(
    project: ProjectArg,
    index: Annotated[str | None, Option(help="Index name.")] = None,
):
    """List text search workers."""
    index_id = get_text_index_id(project, index)
    worker_ids = state.spiral.api.text_indexes.list_workers(index_id)

    rich_table = rich.table.Table("Worker ID", "URL", title=f"Text Search Workers for {index_id}")
    for worker_id in worker_ids:
        try:
            worker = state.spiral.api.text_indexes.get_worker(worker_id)
            rich_table.add_row(
                worker_id,
                worker.url,
            )
        except Exception:
            rich_table.add_row(
                worker_id,
                "Unavailable",
            )
    rich.print(rich_table)
