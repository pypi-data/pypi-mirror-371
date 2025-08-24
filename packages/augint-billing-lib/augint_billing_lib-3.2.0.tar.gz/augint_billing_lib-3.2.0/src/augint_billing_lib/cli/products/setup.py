"""Setup Stripe products and prices for an environment."""

import os
import sys
from typing import Any

import click
import stripe
from stripe.error import StripeError

from augint_billing_lib.config import config


def get_stripe_key(environment: str) -> str:
    """Get the appropriate Stripe key for the environment."""
    if environment == "production":
        # Check for production keys
        key = os.getenv("STRIPE_LIVE_SECRET_KEY") or os.getenv("PROD_STRIPE_SECRET_KEY")
        if not key:
            click.echo(
                click.style(
                    "❌ No production Stripe key found (STRIPE_LIVE_SECRET_KEY or PROD_STRIPE_SECRET_KEY)",
                    fg="red",
                )
            )
            sys.exit(1)
    else:  # staging
        # Check for staging/test keys
        key = (
            os.getenv("STRIPE_TEST_SECRET_KEY")
            or os.getenv("STAGING_STRIPE_SECRET_KEY")
            or config.stripe_secret_key
        )
        if not key:
            click.echo(
                click.style(
                    "❌ No staging Stripe key found (STRIPE_TEST_SECRET_KEY, STAGING_STRIPE_SECRET_KEY, or STRIPE_SECRET_KEY)",
                    fg="red",
                )
            )
            sys.exit(1)

    return key


def find_existing_product(name: str, environment: str) -> Any | None:
    """Find an existing product by name and environment."""
    try:
        products = stripe.Product.list(limit=100)
        for product in products.data:
            if (
                product.name == name
                and product.metadata.get("environment") == environment
                and product.metadata.get("created_by") == "ai-billing-cli"
            ):
                return product
    except StripeError:
        pass
    return None


def create_subscription_price(
    product_id: str,
    amount: int,
    currency: str,
    interval: str = "month",
) -> Any:
    """Create a subscription price."""
    return stripe.Price.create(
        product=product_id,
        currency=currency,
        unit_amount=amount,
        recurring={"interval": interval},
        metadata={"created_by": "ai-billing-cli", "type": "subscription_base"},
    )


def create_metered_price_with_tiers(
    product_id: str,
    currency: str,
    tiers: list[dict[str, Any]],
) -> Any:
    """Create a metered price with graduated tiers."""
    # Convert "inf" string to None for Stripe API
    formatted_tiers = []
    for tier in tiers:
        formatted_tier = {"unit_amount": tier["unit_amount"]}
        if tier["up_to"] != "inf":
            formatted_tier["up_to"] = tier["up_to"]
        formatted_tiers.append(formatted_tier)

    return stripe.Price.create(
        product=product_id,
        currency=currency,
        recurring={
            "interval": "month",
            "usage_type": "metered",
        },
        billing_scheme="tiered",
        tiers_mode="graduated",
        tiers=formatted_tiers,
        metadata={"created_by": "ai-billing-cli", "type": "metered_usage"},
    )


def calculate_example_bills(
    base_price: int,
    included_requests: int,
    tiers: list[dict[str, Any]],
    example_requests: list[int],
) -> dict[int, float]:
    """Calculate example monthly bills for different usage levels."""
    bills = {}

    for requests in example_requests:
        # Start with base subscription
        total_cents = base_price

        # Calculate billable requests (after included)
        billable = max(0, requests - included_requests)

        # Calculate tiered pricing
        remaining = billable
        for tier in tiers:
            if remaining <= 0:
                break

            # Determine how many units in this tier
            if tier.get("up_to") == "inf":
                units_in_tier = remaining
            else:
                tier_limit = tier["up_to"]
                # For first tier, it's just the limit
                # For subsequent tiers, need to account for previous tiers
                prev_tier_limit = 0
                for prev_tier in tiers:
                    if prev_tier == tier:
                        break
                    if prev_tier.get("up_to") != "inf":
                        prev_tier_limit = prev_tier["up_to"]

                tier_size = tier_limit - prev_tier_limit
                units_in_tier = min(remaining, tier_size)

            # Add cost for this tier
            if tier.get("unit_amount"):
                total_cents += units_in_tier * tier["unit_amount"]
            elif tier.get("flat_amount"):
                total_cents += tier["flat_amount"]

            remaining -= units_in_tier

        bills[requests] = total_cents / 100.0

    return bills


