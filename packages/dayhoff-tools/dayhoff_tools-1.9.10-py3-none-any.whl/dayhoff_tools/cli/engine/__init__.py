"""Engine and Studio management commands for DHT CLI."""

import typer

# Initialize Typer apps
engine_app = typer.Typer(help="Manage compute engines for development.")
studio_app = typer.Typer(help="Manage persistent development studios.")

# Import all command functions
from .engine_core import engine_status, launch_engine, list_engines
from .engine_lifecycle import start_engine, stop_engine, terminate_engine
from .engine_maintenance import coffee, debug_engine, idle_timeout_cmd, repair_engine
from .engine_management import config_ssh, create_ami, resize_engine, ssh_engine
from .studio_commands import (
    attach_studio,
    create_studio,
    delete_studio,
    detach_studio,
    list_studios,
    reset_studio,
    resize_studio,
    studio_status,
)

# Register engine commands
engine_app.command("launch")(launch_engine)
engine_app.command("list")(list_engines)
engine_app.command("status")(engine_status)
engine_app.command("start")(start_engine)
engine_app.command("stop")(stop_engine)
engine_app.command("terminate")(terminate_engine)
engine_app.command("ssh")(ssh_engine)
engine_app.command("config-ssh")(config_ssh)
engine_app.command("resize")(resize_engine)
engine_app.command("gami")(create_ami)
engine_app.command("coffee")(coffee)
engine_app.command("idle")(idle_timeout_cmd)
engine_app.command("debug")(debug_engine)
engine_app.command("repair")(repair_engine)

# Register studio commands
studio_app.command("create")(create_studio)
studio_app.command("status")(studio_status)
studio_app.command("attach")(attach_studio)
studio_app.command("detach")(detach_studio)
studio_app.command("delete")(delete_studio)
studio_app.command("list")(list_studios)
studio_app.command("reset")(reset_studio)
studio_app.command("resize")(resize_studio)
