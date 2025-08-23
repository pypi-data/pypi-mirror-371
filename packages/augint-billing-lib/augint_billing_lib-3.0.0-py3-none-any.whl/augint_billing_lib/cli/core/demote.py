"""Demote API key to free tier."""

import click

from augint_billing_lib.config import get_service


@click.command("demote")
@click.option(
    "--api-key",
    "api_key_id",
    required=True,
    help="API key to demote",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force demotion without confirmation",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def demote(
    api_key_id: str,
    force: bool,
    dry_run: bool,
) -> None:
    """
    Demote API key to the free tier.

    This command moves an API key from the metered usage plan back to
    the free usage plan. Use with caution as this stops billing.

    Examples:

        # Demote with confirmation
        ai-billing core demote --api-key KEY

        # Force demotion without confirmation
        ai-billing core demote --api-key KEY --force

        # Preview changes
        ai-billing core demote --api-key KEY --dry-run
    """
    service = get_service()

    try:
        # Check current status
        link = service.customer_repo.get_link(api_key_id)

        if link and link.plan == "free":
            click.echo(f"INFO: {api_key_id} is already on free plan")
            return

        # Confirmation for non-dry-run
        if not dry_run and not force:
            click.echo(
                click.style(
                    "⚠️  WARNING: Demotion will stop billing for this API key",
                    fg="yellow",
                    bold=True,
                )
            )
            if link and link.stripe_customer_id:
                click.echo(f"  Stripe Customer: {link.stripe_customer_id}")

            if not click.confirm("Do you want to continue?"):
                raise click.Abort()

        if dry_run:
            click.echo(f"[DRY RUN] Would demote {api_key_id} to free plan")
            if link:
                click.echo(f"  Current plan: {link.plan}")
                click.echo(f"  Current usage plan: {link.usage_plan_id}")
        else:
            # Perform demotion
            click.echo(f"Demoting {api_key_id}...")

            service.plan_admin.assign_api_key_to_plan(
                api_key_id=api_key_id,
                usage_plan_id=service.config.free_usage_plan_id,
            )

            # Update database
            if link:
                link.plan = "free"
                link.usage_plan_id = service.config.free_usage_plan_id
                # Clear metered subscription item ID
                link.metered_subscription_item_id = None
                service.customer_repo.save_link(link)

            click.echo(click.style(f"✅ Demoted {api_key_id} to free plan", fg="green"))

    except Exception as e:
        click.echo(
            click.style(f"❌ Failed to demote {api_key_id}: {e}", fg="red"),
            err=True,
        )
        raise


__all__ = ["demote"]
