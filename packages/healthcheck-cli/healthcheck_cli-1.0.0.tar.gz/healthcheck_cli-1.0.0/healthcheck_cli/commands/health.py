import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from healthcheck_cli.utils.healthchecker import HealthChecker

health_checker = HealthChecker()
console = Console()


app = typer.Typer()


@app.command()
def add(
    name: str = typer.Argument(..., help="Name of api endpoint"),
    url: str = typer.Argument(..., help="URL of the api endpoint"),
    description: str = typer.Option(
        "", "--description", "--d", help="Description of endpoint"
    ),
    timeout: int = typer.Option(10, "--timeout", "--t", help="Timeout in seconds"),
):
    config = health_checker.load_config()

    if name in config["endpoints"]:
        if not typer.confirm(
            f"Endpoint with name {name} already exists. Want to overwrite ?"
        ):
            rprint("❌ Cancelled")

    config["endpoints"][name] = {
        "url": url,
        "description": description,
        "timeout": timeout,
        "added_at": datetime.utcnow().isoformat(),
    }

    health_checker.save_config(config=config)
    rprint(f"✅ Added endpoint: [bold green]{name}[/bold green] -> {url}")


@app.command()
def remove(name: str):
    config = health_checker.load_config()

    if name not in config["endpoints"]:
        rprint(f"❌ Endpoint '{name}' not found")
        raise typer.Exit(1)

    if typer.confirm(f"Remove endpoint '{name}'?"):
        del config["endpoints"][name]
        health_checker.save_config(config=config)
        rprint(f"✅ Removed endpoint: [bold red]{name}[/bold red]")
    else:
        rprint("❌ Cancelled")


@app.command()
def list():
    config = health_checker.load_config()
    endpoints = config["endpoints"]

    if not endpoints:
        rprint("📋 No endpoints configured. Use 'healthcheck add' to add some!")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("URL", style="blue")
    table.add_column("Description", style="green")
    table.add_column("Timeout", justify="center")
    table.add_column("Added", style="dim")

    for name, details in endpoints.items():
        added_date = datetime.fromisoformat(details["added_at"]).strftime(
            "%Y-%m-%d %H:%M"
        )
        table.add_row(
            name,
            details["url"],
            details["description"] or "-",
            f"{details['timeout']}s",
            added_date,
        )

        console.print(table)


@app.command()
def check(
    name: Optional[str] = typer.Argument(None, help="Specific endpoint name to check"),
    all_endpoints: bool = typer.Option(
        False, "--all", "-a", help="Check all endpoints"
    ),
    timeout: Optional[int] = typer.Option(
        None, "--timeout", "-t", help="Override timeout in seconds"
    ),
):
    config = health_checker.load_config()
    endpoints = config["endpoints"]

    if not endpoints:
        rprint("❌ No endpoints configured. Use 'healthcheck add' to add some!")
        return

    if all_endpoints:
        to_check = endpoints
    elif name:
        if name not in endpoints:
            rprint(f"❌ Endpoint '{name}' not found")
            raise typer.Exit(1)
        to_check = {name: endpoints[name]}
    else:
        rprint("❌ Please specify an endpoint name or use --all")
        raise typer.Exit(1)

    asyncio.run(run_health_checks(to_check, timeout))


async def run_health_checks(endpoints: Dict, custom_timeout: Optional[int] = None):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:

        task = progress.add_task("Checking endpoints...", total=len(endpoints))

        results = []

        for name, details in endpoints.items():
            progress.update(task, description=f"Checking {name}...")

            timeout = custom_timeout or details["timeout"]
            status, code, response_time, error = (
                await health_checker.check_endpoint_health(details["url"], timeout)
            )

            results.append(
                {
                    "name": name,
                    "url": details["url"],
                    "status": status,
                    "code": code,
                    "response_time": response_time,
                    "error": error,
                }
            )

            progress.advance(task)

    display_results(results)


