# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""CLI for the Market Metering client."""

import asyncio
import os
import shlex
from datetime import datetime, timezone
from pprint import pformat
from typing import Any

import asyncclick as click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import CompleteStyle

from ._client import MarketMeteringApiClient
from .types import (
    EnergyFlowDirection,
    MarketLocationId,
    MarketLocationIdType,
    MarketLocationRef,
    MarketLocationSeries,
    MetricType,
    ResamplingOptions,
    TimeResolution,
)


def format_datetime(dt: datetime | None) -> str:
    """Format datetime object to a readable string, or return 'N/A' if None."""
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z") if dt else "N/A"


def print_series(series: MarketLocationSeries, raw: bool = False) -> None:
    """Print the series details in a nicely formatted way with colors."""
    if raw:
        click.echo(pformat(series, compact=True))
        return

    # Header
    click.echo(click.style("Market Location Series:", bold=True, underline=True))

    # Market Location info
    ml_ref = series.market_location_ref
    click.echo(f"  {click.style('Enterprise ID:', fg='cyan')} {ml_ref.enterprise_id}")
    click.echo(
        f"  {click.style('Location ID:', fg='cyan')} "
        f"{ml_ref.market_location_id.value} ({ml_ref.market_location_id.type.name})"
    )
    click.echo(f"  {click.style('Direction:', fg='cyan')} {series.direction.name}")
    click.echo(
        f"  {click.style('Metric:', fg='cyan')} "
        f"{series.metric_type.name} [{series.metric_unit.name}]"
    )
    click.echo(f"  {click.style('Resolution:', fg='cyan')} {series.resolution.name}")

    # Samples
    click.echo(
        f"\n  {click.style('Samples:', fg='green')} ({len(series.samples)} total)"
    )
    for sample in series.samples[:10]:  # Limit display to first 10
        value_str = f"{sample.value:.4f}" if sample.value is not None else "N/A"
        quality_color = "green" if sample.quality.name == "MEASURED" else "yellow"
        click.echo(
            f"    {format_datetime(sample.sample_time)}: "
            f"{click.style(value_str, fg='white')} "
            f"[{click.style(sample.quality.name, fg=quality_color)}]"
        )

    if len(series.samples) > 10:
        click.echo(f"    ... and {len(series.samples) - 10} more samples")

    click.echo()


@click.group(invoke_without_command=True)
@click.option(
    "--url",
    help="Market Metering API URL",
    envvar="MARKETMETERING_API_URL",
    show_envvar=True,
)
@click.option(
    "--auth-key",
    help="API auth key for authentication",
    envvar="MARKETMETERING_API_AUTH_KEY",
    show_envvar=True,
    required=False,
)
@click.option(
    "--sign-secret",
    help="API signing secret for authentication",
    envvar="MARKETMETERING_API_SIGN_SECRET",
    show_envvar=True,
    required=False,
    default=None,
)
@click.option(
    "--raw",
    is_flag=True,
    help="Print output raw instead of formatted and colored",
    required=False,
    default=False,
)
@click.pass_context
async def cli(
    ctx: click.Context,
    url: str,
    auth_key: str | None,
    sign_secret: str | None,
    raw: bool,
) -> None:
    """Market Metering Service CLI."""
    if ctx.obj is None:
        ctx.obj = {}

    if not auth_key:
        raise click.BadParameter(
            "You must provide an API auth key using --auth-key or "
            "the MARKETMETERING_API_AUTH_KEY environment variable."
        )

    click.echo(f"Using API URL: {url}", err=True)
    click.echo(f"Using API Auth Key: {auth_key[:4]}{'*' * 8}", err=True)

    if sign_secret:
        if len(sign_secret) > 8:
            click.echo(
                f"Using API Signing Secret: {sign_secret[:4]}{'*' * 8}", err=True
            )
        else:
            click.echo("Using API Signing Secret (not shown).", err=True)

    ctx.obj["client"] = MarketMeteringApiClient(
        server_url=url,
        auth_key=auth_key,
        sign_secret=sign_secret,
        connect=True,
    )

    ctx.obj["params"] = {
        "url": url,
        "auth_key": auth_key,
        "sign_secret": sign_secret,
    }

    ctx.obj["raw"] = raw

    # Check if a subcommand was given
    if ctx.invoked_subcommand is None:
        await interactive_mode(url, auth_key, sign_secret)


def parse_market_location(value: str) -> MarketLocationRef:
    """Parse a market location string.

    Format: enterprise_id:location_id:type
    Example: 42:DE01234567890:MALO_ID
    """
    parts = value.split(":")
    if len(parts) != 3:
        raise click.BadParameter(
            f"Invalid market location format: {value}. "
            "Expected format: enterprise_id:location_id:type"
        )

    try:
        enterprise_id = int(parts[0])
    except ValueError as exc:
        raise click.BadParameter(f"Invalid enterprise_id: {parts[0]}") from exc

    location_id = parts[1]

    try:
        id_type = MarketLocationIdType[parts[2].upper()]
    except KeyError as exc:
        valid_types = ", ".join(
            t.name for t in MarketLocationIdType if t.name != "UNSPECIFIED"
        )
        raise click.BadParameter(
            f"Invalid location type: {parts[2]}. Valid types: {valid_types}"
        ) from exc

    return MarketLocationRef(
        enterprise_id=enterprise_id,
        market_location_id=MarketLocationId(value=location_id, type=id_type),
    )


