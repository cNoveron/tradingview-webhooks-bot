from components.actions.base.action import Action
from utils.log import get_logger
from config import mt5_config
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import json

logger = get_logger(__name__)


class MT5Demo(Action):
    def __init__(self):
        logger.info(f"MT5Demo.__init__() called with config: {mt5_config}")
        super().__init__()

        self.config = mt5_config
        self.connected = False
        self._initialize_connection()
        logger.info("MT5Demo: Successfully initialized")

    def _initialize_connection(self):
        """
        Initialize MetaTrader 5 connection to demo account
        """
        try:
            # Initialize MT5 connection
            if not mt5.initialize():
                error_code = mt5.last_error()
                logger.error(f"MT5 initialize failed, error code = {error_code}")
                raise Exception(f"MT5 initialization failed: {error_code}")

            # Connect to demo account
            authorized = mt5.login(
                login=self.config.login,
                password=self.config.password,
                server=self.config.server
            )

            if authorized:
                self.connected = True
                account_info = mt5.account_info()
                logger.info(f"Connected to MT5 demo account")
                logger.info(f"Login: {account_info.login}")
                logger.info(f"Balance: {account_info.balance}")
                logger.info(f"Server: {account_info.server}")
                logger.info(f"Currency: {account_info.currency}")
            else:
                error_code = mt5.last_error()
                logger.error(f"Failed to connect to demo account, error code: {error_code}")
                raise Exception(f"MT5 login failed: {error_code}")

        except Exception as e:
            logger.error(f"Error initializing MT5 connection: {e}")
            self.connected = False
            raise

    def get_account_info(self):
        """
        Get account information from MetaTrader 5
        """
        try:
            if not self.connected:
                self._initialize_connection()

            account_info = mt5.account_info()
            if account_info is None:
                error_code = mt5.last_error()
                logger.error(f"Failed to get account info, error code: {error_code}")
                return None

            # Convert to dict for easier handling
            account_dict = {
                'login': account_info.login,
                'trade_mode': account_info.trade_mode,
                'name': account_info.name,
                'server': account_info.server,
                'currency': account_info.currency,
                'leverage': account_info.leverage,
                'limit_orders': account_info.limit_orders,
                'margin_so_mode': account_info.margin_so_mode,
                'trade_allowed': account_info.trade_allowed,
                'trade_expert': account_info.trade_expert,
                'margin_mode': account_info.margin_mode,
                'currency_digits': account_info.currency_digits,
                'fifo_close': account_info.fifo_close,
                'balance': account_info.balance,
                'credit': account_info.credit,
                'profit': account_info.profit,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'margin_free': account_info.margin_free,
                'margin_level': account_info.margin_level
            }

            logger.info(f"Account info retrieved: Balance={account_dict['balance']}, Equity={account_dict['equity']}")
            return account_dict

        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None

    def get_symbol_info(self, symbol: str):
        """
        Get symbol information (currency pair details)
        """
        try:
            if not self.connected:
                self._initialize_connection()

            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                error_code = mt5.last_error()
                logger.error(f"Failed to get symbol info for {symbol}, error code: {error_code}")
                return None

            # Convert to dict
            symbol_dict = {
                'name': symbol_info.name,
                'basis': symbol_info.basis,
                'category': symbol_info.category,
                'currency_base': symbol_info.currency_base,
                'currency_profit': symbol_info.currency_profit,
                'currency_margin': symbol_info.currency_margin,
                'digits': symbol_info.digits,
                'trade_tick_value': symbol_info.trade_tick_value,
                'trade_tick_size': symbol_info.trade_tick_size,
                'trade_contract_size': symbol_info.trade_contract_size,
                'trade_mode': symbol_info.trade_mode,
                'volume_min': symbol_info.volume_min,
                'volume_max': symbol_info.volume_max,
                'volume_step': symbol_info.volume_step,
                'spread': symbol_info.spread,
                'bid': symbol_info.bid,
                'ask': symbol_info.ask
            }

            logger.info(f"Symbol info for {symbol}: bid={symbol_dict['bid']}, ask={symbol_dict['ask']}")
            return symbol_dict

        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None

    def place_order(self, symbol: str, order_type: str, volume: float, price: float = None,
                   stop_loss: float = None, take_profit: float = None, comment: str = "Webhook order"):
        """
        Place an order on MetaTrader 5

        Args:
            symbol: Trading symbol (e.g., 'EURUSD', 'GBPUSD')
            order_type: 'buy' or 'sell' for market orders, 'buy_limit', 'sell_limit', etc.
            volume: Volume to trade (in lots)
            price: Price for limit/stop orders (None for market orders)
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            comment: Order comment
        """
        try:
            if not self.connected:
                self._initialize_connection()

            # Get symbol info for proper lot size
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                raise ValueError(f"Could not get symbol info for {symbol}")

            # Validate volume
            volume = max(symbol_info['volume_min'], min(volume, symbol_info['volume_max']))

            # Round volume to step
            volume_step = symbol_info['volume_step']
            volume = round(volume / volume_step) * volume_step

            # Map order types
            order_type_map = {
                'buy': mt5.ORDER_TYPE_BUY,
                'sell': mt5.ORDER_TYPE_SELL,
                'buy_limit': mt5.ORDER_TYPE_BUY_LIMIT,
                'sell_limit': mt5.ORDER_TYPE_SELL_LIMIT,
                'buy_stop': mt5.ORDER_TYPE_BUY_STOP,
                'sell_stop': mt5.ORDER_TYPE_SELL_STOP
            }

            if order_type not in order_type_map:
                raise ValueError(f"Invalid order type: {order_type}")

            mt5_order_type = order_type_map[order_type]

            # For market orders, use current market price
            if order_type in ['buy', 'sell'] and price is None:
                if order_type == 'buy':
                    price = symbol_info['ask']
                else:
                    price = symbol_info['bid']

            # Create order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5_order_type,
                "price": price,
                "deviation": 20,  # Allowed price deviation in points
                "magic": 234000,  # Expert Advisor ID
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled
                "type_filling": mt5.ORDER_FILLING_IOC,  # Immediate or Cancel
            }

            # Add stop loss and take profit if specified
            if stop_loss:
                request["sl"] = stop_loss
            if take_profit:
                request["tp"] = take_profit

            logger.info(f"MT5Demo: Placing order: {request}")

            # Send order
            result = mt5.order_send(request)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order failed, return code: {result.retcode}")
                logger.error(f"Error details: {result}")
                return None

            logger.info(f"Order placed successfully: ticket={result.order}, volume={result.volume}")

            # Convert result to dict
            result_dict = {
                'retcode': result.retcode,
                'deal': result.deal,
                'order': result.order,
                'volume': result.volume,
                'price': result.price,
                'bid': result.bid,
                'ask': result.ask,
                'comment': result.comment,
                'request_id': result.request_id
            }

            return result_dict

        except Exception as e:
            logger.error(f"Error placing order: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_positions(self, symbol: str = None):
        """
        Get open positions
        """
        try:
            if not self.connected:
                self._initialize_connection()

            if symbol:
                positions = mt5.positions_get(symbol=symbol)
            else:
                positions = mt5.positions_get()

            if positions is None:
                error_code = mt5.last_error()
                logger.error(f"Failed to get positions, error code: {error_code}")
                return []

            # Convert to list of dicts
            positions_list = []
            for pos in positions:
                pos_dict = {
                    'ticket': pos.ticket,
                    'time': pos.time,
                    'type': pos.type,
                    'magic': pos.magic,
                    'identifier': pos.identifier,
                    'reason': pos.reason,
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'stop_loss': pos.sl,
                    'take_profit': pos.tp,
                    'price_current': pos.price_current,
                    'swap': pos.swap,
                    'profit': pos.profit,
                    'symbol': pos.symbol,
                    'comment': pos.comment,
                    'external_id': pos.external_id
                }
                positions_list.append(pos_dict)

            logger.info(f"Retrieved {len(positions_list)} positions")
            return positions_list

        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []

    def close_position(self, ticket: int):
        """
        Close a position by ticket
        """
        try:
            if not self.connected:
                self._initialize_connection()

            # Get position info
            positions = mt5.positions_get(ticket=ticket)
            if not positions:
                logger.error(f"Position with ticket {ticket} not found")
                return None

            position = positions[0]

            # Determine opposite order type
            if position.type == mt5.POSITION_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(position.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(position.symbol).ask

            # Create close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": "Close position",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            logger.info(f"MT5Demo: Closing position: {request}")

            # Send close order
            result = mt5.order_send(request)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Position close failed, return code: {result.retcode}")
                logger.error(f"Error details: {result}")
                return None

            logger.info(f"Position closed successfully: ticket={ticket}")
            return result

        except Exception as e:
            logger.error(f"Error closing position {ticket}: {e}")
            return None

    def run(self, *args, **kwargs):
        """
        Main run method called by the webhook system
        Expected data format: {
            "action": "buy/sell/close/info",  # Action to perform
            "symbol": "EURUSD",               # Trading symbol
            "volume": "0.1",                  # Volume in lots (for buy/sell)
            "order_type": "market",           # "market", "limit", "stop" (optional, defaults to market)
            "price": "1.1000",                # Price for limit/stop orders (optional)
            "stop_loss": "1.0950",            # Stop loss price (optional)
            "take_profit": "1.1050",          # Take profit price (optional)
            "comment": "Webhook trade",       # Order comment (optional)
            "ticket": "12345"                 # Position ticket for close action (required for close)
        }
        """
        logger.info("==================== MT5Demo.run() START ====================")
        logger.info(f"MT5Demo.run() called with args: {args}, kwargs: {kwargs}")
        super().run(*args, **kwargs)  # this is required
        logger.info("==================== MT5Demo.run() AFTER SUPER ====================")

        try:
            logger.info("MT5Demo: Validating data...")
            data = self.validate_data()
            logger.info(f"MT5Demo: Validated data: {data}")

            action = data.get('action', '').lower()
            symbol = data.get('symbol', 'EURUSD').upper()

            if action == 'info':
                # Get account information
                logger.info("MT5Demo: Getting account information...")
                account_info = self.get_account_info()
                if account_info:
                    logger.info(f"Account info retrieved successfully: {account_info}")
                else:
                    logger.error("Failed to get account information")

            elif action == 'positions':
                # Get positions
                logger.info("MT5Demo: Getting positions...")
                positions = self.get_positions(symbol if symbol != 'ALL' else None)
                logger.info(f"Positions retrieved: {len(positions)} positions")
                for pos in positions:
                    logger.info(f"Position: {pos['symbol']} {pos['type']} {pos['volume']} @ {pos['price_open']}, profit: {pos['profit']}")

            elif action in ['buy', 'sell']:
                # Place market order
                volume = float(data.get('volume', '0.01'))
                order_type = data.get('order_type', 'market').lower()
                price = float(data.get('price', 0)) if data.get('price') else None
                stop_loss = float(data.get('stop_loss', 0)) if data.get('stop_loss') else None
                take_profit = float(data.get('take_profit', 0)) if data.get('take_profit') else None
                comment = data.get('comment', 'Webhook trade')

                # Determine order type
                if order_type == 'limit':
                    mt5_order_type = f"{action}_limit"
                elif order_type == 'stop':
                    mt5_order_type = f"{action}_stop"
                else:
                    mt5_order_type = action

                logger.info(f"MT5Demo: Placing {mt5_order_type} order for {symbol}, volume={volume}")

                result = self.place_order(
                    symbol=symbol,
                    order_type=mt5_order_type,
                    volume=volume,
                    price=price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    comment=comment
                )

                if result:
                    logger.info(f"MT5 order executed successfully: {result}")
                else:
                    logger.error("Failed to execute MT5 order")

            elif action == 'close':
                # Close position
                ticket = int(data.get('ticket', 0))
                if not ticket:
                    raise ValueError("Ticket number is required for close action")

                logger.info(f"MT5Demo: Closing position with ticket={ticket}")
                result = self.close_position(ticket)

                if result:
                    logger.info(f"MT5 position closed successfully: ticket={ticket}")
                else:
                    logger.error(f"Failed to close MT5 position: ticket={ticket}")

            else:
                raise ValueError(f"Invalid action: {action}. Must be 'buy', 'sell', 'close', 'info', or 'positions'")

        except Exception as e:
            logger.error(f"Error in MT5Demo action run: {e}")
            import traceback
            traceback.print_exc()
            raise

    def __del__(self):
        """
        Clean up MT5 connection when object is destroyed
        """
        try:
            if self.connected:
                mt5.shutdown()
                logger.info("MT5 connection closed")
        except:
            pass
