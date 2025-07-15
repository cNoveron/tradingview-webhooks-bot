from components.actions.base.action import Action
from utils.hmac_auth import create_hmac_authenticator
from utils.log import get_logger
from config import bitso_config
import json

logger = get_logger(__name__)


class BitsoSpot(Action):
    def __init__(self):
        logger.info(f"BitsoSpot.__init__() called with config: {bitso_config}")
        super().__init__()

        self.config = bitso_config
        self.authenticator = create_hmac_authenticator(self.config.api_key, self.config.api_secret)
        logger.info("BitsoSpot: Successfully initialized with authenticator")

    def get_account_status(self):
        """
        Get account status from Bitso API
        """
        try:
            response = self.authenticator.authenticated_request(
                url=f"{self.config.base_url}/v3/account_status",
                method='GET'
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting account status: {e}")
            return None

    def get_balance(self):
        """
        Get account balance from Bitso API
        """
        try:
            response = self.authenticator.authenticated_request(
                url=f"{self.config.base_url}/v3/balance",
                method='GET'
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None

    def get_available_books(self):
        """
        Get available trading books (pairs) from Bitso API
        """
        try:
            response = self.authenticator.authenticated_request(
                url=f"{self.config.base_url}/v3/available_books",
                method='GET'
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting available books: {e}")
            return None

    def place_order(self, book: str, side: str, order_type: str = 'market', amount: str = None, price: str = None):
        """
        Place an order on Bitso

        Args:
            book: Trading pair (e.g., 'btc_mxn', 'eth_mxn')
            side: 'buy' or 'sell'
            order_type: 'market' or 'limit'
            amount: Amount to buy/sell
            price: Price for limit orders
        """
        try:
            logger.info(f"BitsoSpot: place_order called with book={book}, side={side}, type={order_type}, amount={amount}, price={price}")

            # Build order payload
            order_payload = {
                'book': book,
                'side': side,
                'type': order_type
            }

            if amount:
                if side == 'buy':
                    order_payload['minor'] = amount  # Amount in quote currency for buy orders
                else:
                    order_payload['major'] = amount  # Amount in base currency for sell orders

            if order_type == 'limit' and price:
                order_payload['price'] = price

            logger.info(f"BitsoSpot: Order payload: {order_payload}")
            logger.info(f"BitsoSpot: Making API call to {self.config.base_url}/v3/orders")

            response = self.authenticator.authenticated_request(
                url=f"{self.config.base_url}/v3/orders",
                method='POST',
                body=order_payload
            )

            logger.info(f"BitsoSpot: API response status: {response.status_code}")
            logger.info(f"BitsoSpot: API response headers: {dict(response.headers)}")
            logger.info(f"BitsoSpot: API response body: {response.text}")

            response.raise_for_status()
            result = response.json()
            logger.info(f"Order placed successfully: {result}")
            return result

        except Exception as e:
            logger.error(f"Error placing order: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return None

    def cancel_order(self, order_id: str):
        """
        Cancel an order on Bitso
        """
        try:
            response = self.authenticator.authenticated_request(
                url=f"{self.config.base_url}/v3/orders/{order_id}",
                method='DELETE'
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Order cancelled successfully: {result}")
            return result
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return None

    def get_orders(self, book: str = None, status: str = None):
        """
        Get orders from Bitso

        Args:
            book: Trading pair to filter by
            status: Order status to filter by ('open', 'partial-fill', 'completed', 'cancelled')
        """
        try:
            params = {}
            if book:
                params['book'] = book
            if status:
                params['status'] = status

            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{self.config.base_url}/v3/orders"
            if query_string:
                url += f"?{query_string}"

            response = self.authenticator.authenticated_request(url=url, method='GET')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return None

    def run(self, *args, **kwargs):
        """
        Main run method called by the webhook system
        Expected data format: {"action": "buy/sell", "order_size": "amount"}
        """
        logger.info("==================== BitsoSpot.run() START ====================")
        logger.info(f"BitsoSpot.run() called with args: {args}, kwargs: {kwargs}")
        super().run(*args, **kwargs)  # this is required
        logger.info("==================== BitsoSpot.run() AFTER SUPER ====================")

        try:
            logger.info("BitsoSpot: Validating data...")
            data = self.validate_data()
            logger.info(f"BitsoSpot: Validated data: {data}")

            # Extract action and order_size from webhook data
            action = data.get('action')
            order_size = data.get('order_size')
            logger.info(f"BitsoSpot: Extracted action='{action}', order_size='{order_size}'")

            if not action or not order_size:
                raise ValueError("Both 'action' and 'order_size' are required in webhook data")

            # Default trading pair - you can modify this or make it configurable
            book = data.get('book', 'btc_mxn')  # Default to BTC/MXN
            logger.info(f"BitsoSpot: Using book='{book}' for {action} order of size {order_size}")

            # Place the order
            logger.info("BitsoSpot: Attempting to place order...")
            result = self.place_order(
                book=book,
                side=action,
                order_type='market',
                amount=str(order_size)
            )

            if result:
                logger.info(f"Bitso order executed successfully: {result}")
            else:
                logger.error("Failed to execute Bitso order")

        except Exception as e:
            logger.error(f"Error in Bitso action run: {e}")
            import traceback
            traceback.print_exc()
            raise