from components.actions.base.action import Action
from utils.hmac_auth import create_hmac_authenticator
import json


class BitsoSpot(Action):
    # Add your API_KEY from Bitso
    API_KEY = ''
    # Add your API_SECRET from Bitso
    API_SECRET = ''

    # Bitso API base URL
    BASE_URL = 'https://api.bitso.com'

    def __init__(self):
        super().__init__()
        if not self.API_KEY or not self.API_SECRET:
            raise ValueError("API_KEY and API_SECRET must be set")

        self.authenticator = create_hmac_authenticator(self.API_KEY, self.API_SECRET)

    def get_account_status(self):
        """
        Get account status from Bitso API
        """
        try:
            response = self.authenticator.authenticated_request(
                url=f"{self.BASE_URL}/v3/account_status",
                method='GET'
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting account status: {e}")
            return None

    def get_balance(self):
        """
        Get account balance from Bitso API
        """
        try:
            response = self.authenticator.authenticated_request(
                url=f"{self.BASE_URL}/v3/balance",
                method='GET'
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting balance: {e}")
            return None

    def get_available_books(self):
        """
        Get available trading books (pairs) from Bitso API
        """
        try:
            response = self.authenticator.authenticated_request(
                url=f"{self.BASE_URL}/v3/available_books",
                method='GET'
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting available books: {e}")
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

            response = self.authenticator.authenticated_request(
                url=f"{self.BASE_URL}/v3/orders",
                method='POST',
                body=order_payload
            )

            response.raise_for_status()
            result = response.json()
            print(f"Order placed successfully: {result}")
            return result

        except Exception as e:
            print(f"Error placing order: {e}")
            return None

    def cancel_order(self, order_id: str):
        """
        Cancel an order on Bitso
        """
        try:
            response = self.authenticator.authenticated_request(
                url=f"{self.BASE_URL}/v3/orders/{order_id}",
                method='DELETE'
            )
            response.raise_for_status()
            result = response.json()
            print(f"Order cancelled successfully: {result}")
            return result
        except Exception as e:
            print(f"Error cancelling order: {e}")
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
            url = f"{self.BASE_URL}/v3/orders"
            if query_string:
                url += f"?{query_string}"

            response = self.authenticator.authenticated_request(url=url, method='GET')
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting orders: {e}")
            return None

    def run(self, *args, **kwargs):
        """
        Main run method called by the webhook system
        Expected data format: {"action": "buy/sell", "order_size": "amount"}
        """
        super().run(*args, **kwargs)  # this is required

        try:
            data = self.validate_data()

            # Extract action and order_size from webhook data
            action = data.get('action')
            order_size = data.get('order_size')

            if not action or not order_size:
                raise ValueError("Both 'action' and 'order_size' are required in webhook data")

            # Default trading pair - you can modify this or make it configurable
            book = data.get('book', 'btc_mxn')  # Default to BTC/MXN

            # Place the order
            result = self.place_order(
                book=book,
                side=action,
                order_type='market',
                amount=str(order_size)
            )

            if result:
                print(f"Bitso order executed successfully: {result}")
            else:
                print("Failed to execute Bitso order")

        except Exception as e:
            print(f"Error in Bitso action run: {e}")
            raise