class MarketLocationParamType(click.ParamType):
    """Click parameter type for market locations."""

    name = "market_location"

    def convert(
        self, value: Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> MarketLocationRef:
        """Convert the value to a MarketLocationRef."""
        if isinstance(value, MarketLocationRef):
            return value
        try:
            return parse_market_location(str(value))
        except click.BadParameter as e:
            self.fail(str(e), param, ctx)


@cli.command("stream")
@click.pass_context
@click.argument(
    "market-locations",
    required=True,
    type=MarketLocationParamType(),
    nargs=-1,
)
@click.option(
    "--direction",
    "-d",
    type=click.Choice([d.name for d in EnergyFlowDirection if d.name != "UNSPECIFIED"]),
    multiple=True,
    default=["IMPORT"],
    help="Energy flow direction(s)",
)
@click.option(
    "--metric",
    "-m",
    type=click.Choice([m.name for m in MetricType if m.name != "UNSPECIFIED"]),
    multiple=True,
    default=["ACTIVE_ENERGY"],
    help="Metric type(s)",
)
@click.option(
    "--start-time",
    type=click.DateTime(),
    help="Start time for historical data (ISO format)",
)
@click.option(
    "--end-time",
    type=click.DateTime(),
    help="End time (ISO format). If omitted, streams in real-time.",
)
@click.option(
    "--resolution",
    type=click.Choice([r.name for r in TimeResolution if r.name != "UNSPECIFIED"]),
    help="Resampling resolution",
)
# pylint: disable=too-many-arguments,too-many-positional-arguments
async def stream_cmd(
    ctx: click.Context,
    market_locations: tuple[MarketLocationRef, ...],
    direction: tuple[str, ...],
    metric: tuple[str, ...],
    start_time: datetime | None,
    end_time: datetime | None,
    resolution: str | None,
) -> None:
    """Stream metering samples from Market Locations.

    MARKET_LOCATIONS are specified as: enterprise_id:location_id:type

    Example:
        42:DE01234567890:MALO_ID

    Valid types: MALO_ID, MPAN, ESI_ID, NMI, OTHER

    Args:
        ctx: Click context with client and options.
        market_locations: Market location references to stream.
        direction: Energy flow directions (IMPORT/EXPORT).
        metric: Metric types to request.
        start_time: Optional start time for historical data.
        end_time: Optional end time.
        resolution: Optional resampling resolution.
    """
    client: MarketMeteringApiClient = ctx.obj["client"]
    raw: bool = ctx.obj["raw"]

    directions = [EnergyFlowDirection[d] for d in direction]
    metric_types = [MetricType[m] for m in metric]

    # Make times timezone-aware if provided
    if start_time and start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time and end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)

    resampling = None
    if resolution:
        resampling = ResamplingOptions(resolution=TimeResolution[resolution])

    click.echo(
        f"Streaming from {len(market_locations)} market location(s)...", err=True
    )

    try:
        async for series in client.stream_samples(
            market_locations=list(market_locations),
            directions=directions,
            metric_types=metric_types,
            start_time=start_time,
            end_time=end_time,
            resampling=resampling,
        ):
            print_series(series, raw=raw)
    except KeyboardInterrupt:
        click.echo("\nStream interrupted.", err=True)


@cli.command()
@click.pass_obj
async def repl(obj: dict[str, Any]) -> None:
    """Start an interactive interface."""
    await interactive_mode(
        obj["params"]["url"],
        obj["params"]["auth_key"],
        obj["params"]["sign_secret"],
    )


async def interactive_mode(url: str, auth_key: str, sign_secret: str | None) -> None:
    """Interactive mode for the CLI."""
    hist_file = os.path.expanduser("~/.marketmetering_cli_history.txt")
    session: PromptSession[str] = PromptSession(history=FileHistory(filename=hist_file))

    user_commands = [
        "stream",
        "exit",
        "help",
    ]

    async def display_help() -> None:
        await cli.main(args=["--help"], standalone_mode=False)

    completer = NestedCompleter.from_nested_dict(
        {command: None for command in user_commands}
    )

    while True:
        with patch_stdout():
            try:
                user_input = await session.prompt_async(
                    "> ",
                    completer=completer,
                    complete_style=CompleteStyle.READLINE_LIKE,
                )
            except EOFError:
                break

        if user_input == "help" or not user_input:
            await display_help()
        elif user_input == "exit":
            break
        else:
            params = (
                ["--url", url, "--auth-key", auth_key]
                + (["--sign-secret", sign_secret] if sign_secret else [])
                + shlex.split(user_input)
            )

            try:
                await cli.main(args=params, standalone_mode=False)
            except click.ClickException as e:
                click.echo(e)


def main() -> None:
    """Entrypoint for the CLI."""
    asyncio.run(cli.main())


if __name__ == "__main__":
    main()
