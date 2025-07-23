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

    def execute_trade(self, from_token: str, to_token: str, amount: str, reason: str = "Webhook trade execution",
                     slippage_tolerance: str = "0.5", from_chain: str = "evm", from_specific_chain: str = "mainnet",
                     to_chain: str = "evm", to_specific_chain: str = "mainnet"):
        """
        Execute a token swap trade on Recall

        Args:
            from_token: Source token contract address
            to_token: Destination token contract address
            amount: Amount to swap (in human units)
            reason: Reason for the trade
            slippage_tolerance: Slippage tolerance percentage
            from_chain: Source chain type
            from_specific_chain: Specific source chain
            to_chain: Destination chain type
            to_specific_chain: Specific destination chain
        """
        try:
            logger.info(f"RecallSpot: execute_trade called with from_token={from_token}, to_token={to_token}, amount={amount}")

            # Build trade payload according to Recall API schema
            trade_payload = {
                'fromToken': from_token,
                'toToken': to_token,
                'amount': amount,
                'reason': reason,
                'slippageTolerance': slippage_tolerance,
                'fromChain': from_chain,
                'fromSpecificChain': from_specific_chain,
                'toChain': to_chain,
                'toSpecificChain': to_specific_chain
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
            "side": "buy",  # "buy" or "sell"
            "base_token": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",    # WETH (token being bought/sold)
            "quote_token": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",   # USDC (token used to buy/sell)
            "amount": "100",
            "reason": "Optional reason for trade",
            "slippageTolerance": "0.5",  # Optional, defaults to 0.5%
            "fromChain": "evm",  # Optional, defaults to evm
            "fromSpecificChain": "mainnet",  # Optional, defaults to mainnet
            "toChain": "evm",  # Optional, defaults to evm
            "toSpecificChain": "mainnet"  # Optional, defaults to mainnet
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
            side = data.get('side')
            base_token = data.get('base_token')
            quote_token = data.get('quote_token')
            amount = data.get('amount')
            reason = data.get('reason', 'Webhook trade execution')

            # Optional fields with defaults
            slippage_tolerance = data.get('slippageTolerance', '0.5')
            from_chain = data.get('fromChain', 'evm')
            from_specific_chain = data.get('fromSpecificChain', 'mainnet')
            to_chain = data.get('toChain', 'evm')
            to_specific_chain = data.get('toSpecificChain', 'mainnet')

            logger.info(f"RecallSpot: Extracted side='{side}', base_token='{base_token}', quote_token='{quote_token}', amount='{amount}'")

            if not side or side not in ['buy', 'sell']:
                raise ValueError("Side must be 'buy' or 'sell'")

            if not base_token or not quote_token or not amount:
                raise ValueError("base_token, quote_token, and amount are required")

            # Determine fromToken and toToken based on side
            if side == 'buy':
                # Buying base_token with quote_token
                from_token = quote_token  # Selling quote token (e.g., USDC)
                to_token = base_token     # Buying base token (e.g., WETH)
                logger.info(f"RecallSpot: BUY order - selling {from_token} to buy {to_token}")
            else:  # side == 'sell'
                # Selling base_token for quote_token
                from_token = base_token   # Selling base token (e.g., WETH)
                to_token = quote_token    # Getting quote token (e.g., USDC)
                logger.info(f"RecallSpot: SELL order - selling {from_token} to get {to_token}")

            logger.info("RecallSpot: Attempting to execute trade...")
            result = self.execute_trade(
                from_token=from_token,
                to_token=to_token,
                amount=str(amount),
                reason=reason,
                slippage_tolerance=slippage_tolerance,
                from_chain=from_chain,
                from_specific_chain=from_specific_chain,
                to_chain=to_chain,
                to_specific_chain=to_specific_chain
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