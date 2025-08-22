#!/usr/bin/env python3
"""Command-line interface for the billing system.

This module provides CLI commands for testing and administering the billing
system. It includes commands for processing events, reporting usage, and
managing customer plans.

The CLI is designed for:
    - Local testing and development
    - Emergency production operations
    - Integration testing
    - Debugging and troubleshooting

Commands:
    - env-dump: Display current environment configuration
    - handle-event: Process a Stripe event locally
    - sync-usage: Report usage to Stripe
    - promote: Upgrade an API key to metered plan
    - demote: Downgrade an API key to free plan

Example:
    Basic CLI usage::

        # Show environment configuration
        $ ai-billing env-dump
        {
          "STACK_NAME": "billing-prod",
          "AWS_REGION": "us-east-1",
          "STRIPE_SECRET_KEY": "sk_test_..."
        }

        # Process a Stripe event
        $ ai-billing handle-event --file events/payment.json

        # Report usage for the last hour
        $ ai-billing sync-usage

        # Promote a customer
        $ ai-billing promote --api-key key_abc123

Environment:
    The CLI automatically loads .env files from the current directory
    or parent directory if present. All AWS and Stripe configuration
    is read from environment variables.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import click

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover

    def load_dotenv(*_a: Any, **_k: Any) -> bool:  # type: ignore[misc]
        return False


from .adapters.ddb_audit import DdbAuditRepo
from .bootstrap import build_service, process_event_and_apply_plan_moves
from .models import UsageReport


def _apply_env_overrides(**overrides: str | None) -> None:
    """Apply command-line overrides to environment variables.

    Args:
        **overrides: Key-value pairs of environment variables to override.
            Only non-None values are applied.
    """
    for key, value in overrides.items():
        if value is not None:
            # Convert parameter names to env var names (e.g., stack_name -> STACK_NAME)
            env_key = key.upper()
            os.environ[env_key] = value


def _load_env_if_present() -> None:
    """Load environment variables from .env file if present.

    Searches for .env file in current directory or parent directory
    and loads environment variables from it. Does not override
    existing environment variables.
    """
    for p in [Path.cwd() / ".env", Path.cwd().parent / ".env"]:
        if p.exists():
            load_dotenv(p, override=False)
            break


def _pick(cli_value: str | None, env_key: str, default: str | None = None) -> str | None:
    """Pick value from CLI argument, environment, or default.

    Args:
        cli_value: Value provided via CLI argument
        env_key: Environment variable key to check
        default: Default value if neither CLI nor env is set

    Returns:
        First non-empty value from: CLI, environment, default
    """
    if cli_value not in (None, ""):
        return cli_value
    val = os.environ.get(env_key)
    return val if val not in (None, "") else default


def _run(cmd: list[str], cwd: Path | None = None) -> int:
    """Run a shell command and display it.

    Args:
        cmd: Command and arguments to run
        cwd: Working directory for command

    Returns:
        Command exit code
    """
    click.echo(click.style("+ " + " ".join(cmd), fg="cyan"))
    return subprocess.run(cmd, check=False, cwd=str(cwd) if cwd else None).returncode  # noqa: S603


@click.group(help="AugInt Billing CLI (single tool). Local E2E + deploy/delete/tests.")
def cli() -> None:
    """Main CLI entry point.

    Loads environment variables and provides command grouping.
    """
    _load_env_if_present()


@cli.command("env-dump")
@click.option("--stack-name", help="Override STACK_NAME environment variable")
@click.option("--aws-region", help="Override AWS_REGION environment variable")
@click.option("--stripe-secret-key", help="Override STRIPE_SECRET_KEY environment variable")
@click.option("--stripe-secret-arn", help="Override STRIPE_SECRET_ARN environment variable")
@click.option("--table-name", help="Override TABLE_NAME environment variable")
@click.option("--free-usage-plan-id", help="Override FREE_USAGE_PLAN_ID environment variable")
@click.option("--metered-usage-plan-id", help="Override METERED_USAGE_PLAN_ID environment variable")
@click.option("--api-usage-product-id", help="Override API_USAGE_PRODUCT_ID environment variable")
def env_dump(
    stack_name: str | None,
    aws_region: str | None,
    stripe_secret_key: str | None,
    stripe_secret_arn: str | None,
    table_name: str | None,
    free_usage_plan_id: str | None,
    metered_usage_plan_id: str | None,
    api_usage_product_id: str | None,
) -> None:
    """Display current environment configuration.

    Shows all billing-related environment variables in JSON format.
    Useful for debugging configuration issues.

    Example:
        $ ai-billing env-dump
        {
          "STACK_NAME": "billing-prod",
          "AWS_REGION": "us-east-1",
          "STRIPE_SECRET_KEY": "sk_test_...",
          "TABLE_NAME": "customer-links",
          "FREE_USAGE_PLAN_ID": "plan_free",
          "METERED_USAGE_PLAN_ID": "plan_metered"
        }

        $ ai-billing env-dump --stack-name billing-staging --aws-region us-west-2
    """
    # Apply any command-line overrides
    _apply_env_overrides(
        stack_name=stack_name,
        aws_region=aws_region,
        stripe_secret_key=stripe_secret_key,
        stripe_secret_arn=stripe_secret_arn,
        table_name=table_name,
        free_usage_plan_id=free_usage_plan_id,
        metered_usage_plan_id=metered_usage_plan_id,
        api_usage_product_id=api_usage_product_id,
    )

    keys = [
        "STACK_NAME",
        "AWS_REGION",
        "STRIPE_SECRET_KEY",
        "STRIPE_SECRET_ARN",
        "TABLE_NAME",
        "FREE_USAGE_PLAN_ID",
        "METERED_USAGE_PLAN_ID",
        "API_USAGE_PRODUCT_ID",
    ]
    click.echo(json.dumps({k: os.environ.get(k, "") for k in keys}, indent=2))


@cli.command("handle-event")
@click.option(
    "--file",
    "file_path",
    type=click.Path(exists=True, dir_okay=False),
    help="JSON file containing Stripe event",
)
@click.option("--stack-name", help="Override STACK_NAME environment variable")
@click.option("--aws-region", help="Override AWS_REGION environment variable")
@click.option("--stripe-secret-key", help="Override STRIPE_SECRET_KEY environment variable")
@click.option("--stripe-secret-arn", help="Override STRIPE_SECRET_ARN environment variable")
@click.option("--table-name", help="Override TABLE_NAME environment variable")
@click.option("--free-usage-plan-id", help="Override FREE_USAGE_PLAN_ID environment variable")
@click.option("--metered-usage-plan-id", help="Override METERED_USAGE_PLAN_ID environment variable")
def handle_event(
    file_path: str | None,
    stack_name: str | None,
    aws_region: str | None,
    stripe_secret_key: str | None,
    stripe_secret_arn: str | None,
    table_name: str | None,
    free_usage_plan_id: str | None,
    metered_usage_plan_id: str | None,
) -> None:
    """Process a Stripe event and apply plan changes.

    Reads a Stripe event from file or stdin, processes it to determine
    the target plan, and applies the changes to affected API keys.

    Args:
        file_path: Path to JSON file containing event (or stdin if not provided)

    Example:
        From file::

            $ ai-billing handle-event --file events/payment_method.attached.json
            {
              "target_plan": "metered",
              "moved": 2,
              "stripe_customer_id": "cus_123"
            }

        From stdin::

            $ cat event.json | ai-billing handle-event

        With environment overrides::

            $ ai-billing handle-event --file event.json --stack-name staging --stripe-secret-key sk_test_xyz
    """
    # Apply any command-line overrides
    _apply_env_overrides(
        stack_name=stack_name,
        aws_region=aws_region,
        stripe_secret_key=stripe_secret_key,
        stripe_secret_arn=stripe_secret_arn,
        table_name=table_name,
        free_usage_plan_id=free_usage_plan_id,
        metered_usage_plan_id=metered_usage_plan_id,
    )

    payload = (
        json.loads(Path(file_path).read_text())
        if file_path
        else json.loads(click.get_text_stream("stdin").read())
    )
    click.echo(json.dumps(process_event_and_apply_plan_moves(payload), indent=2))


@cli.command("sync-usage")
@click.option("--since", help="Start of usage window (ISO format)")
@click.option("--until", help="End of usage window (ISO format)")
@click.option("--stack-name", help="Override STACK_NAME environment variable")
@click.option("--aws-region", help="Override AWS_REGION environment variable")
@click.option("--stripe-secret-key", help="Override STRIPE_SECRET_KEY environment variable")
@click.option("--stripe-secret-arn", help="Override STRIPE_SECRET_ARN environment variable")
@click.option("--table-name", help="Override TABLE_NAME environment variable")
def sync_usage(
    since: str | None,
    until: str | None,
    stack_name: str | None,
    aws_region: str | None,
    stripe_secret_key: str | None,
    stripe_secret_arn: str | None,
    table_name: str | None,
) -> None:
    """Report API usage to Stripe for billing.

    Fetches usage data from API Gateway and reports it to Stripe
    for all metered customers. By default, reports the last hour.

    Args:
        since: Start time in ISO format (defaults to 1 hour ago)
        until: End time in ISO format (defaults to current hour)

    Example:
        Report last hour::

            $ ai-billing sync-usage
            {
              "reported": 5,
              "window": {
                "since": "2024-01-15T09:00:00+00:00",
                "until": "2024-01-15T10:00:00+00:00"
              }
            }

        Report specific window::

            $ ai-billing sync-usage --since 2024-01-15T00:00:00Z --until 2024-01-15T12:00:00Z

        With environment overrides::

            $ ai-billing sync-usage --stack-name staging --aws-region us-west-2
    """
    # Apply any command-line overrides
    _apply_env_overrides(
        stack_name=stack_name,
        aws_region=aws_region,
        stripe_secret_key=stripe_secret_key,
        stripe_secret_arn=stripe_secret_arn,
        table_name=table_name,
    )

    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    u = datetime.fromisoformat(until.replace("Z", "+00:00")) if until else now
    s = datetime.fromisoformat(since.replace("Z", "+00:00")) if since else (u - timedelta(hours=1))
    svc = build_service(include_usage=True)
    click.echo(
        json.dumps(
            {
                "reported": len(svc.reconcile_usage_window(s, u)),
                "window": {"since": s.isoformat(), "until": u.isoformat()},
            },
            indent=2,
        )
    )


@cli.command("promote")
@click.option("--api-key", "api_key_id", required=True, help="API key to promote")
@click.option("--stack-name", help="Override STACK_NAME environment variable")
@click.option("--aws-region", help="Override AWS_REGION environment variable")
@click.option("--stripe-secret-key", help="Override STRIPE_SECRET_KEY environment variable")
@click.option("--stripe-secret-arn", help="Override STRIPE_SECRET_ARN environment variable")
@click.option("--table-name", help="Override TABLE_NAME environment variable")
def promote(
    api_key_id: str,
    stack_name: str | None,
    aws_region: str | None,
    stripe_secret_key: str | None,
    stripe_secret_arn: str | None,
    table_name: str | None,
) -> None:
    """Promote an API key to metered plan.

    Creates a metered subscription for the customer and updates
    their plan status. This bypasses payment method checks.

    Args:
        api_key_id: The API key to promote

    Example:
        $ ai-billing promote --api-key key_abc123
        {
          "target_plan": "metered",
          "stripe_customer_id": "cus_456",
          "subscription_item_id": "si_789"
        }

        $ ai-billing promote --api-key key_abc123 --stack-name staging
    """
    # Apply any command-line overrides
    _apply_env_overrides(
        stack_name=stack_name,
        aws_region=aws_region,
        stripe_secret_key=stripe_secret_key,
        stripe_secret_arn=stripe_secret_arn,
        table_name=table_name,
    )

    svc = build_service(include_usage=False)
    click.echo(json.dumps(svc.promote(api_key_id), indent=2))


@cli.command("demote")
@click.option("--api-key", "api_key_id", required=True, help="API key to demote")
@click.option("--stack-name", help="Override STACK_NAME environment variable")
@click.option("--aws-region", help="Override AWS_REGION environment variable")
@click.option("--stripe-secret-key", help="Override STRIPE_SECRET_KEY environment variable")
@click.option("--stripe-secret-arn", help="Override STRIPE_SECRET_ARN environment variable")
@click.option("--table-name", help="Override TABLE_NAME environment variable")
def demote(
    api_key_id: str,
    stack_name: str | None,
    aws_region: str | None,
    stripe_secret_key: str | None,
    stripe_secret_arn: str | None,
    table_name: str | None,
) -> None:
    """Demote an API key to free plan.

    Cancels any active subscriptions for the customer and updates
    their plan status to free tier.

    Args:
        api_key_id: The API key to demote

    Example:
        $ ai-billing demote --api-key key_abc123
        {
          "target_plan": "free",
          "stripe_customer_id": "cus_456",
          "subscription_item_id": null
        }

        $ ai-billing demote --api-key key_abc123 --stack-name staging
    """
    # Apply any command-line overrides
    _apply_env_overrides(
        stack_name=stack_name,
        aws_region=aws_region,
        stripe_secret_key=stripe_secret_key,
        stripe_secret_arn=stripe_secret_arn,
        table_name=table_name,
    )

    svc = build_service(include_usage=False)
    click.echo(json.dumps(svc.demote(api_key_id), indent=2))


@cli.command("find-billing-gaps")
@click.option("--api-key", "api_key_id", required=True, help="API key to analyze")
@click.option("--interval-hours", default=1, help="Expected reporting interval in hours")
@click.option("--stack-name", help="Override STACK_NAME environment variable")
@click.option("--aws-region", help="Override AWS_REGION environment variable")
@click.option("--table-name", help="Override audit table name")
def find_billing_gaps(
    api_key_id: str,
    interval_hours: int,
    stack_name: str | None,
    aws_region: str | None,
    table_name: str | None,
) -> None:
    """Find gaps in usage reporting for an API key.

    Analyzes the audit trail to identify missing reporting windows
    where usage wasn't reported to Stripe.

    Args:
        api_key_id: The API key to analyze
        interval_hours: Expected reporting interval (default: 1 hour)

    Example:
        $ ai-billing find-billing-gaps --api-key key_abc123
        [
          {
            "gap_start": "2024-01-15T10:00:00",
            "gap_end": "2024-01-15T12:00:00"
          }
        ]
    """
    # Apply any command-line overrides
    _apply_env_overrides(
        stack_name=stack_name,
        aws_region=aws_region,
    )

    audit_repo = DdbAuditRepo(table_name=table_name)
    gaps = audit_repo.find_gaps(api_key_id, timedelta(hours=interval_hours))

    result = [{"gap_start": gap[0].isoformat(), "gap_end": gap[1].isoformat()} for gap in gaps]

    if result:
        click.echo(f"Found {len(result)} gap(s) in usage reporting:")
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo("No gaps found in usage reporting")


@cli.command("reconcile-customer-usage")
@click.option("--customer-id", required=True, help="Stripe customer ID")
@click.option("--since", required=True, help="Start date (ISO format)")
@click.option("--until", help="End date (ISO format, defaults to now)")
@click.option("--stack-name", help="Override STACK_NAME environment variable")
@click.option("--aws-region", help="Override AWS_REGION environment variable")
@click.option("--table-name", help="Override audit table name")
def reconcile_customer_usage(
    customer_id: str,
    since: str,
    until: str | None,
    stack_name: str | None,
    aws_region: str | None,
    table_name: str | None,
) -> None:
    """Reconcile customer usage reports with Stripe.

    Retrieves all usage reports for a customer within a time range
    for reconciliation with Stripe invoices.

    Args:
        customer_id: Stripe customer ID
        since: Start of time range (ISO format)
        until: End of time range (ISO format, defaults to now)

    Example:
        $ ai-billing reconcile-customer-usage --customer-id cus_123 --since 2024-01-01T00:00:00
        {
          "total_reports": 720,
          "total_units": 1500000,
          "first_report": "2024-01-01T00:00:00",
          "last_report": "2024-01-31T00:00:00"
        }
    """
    # Apply any command-line overrides
    _apply_env_overrides(
        stack_name=stack_name,
        aws_region=aws_region,
    )

    audit_repo = DdbAuditRepo(table_name=table_name)

    since_dt = datetime.fromisoformat(since)
    until_dt = datetime.fromisoformat(until) if until else datetime.now(UTC)

    reports = audit_repo.get_reports_for_customer(customer_id, since_dt, until_dt)

    if reports:
        total_units = sum(r.units_reported for r in reports)
        result = {
            "total_reports": len(reports),
            "total_units": total_units,
            "first_report": reports[0].window_end.isoformat(),
            "last_report": reports[-1].window_end.isoformat(),
            "reports": [
                {
                    "window_end": r.window_end.isoformat(),
                    "units": r.units_reported,
                    "api_key": r.api_key_id,
                }
                for r in reports
            ],
        }
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"No usage reports found for customer {customer_id}")


@cli.command("check-duplicate-reports")
@click.option("--api-key", "api_key_id", required=True, help="API key to check")
@click.option("--since", help="Start date (ISO format)")
@click.option("--until", help="End date (ISO format)")
@click.option("--stack-name", help="Override STACK_NAME environment variable")
@click.option("--aws-region", help="Override AWS_REGION environment variable")
@click.option("--table-name", help="Override audit table name")
def check_duplicate_reports(
    api_key_id: str,
    since: str | None,
    until: str | None,
    stack_name: str | None,
    aws_region: str | None,
    table_name: str | None,
) -> None:
    """Check for duplicate usage reports.

    Analyzes the audit trail to find any duplicate reports for the
    same usage window, which would indicate an idempotency issue.

    Args:
        api_key_id: The API key to check
        since: Start of time range (ISO format)
        until: End of time range (ISO format)

    Example:
        $ ai-billing check-duplicate-reports --api-key key_abc123
        No duplicate reports found
    """
    # Apply any command-line overrides
    _apply_env_overrides(
        stack_name=stack_name,
        aws_region=aws_region,
    )

    audit_repo = DdbAuditRepo(table_name=table_name)

    # Default to last 7 days if not specified
    since_dt = datetime.now(UTC) - timedelta(days=7) if not since else datetime.fromisoformat(since)
    until_dt = datetime.now(UTC) if not until else datetime.fromisoformat(until)

    reports = audit_repo.get_reports_for_window(api_key_id, since_dt, until_dt)

    # Group by window to find duplicates
    windows: dict[str, list[UsageReport]] = {}
    for report in reports:
        window_key = f"{report.window_start.isoformat()}-{report.window_end.isoformat()}"
        if window_key not in windows:
            windows[window_key] = []
        windows[window_key].append(report)

    duplicates = {k: v for k, v in windows.items() if len(v) > 1}

    if duplicates:
        click.echo(f"Found duplicates in {len(duplicates)} window(s):")
        for window, reports in duplicates.items():
            click.echo(f"\nWindow: {window}")
            for r in reports:
                click.echo(
                    f"  - Reported at: {r.reported_at.isoformat()}, "
                    f"Units: {r.units_reported}, "
                    f"Idempotency key: {r.stripe_idempotency_key}"
                )
    else:
        click.echo("No duplicate reports found")


if __name__ == "__main__":
    cli()
