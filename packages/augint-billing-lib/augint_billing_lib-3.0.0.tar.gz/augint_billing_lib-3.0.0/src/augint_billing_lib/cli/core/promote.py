"""Promote API key to paid tier."""

import click

from augint_billing_lib.config import get_service


@click.command("promote")
@click.option(
    "--api-key",
    "api_key_id",
    required=False,
    help="API key to promote",
)
@click.option(
    "--batch",
    is_flag=True,
    help="Batch promotion mode",
)
@click.option(
    "--file",
    "batch_file",
    type=click.Path(exists=True),
    help="File containing API keys (one per line)",
)
@click.option(
    "--validate",
    is_flag=True,
    default=True,
    help="Validate before promotion",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
def promote(
    api_key_id: str | None,
    batch: bool,
    batch_file: str | None,
    validate: bool,
    dry_run: bool,
) -> None:
    """
    Promote API key(s) to the paid/metered tier.

    This command moves API keys from the free usage plan to the metered
    usage plan, enabling billing for API usage.

    Examples:

        # Promote single key with validation
        ai-billing core promote --api-key KEY --validate

        # Batch promotion from file
        ai-billing core promote --batch --file keys.txt

        # Dry run to preview changes
        ai-billing core promote --api-key KEY --dry-run
    """
    # Determine which keys to promote
    keys_to_promote: list[str] = []

    if batch or batch_file:
        if not batch_file:
            click.echo(
                click.style("❌ --file required for batch mode", fg="red"),
                err=True,
            )
            raise click.Abort()

        with open(batch_file) as f:
            keys_to_promote = [line.strip() for line in f if line.strip()]

        click.echo(f"Batch mode: {len(keys_to_promote)} keys to promote")
    elif api_key_id:
        keys_to_promote = [api_key_id]
    else:
        click.echo(
            click.style("❌ Either --api-key or --batch required", fg="red"),
            err=True,
        )
        raise click.Abort()

    # Get service
    service = get_service()

    # Process each key
    success_count = 0
    failure_count = 0

    for key in keys_to_promote:
        try:
            if validate and not dry_run:
                # Validate key exists and is eligible
                click.echo(f"Validating {key}...")

                # Check if key exists in DynamoDB
                link = service.customer_repo.get_link(key)
                if not link:
                    click.echo(
                        click.style(
                            f"⚠️  No link found for {key} - creating link first",
                            fg="yellow",
                        )
                    )

                # Check current plan
                if link and link.plan == "metered":
                    click.echo(f"INFO: {key} is already on metered plan")
                    continue

            if dry_run:
                click.echo(f"[DRY RUN] Would promote {key} to metered plan")
            else:
                # Perform promotion
                click.echo(f"Promoting {key}...")
                service.plan_admin.assign_api_key_to_plan(
                    api_key_id=key,
                    usage_plan_id=service.config.metered_usage_plan_id,
                )

                # Update database
                if link:
                    link.plan = "metered"
                    link.usage_plan_id = service.config.metered_usage_plan_id
                    service.customer_repo.save_link(link)

                click.echo(click.style(f"✅ Promoted {key} to metered plan", fg="green"))
                success_count += 1

        except Exception as e:
            click.echo(
                click.style(f"❌ Failed to promote {key}: {e}", fg="red"),
                err=True,
            )
            failure_count += 1
            if not batch:
                raise

    # Summary for batch mode
    if batch or len(keys_to_promote) > 1:
        click.echo("\n" + "=" * 50)
        click.echo("Promotion Summary:")
        click.echo(f"  Successful: {success_count}")
        click.echo(f"  Failed:     {failure_count}")
        click.echo(f"  Total:      {len(keys_to_promote)}")

        if failure_count > 0:
            raise click.Abort()


__all__ = ["promote"]
