"""Core engine commands: launch, list, and status."""

import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import boto3
import typer
from rich import box
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .shared import (
    HOURLY_COSTS,
    _fetch_init_stages,
    check_aws_sso,
    console,
    format_duration,
    format_status,
    get_disk_usage_via_ssm,
    make_api_request,
    parse_launch_time,
    resolve_engine,
)


def launch_engine(
    name: str = typer.Argument(help="Name for the new engine"),
    engine_type: str = typer.Option(
        "cpu",
        "--type",
        "-t",
        help="Engine type: cpu, cpumax, t4, a10g, a100, 4_t4, 8_t4, 4_a10g, 8_a10g",
    ),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Override username"),
    boot_disk_size: Optional[int] = typer.Option(
        None,
        "--size",
        "-s",
        help="Boot disk size in GB (default: 50GB, min: 20GB, max: 1000GB)",
    ),
    availability_zone: Optional[str] = typer.Option(
        None,
        "--az",
        help="Prefer a specific Availability Zone (e.g., us-east-1b). If omitted the service will try all public subnets.",
    ),
):
    """Launch a new engine instance."""
    username = check_aws_sso()
    if user:
        username = user

    # Validate engine type
    valid_types = [
        "cpu",
        "cpumax",
        "t4",
        "a10g",
        "a100",
        "4_t4",
        "8_t4",
        "4_a10g",
        "8_a10g",
    ]
    if engine_type not in valid_types:
        console.print(f"[red]❌ Invalid engine type: {engine_type}[/red]")
        console.print(f"Valid types: {', '.join(valid_types)}")
        raise typer.Exit(1)

    # Validate boot disk size
    if boot_disk_size is not None:
        if boot_disk_size < 20:
            console.print("[red]❌ Boot disk size must be at least 20GB[/red]")
            raise typer.Exit(1)
        if boot_disk_size > 1000:
            console.print("[red]❌ Boot disk size cannot exceed 1000GB[/red]")
            raise typer.Exit(1)

    cost = HOURLY_COSTS.get(engine_type, 0)
    disk_info = f" with {boot_disk_size}GB boot disk" if boot_disk_size else ""
    console.print(
        f"Launching [cyan]{name}[/cyan] ({engine_type}){disk_info} for ${cost:.2f}/hour..."
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("Creating engine...", total=None)

        request_data: Dict[str, Any] = {
            "name": name,
            "user": username,
            "engine_type": engine_type,
        }
        if boot_disk_size is not None:
            request_data["boot_disk_size"] = boot_disk_size
        if availability_zone:
            request_data["availability_zone"] = availability_zone

        response = make_api_request("POST", "/engines", json_data=request_data)

    if response.status_code == 201:
        data = response.json()
        console.print(f"[green]✓ Engine launched successfully![/green]")
        console.print(f"Instance ID: [cyan]{data['instance_id']}[/cyan]")
        console.print(f"Type: {data['instance_type']} (${cost:.2f}/hour)")
        if boot_disk_size:
            console.print(f"Boot disk: {boot_disk_size}GB")
        console.print("\nThe engine is initializing. This may take a few minutes.")
        console.print(f"Check status with: [cyan]dh engine status {name}[/cyan]")
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to launch engine: {error}[/red]")


def list_engines(
    user: Optional[str] = typer.Option(None, "--user", "-u", help="Filter by user"),
    running_only: bool = typer.Option(
        False, "--running", help="Show only running engines"
    ),
    stopped_only: bool = typer.Option(
        False, "--stopped", help="Show only stopped engines"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed status (slower)"
    ),
):
    """List engines (shows all engines by default)."""
    current_user = check_aws_sso()

    params = {}
    if user:
        params["user"] = user
    if detailed:
        params["check_ready"] = "true"

    response = make_api_request("GET", "/engines", params=params)

    if response.status_code == 200:
        data = response.json()
        engines = data.get("engines", [])

        # Filter by state if requested
        if running_only:
            engines = [e for e in engines if e["state"].lower() == "running"]
        elif stopped_only:
            engines = [e for e in engines if e["state"].lower() == "stopped"]

        if not engines:
            console.print("No engines found.")
            return

        # Only fetch detailed info if requested (slow)
        stages_map = {}
        if detailed:
            stages_map = _fetch_init_stages([e["instance_id"] for e in engines])

        # Create table
        table = Table(title="Engines", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Instance ID", style="dim")
        table.add_column("Type")
        table.add_column("User")
        table.add_column("Status")
        if detailed:
            table.add_column("Disk Usage")
        table.add_column("Uptime/Since")
        table.add_column("$/hour", justify="right")

        for engine in engines:
            launch_time = parse_launch_time(engine["launch_time"])
            uptime = datetime.now(timezone.utc) - launch_time
            hourly_cost = HOURLY_COSTS.get(engine["engine_type"], 0)

            if engine["state"].lower() == "running":
                time_str = format_duration(uptime)
                # Only get disk usage if detailed mode
                if detailed:
                    disk_usage = get_disk_usage_via_ssm(engine["instance_id"]) or "-"
                else:
                    disk_usage = None
            else:
                time_str = launch_time.strftime("%Y-%m-%d %H:%M")
                disk_usage = "-" if detailed else None

            row_data = [
                engine["name"],
                engine["instance_id"],
                engine["engine_type"],
                engine["user"],
                format_status(engine["state"], engine.get("ready")),
            ]
            if detailed:
                row_data.append(disk_usage)
            row_data.extend(
                [
                    time_str,
                    f"${hourly_cost:.2f}",
                ]
            )

            table.add_row(*row_data)

        console.print(table)
        if not detailed and any(e["state"].lower() == "running" for e in engines):
            console.print(
                "\n[dim]Tip: Use --detailed to see disk usage and bootstrap status (slower)[/dim]"
            )
    else:
        error = response.json().get("error", "Unknown error")
        console.print(f"[red]❌ Failed to list engines: {error}[/red]")


def engine_status(
    name_or_id: str = typer.Argument(help="Engine name or instance ID"),
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed status (slower)"),
    show_log: bool = typer.Option(False, "--show-log", help="Show bootstrap log (requires --detailed)"),
):
    """Show engine status and information."""
    check_aws_sso()

    # Get all engines to resolve name
    response = make_api_request("GET", "/engines")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engines[/red]")
        raise typer.Exit(1)

    engines = response.json().get("engines", [])
    engine = resolve_engine(name_or_id, engines)
    
    # Fast status display (default)
    if not detailed:       
        # Fetch idle status via SSM with longer timeout
        ssm = boto3.client("ssm", region_name="us-east-1")
        idle_data = None  # Use None to indicate no data received
        
        if engine["state"].lower() == "running":
            try:
                resp = ssm.send_command(
                    InstanceIds=[engine["instance_id"]],
                    DocumentName="AWS-RunShellScript",
                    Parameters={
                        "commands": [
                            "cat /var/run/idle-detector/last_state.json 2>/dev/null || echo '{}'"
                        ],
                        "executionTimeout": ["10"],
                    },
                )
                cid = resp["Command"]["CommandId"]
                
                # Wait up to 3 seconds for result
                for _ in range(6):  # 6 * 0.5 = 3 seconds
                    time.sleep(0.5)
                    inv = ssm.get_command_invocation(
                        CommandId=cid, InstanceId=engine["instance_id"]
                    )
                    if inv["Status"] in ["Success", "Failed"]:
                        break
                
                if inv["Status"] == "Success":
                    content = inv["StandardOutputContent"].strip()
                    if content and content != "{}":
                        idle_data = json.loads(content)
                    else:
                        idle_data = {}  # Empty response but SSM worked
            except Exception:
                idle_data = None  # SSM failed
        
        # Determine running state display
        running_state = engine["state"].lower()
        if running_state == "running":
            run_disp = "[green]Running[/green]"
        elif running_state == "pending":
            run_disp = "[yellow]Starting...[/yellow]"
        elif running_state == "stopping":
            run_disp = "[yellow]Stopping...[/yellow]"
        elif running_state == "stopped":
            run_disp = "[dim]Stopped[/dim]"
        else:
            run_disp = engine["state"].capitalize()
        
        # Determine idle/active status
        idle_disp = ""
        if running_state == "running":
            if idle_data is None:
                # SSM failed - we don't know the status
                idle_disp = "  [dim]N/A[/dim]"
            elif not idle_data:
                # Empty data - likely very early in boot
                idle_disp = "  [dim]N/A[/dim]"
            else:
                # We have data
                is_idle = idle_data.get("idle", False)
                timeout_sec = idle_data.get("timeout_sec")
                idle_seconds = idle_data.get("idle_seconds", 0) if is_idle else 0
                
                if is_idle:
                    if isinstance(timeout_sec, int) and isinstance(idle_seconds, int):
                        remaining = max(0, timeout_sec - idle_seconds)
                        remaining_mins = remaining // 60
                        if remaining_mins == 0:
                            idle_disp = f"  [yellow]Idle {idle_seconds//60}m/{timeout_sec//60}m: [red]<1m[/red] left[/yellow]"
                        else:
                            idle_disp = f"  [yellow]Idle {idle_seconds//60}m/{timeout_sec//60}m: [red]{remaining_mins}m[/red] left[/yellow]"
                    else:
                        idle_disp = "  [yellow]Idle ?/?[/yellow]"
                else:
                    # Actively not idle
                    idle_disp = "  [green]Active[/green]"
        
        # Build status lines - minimal info for fast view
        status_lines = [
            f"[blue]{engine['name']}[/blue]  {run_disp}{idle_disp}",
        ]
        
        # Add activity sensors if we have idle data
        if idle_data and idle_data.get("reasons"):
            status_lines.append("")  # blank line before sensors
            
            sensor_map = {
                "CoffeeLockSensor": ("☕", "Coffee"),
                "ActiveLoginSensor": ("🐚", "SSH"),
                "IDEConnectionSensor": ("🖥 ", "IDE"),
                "DockerWorkloadSensor": ("🐳", "Docker"),
            }
            
            for r in idle_data.get("reasons", []):
                sensor = r.get("sensor", "Unknown")
                active = r.get("active", False)
                icon, label = sensor_map.get(sensor, ("?", sensor))
                status_str = "[green]YES[/green]" if active else "[dim]nope[/dim]"
                status_lines.append(f"  {icon} {label:6} {status_str}")
        
        # Display in a nice panel
        console.print(
            Panel("\n".join(status_lines), title="Engine Status", border_style="blue")
        )
        return  # Exit early for fast status

    # Get detailed engine status including idle detector info (for --detailed mode)
    response = make_api_request("GET", f"/engines/{engine['instance_id']}")
    if response.status_code != 200:
        console.print("[red]❌ Failed to fetch engine details[/red]")
        raise typer.Exit(1)

    engine_details = response.json()
    engine = engine_details.get("engine", engine)  # Use detailed info if available
    idle_detector = engine_details.get("idle_detector", {}) or {}
    attached_studios = engine_details.get("attached_studios", [])

    # Calculate costs
    launch_time = parse_launch_time(engine["launch_time"])
    uptime = datetime.now(timezone.utc) - launch_time
    hourly_cost = HOURLY_COSTS.get(engine["engine_type"], 0)
    # total_cost intentionally not shown in status view

    stages_map = _fetch_init_stages([engine["instance_id"]])
    stage_val = stages_map.get(engine["instance_id"], "-")

    # Try to fetch actual boot time via SSM (best-effort)
    boot_time_str: Optional[str] = None
    try:
        if engine["state"].lower() == "running":
            ssm = boto3.client("ssm", region_name="us-east-1")
            resp = ssm.send_command(
                InstanceIds=[engine["instance_id"]],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    "commands": ["uptime -s || who -b | awk '{print $3\" \"$4}'"]
                },
            )
            cid = resp["Command"]["CommandId"]
            time.sleep(1)
            inv = ssm.get_command_invocation(
                CommandId=cid, InstanceId=engine["instance_id"]
            )
            if inv.get("Status") == "Success":
                boot_time_str = (
                    (inv.get("StandardOutputContent") or "").strip().splitlines()[0]
                    if inv.get("StandardOutputContent")
                    else None
                )
    except Exception:
        boot_time_str = None

    started_line = (
        f"[bold]Started:[/bold]     {boot_time_str} ({format_duration(uptime)} ago)"
        if boot_time_str
        else f"[bold]Started:[/bold]     {launch_time.strftime('%Y-%m-%d %H:%M:%S')} ({format_duration(uptime)} ago)"
    )

    # ---------------- Front-loaded summary ----------------
    running_state = engine["state"].lower()
    if running_state == "running":
        run_disp = "[green]Running[/green]"
    elif running_state == "pending":
        run_disp = "[yellow]Starting...[/yellow]"
    elif running_state == "stopping":
        run_disp = "[yellow]Stopping...[/yellow]"
    elif running_state == "stopped":
        run_disp = "[dim]Stopped[/dim]"
    else:
        run_disp = engine["state"].capitalize()

    # Compose Active/Idle header with extra detail when idle
    def _compute_active_disp(idle_info: Dict[str, Any]) -> str:
        # If we don't have idle info or it's explicitly unavailable, show N/A
        if not idle_info or idle_info.get("available") == False:
            return "[dim]N/A[/dim]"
            
        if idle_info.get("status") == "active":
            return "[green]Active[/green]"
        if running_state in ("stopped", "stopping"):
            return "[dim]N/A[/dim]"
            
        # If idle, show time/threshold with time remaining if available
        if idle_info.get("status") == "idle":
            idle_seconds_v = idle_info.get("idle_seconds")
            thresh_v = idle_info.get("idle_threshold")
            if isinstance(idle_seconds_v, (int, float)) and isinstance(thresh_v, (int, float)):
                remaining = max(0, int(thresh_v) - int(idle_seconds_v))
                remaining_mins = remaining // 60
                if remaining_mins == 0:
                    return f"[yellow]Idle {int(idle_seconds_v)//60}m/{int(thresh_v)//60}m: [red]<1m[/red] left[/yellow]"
                else:
                    return f"[yellow]Idle {int(idle_seconds_v)//60}m/{int(thresh_v)//60}m: [red]{remaining_mins}m[/red] left[/yellow]"
            elif isinstance(thresh_v, (int, float)):
                return f"[yellow]Idle ?/{int(thresh_v)//60}m[/yellow]"
            else:
                return "[yellow]Idle ?/?[/yellow]"
        
        # Default to N/A if we can't determine status
        return "[dim]N/A[/dim]"

    active_disp = _compute_active_disp(idle_detector)

    top_lines = [
        f"[blue]{engine['name']}[/blue]  {run_disp}  {active_disp}\n",
    ]

    # Studios summary next, with studio name in purple/magenta
    studios_line = None
    if attached_studios:
        stu_texts = [
            f"[magenta]{s.get('user', 'studio')}[/magenta] ({s.get('studio_id', 'unknown')})"
            for s in attached_studios
        ]
        studios_line = "Studios: " + ", ".join(stu_texts)
        top_lines.append(studios_line)

    # Paragraph break
    top_lines.append("")

    # ---------------- Details block (white/default) ----------------
    status_lines = [
        f"Name:        {engine['name']}",
        f"Instance:    {engine['instance_id']}",
        f"Type:        {engine['engine_type']} ({engine['instance_type']})",
        f"Status:      {engine['state']}",
        f"User:        {engine['user']}",
        f"IP:          {engine.get('public_ip', 'N/A')}",
        started_line,
        f"$/hour:     ${hourly_cost:.2f}",
    ]

    # Disk usage (like list --detailed)
    if engine["state"].lower() == "running":
        disk_usage = get_disk_usage_via_ssm(engine["instance_id"]) or "-"
        status_lines.append(f"Disk:       {disk_usage}")

    # Idle timeout (show even when not idle) - but only if we have data
    if idle_detector.get("available"):
        idle_threshold_secs: Optional[int] = None
        # Prefer value from idle detector overlay if present
        try:
            if isinstance(idle_detector.get("idle_threshold"), (int, float)):
                idle_threshold_secs = int(idle_detector["idle_threshold"])
        except Exception:
            idle_threshold_secs = None

        if idle_threshold_secs is None and engine["state"].lower() == "running":
            # Fallback: read /etc/engine.env via SSM
            try:
                ssm = boto3.client("ssm", region_name="us-east-1")
                resp = ssm.send_command(
                    InstanceIds=[engine["instance_id"]],
                    DocumentName="AWS-RunShellScript",
                    Parameters={
                        "commands": [
                            "grep -E '^IDLE_TIMEOUT_SECONDS=' /etc/engine.env | cut -d'=' -f2 || echo '?'",
                        ],
                        "executionTimeout": ["5"],
                    },
                )
                cid = resp["Command"]["CommandId"]
                time.sleep(1)
                inv = ssm.get_command_invocation(
                    CommandId=cid, InstanceId=engine["instance_id"]
                )
                if inv.get("Status") == "Success":
                    out = (inv.get("StandardOutputContent") or "").strip()
                    if out and out != "?" and out.isdigit():
                        idle_threshold_secs = int(out)
            except Exception:
                idle_threshold_secs = None

        if idle_threshold_secs is not None:
            status_lines.append(
                f"Idle timeout: {idle_threshold_secs//60}m ({idle_threshold_secs}s)"
            )
        else:
            status_lines.append("Idle timeout: unknown")
    else:
        # No idle detector data available
        status_lines.append("Idle timeout: N/A")

    # Health report (only if bootstrap finished)
    if stage_val == "finished":
        try:
            ssm = boto3.client("ssm", region_name="us-east-1")
            res = ssm.send_command(
                InstanceIds=[engine["instance_id"]],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    "commands": [
                        "cat /opt/dayhoff/state/engine-health.json 2>/dev/null || cat /var/run/engine-health.json 2>/dev/null || true"
                    ],
                    "executionTimeout": ["10"],
                },
            )
            cid = res["Command"]["CommandId"]
            time.sleep(1)
            inv = ssm.get_command_invocation(
                CommandId=cid, InstanceId=engine["instance_id"]
            )
            if inv["Status"] == "Success":
                import json as _json

                health = _json.loads(inv["StandardOutputContent"].strip() or "{}")
                status_lines.append("")
                status_lines.append("[bold]Health:[/bold]")
                status_lines.append(
                    f"  • GPU Drivers: {'OK' if health.get('drivers_ok') else 'MISSING'}"
                )
                idle_stat = health.get("idle_detector_service") or health.get(
                    "idle_detector_timer", "unknown"
                )
                status_lines.append(f"  • Idle Detector: {idle_stat}")
        except Exception:
            pass

    # Try to enrich/fallback idle-detector details from on-engine summary file via SSM
    def _fetch_idle_summary_via_ssm(instance_id: str) -> Optional[Dict]:
        try:
            ssm = boto3.client("ssm", region_name="us-east-1")
            res = ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    "commands": [
                        "cat /var/run/idle-detector/last_state.json 2>/dev/null || true",
                    ],
                    "executionTimeout": ["5"],
                },
            )
            cid = res["Command"]["CommandId"]
            # Wait up to 2 seconds for SSM command to complete (was 1 second)
            for _ in range(4):  # 4 * 0.5 = 2 seconds
                time.sleep(0.5)
                inv = ssm.get_command_invocation(CommandId=cid, InstanceId=instance_id)
                if inv["Status"] in ["Success", "Failed"]:
                    break
            if inv["Status"] != "Success":
                return None
            content = inv["StandardOutputContent"].strip()
            if not content:
                return None
            data = json.loads(content)
            # Convert last_state schema (new or old) to idle_detector schema used by CLI output
            idle_info: Dict[str, Any] = {"available": True}

            # Active/idle
            idle_flag = bool(data.get("idle", False))
            idle_info["status"] = "idle" if idle_flag else "active"

            # Threshold and elapsed
            if isinstance(data.get("timeout_sec"), (int, float)):
                idle_info["idle_threshold"] = int(data["timeout_sec"])  # seconds
            if isinstance(data.get("idle_seconds"), (int, float)):
                idle_info["idle_seconds"] = int(data["idle_seconds"])

            # Keep raw reasons for sensor display when available (new schema)
            if isinstance(data.get("reasons"), list):
                idle_info["_reasons_raw"] = data["reasons"]
            else:
                # Fallback: synthesize reasons from the old forensics layout
                f_all = data.get("forensics", {}) or {}
                synthesized = []

                def _mk(sensor_name: str, key: str):
                    entry = f_all.get(key, {}) or {}
                    synthesized.append(
                        {
                            "sensor": sensor_name,
                            "active": bool(entry.get("active", False)),
                            "reason": entry.get("reason", ""),
                            "forensic": entry.get("forensic", {}),
                        }
                    )

                _mk("CoffeeLockSensor", "coffee")
                _mk("ActiveLoginSensor", "ssh")
                _mk("IDEConnectionSensor", "ide")
                _mk("DockerWorkloadSensor", "docker")
                idle_info["_reasons_raw"] = synthesized

            # Derive details from sensors
            for r in idle_info.get("_reasons_raw", []):
                if not r.get("active"):
                    continue
                sensor = (r.get("sensor") or "").lower()
                forensic = r.get("forensic") or {}
                if sensor == "ideconnectionsensor":
                    # Prefer unique_pid_count written by new detector
                    cnt = forensic.get("unique_pid_count")
                    if not isinstance(cnt, int):
                        cnt = forensic.get("matches")
                    if isinstance(cnt, int):
                        idle_info["ide_connections"] = {"connection_count": cnt}
                    else:
                        idle_info["ide_connections"] = {"connection_count": 1}
                elif sensor == "coffeelocksensor":
                    rem = forensic.get("remaining_sec")
                    if isinstance(rem, (int, float)) and rem > 0:
                        idle_info["coffee_lock"] = format_duration(
                            timedelta(seconds=int(rem))
                        )
                elif sensor == "activeloginsensor":
                    sess = {
                        "tty": forensic.get("tty", "pts/?"),
                        "pid": forensic.get("pid", "?"),
                        "idle_time": forensic.get("idle_sec", 0),
                        "from_ip": forensic.get("remote_addr", "unknown"),
                    }
                    idle_info.setdefault("ssh_sessions", []).append(sess)
            return idle_info
        except Exception:
            return None

    # Always try to enrich from on-engine summary (fast, best-effort)
    overlay = _fetch_idle_summary_via_ssm(engine["instance_id"])
    if overlay:
        # If API didn't indicate availability, replace entirely; otherwise fill gaps
        if not idle_detector.get("available"):
            idle_detector = overlay
        else:
            for k, v in overlay.items():
                idle_detector.setdefault(k, v)
    else:
        # SSM failed - mark as unavailable if we don't have good data
        if not idle_detector.get("available"):
            idle_detector = {"available": False}  # Mark as unavailable

    # Recompute header display with latest data
    active_disp = _compute_active_disp(idle_detector)
    top_lines[0] = f"[blue]{engine['name']}[/blue]  {run_disp}  {active_disp}\n"

    # Activity Sensors (show all with YES/no)
    if idle_detector.get("available"):
        status_lines.append("")
        status_lines.append("[bold]Activity Sensors:[/bold]")
        reasons_raw = idle_detector.get("_reasons_raw", []) or []
        by_sensor: Dict[str, Dict[str, Any]] = {}
        for r in reasons_raw:
            nm = r.get("sensor")
            if nm:
                by_sensor[nm] = r

        def _sensor_line(label: str, key: str, emoji: str) -> str:
            r = by_sensor.get(key, {})
            active = bool(r.get("active"))
            reason_txt = r.get("reason") or ("" if not active else "active")
            flag = "[green]YES[/green]" if active else "[dim]nope[/dim]"
            return (
                f"  {emoji} {label}: {flag} {('- ' + reason_txt) if reason_txt else ''}"
            )

        status_lines.append(_sensor_line("Coffee", "CoffeeLockSensor", "☕"))
        status_lines.append(_sensor_line("Shell ", "ActiveLoginSensor", "🐚"))
        status_lines.append(_sensor_line(" IDE   ", "IDEConnectionSensor", "🖥"))
        status_lines.append(_sensor_line("Docker", "DockerWorkloadSensor", "🐳"))

        # Recompute display with latest idle detector data
        active_disp = _compute_active_disp(idle_detector)
        # Rewrite top header line (index 0) to include updated display
        top_lines[0] = f"[blue]{engine['name']}[/blue]  {run_disp}  {active_disp}\n"

    # Combine top summary and details
    all_lines = top_lines + status_lines
    console.print(
        Panel("\n".join(all_lines), title="Engine Status", border_style="blue")
    )

    if show_log:
        if not detailed:
            console.print("[yellow]Note: --show-log requires --detailed flag[/yellow]")
            return
        console.print("\n[bold]Bootstrap Log:[/bold]")
        try:
            ssm = boto3.client("ssm", region_name="us-east-1")
            resp = ssm.send_command(
                InstanceIds=[engine["instance_id"]],
                DocumentName="AWS-RunShellScript",
                Parameters={
                    "commands": [
                        "cat /var/log/engine-setup.log 2>/dev/null || echo 'No setup log found'"
                    ],
                    "executionTimeout": ["15"],
                },
            )
            cid = resp["Command"]["CommandId"]
            time.sleep(2)
            inv = ssm.get_command_invocation(
                CommandId=cid, InstanceId=engine["instance_id"]
            )
            if inv["Status"] == "Success":
                log_content = inv["StandardOutputContent"].strip()
                if log_content:
                    console.print(f"[dim]{log_content}[/dim]")
                else:
                    console.print("[yellow]No bootstrap log available[/yellow]")
            else:
                console.print("[red]❌ Could not retrieve bootstrap log[/red]")
        except Exception as e:
            console.print(f"[red]❌ Error fetching log: {e}[/red]")
