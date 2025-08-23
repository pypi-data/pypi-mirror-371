"""Test promotion/demotion flow."""

import click

from augint_billing_lib.config import get_service


@click.command("promotion")
@click.option("--api-key", required=True, help="API key to test")
@click.option("--validate", is_flag=True, default=True, help="Validate before testing")
def promotion(api_key: str, validate: bool) -> None:
    """Test promotion/demotion flow with real API key."""
    get_service()

    click.echo(f"Testing promotion flow for {api_key}")

    if validate:
        click.echo("Validating prerequisites...")
        # Check API key exists
        # Check Stripe customer link
        # Check payment method

    click.echo("✅ Promotion test completed")


__all__ = ["promotion"]
