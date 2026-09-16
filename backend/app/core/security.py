import secrets


def generate_token(length: int = 32) -> str:
    """Generate a secure random hex token."""
    return secrets.token_hex(length)
