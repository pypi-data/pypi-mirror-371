"""Augint Billing CLI - Complete ground-up redesign."""

import click

from augint_billing_lib.cli.admin import admin_group
from augint_billing_lib.cli.core import core_group
from augint_billing_lib.cli.report import report_group
from augint_billing_lib.cli.setup import setup_group
from augint_billing_lib.cli.test import test_group
from augint_billing_lib.cli.troubleshoot import troubleshoot_group
from augint_billing_lib.cli.validate import validate_group


@click.group(
    name="ai-billing",
    help="""
    Augint Billing CLI - Manage API billing with Stripe integration.

    This CLI provides tools for managing the billing system, from production
    operations to testing and troubleshooting.

    IMPORTANT: Commands are organized by capability:

    • core/         - Production-ready operational commands
    • test/         - Testing commands (separated by capability)
    • validate/     - Validation and verification
    • troubleshoot/ - Diagnostic and debugging
    • report/       - Reporting and analytics
    • admin/        - Administrative operations

    Use 'ai-billing COMMAND --help' for more information on a command.
    """,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Main CLI entry point."""
    # Store common settings in context
    ctx.ensure_object(dict)


# Register command groups
cli.add_command(core_group)
cli.add_command(test_group)
cli.add_command(validate_group)
cli.add_command(troubleshoot_group)
cli.add_command(report_group)
cli.add_command(admin_group)
cli.add_command(setup_group)


# Provide legacy command mappings with deprecation warnings
@cli.command(
    "env-dump",
    hidden=True,  # Hide from help but still available
    help="[DEPRECATED] Use 'core env show' instead",
)
@click.pass_context
def env_dump_legacy(ctx: click.Context) -> None:
    """Legacy env-dump command - redirects to core env show."""
    from augint_billing_lib.cli.core.env import show

    click.echo(
        click.style(
            "⚠️  'env-dump' is deprecated. Use 'ai-billing core env show' instead.",
            fg="yellow",
        ),
        err=True,
    )
    ctx.invoke(show)


@cli.command(
    "promote",
    hidden=True,
    help="[DEPRECATED] Use 'core promote' instead",
)
@click.option("--api-key", "api_key_id", required=True)
@click.pass_context
def promote_legacy(ctx: click.Context, api_key_id: str) -> None:
    """Legacy promote command."""
    from augint_billing_lib.cli.core.promote import promote

    click.echo(
        click.style(
            "⚠️  'promote' is deprecated. Use 'ai-billing core promote' instead.",
            fg="yellow",
        ),
        err=True,
    )
    ctx.invoke(promote, api_key_id=api_key_id)


@cli.command(
    "demote",
    hidden=True,
    help="[DEPRECATED] Use 'core demote' instead",
)
@click.option("--api-key", "api_key_id", required=True)
@click.pass_context
def demote_legacy(ctx: click.Context, api_key_id: str) -> None:
    """Legacy demote command."""
    from augint_billing_lib.cli.core.demote import demote

    click.echo(
        click.style(
            "⚠️  'demote' is deprecated. Use 'ai-billing core demote' instead.",
            fg="yellow",
        ),
        err=True,
    )
    ctx.invoke(demote, api_key_id=api_key_id)


if __name__ == "__main__":
    cli()
