from components.actions.base.action import Action
from utils.bearer_auth import create_bearer_authenticator
from utils.log import get_logger
from config import recall_config
import json

logger = get_logger(__name__)


class RecallSpot(Action):
    def __init__(self):
        logger.info(f"RecallSpot.__init__() called with config: {recall_config}")
        super().__init__()

        self.config = recall_config
        self.authenticator = create_bearer_authenticator(self.config.api_key)
        logger.info("RecallSpot: Successfully initialized with authenticator")

    def execute_trade(self, from_token: str, to_token: str, amount: str, reason: str = "Webhook trade execution"):
        """
        Execute a token swap trade on Recall

        Args:
            from_token: Source token contract address
            to_token: Destination token contract address
            amount: Amount to swap (in human units)
            reason: Reason for the trade
        """
        try:
            logger.info(f"RecallSpot: execute_trade called with from_token={from_token}, to_token={to_token}, amount={amount}, reason={reason}")

            # Build trade payload
            trade_payload = {
                'fromToken': from_token,
                'toToken': to_token,
                'amount': amount,
                'reason': reason
            }

            endpoint = f"{self.config.base_url}/api/trade/execute"
            logger.info(f"RecallSpot: Trade payload: {trade_payload}")
            logger.info(f"RecallSpot: Making API call to {endpoint}")

            response = self.authenticator.authenticated_request(
                url=endpoint,
                method='POST',
                body=trade_payload
            )

            logger.info(f"RecallSpot: API response status: {response.status_code}")
            logger.info(f"RecallSpot: API response headers: {dict(response.headers)}")
            logger.info(f"RecallSpot: API response body: {response.text}")

            response.raise_for_status()
            result = response.json()
            logger.info(f"Trade executed successfully: {result}")
            return result

        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return None

    def get_balance(self):
        """
        Get account balance (if supported by Recall API)
        Note: This is a placeholder - check Recall API documentation for actual balance endpoint
        """
        try:
            # This is a placeholder - adjust based on actual Recall API
            response = self.authenticator.authenticated_request(
                url=f"{self.config.base_url}/api/account/balance",
                method='GET'
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None

    def get_trade_history(self):
        """
        Get trade history (if supported by Recall API)
        Note: This is a placeholder - check Recall API documentation for actual history endpoint
        """
        try:
            # This is a placeholder - adjust based on actual Recall API
            response = self.authenticator.authenticated_request(
                url=f"{self.config.base_url}/api/account/trades",
                method='GET'
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            return None

    def run(self, *args, **kwargs):
        """
        Main run method called by the webhook system
        Expected data format: {
            "action": "swap",
            "from_token": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
            "to_token": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",    # WETH
            "amount": "100",
            "reason": "Optional reason for trade"
        }
        """
        logger.info("==================== RecallSpot.run() START ====================")
        logger.info(f"RecallSpot.run() called with args: {args}, kwargs: {kwargs}")
        super().run(*args, **kwargs)  # this is required
        logger.info("==================== RecallSpot.run() AFTER SUPER ====================")

        try:
            logger.info("RecallSpot: Validating data...")
            data = self.validate_data()
            logger.info(f"RecallSpot: Validated data: {data}")

            # Extract required fields from webhook data
            action = data.get('action')
            from_token = data.get('from_token')
            to_token = data.get('to_token')
            amount = data.get('amount')
            reason = data.get('reason', 'Webhook trade execution')

            logger.info(f"RecallSpot: Extracted action='{action}', from_token='{from_token}', to_token='{to_token}', amount='{amount}', reason='{reason}'")

            if not action or action != 'swap':
                raise ValueError("Action must be 'swap' for Recall trades")

            if not from_token or not to_token or not amount:
                raise ValueError("from_token, to_token, and amount are required for Recall trades")

            logger.info("RecallSpot: Attempting to execute trade...")
            result = self.execute_trade(
                from_token=from_token,
                to_token=to_token,
                amount=str(amount),
                reason=reason
            )

            if result:
                logger.info(f"Recall trade executed successfully: {result}")
            else:
                logger.error("Failed to execute Recall trade")

        except Exception as e:
            logger.error(f"Error in Recall action run: {e}")
            import traceback
            traceback.print_exc()
            raise