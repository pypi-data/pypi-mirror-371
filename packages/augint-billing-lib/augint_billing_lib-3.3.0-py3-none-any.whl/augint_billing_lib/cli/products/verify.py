"""Verify Stripe products are configured correctly."""

import os
import sys
from typing import Any

import click
import stripe
from dotenv import load_dotenv
from stripe.error import StripeError

# Load environment variables from .env file
load_dotenv()


def get_stripe_key(environment: str) -> str:
    """Get the appropriate Stripe key for the environment."""
    if environment == "production":
        key = os.getenv("STRIPE_LIVE_SECRET_KEY") or os.getenv("PROD_STRIPE_SECRET_KEY")
        if not key:
            click.echo(
                click.style(
                    "❌ No production Stripe key found",
                    fg="red",
                )
            )
            sys.exit(1)
    else:  # staging
        key = (
            os.getenv("STRIPE_TEST_SECRET_KEY")
            or os.getenv("STAGING_STRIPE_SECRET_KEY")
            or os.getenv("STRIPE_SECRET_KEY")
        )
        if not key:
            click.echo(
                click.style(
                    "❌ No staging Stripe key found",
                    fg="red",
                )
            )
            sys.exit(1)

    return key


def verify_env_var(var_name: str) -> tuple[bool, str | None]:
    """Verify an environment variable is set."""
    value = os.getenv(var_name)
    return (value is not None, value)


def verify_product_exists(product_id: str) -> tuple[bool, Any | None]:
    """Verify a product exists in Stripe."""
    try:
        product = stripe.Product.retrieve(product_id)
        return (True, product)
    except StripeError:
        return (False, None)


def verify_price_exists(price_id: str) -> tuple[bool, Any | None]:
    """Verify a price exists in Stripe."""
    try:
        price = stripe.Price.retrieve(price_id)
        return (True, price)
    except StripeError:
        return (False, None)


def get_price_description(price: Any) -> str:
    """Get a human-readable description of a price."""
    if not price:
        return "N/A"

    if price.type == "recurring":
        if price.recurring.get("usage_type") == "metered":
            if price.billing_scheme == "tiered":
                tier_count = len(price.tiers) if hasattr(price, "tiers") else 0
                return f"Metered with {tier_count} tiers"
            amount = price.unit_amount / 100.0 if price.unit_amount else 0
            return f"Metered at ${amount:.3f}/unit"
        amount = price.unit_amount / 100.0 if price.unit_amount else 0
        interval = price.recurring.get("interval", "month")
        return f"${amount:.2f}/{interval}"
    amount = price.unit_amount / 100.0 if price.unit_amount else 0
    return f"${amount:.2f} one-time"


