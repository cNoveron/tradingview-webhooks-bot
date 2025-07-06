import datetime
import json

from components.actions.base.action import Action
from components.logs.log_event import LogEvent


class ProcessSignal(Action):
    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required
        """
        Custom run method. Processes trading signals from webhook data.
        """
        data = self.validate_data()
        print(f'{self.name} ---> Processing trading signal...')

        # Extract signal information
        signal_info = self._extract_signal_data(data)

        # Process and analyze the signal
        analysis = self._analyze_signal(signal_info)

        # Log the processed signal
        self._log_signal(signal_info, analysis)

        print(f'{self.name} ---> Signal processing completed!')

    def _extract_signal_data(self, data):
        """
        Extract relevant signal data from webhook payload
        """
        try:
            # Handle different data formats
            if isinstance(data, str):
                signal_data = json.loads(data)
            else:
                signal_data = data

            # Extract common signal fields
            signal_info = {
                'symbol': signal_data.get('symbol', 'Unknown'),
                'action': signal_data.get('action', 'Unknown'),
                'price': signal_data.get('price', 0),
                'timestamp': signal_data.get('timestamp', datetime.datetime.now().isoformat()),
                'strategy': signal_data.get('strategy', 'Unknown'),
                'confidence': signal_data.get('confidence', 0)
            }

            return signal_info

        except (json.JSONDecodeError, AttributeError) as e:
            print(f'Error extracting signal data: {e}')
            return {
                'symbol': 'Unknown',
                'action': 'Unknown',
                'price': 0,
                'timestamp': datetime.datetime.now().isoformat(),
                'strategy': 'Unknown',
                'confidence': 0
            }

    def _analyze_signal(self, signal_info):
        """
        Analyze the trading signal and provide insights
        """
        analysis = {
            'signal_strength': 'Weak',
            'recommendation': 'Hold',
            'risk_level': 'Medium'
        }

        # Simple analysis based on confidence level
        confidence = signal_info.get('confidence', 0)
        if confidence >= 80:
            analysis['signal_strength'] = 'Strong'
            analysis['recommendation'] = 'Execute'
            analysis['risk_level'] = 'Low'
        elif confidence >= 60:
            analysis['signal_strength'] = 'Moderate'
            analysis['recommendation'] = 'Consider'
            analysis['risk_level'] = 'Medium'
        else:
            analysis['signal_strength'] = 'Weak'
            analysis['recommendation'] = 'Hold'
            analysis['risk_level'] = 'High'

        return analysis

    def _log_signal(self, signal_info, analysis):
        """
        Log the processed signal with analysis
        """
        timestamp = datetime.datetime.now()

        # Create detailed log message
        log_message = (
            f"Signal: {signal_info['symbol']} | "
            f"Action: {signal_info['action']} | "
            f"Price: {signal_info['price']} | "
            f"Strategy: {signal_info['strategy']} | "
            f"Confidence: {signal_info['confidence']}% | "
            f"Strength: {analysis['signal_strength']} | "
            f"Recommendation: {analysis['recommendation']} | "
            f"Risk: {analysis['risk_level']}"
        )

        # Write to log
        log_event = LogEvent(
            self.name,
            'signal_processed',
            timestamp,
            log_message
        )
        log_event.write()

        # Also print to console for immediate feedback
        print(f"📊 {log_message}")