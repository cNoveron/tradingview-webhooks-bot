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
        self._token_mappings = {}  # Cache for symbol -> address mappings
        logger.info("RecallSpot: Successfully initialized with authenticator")

    def get_portfolio(self):
        """
        Get portfolio information from Recall API including available tokens
        """
        try:
            response = self.authenticator.authenticated_request(
                url=f"{self.config.base_url}/api/agent/portfolio",
                method='GET'
            )
            response.raise_for_status()
            portfolio = response.json()
            logger.info(f"Portfolio retrieved successfully")
            return portfolio
        except Exception as e:
            logger.error(f"Error getting portfolio: {e}")
            return None

    def build_token_mappings(self):
        """
        Build symbol -> address mappings from portfolio data, organized by chain
        Returns dict like: {'mainnet': {'ETH': '0x...', 'USDC': '0x...'}, 'polygon': {...}}
        """
        try:
            portfolio = self.get_portfolio()
            if not portfolio:
                logger.error("Failed to retrieve portfolio for token mappings")
                return {}

            mappings = {}

            # Extract token information from portfolio
            # Adjust this based on actual Recall API response structure
            if 'tokens' in portfolio:
                for token_info in portfolio['tokens']:
                    chain = token_info.get('chain', 'mainnet')
                    symbol = token_info.get('symbol', '').upper()
                    address = token_info.get('address', '')

                    if chain not in mappings:
                        mappings[chain] = {}

                    if symbol and address:
                        mappings[chain][symbol] = address
                        logger.debug(f"Added mapping: {chain}.{symbol} -> {address}")

            # If tokens are nested differently, try alternative structures
            elif 'balances' in portfolio:
                for balance_info in portfolio['balances']:
                    chain = balance_info.get('chain', 'mainnet')
                    symbol = balance_info.get('symbol', '').upper()
                    address = balance_info.get('tokenAddress', '') or balance_info.get('address', '')

                    if chain not in mappings:
                        mappings[chain] = {}

                    if symbol and address:
                        mappings[chain][symbol] = address
                        logger.debug(f"Added mapping: {chain}.{symbol} -> {address}")

            self._token_mappings = mappings
            logger.info(f"Built token mappings for {len(mappings)} chains with {sum(len(tokens) for tokens in mappings.values())} total tokens")
            return mappings

        except Exception as e:
            logger.error(f"Error building token mappings: {e}")
            return {}

    def get_token_address(self, symbol: str, chain: str = 'mainnet'):
        """
        Get token address for a given symbol and chain
        """
        # Build mappings if not cached
        if not self._token_mappings:
            self.build_token_mappings()

        symbol = symbol.upper()

        if chain in self._token_mappings and symbol in self._token_mappings[chain]:
            address = self._token_mappings[chain][symbol]
            logger.info(f"Found address for {symbol} on {chain}: {address}")
            return address
        else:
            logger.error(f"No address found for symbol '{symbol}' on chain '{chain}'")
            logger.info(f"Available chains: {list(self._token_mappings.keys())}")
            if chain in self._token_mappings:
                logger.info(f"Available symbols on {chain}: {list(self._token_mappings[chain].keys())}")
            return None

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
            "base": "ETH",    # Symbol of token being bought/sold (e.g., "ETH", "BTC")
            "quote": "USDC",  # Symbol of quote token (e.g., "USDC", "USDT")
            "size": "1.5",    # Amount to trade
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
            base_symbol = data.get('base')
            quote_symbol = data.get('quote')
            amount = data.get('size')
            reason = data.get('reason', 'Webhook trade execution')

            # Optional fields with defaults
            slippage_tolerance = data.get('slippageTolerance', '0.5')
            from_chain = data.get('fromChain', 'evm')
            from_specific_chain = data.get('fromSpecificChain', 'mainnet')
            to_chain = data.get('toChain', 'evm')
            to_specific_chain = data.get('toSpecificChain', 'mainnet')

            logger.info(f"RecallSpot: Extracted side='{side}', base='{base_symbol}', quote='{quote_symbol}', size='{amount}'")

            if not side or side not in ['buy', 'sell']:
                raise ValueError("Side must be 'buy' or 'sell'")

            if not base_symbol or not quote_symbol or not amount:
                raise ValueError("base, quote, and size are required")
            # Determine fromToken and toToken based on side
            if side == 'buy':
                # Buying base_token with quote_token
                from_token = self.get_token_address(quote_symbol, from_specific_chain)  # Selling quote token (e.g., USDC)
                to_token = self.get_token_address(base_symbol, to_specific_chain)     # Buying base token (e.g., ETH)
                logger.info(f"RecallSpot: BUY {base_symbol} with {quote_symbol}")
                logger.info(f"RecallSpot: OUT - {quote_symbol}: {from_token}")
                logger.info(f"RecallSpot: IN - {base_symbol}: {to_token}")
            else:  # side == 'sell'
                # Selling base_token for quote_token
                from_token = self.get_token_address(base_symbol, from_specific_chain)   # Selling base token (e.g., ETH)
                to_token = self.get_token_address(quote_symbol, to_specific_chain)    # Getting quote token (e.g., USDC)
                logger.info(f"RecallSpot: SELL {base_symbol} for {quote_symbol} - selling {from_token} to get {to_token}")
                logger.info(f"RecallSpot: OUT - {base_symbol}: {from_token}")
                logger.info(f"RecallSpot: IN - {quote_symbol}: {to_token}")

            # if not base_token_address:
            #     raise ValueError(f"Could not find address for base token '{base_symbol}' on {from_specific_chain}")

            # if not quote_token_address:
            #     raise ValueError(f"Could not find address for quote token '{quote_symbol}' on {from_specific_chain}")

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