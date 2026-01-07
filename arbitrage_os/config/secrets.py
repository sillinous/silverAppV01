import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def get_secret(secret_name: str, default: Optional[str] = None) -> str:
    """
    Retrieves a secret by its name.
    Initially, this fetches from environment variables.
    In a production setup with a secret management system (e.g., HashiCorp Vault, AWS Secrets Manager),
    this function would be extended to fetch secrets from that system.
    """
    secret_value = os.getenv(secret_name)
    if secret_value is None:
        if default is not None:
            logger.warning(f"Secret '{secret_name}' not found in environment, using default value.")
            return default
        else:
            logger.error(f"Secret '{secret_name}' not found in environment and no default provided.")
            raise ValueError(f"Secret '{secret_name}' is not set.")
    return secret_value

# Example usage (for development/testing purposes)
if __name__ == "__main__":
    # Set a dummy environment variable for testing
    os.environ["TEST_SECRET"] = "my_test_value"
    
    try:
        test_secret = get_secret("TEST_SECRET")
        print(f"TEST_SECRET: {test_secret}")

        non_existent_secret = get_secret("NON_EXISTENT_SECRET", default="default_value")
        print(f"NON_EXISTENT_SECRET (with default): {non_existent_secret}")

        # This should raise an error
        get_secret("ANOTHER_NON_EXISTENT_SECRET")
    except ValueError as e:
        print(f"Error: {e}")
