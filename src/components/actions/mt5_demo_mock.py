"""
Mock version of MT5Demo for development and testing on non-Windows systems.
This allows the webhook bot to run without MetaTrader 5 installed.
"""

from components.actions.base.action import Action
from utils.log import get_logger
from config import mt5_config
import json
import time
from datetime import datetime

logger = get_logger(__name__)


class Mt5DemoMock(Action):
    """
    Mock implementation of MT5Demo for development/testing on systems
    where MetaTrader5 Python package is not available (macOS, Linux)
    """

    def __init__(self):
        logger.info(f"Mt5DemoMock.__init__() called with config: {mt5_config}")
        super().__init__()

        self.config = mt5_config
        self.connected = True  # Always "connected" in mock mode
        logger.info("Mt5DemoMock: Successfully initialized (MOCK MODE)")

        # Mock account data
        self.mock_account = {
            'login': self.config.login,
            'balance': 10000.0,
            'equity': 10000.0,
            'margin': 0.0,
            'margin_free': 10000.0,
            'margin_level': 0.0,
            'currency': 'USD',
            'server': self.config.server,
            'name': 'Demo Account',
            'trade_mode': 0,
            'limit_orders': 200,
            'margin_so_mode': 0,
            'trade_allowed': True,
            'trade_expert': True,
            'margin_mode': 0,
            'currency_digits': 2,
            'fifo_close': False,
            'credit': 0.0,
            'profit': 0.0
        }

        # Mock positions storage
        self.mock_positions = []
        self.next_ticket = 1000

    def get_account_info(self):
        """Mock account information"""
        logger.info("Mt5DemoMock: Getting mock account information")
        return self.mock_account.copy()

    def get_symbol_info(self, symbol: str):
        """Mock symbol information"""
        logger.info(f"Mt5DemoMock: Getting mock symbol info for {symbol}")

        # Mock symbol data for common pairs
        mock_symbols = {
            'EURUSD': {'bid': 1.0850, 'ask': 1.0852, 'digits': 5, 'volume_min': 0.01, 'volume_max': 100.0, 'volume_step': 0.01},
            'GBPUSD': {'bid': 1.2650, 'ask': 1.2652, 'digits': 5, 'volume_min': 0.01, 'volume_max': 100.0, 'volume_step': 0.01},
            'USDJPY': {'bid': 149.85, 'ask': 149.87, 'digits': 3, 'volume_min': 0.01, 'volume_max': 100.0, 'volume_step': 0.01},
            'USDCHF': {'bid': 0.8750, 'ask': 0.8752, 'digits': 5, 'volume_min': 0.01, 'volume_max': 100.0, 'volume_step': 0.01},
        }

        if symbol in mock_symbols:
            base_info = mock_symbols[symbol]
            return {
                'name': symbol,
                'basis': 0,
                'category': 'Forex',
                'currency_base': symbol[:3],
                'currency_profit': symbol[3:],
                'currency_margin': symbol[3:],
                'digits': base_info['digits'],
                'trade_tick_value': 1.0,
                'trade_tick_size': 0.00001,
                'trade_contract_size': 100000.0,
                'trade_mode': 4,
                'volume_min': base_info['volume_min'],
                'volume_max': base_info['volume_max'],
                'volume_step': base_info['volume_step'],
                'spread': 2,
                'bid': base_info['bid'],
                'ask': base_info['ask']
            }
        else:
            logger.warning(f"Mt5DemoMock: Unknown symbol {symbol}, returning default")
            return {
                'name': symbol,
                'bid': 1.0000,
                'ask': 1.0002,
                'digits': 5,
                'volume_min': 0.01,
                'volume_max': 100.0,
                'volume_step': 0.01
            }

    def place_order(self, symbol: str, order_type: str, volume: float, price: float = None,
                   stop_loss: float = None, take_profit: float = None, comment: str = "Mock order"):
        """Mock order placement"""
        logger.info(f"Mt5DemoMock: Placing mock {order_type} order for {symbol}, volume={volume}")

        symbol_info = self.get_symbol_info(symbol)

        # Generate mock order result
        ticket = self.next_ticket
        self.next_ticket += 1

        # Use current market price if not specified
        if price is None:
            if order_type in ['buy']:
                price = symbol_info['ask']
            else:
                price = symbol_info['bid']

        # Create mock position
        position = {
            'ticket': ticket,
            'time': int(time.time()),
            'type': 0 if order_type == 'buy' else 1,  # 0=buy, 1=sell
            'magic': 234000,
            'identifier': ticket,
            'reason': 0,
            'volume': volume,
            'price_open': price,
            'sl': stop_loss or 0.0,
            'tp': take_profit or 0.0,
            'price_current': price,
            'swap': 0.0,
            'profit': 0.0,
            'symbol': symbol,
            'comment': comment,
            'external_id': ''
        }

        self.mock_positions.append(position)

        result = {
            'retcode': 10009,  # TRADE_RETCODE_DONE
            'deal': ticket,
            'order': ticket,
            'volume': volume,
            'price': price,
            'bid': symbol_info['bid'],
            'ask': symbol_info['ask'],
            'comment': comment,
            'request_id': ticket
        }

        logger.info(f"Mt5DemoMock: Mock order placed successfully: ticket={ticket}")
        return result

    def get_positions(self, symbol: str = None):
        """Get mock positions"""
        logger.info(f"Mt5DemoMock: Getting mock positions for symbol={symbol}")

        if symbol:
            positions = [pos for pos in self.mock_positions if pos['symbol'] == symbol]
        else:
            positions = self.mock_positions.copy()

        logger.info(f"Mt5DemoMock: Retrieved {len(positions)} mock positions")
        return positions

    def close_position(self, ticket: int):
        """Mock position closing"""
        logger.info(f"Mt5DemoMock: Closing mock position with ticket={ticket}")

        # Find and remove position
        for i, pos in enumerate(self.mock_positions):
            if pos['ticket'] == ticket:
                del self.mock_positions[i]
                logger.info(f"Mt5DemoMock: Mock position {ticket} closed successfully")
                return {'retcode': 10009, 'deal': ticket}

        logger.error(f"Mt5DemoMock: Position {ticket} not found")
        return None

    def run(self, *args, **kwargs):
        """
        Main run method - same interface as real MT5Demo
        """
        logger.info("==================== Mt5DemoMock.run() START ====================")
        logger.info(f"Mt5DemoMock.run() called with args: {args}, kwargs: {kwargs}")
        super().run(*args, **kwargs)
        logger.info("==================== Mt5DemoMock.run() AFTER SUPER ====================")

        try:
            logger.info("Mt5DemoMock: Validating data...")
            data = self.validate_data()
            logger.info(f"Mt5DemoMock: Validated data: {data}")

            action = data.get('action', '').lower()
            symbol = data.get('symbol', 'EURUSD').upper()

            if action == 'info':
                logger.info("Mt5DemoMock: Getting mock account information...")
                account_info = self.get_account_info()
                logger.info(f"Mock account info: {account_info}")

            elif action == 'positions':
                logger.info("Mt5DemoMock: Getting mock positions...")
                positions = self.get_positions(symbol if symbol != 'ALL' else None)
                logger.info(f"Mock positions: {len(positions)} positions")
                for pos in positions:
                    logger.info(f"Position: {pos['symbol']} {pos['type']} {pos['volume']} @ {pos['price_open']}")

            elif action in ['buy', 'sell']:
                volume = float(data.get('volume', '0.01'))
                order_type = data.get('order_type', 'market').lower()
                price = float(data.get('price', 0)) if data.get('price') else None
                stop_loss = float(data.get('stop_loss', 0)) if data.get('stop_loss') else None
                take_profit = float(data.get('take_profit', 0)) if data.get('take_profit') else None
                comment = data.get('comment', 'Mock webhook trade')

                logger.info(f"Mt5DemoMock: Placing mock {action} order for {symbol}, volume={volume}")

                result = self.place_order(
                    symbol=symbol,
                    order_type=action,
                    volume=volume,
                    price=price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    comment=comment
                )

                if result:
                    logger.info(f"Mt5DemoMock: Mock order executed successfully: {result}")
                else:
                    logger.error("Mt5DemoMock: Failed to execute mock order")

            elif action == 'close':
                ticket = int(data.get('ticket', 0))
                if not ticket:
                    raise ValueError("Ticket number is required for close action")

                logger.info(f"Mt5DemoMock: Closing mock position with ticket={ticket}")
                result = self.close_position(ticket)

                if result:
                    logger.info(f"Mt5DemoMock: Mock position closed successfully: ticket={ticket}")
                else:
                    logger.error(f"Mt5DemoMock: Failed to close mock position: ticket={ticket}")

            else:
                raise ValueError(f"Invalid action: {action}")

        except Exception as e:
            logger.error(f"Error in Mt5DemoMock action run: {e}")
            import traceback
            traceback.print_exc()
            raise
