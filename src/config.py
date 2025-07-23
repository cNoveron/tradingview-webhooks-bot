import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BitsoConfig:
    """Configuration class for Bitso API credentials and settings"""

    def __init__(self):
        self.api_key = os.getenv('BITSO_API_KEY')
        self.api_secret = os.getenv('BITSO_API_SECRET')
        self.environment = os.getenv('BITSO_ENVIRONMENT', 'staging')

        # Set base URL based on environment
        if self.environment == 'production':
            self.base_url = os.getenv('BITSO_PROD_BASE_URL', 'https://api.bitso.com')
        else:
            self.base_url = os.getenv('BITSO_STAGE_BASE_URL', 'https://stage.bitso.com/api')

        # Validate required credentials
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "Bitso API credentials are required. Please set BITSO_API_KEY and BITSO_API_SECRET "
                "environment variables or add them to your .env file"
            )

    def __str__(self):
        return f"BitsoConfig(environment='{self.environment}', base_url='{self.base_url}')"

    def __repr__(self):
        return self.__str__()


class RecallConfig:
    """Configuration class for Recall API credentials and settings"""

    def __init__(self):
        self.api_key = os.getenv('RECALL_API_KEY')
        self.environment = os.getenv('RECALL_ENVIRONMENT', 'sandbox')

        # Set base URL based on environment
        if False and self.environment == 'production':
            self.base_url = os.getenv('RECALL_PROD_BASE_URL', 'https://api.competitions.recall.network')
        else:
            self.base_url = os.getenv('RECALL_SANDBOX_BASE_URL', 'https://api.sandbox.competitions.recall.network')

        # Validate required credentials
        if not self.api_key:
            raise ValueError(
                "Recall API key is required. Please set RECALL_API_KEY "
                "environment variable or add it to your .env file"
            )

    def __str__(self):
        return f"RecallConfig(environment='{self.environment}', base_url='{self.base_url}')"

    def __repr__(self):
        return self.__str__()


# Create singleton instances
bitso_config = BitsoConfig()
recall_config = RecallConfig()