@click.command("verify")
@click.argument(
    "environment",
    type=click.Choice(["staging", "production"]),
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed information",
)
def verify_products(environment: str, verbose: bool) -> None:
    """
    Verify Stripe products are configured correctly for an environment.

    This command checks that:
    - Products exist in Stripe
    - Prices are configured correctly
    - Environment variables are set
    - Products match expected configuration

    Examples:
        # Verify staging setup
        ai-billing products verify staging

        # Verify with detailed output
        ai-billing products verify production --verbose
    """
    click.echo(f"\n🔍 Verifying Stripe products for {environment} environment\n")

    # Get Stripe key
    stripe_key = get_stripe_key(environment)
    stripe.api_key = stripe_key

    # Set API version to match setup command
    stripe.api_version = "2024-06-20"

    # Determine mode
    mode = "TEST" if stripe_key.startswith("sk_test") else "LIVE"
    click.echo(f"Using Stripe {mode} mode\n")

    # Check environment variables
    prefix = "PROD_" if environment == "production" else "STAGING_"

    env_checks = {
        f"{prefix}API_USAGE_PRODUCT_ID": "Product ID",
        f"{prefix}BASE_SUBSCRIPTION_PRICE_ID": "Base subscription price ID",
        f"{prefix}METERED_USAGE_PRICE_ID": "Metered usage price ID",
    }

    all_env_vars_ok = True
    env_values = {}

    click.echo("Environment Variables:")
    for var_name, _description in env_checks.items():
        exists, value = verify_env_var(var_name)
        env_values[var_name] = value

        if exists:
            display_value = (
                value if verbose else f"{value[:20]}..." if value and len(value) > 20 else value
            )
            click.echo(f"  ✅ {var_name}: {display_value}")
        else:
            click.echo(f"  ⚠️  {var_name}: Not set")
            if "BASE_SUBSCRIPTION" not in var_name:  # Base subscription is optional
                all_env_vars_ok = False

    if not all_env_vars_ok:
        click.echo(
            click.style(
                "\n⚠️  Some required environment variables are missing",
                fg="yellow",
            )
        )

    # Check Stripe resources
    click.echo("\nStripe Resources:")
    all_stripe_ok = True

    # Check product
    product_id = env_values.get(f"{prefix}API_USAGE_PRODUCT_ID")
    if product_id:
        exists, product = verify_product_exists(product_id)
        if exists and product:
            click.echo(f"  ✅ Product: {product.name} [{product.id}]")
            if verbose and product.metadata:
                click.echo(f"     Metadata: {dict(product.metadata)}")
        else:
            click.echo(f"  ❌ Product {product_id} not found in Stripe")
            all_stripe_ok = False
    else:
        click.echo("  ⏭️  Product: Skipping (no ID configured)")

    # Check base subscription price
    subscription_price_id = env_values.get(f"{prefix}BASE_SUBSCRIPTION_PRICE_ID")
    if subscription_price_id:
        exists, price = verify_price_exists(subscription_price_id)
        if exists and price:
            description = get_price_description(price)
            click.echo(f"  ✅ Base subscription price: {description} [{price.id}]")
            if verbose:
                click.echo(f"     Product: {price.product}")
                click.echo(f"     Currency: {price.currency}")
                if price.metadata:
                    click.echo(f"     Metadata: {dict(price.metadata)}")
        else:
            click.echo(f"  ❌ Subscription price {subscription_price_id} not found in Stripe")
            all_stripe_ok = False
    else:
        click.echo("  ⏭️  Base subscription price: Not configured (metered-only model?)")

    # Check metered price
    metered_price_id = env_values.get(f"{prefix}METERED_USAGE_PRICE_ID")
    if metered_price_id:
        exists, price = verify_price_exists(metered_price_id)
        if exists and price:
            description = get_price_description(price)
            click.echo(f"  ✅ Metered usage price: {description} [{price.id}]")
            if verbose:
                click.echo(f"     Product: {price.product}")
                click.echo(f"     Currency: {price.currency}")
                if price.billing_scheme == "tiered" and hasattr(price, "tiers"):
                    click.echo("     Tiers:")
                    for i, tier in enumerate(price.tiers, 1):
                        if tier.get("up_to") == "inf":
                            click.echo(
                                f"       Tier {i}: ${tier.get('unit_amount', 0) / 100:.2f}/unit (unlimited)"
                            )
                        else:
                            click.echo(
                                f"       Tier {i}: ${tier.get('unit_amount', 0) / 100:.2f}/unit (up to {tier.get('up_to')})"
                            )
                if price.metadata:
                    click.echo(f"     Metadata: {dict(price.metadata)}")
        else:
            click.echo(f"  ❌ Metered price {metered_price_id} not found in Stripe")
            all_stripe_ok = False
    else:
        click.echo("  ⏭️  Metered usage price: Not configured (subscription-only model?)")

    # Determine pricing model
    click.echo("\nDetected Configuration:")
    if subscription_price_id and metered_price_id:
        click.echo("  📊 Model: subscription-plus-metered")
    elif metered_price_id and not subscription_price_id:
        click.echo("  📊 Model: metered-only")
    elif subscription_price_id and not metered_price_id:
        click.echo("  📊 Model: subscription-only")
    else:
        click.echo("  ⚠️  Model: Unknown (no prices configured)")

    # Overall status
    click.echo("\n" + "=" * 50)
    if all_env_vars_ok and all_stripe_ok:
        click.echo(
            click.style(
                f"✅ Stripe products configured correctly for {environment}",
                fg="green",
                bold=True,
            )
        )
    elif all_stripe_ok and not all_env_vars_ok:
        click.echo(
            click.style(
                "⚠️  Stripe products exist but environment variables need configuration",
                fg="yellow",
                bold=True,
            )
        )
        click.echo("\nRun the setup command to configure:")
        click.echo(f"  ai-billing products setup {environment}")
    else:
        click.echo(
            click.style(
                f"❌ Stripe products not fully configured for {environment}",
                fg="red",
                bold=True,
            )
        )
        click.echo("\nRun the setup command to fix:")
        click.echo(f"  ai-billing products setup {environment}")


__all__ = ["verify_products"]
