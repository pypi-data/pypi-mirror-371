"""Create Stripe test customers (no API keys)."""

import json

import click

from augint_billing_lib.config import get_service


@click.command("customer")
@click.option(
    "--email",
    required=True,
    help="Customer email address",
)
@click.option(
    "--payment-method",
    help="Test payment method token (e.g., pm_card_visa)",
)
@click.option(
    "--metadata",
    multiple=True,
    help="Metadata as key=value pairs",
)
@click.option(
    "--acknowledge-no-api-key",
    is_flag=True,
    help="Acknowledge that this customer will have no API key",
)
@click.option(
    "--json-output",
    "use_json",
    is_flag=True,
    help="Output as JSON",
)
def customer(
    email: str,
    payment_method: str | None,
    metadata: tuple[str, ...],
    acknowledge_no_api_key: bool,
    use_json: bool,
) -> None:
    """
    Create a Stripe test customer (NO API KEY).

    This command creates a customer in Stripe for testing webhook delivery
    and event processing. The customer will NOT have an API key.

    IMPORTANT LIMITATIONS:
    • This customer will NOT have an API key in API Gateway
    • This customer will NOT have a Cognito user account
    • This customer CANNOT make API calls
    • This customer CANNOT be promoted to a paid plan

    This customer CAN be used to:
    • Test Stripe webhook delivery
    • Test EventBridge configuration
    • Test Lambda error handling
    • Test payment method attachment

    To test the complete billing flow, use 'test integration link'
    with an existing API key from your application.
    """
    if not acknowledge_no_api_key:
        # Show prominent warning
        click.echo(
            click.style(
                "⚠️  WARNING: This creates a Stripe customer only!",
                fg="yellow",
                bold=True,
            )
        )
        click.echo("\nThis customer will NOT have:")
        click.echo("  • An API key in API Gateway")
        click.echo("  • A Cognito user account")
        click.echo("  • The ability to make API calls")
        click.echo("\nThis customer CAN be used to:")
        click.echo("  • Test Stripe webhook delivery")
        click.echo("  • Test EventBridge configuration")
        click.echo("  • Test Lambda error handling")
        click.echo("")

        if not click.confirm("Do you want to continue?"):
            raise click.Abort()

    service = get_service()

    try:
        # Parse metadata
        metadata_dict = {}
        for item in metadata:
            if "=" in item:
                key, value = item.split("=", 1)
                metadata_dict[key] = value

        # Add test indicator
        metadata_dict["test"] = "true"
        metadata_dict["created_by"] = "cli"

        # Create customer in Stripe
        import stripe

        stripe.api_key = service.config.stripe_secret_key

        customer_data = stripe.Customer.create(
            email=email,
            description="Test customer created by CLI",
            metadata=metadata_dict,
        )

        # Attach payment method if provided
        if payment_method:
            pm = stripe.PaymentMethod.retrieve(payment_method)
            pm.attach(customer=customer_data.id)
            # Set as default
            stripe.Customer.modify(
                customer_data.id,
                invoice_settings={"default_payment_method": payment_method},
            )

        # Output results
        result = {
            "customer_id": customer_data.id,
            "email": customer_data.email,
            "warning": "This customer has no API key. Use 'test integration link' to connect to existing key.",
            "useful_for": [
                "webhook_testing",
                "event_generation",
                "stripe_api_testing",
            ],
            "not_useful_for": [
                "usage_tracking",
                "promotion_testing",
                "billing_cycles",
            ],
            "next_steps": [
                f"ai-billing test stripe event --customer {customer_data.id}",
                f"ai-billing test integration link --api-key REAL_KEY --customer {customer_data.id}",
            ],
        }

        if use_json:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(
                click.style(
                    f"✅ Created Stripe test customer: {customer_data.id}",
                    fg="green",
                )
            )
            click.echo(f"Email: {customer_data.email}")
            click.echo("")
            click.echo(click.style("⚠️  Remember: This customer has NO API key", fg="yellow"))
            click.echo("\nNext steps:")
            for step in result["next_steps"]:
                click.echo(f"  • {step}")

    except Exception as e:
        click.echo(
            click.style(f"❌ Failed to create customer: {e}", fg="red"),
            err=True,
        )
        raise


__all__ = ["customer"]