@click.command("setup")
@click.argument(
    "environment",
    type=click.Choice(["staging", "production"]),
)
@click.option(
    "--model",
    type=click.Choice(["subscription-plus-metered", "metered-only", "subscription-only"]),
    default="subscription-plus-metered",
    help="Pricing model to use",
)
@click.option(
    "--base-price",
    type=int,
    default=2999,
    help="Base subscription price in cents (default: 2999 for $29.99)",
)
@click.option(
    "--currency",
    default="usd",
    help="Currency code (default: usd)",
)
@click.option(
    "--included-requests",
    type=int,
    default=1000,
    help="Requests included in base subscription (default: 1000)",
)
@click.option(
    "--tier-1-limit",
    type=int,
    default=10000,
    help="Upper limit for tier 1 (default: 10000)",
)
@click.option(
    "--tier-1-price",
    type=int,
    default=10,
    help="Price per request in tier 1 in cents (default: 10 for $0.10)",
)
@click.option(
    "--tier-2-limit",
    type=int,
    default=100000,
    help="Upper limit for tier 2 (default: 100000)",
)
@click.option(
    "--tier-2-price",
    type=int,
    default=8,
    help="Price per request in tier 2 in cents (default: 8 for $0.08)",
)
@click.option(
    "--tier-3-price",
    type=int,
    default=5,
    help="Price per request in tier 3+ in cents (default: 5 for $0.05)",
)
@click.option(
    "--product-name",
    help="Custom product name (default: AI API Subscription (Environment))",
)
@click.option(
    "--update-env/--no-update-env",
    default=True,
    help="Automatically update .env file (default: true)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be created without making changes",
)
def setup_products(
    environment: str,
    model: str,
    base_price: int,
    currency: str,
    included_requests: int,
    tier_1_limit: int,
    tier_1_price: int,
    tier_2_limit: int,
    tier_2_price: int,
    tier_3_price: int,
    product_name: str | None,
    update_env: bool,
    dry_run: bool,
) -> None:
    """
    Create or update Stripe products for an environment.

    This command sets up the necessary Stripe products and prices for your
    billing infrastructure. It supports multiple pricing models and handles
    existing products gracefully.

    Examples:
        # Setup staging with default subscription + metered model
        ai-billing products setup staging

        # Setup production with custom pricing
        ai-billing products setup production --base-price 3999 --tier-1-price 15

        # Dry run to see what would be created
        ai-billing products setup staging --dry-run

        # Metered-only model (no base subscription)
        ai-billing products setup staging --model metered-only
    """
    # Get Stripe key
    stripe_key = get_stripe_key(environment)
    stripe.api_key = stripe_key

    # Determine mode
    mode = "TEST" if stripe_key.startswith("sk_test") else "LIVE"
    click.echo(f"\n🔑 Using Stripe {mode} mode for {environment} environment")

    if dry_run:
        click.echo(click.style("🔍 DRY RUN - No changes will be made\n", fg="yellow", bold=True))

    # Set product name
    if not product_name:
        product_name = f"AI API Subscription ({environment.title()})"

    try:
        # Check for existing product
        existing_product = find_existing_product(product_name, environment)

        if existing_product:
            click.echo(f"✅ Found existing product: {existing_product.id}")
            product = existing_product
        elif dry_run:
            click.echo(f"Would create product: {product_name}")
            product = type("obj", (object,), {"id": f"prod_{environment}_mock"})()
        else:
            product = stripe.Product.create(
                name=product_name,
                description=f"API usage billing for {environment} environment",
                metadata={
                    "created_by": "ai-billing-cli",
                    "environment": environment,
                    "model": model,
                },
            )
            click.echo(f"✅ Created product: {product.id}")

        # Create prices based on model
        subscription_price = None
        metered_price = None

        if model in ["subscription-plus-metered", "subscription-only"]:
            # Create or find subscription price
            if not dry_run and hasattr(product, "id"):
                existing_prices = stripe.Price.list(product=product.id, limit=100)
                for price in existing_prices.data:
                    if (
                        price.type == "recurring"
                        and price.recurring.get("usage_type") != "metered"
                        and price.unit_amount == base_price
                        and price.currency == currency
                    ):
                        subscription_price = price
                        click.echo(f"✅ Found existing subscription price: {price.id}")
                        break

            if not subscription_price:
                if dry_run:
                    click.echo(
                        f"Would create subscription price: ${base_price / 100:.2f}/{currency}/month"
                    )
                    subscription_price = type(
                        "obj", (object,), {"id": f"price_sub_{environment}_mock"}
                    )()
                else:
                    subscription_price = create_subscription_price(product.id, base_price, currency)
                    click.echo(f"✅ Created subscription price: {subscription_price.id}")

        if model in ["subscription-plus-metered", "metered-only"]:
            # Build tiers configuration
            tiers: list[dict[str, Any]] = []

            # First tier (after included requests for subscription model)
            if model == "subscription-plus-metered":
                # Tier 1: From included+1 to tier_1_limit
                tiers.append(
                    {
                        "up_to": tier_1_limit - included_requests,
                        "unit_amount": tier_1_price,
                    }
                )
            else:
                # Tier 1: From 0 to tier_1_limit
                tiers.append(
                    {
                        "up_to": tier_1_limit,
                        "unit_amount": tier_1_price,
                    }
                )

            # Tier 2: From tier_1_limit+1 to tier_2_limit
            tier_2_start = tier_1_limit - (
                included_requests if model == "subscription-plus-metered" else 0
            )
            tier_2_size = tier_2_limit - tier_1_limit
            tiers.append(
                {
                    "up_to": tier_2_start + tier_2_size,
                    "unit_amount": tier_2_price,
                }
            )

            # Tier 3: tier_2_limit+ (infinite)
            tiers.append(
                {
                    "up_to": "inf",
                    "unit_amount": tier_3_price,
                }
            )

            # Create or find metered price
            if not dry_run and hasattr(product, "id"):
                existing_prices = stripe.Price.list(product=product.id, limit=100)
                for price in existing_prices.data:
                    if (
                        price.type == "recurring"
                        and price.recurring.get("usage_type") == "metered"
                        and price.billing_scheme == "tiered"
                    ):
                        # Check if tiers match
                        if len(price.tiers) == len(tiers):
                            metered_price = price
                            click.echo(f"✅ Found existing metered price: {price.id}")
                            break

            if not metered_price:
                if dry_run:
                    click.echo("Would create metered price with tiered pricing")
                    metered_price = type(
                        "obj", (object,), {"id": f"price_metered_{environment}_mock"}
                    )()
                else:
                    metered_price = create_metered_price_with_tiers(product.id, currency, tiers)
                    click.echo(f"✅ Created metered price: {metered_price.id}")

        # Update .env file if requested
        env_vars_to_add = {}

        # Determine environment variable prefix
        prefix = "PROD_" if environment == "production" else "STAGING_"

        # Add product ID
        env_vars_to_add[f"{prefix}API_USAGE_PRODUCT_ID"] = (
            product.id if hasattr(product, "id") else f"prod_{environment}_mock"
        )

        # Add price IDs based on model
        if subscription_price:
            env_vars_to_add[f"{prefix}BASE_SUBSCRIPTION_PRICE_ID"] = (
                subscription_price.id
                if hasattr(subscription_price, "id")
                else f"price_sub_{environment}_mock"
            )

        if metered_price:
            env_vars_to_add[f"{prefix}METERED_USAGE_PRICE_ID"] = (
                metered_price.id
                if hasattr(metered_price, "id")
                else f"price_metered_{environment}_mock"
            )

        if update_env and not dry_run:
            env_file = ".env"
            env_vars = {}

            # Read existing .env
            if os.path.exists(env_file):
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key.strip()] = value.strip().strip("\"'")

            # Update with new values
            env_vars.update(env_vars_to_add)

            # Write updated .env
            with open(env_file, "w") as f:
                for key, value in sorted(env_vars.items()):
                    f.write(f'{key}="{value}"\n')

            click.echo(f"✅ Updated {env_file} with product IDs")

        # Display summary
        click.echo("\n" + "=" * 60)
        click.echo(
            click.style(
                f"✅ Product setup complete for {environment} environment", fg="green", bold=True
            )
        )
        click.echo("=" * 60)

        if not update_env or dry_run:
            click.echo("\nAdd these to your .env file:")
            for key, value in env_vars_to_add.items():
                click.echo(f'{key}="{value}"')

        click.echo(f"\nPricing Structure ({model}):")

        if model == "subscription-plus-metered":
            click.echo(f"- Base: ${base_price / 100:.2f}/month")
            click.echo(f"- Included: {included_requests:,} requests")
            click.echo(
                f"- {included_requests + 1:,}-{tier_1_limit:,}: ${tier_1_price / 100:.2f}/request"
            )
            click.echo(
                f"- {tier_1_limit + 1:,}-{tier_2_limit:,}: ${tier_2_price / 100:.2f}/request"
            )
            click.echo(f"- {tier_2_limit + 1:,}+: ${tier_3_price / 100:.2f}/request")

            # Calculate example bills
            example_requests = [500, 5000, 50000, 150000]
            bills = calculate_example_bills(
                base_price,
                included_requests,
                tiers,
                example_requests,
            )

            click.echo("\nExample monthly bills:")
            for requests, bill in bills.items():
                click.echo(f"- {requests:,} requests: ${bill:,.2f}")

        elif model == "metered-only":
            click.echo(f"- 0-{tier_1_limit:,}: ${tier_1_price / 100:.2f}/request")
            click.echo(
                f"- {tier_1_limit + 1:,}-{tier_2_limit:,}: ${tier_2_price / 100:.2f}/request"
            )
            click.echo(f"- {tier_2_limit + 1:,}+: ${tier_3_price / 100:.2f}/request")

            # Calculate example bills
            example_requests = [1000, 10000, 50000, 150000]
            bills = {}
            for requests in example_requests:
                total = 0
                remaining = requests

                # Tier 1
                tier_1_units = min(remaining, tier_1_limit)
                total += tier_1_units * tier_1_price
                remaining -= tier_1_units

                # Tier 2
                if remaining > 0:
                    tier_2_units = min(remaining, tier_2_limit - tier_1_limit)
                    total += tier_2_units * tier_2_price
                    remaining -= tier_2_units

                # Tier 3
                if remaining > 0:
                    total += remaining * tier_3_price

                bills[requests] = total / 100.0

            click.echo("\nExample monthly bills:")
            for requests, bill in bills.items():
                click.echo(f"- {requests:,} requests: ${bill:,.2f}")

        elif model == "subscription-only":
            click.echo(f"- Fixed price: ${base_price / 100:.2f}/month")
            click.echo("- No usage tracking")

        if not update_env:
            click.echo(
                click.style(
                    "\n⚠️  Run with --update-env to automatically update your .env file",
                    fg="yellow",
                )
            )

    except StripeError as e:
        click.echo(click.style(f"❌ Stripe error: {e}", fg="red"), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        sys.exit(1)


__all__ = ["setup_products"]
