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


class MT5Config:
    """Configuration class for MetaTrader 5 demo account credentials and settings"""

    def __init__(self):
        # Get credentials from environment variables
        login_str = os.getenv('MT5_LOGIN')
        self.password = os.getenv('MT5_PASSWORD')
        self.server = os.getenv('MT5_SERVER', 'MetaQuotes-Demo')  # Demo server
        self.environment = os.getenv('MT5_ENVIRONMENT', 'demo')

        # Validate required credentials
        if not login_str:
            raise ValueError(
                "MT5 login is required. Please set MT5_LOGIN "
                "environment variable or add it to your .env file"
            )

        if not self.password:
            raise ValueError(
                "MT5 password is required. Please set MT5_PASSWORD "
                "environment variable or add it to your .env file"
            )

        # Convert login to integer
        try:
            self.login = int(login_str)
        except ValueError:
            raise ValueError(
                f"MT5_LOGIN must be a valid integer, got: {login_str}"
            )

    def __str__(self):
        return f"MT5Config(login='{self.login}', server='{self.server}', environment='{self.environment}')"

    def __repr__(self):
        return self.__str__()


# Create singleton instances
bitso_config = BitsoConfig()
recall_config = RecallConfig()
mt5_config = MT5Config()