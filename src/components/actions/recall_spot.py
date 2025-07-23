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
        self._initialize_token_mappings()  # Pre-populate with known tokens
        logger.info("RecallSpot: Successfully initialized with authenticator")

    def _initialize_token_mappings(self):
        """
        Pre-populate token mappings with known tokens from portfolio
        """
        # Pre-populated token data from Recall portfolio
        portfolio_data = {
            "tokens": [
                {"token": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "symbol": "WETH", "chain": "evm"},
                {"token": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "symbol": "USDC", "chain": "evm"},
                {"token": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", "symbol": "USDC", "chain": "evm"},  # Polygon USDC
                {"token": "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA", "symbol": "USDbC", "chain": "evm"},
                {"token": "0xaf88d065e77c8cc2239327c5edb3a432268e5831", "symbol": "USDC", "chain": "evm"},  # Arbitrum USDC
                {"token": "0x7f5c764cbc14f9669b88837ca1490cca17c31607", "symbol": "USDC", "chain": "evm"},  # Optimism USDC
                {"token": "So11111111111111111111111111111111111111112", "symbol": "SOL", "chain": "svm", "specificChain": "svm"},
                {"token": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "symbol": "USDC", "chain": "svm", "specificChain": "svm"}
            ]
        }

        mappings = {}

        for token_info in portfolio_data["tokens"]:
            chain_type = token_info.get('chain', 'evm')
            specific_chain = token_info.get('specificChain', 'mainnet' if chain_type == 'evm' else chain_type)
            symbol = token_info.get('symbol', '').upper()
            address = token_info.get('token', '')

            # Use specificChain as the key for mapping
            chain_key = specific_chain

            if chain_key not in mappings:
                mappings[chain_key] = {}

            if symbol and address:
                # For multiple USDC addresses, prefer mainnet (first one in our list)
                if symbol not in mappings[chain_key]:
                    mappings[chain_key][symbol] = address
                    logger.debug(f"Added mapping: {chain_key}.{symbol} -> {address}")
                else:
                    logger.debug(f"Skipped duplicate mapping for {chain_key}.{symbol}")

        # Add some common aliases
        if 'mainnet' in mappings:
            # Add ETH as alias for WETH on mainnet
            if 'WETH' in mappings['mainnet'] and 'ETH' not in mappings['mainnet']:
                mappings['mainnet']['ETH'] = mappings['mainnet']['WETH']
                logger.debug(f"Added ETH alias for WETH on mainnet")

        self._token_mappings = mappings
        logger.info(f"Pre-populated token mappings for {len(mappings)} chains with {sum(len(tokens) for tokens in mappings.values())} total tokens")
        logger.info(f"Available chains: {list(mappings.keys())}")
        for chain, tokens in mappings.items():
            logger.info(f"  {chain}: {list(tokens.keys())}")

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
        This will refresh mappings from the live API (fallback to pre-populated data)
        """
        try:
            portfolio = self.get_portfolio()
            if not portfolio:
                logger.warning("Failed to retrieve portfolio, using pre-populated mappings")
                return self._token_mappings

            mappings = {}

            # Extract token information from portfolio
            if 'tokens' in portfolio:
                for token_info in portfolio['tokens']:
                    chain_type = token_info.get('chain', 'evm')
                    specific_chain = token_info.get('specificChain', 'mainnet' if chain_type == 'evm' else chain_type)
                    symbol = token_info.get('symbol', '').upper()
                    address = token_info.get('token', '') or token_info.get('address', '')

                    # Use specificChain as the key
                    chain_key = specific_chain

                    if chain_key not in mappings:
                        mappings[chain_key] = {}

                    if symbol and address:
                        mappings[chain_key][symbol] = address
                        logger.debug(f"Updated mapping: {chain_key}.{symbol} -> {address}")

            # Add common aliases
            if 'mainnet' in mappings:
                if 'WETH' in mappings['mainnet'] and 'ETH' not in mappings['mainnet']:
                    mappings['mainnet']['ETH'] = mappings['mainnet']['WETH']

            self._token_mappings = mappings
            logger.info(f"Updated token mappings from API for {len(mappings)} chains")
            return mappings

        except Exception as e:
            logger.error(f"Error building token mappings from API: {e}")
            logger.info("Falling back to pre-populated mappings")
            return self._token_mappings

    def get_token_address(self, symbol: str, chain: str = 'mainnet'):
        """
        Get token address for a given symbol and chain
        """
        symbol = symbol.upper()

        if chain in self._token_mappings and symbol in self._token_mappings[chain]:
            address = self._token_mappings[chain][symbol]
            logger.info(f"Found address for {symbol} on {chain}: {address}")
            return address
        else:
            # Try to refresh mappings from API if symbol not found
            logger.info(f"Symbol '{symbol}' not found on {chain}, trying to refresh from API...")
            self.build_token_mappings()

            # Try again after refresh
            if chain in self._token_mappings and symbol in self._token_mappings[chain]:
                address = self._token_mappings[chain][symbol]
                logger.info(f"Found address for {symbol} on {chain} after refresh: {address}")
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
                # 'slippageTolerance': slippage_tolerance,
                # 'fromChain': from_chain,
                # 'fromSpecificChain': from_specific_chain,
                # 'toChain': to_chain,
                # 'toSpecificChain': to_specific_chain
            }

            endpoint = f"{self.config.base_url}/api/trade/execute"
            logger.info(f"RecallSpot: Trade payload: {trade_payload}")
            logger.info(f"RecallSpot: Making API call to {endpoint}")

            # DEBUG: Let's manually make the request to see what's different
            import requests
            import json

            headers = {
                'Authorization': f'Bearer {self.config.api_key}',
                'Content-Type': 'application/json'
            }

            logger.info(f"DEBUG: Headers being sent: {headers}")
            logger.info(f"DEBUG: Raw JSON payload: {json.dumps(trade_payload)}")

            # Make request manually for debugging
            response = requests.post(endpoint, json=trade_payload, headers=headers, timeout=30)

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
            "base": "ETH",    # Symbol of token being bought/sold (e.g., "ETH", "BTC", "SOL")
            "quote": "USDC",  # Symbol of quote token (e.g., "USDC", "USDT")
            "size": "1.5",    # Amount to trade
            "reason": "Optional reason for trade",
            "slippageTolerance": "0.5",  # Optional, defaults to 0.5%
            "fromChain": "evm",  # Optional, defaults to evm
            "fromSpecificChain": "mainnet",  # Optional, defaults to mainnet (or svm for Solana)
            "toChain": "evm",  # Optional, defaults to evm
            "toSpecificChain": "mainnet"  # Optional, defaults to mainnet (or svm for Solana)
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
                # slippage_tolerance=slippage_tolerance,
                # from_chain=from_chain,
                # from_specific_chain=from_specific_chain,
                # to_chain=to_chain,
                # to_specific_chain=to_specific_chain
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