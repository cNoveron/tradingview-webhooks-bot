import hashlib
import hmac
import json
import time
import base64
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import requests


class HMACAuthConfig:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret


class AuthenticatedRequest:
    def __init__(self, method: str, path: str, body: Optional[Any] = None):
        self.method = method
        self.path = path
        self.body = body


class HMACAuthenticator:
    def __init__(self, config: HMACAuthConfig):
        self.api_key = config.api_key
        self.api_secret = config.api_secret
        self.last_nonce = 0

    def _generate_nonce(self) -> int:
        """
        Generate a unique nonce that increases with each API call
        Uses UNIX timestamp with additional uniqueness
        """
        timestamp = int(time.time())
        # Ensure nonce is always increasing
        self.last_nonce = max(self.last_nonce + 1, timestamp)
        return self.last_nonce

    def _build_signature_string(self, nonce: int, method: str, path: str, payload: Optional[Any] = None) -> str:
        """
        Build the signature string according to Bitso's specification:
        nonce + HTTP method + request path + JSON payload
        """
        json_payload = json.dumps(payload) if payload else ''
        return f"{nonce}{method}{path}{json_payload}"

    def _generate_signature(self, signature_string: str) -> str:
        """
        Generate HMAC-SHA256 signature
        """
        return hmac.new(
            self.api_secret.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _create_auth_header(self, nonce: int, signature: str) -> str:
        """
        Create authorization header in Bitso format: Bitso <key>:<nonce>:<signature>
        """
        return f"Bitso {self.api_key}:{nonce}:{signature}"

    def authenticate_request(self, request: AuthenticatedRequest) -> Dict[str, str]:
        """
        Authenticate a request and return headers
        """
        nonce = self._generate_nonce()
        signature_string = self._build_signature_string(
            nonce,
            request.method.upper(),
            request.path,
            request.body
        )
        signature = self._generate_signature(signature_string)
        auth_header = self._create_auth_header(nonce, signature)

        return {
            'Content-Type': 'application/json',
            'Authorization': auth_header
        }

    def authenticated_request(self, url: str, method: str, body: Optional[Any] = None) -> requests.Response:
        """
        Create an authenticated HTTP request
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        if parsed_url.query:
            path += f"?{parsed_url.query}"

        headers = self.authenticate_request(AuthenticatedRequest(method, path, body))

        return requests.request(
            method=method,
            url=url,
            headers=headers,
            json=body if body else None
        )

    def validate_response_signature(self, response_body: str, expected_signature: str) -> bool:
        """
        Validate response signature (if provided by the API)
        """
        calculated_signature = hmac.new(
            self.api_secret.encode('utf-8'),
            response_body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return calculated_signature == expected_signature


def create_hmac_authenticator(api_key: str, api_secret: str) -> HMACAuthenticator:
    """
    Factory function to create an HMAC authenticator
    """
    if not api_key or not api_secret:
        raise ValueError('API key and API secret are required')

    return HMACAuthenticator(HMACAuthConfig(api_key, api_secret))


def create_authenticated_headers(api_key: str, api_secret: str, method: str, path: str, body: Optional[Any] = None) -> Dict[str, str]:
    """
    Utility function to create authenticated headers for any request
    """
    authenticator = create_hmac_authenticator(api_key, api_secret)
    return authenticator.authenticate_request(AuthenticatedRequest(method, path, body))