def display_results(results: List[Dict]):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Endpoint", style="cyan", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Code", justify="center")
    table.add_column("Response Time", justify="right")
    table.add_column("Error", style="red")

    healthy_count = 0

    for result in results:
        response_time_ms = float(result["response_time"])
        response_time_str = f"{response_time_ms:.0f}ms"
        if response_time_ms < 200:
            response_time_style = "green"
        elif response_time_ms < 1000:
            response_time_style = "yellow"
        else:
            response_time_style = "red"

        # Count healthy endpoints
        if "🟢" in result["status"]:
            healthy_count += 1

        table.add_row(
            result["name"],
            result["status"],
            str(result["code"]) if result["code"] else "-",
            f"[{response_time_style}]{response_time_str}[/{response_time_style}]",
            (
                result["error"][:50] + "..."
                if len(result["error"]) > 50
                else result["error"]
            ),
        )

    console.print(table)

    total = len(results)
    unhealthy_count = total - healthy_count

    if unhealthy_count == 0:
        console.print(Panel(f"🎉 All {total} endpoints are healthy!", style="green"))
    else:
        console.print(
            Panel(
                f"⚠️  {healthy_count}/{total} endpoints healthy, {unhealthy_count} need attention",
                style="yellow",
            )
        )


@app.command()
def monitor(
    interval: int = typer.Option(
        30, "--interval", "-i", help="Check interval in seconds"
    ),
    name: Optional[str] = typer.Argument(None, help="Specific endpoint to monitor"),
    all_endpoints: bool = typer.Option(
        False, "--all", "-a", help="Monitor all endpoints"
    ),
):
    config = health_checker.load_config()
    endpoints = config["endpoints"]

    if not endpoints:
        rprint("❌ No endpoints configured. Use 'healthcheck add' to add some!")
        return

    if all_endpoints:
        to_monitor = endpoints
    elif name:
        if name not in endpoints:
            rprint(f"❌ Endpoint '{name}' not found")
            raise typer.Exit(1)
        to_monitor = {name: endpoints[name]}
    else:
        rprint("❌ Please specify an endpoint name or use --all")
        raise typer.Exit(1)

    rprint(f"🔄 Starting monitoring every {interval} seconds... (Press Ctrl+C to stop)")

    try:
        asyncio.run(continuous_monitor(to_monitor, interval))
    except KeyboardInterrupt:
        rprint("\n👋 Monitoring stopped")


async def continuous_monitor(endpoints: Dict, interval: int):
    while True:
        console.clear()
        rprint(
            f"🩺 [bold]Health Check Monitor[/bold] - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        rprint(f"Checking {len(endpoints)} endpoint(s) every {interval}s\n")

        await run_health_checks(endpoints)

        rprint(f"\n⏰ Next check in {interval} seconds... (Press Ctrl+C to stop)")
        await asyncio.sleep(interval)


@app.command()
def export(
    output_file: str = typer.Option(
        "healthcheck-config.json", "--output", "-o", help="Output file path"
    )
):
    config = health_checker.load_config()

    output_path = Path(output_file)
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)

    rprint(
        f"✅ Configuration exported to: [bold green]{output_path.absolute()}[/bold green]"
    )


@app.command()
def import_config(input_file: str = typer.Argument(..., help="Input file path")):
    input_path = Path(input_file)

    if not input_path.exists():
        rprint(f"❌ File not found: {input_path}")
        raise typer.Exit(1)

    try:
        with open(input_path, "r") as f:
            new_config = json.load(f)

        if "endpoints" not in new_config:
            rprint("❌ Invalid configuration file format")
            raise typer.Exit(1)

        current_config = health_checker.load_config()

        if current_config["endpoints"] and not typer.confirm(
            "This will merge with existing endpoints. Continue?"
        ):
            rprint("❌ Cancelled")
            return

        current_config["endpoints"].update(new_config["endpoints"])
        health_checker.save_config(current_config)

        rprint(
            f"✅ Imported {len(new_config['endpoints'])} endpoint(s) from: [bold green]{input_path}[/bold green]"
        )

    except json.JSONDecodeError:
        rprint("❌ Invalid JSON file")
        raise typer.Exit(1)
