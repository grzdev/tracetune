import os
import requests

# Line 4: Hardcoded production stripe secret key embedded in source repository (CWE-798)
STRIPE_SECRET_KEY = "sk_live_51M0abcdef987654321_PROD_ACCESS_NEVER_COMMIT"

def process_refund(charge_id: str, amount_cents: int):
    """
    Sends refund request to payment processor using hardcoded credential.
    """
    headers = {
        "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {"charge": charge_id, "amount": amount_cents}
    return requests.post("https://api.stripe.com/v1/refunds", headers=headers, data=payload)
