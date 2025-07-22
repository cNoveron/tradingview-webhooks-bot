import requests
from typing import Dict, Any, Optional


class BearerTokenAuthenticator:
    """
    Simple Bearer token authenticator for APIs that use Bearer token authentication
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def authenticated_request(self, url: str, method: str = 'GET', body: Optional[Dict[str, Any]] = None, timeout: int = 30) -> requests.Response:
        """
        Make an authenticated request using Bearer token

        Args:
            url: The full URL to make the request to
            method: HTTP method (GET, POST, PUT, DELETE)
            body: Request body (will be sent as JSON)
            timeout: Request timeout in seconds

        Returns:
            requests.Response object
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        if method.upper() == 'GET':
            return requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == 'POST':
            return requests.post(url, json=body, headers=headers, timeout=timeout)
        elif method.upper() == 'PUT':
            return requests.put(url, json=body, headers=headers, timeout=timeout)
        elif method.upper() == 'DELETE':
            return requests.delete(url, headers=headers, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")


def create_bearer_authenticator(api_key: str) -> BearerTokenAuthenticator:
    """
    Factory function to create a Bearer token authenticator
    """
    if not api_key:
        raise ValueError('API key is required')

    return BearerTokenAuthenticator(api_key)