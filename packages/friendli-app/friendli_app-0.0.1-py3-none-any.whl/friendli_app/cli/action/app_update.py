# Copyright (c) 2025-present, FriendliAI Inc. All rights reserved.

"""Friendli App update action."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import typer

from friendli_app.cli.util.file_utils import get_directory_size, scan_directory_structure
from friendli_app.cli.util.humanize.bytes import format_bytes

if TYPE_CHECKING:
    from ..context import AppContext


MAX_APP_DIR_SIZE_MB = 50
MAX_APP_DIR_SIZE_BYTES = MAX_APP_DIR_SIZE_MB * 1024 * 1024


def run(ctx: AppContext, app_id: str, app_dir_path: str) -> None:
    """Update an app's source archive."""
    ctx.console.print(f"🚀 Updating app '{app_id}' from '{app_dir_path}'")

    app_dir = Path(app_dir_path)

    # 1. Validate directory and main.py existence
    main_py_path = app_dir / "main.py"
    if not app_dir.is_dir():
        ctx.console.print(f"[error]❌ Directory not found: '{app_dir_path}'[/]")
        raise typer.Exit(1)
    if not main_py_path.is_file():
        ctx.console.print(f"[error]❌ 'main.py' not found in '{app_dir_path}'.[/]")
        raise typer.Exit(1)

    # 2. Check directory size
    dir_size = get_directory_size(str(app_dir))
    if dir_size > MAX_APP_DIR_SIZE_BYTES:
        ctx.console.print(
            f"[error]❌ Directory size ({format_bytes(dir_size)})[/]"
            f"exceeds the limit of {MAX_APP_DIR_SIZE_MB}MB."
        )
        raise typer.Exit(1)

    http_client = ctx.http_client
    update_app_url = f"/beta/agent/agent-beta/{app_id}/update-source-archive"

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            archive_path = os.path.join(tmpdir, "app_archive")
            shutil.make_archive(
                base_name=archive_path,
                format="zip",
                root_dir=app_dir,
            )
            archive_file = f"{archive_path}.zip"

            # Scan the directory structure
            metadata_structure = scan_directory_structure(str(app_dir), exclude_dirs=[".venv"])

            data = {
                "metadata": json.dumps(metadata_structure).encode("utf-8"),
            }

            with open(archive_file, "rb") as f:
                files = {"file": ("app.zip", f, "application/zip")}
                response = http_client.post(update_app_url, data=data, files=files)
                response.raise_for_status()

                ctx.console.print(f"[success]✅ App '{app_id}' updated successfully.[/]")

    except httpx.HTTPStatusError as e:
        ctx.console.print(
            f"[error]❌ Failed to update app. Server responded with {e.response.status_code}[/]"
        )
        try:
            error_detail = e.response.json()
            ctx.console.print(f"   Detail: {error_detail}")
        except json.JSONDecodeError:
            ctx.console.print(f"   Response: {e.response.text}")
        raise typer.Exit(1) from e
    except httpx.RequestError as e:
        ctx.console.print(
            "[error]❌ Failed to update app. An error occurred while making the request.[/]"
        )
        ctx.console.print(f"   Error: {e}")
        raise typer.Exit(1) from e
    except (OSError, shutil.Error) as e:
        ctx.console.print("[error]❌ Failed to create or read app archive file.[/]")
        ctx.console.print(f"   Error: {e}")
        raise typer.Exit(1) from e
