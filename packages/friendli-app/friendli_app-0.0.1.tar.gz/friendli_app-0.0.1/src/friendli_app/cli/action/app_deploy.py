# Copyright (c) 2025-present, FriendliAI Inc. All rights reserved.

"""Friendli App deploy action."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import httpx
import typer

from friendli_app.cli.util.file_utils import (
    get_directory_size,
    scan_directory_structure,
)
from friendli_app.cli.util.humanize.bytes import format_bytes

if TYPE_CHECKING:
    from ..context import AppContext


MAX_APP_DIR_SIZE_MB = 50
MAX_APP_DIR_SIZE_BYTES = MAX_APP_DIR_SIZE_MB * 1024 * 1024


def run(
    ctx: AppContext,
    app_dir_path: str,
    env: list[str],
    name: str | None = None,
    project_id: str | None = None,
) -> None:
    """Deploy an app."""
    ctx.console.print(f"🚀 Deploying app from '{app_dir_path}'")

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
    dir_size = get_directory_size(str(app_dir), exclude_dirs=[".venv"])
    if dir_size > MAX_APP_DIR_SIZE_BYTES:
        ctx.console.print(
            f"[error]❌ Directory size ({format_bytes(dir_size)})[/]"
            f"exceeds the limit of {MAX_APP_DIR_SIZE_MB}MB."
        )
        raise typer.Exit(1)

    # Check for dependency files
    pyproject_path = app_dir / "pyproject.toml"
    requirements_path = app_dir / "requirements.txt"
    pyproject_exists = pyproject_path.is_file()
    requirements_exists = requirements_path.is_file()

    install_command = ""
    if pyproject_exists:
        ctx.console.print("   Detected 'pyproject.toml'.")
        install_command = "pip3 install ${SRC_PKG} -t ${SRC_PKG}"
        if requirements_exists:
            ctx.console.print(
                "   Detected 'requirements.txt'. 'pyproject.toml' will be used for dependencies."
            )
    elif requirements_exists:
        ctx.console.print("   Detected 'requirements.txt'.")
        install_command = "pip3 install -r ${SRC_PKG}/requirements.txt -t ${SRC_PKG}"

    if env:
        ctx.console.print("   with environment variables:")
        for var in env:
            ctx.console.print(f"     - {var}")

    try:
        env_vars = dict(item.split("=", 1) for item in env)
    except ValueError:
        ctx.console.print("[error]❌ Invalid environment variable format. Please use KEY=VALUE.[/]")
        raise typer.Exit(1) from None

    http_client = ctx.http_client
    deploy_agent = "/beta/agent/agent-beta/deploy"

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            staging_dir = Path(tmpdir) / "app_src"
            shutil.copytree(
                app_dir,
                staging_dir,
                ignore=shutil.ignore_patterns(".venv", "__pycache__"),
            )

            # Generate and add build.sh to staging directory
            if install_command:
                script_content = (
                    f"#!/bin/sh\n{install_command} && cp -r ${{SRC_PKG}} ${{DEPLOY_PKG}}"
                )
            else:
                script_content = "#!/bin/sh\ncp -r ${SRC_PKG} ${DEPLOY_PKG}"

            build_script_path = staging_dir / "build.sh"
            build_script_path.write_text(script_content)
            build_script_path.chmod(0o755)  # Make the script executable

            archive_path = os.path.join(tmpdir, "agent_archive")
            shutil.make_archive(
                base_name=archive_path,
                format="zip",
                root_dir=staging_dir,
            )
            archive_file = f"{archive_path}.zip"

            # Scan the directory structure
            metadata_structure = scan_directory_structure(str(app_dir), exclude_dirs=[".venv"])

            data = {
                "env_variables": json.dumps(env_vars).encode("utf-8"),
                "metadata": json.dumps(metadata_structure).encode("utf-8"),
            }
            if name:
                data["name"] = name.encode("utf-8")
            if project_id:
                data["project_id"] = project_id.encode("utf-8")

            with open(archive_file, "rb") as f:
                files = {"file": ("app.zip", f, "application/zip")}

                response = http_client.post(deploy_agent, data=data, files=files)
                response.raise_for_status()

                response_data = response.json()
                agent_id = response_data.get("agent_id")

                ctx.console.print(
                    f"[success]✅ App '{name}' ({agent_id}) deploy triggered successfully.[/]"
                )
                ctx.console.print("   View status and usage details in the 'Overview' tab:")
                if "dev" in str(ctx.http_client.base_url):
                    base_url = "https://website-dev.friendli.site"
                else:
                    base_url = "https://friendli.ai"
                ctx.console.print(
                    f"   {urljoin(base_url, f'/suite/default-team/{project_id}/apps/{agent_id}/overview')}"
                )

    except httpx.HTTPStatusError as e:
        ctx.console.print(
            f"[error]❌ Failed to deploy app. Server responded with {e.response.status_code}[/]"
        )
        try:
            error_detail = e.response.json()
            ctx.console.print(f"   Detail: {error_detail}")
        except json.JSONDecodeError:
            ctx.console.print(f"   Response: {e.response.text}")
        raise typer.Exit(1) from e
    except httpx.RequestError as e:
        ctx.console.print(
            "[error]❌ Failed to deploy app. An error occurred while making the request.[/]"
        )
        ctx.console.print(f"   Error: {e}")
        raise typer.Exit(1) from e
    except (OSError, shutil.Error) as e:
        ctx.console.print("[error]❌ Failed to create or read app archive file.[/]")
        ctx.console.print(f"   Error: {e}")
        raise typer.Exit(1) from e
