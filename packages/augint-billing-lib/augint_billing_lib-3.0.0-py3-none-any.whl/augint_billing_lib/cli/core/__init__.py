"""Core operational commands for production use."""

import click

from augint_billing_lib.cli.core.demote import demote
from augint_billing_lib.cli.core.env import env_group
from augint_billing_lib.cli.core.process import process
from augint_billing_lib.cli.core.promote import promote
from augint_billing_lib.cli.core.sync import sync


@click.group(
    name="core",
    help="""
    Core operational commands for production use.

    These commands are production-ready and work with real resources.
    They handle environment configuration, API key management, usage
    synchronization, and event processing.

    Commands:
    • env     - Environment configuration management
    • promote - Promote API key to paid tier
    • demote  - Demote API key to free tier
    • sync    - Sync usage to Stripe
    • process - Process Stripe events
    """,
)
def core_group() -> None:
    """Core command group."""


# Add subcommands
core_group.add_command(env_group)
core_group.add_command(promote)
core_group.add_command(demote)
core_group.add_command(sync)
core_group.add_command(process)


__all__ = ["core_group"]
