"""Eastmoney Trading Agent Module

This module provides a trading agent class for interacting with Eastmoney trading services.
"""

import base64
import re
from dataclasses import dataclass
from enum import Enum
from random import SystemRandom
from typing import Any, TypedDict

import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from ddddocr import DdddOcr
from loguru import logger

# RSA Public Key for Eastmoney API encryption
RSA_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDHdsyxT66pDG4p73yope7jxA92
c0AT4qIJ/xtbBcHkFPK77upnsfDTJiVEuQDH+MiMeb+XhCLNKZGp0yaUU6GlxZdp
+nLW8b7Kmijr3iepaDhcbVTsYBWchaWUXauj9Lrhz58/6AE/NF0aMolxIGpsi+ST
2hSHPu3GSXMdhPCkWQIDAQAB
-----END PUBLIC KEY-----
"""

# Constants
LOGIN_URL = "https://jywg.18.cn/Login/Authentication?validatekey="
YZM_URL = "https://jywg.18.cn/Login/YZM?randNum="
BASE_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36",
    "Origin": "https://jywg.18.cn",
    "Host": "jywg.18.cn",
}

# Initialize OCR
ocr = DdddOcr(show_ad=False)


def encrypt_password(password: str) -> str:
    """Encrypt password using Eastmoney's RSA public key.

    Args:
        password: Plain text password

    Returns:
        Base64 encoded encrypted password
    """
    public_key = serialization.load_pem_public_key(RSA_PUBLIC_KEY.encode("utf-8"))
    # Type cast to RSAPublicKey since we know it is one
    rsa_public_key: RSAPublicKey = public_key  # type: ignore[assignment]
    encrypted = rsa_public_key.encrypt(password.encode(), PKCS1v15())
    return base64.b64encode(encrypted).decode("utf-8")


class OrderType(Enum):
    """Order types for trading"""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order status types"""

    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Represents a trading order"""

    symbol: str
    order_type: OrderType
    quantity: float
    price: float
    order_id: str | None = None
    status: OrderStatus = OrderStatus.PENDING


class Position(TypedDict):
    """Represents a position in the account"""

    symbol: str
    quantity: float
    price: float


class AccountInfo(TypedDict):
    """Represents account information"""

    username: str
    account_balance: float
    positions: list[Position]


class MarketData(TypedDict):
    """Represents market data for a symbol"""

    symbol: str
    last_price: float
    bid_price: float
    ask_price: float
    volume: int
    timestamp: str


class LoginError(Exception):
    """Exception raised for login errors"""

    pass


class ValidateKeyError(Exception):
    """Exception raised for login errors"""

    pass


class TradingAgent:
    """Eastmoney Trading Agent

    This class provides methods for interacting with Eastmoney trading services,
    including login, placing orders, checking account status, and retrieving market data.
    """

    def __init__(self, username: str | None = None, password: str | None = None):
        """Initialize the trading agent

        Args:
            username: Eastmoney account username
            password: Eastmoney account password
        """
        self.username = username
        self.password = password
        self.is_logged_in = False
        self.account_info: AccountInfo | dict[str, Any] = {}
        self.logger = logger
        self.session = httpx.Client()
        self.identify_code: str | None = None
        self.random_code: float | None = None
        self.validate_key: str | None = None
        self._get_captcha()

    def _get_validate_key(self) -> None:
        """Get validate key from Eastmoney login page.

        Returns:
            Validate key string

        Raises:
            LoginError: If unable to retrieve validate key
        """
        # url = "https://jywg.18.cn/Login?el=1&clear=&returl=%2fTrade%2fBuy"
        url = "https://jywg.18.cn/Trade/Buy"
        # url = "https://jywg.18.cn/LogIn/ExitLogin?returl=%2fTrade%2fBuy"
        # url = "https://jywg.18.cn/Login?el=1&clear=&returl=%2fTrade%2fBuy"
        try:
            response = self.session.get(url, headers=BASE_HEADERS)
            response.raise_for_status()
            logger.info(response.text)

            match_result = re.findall(
                r'id="em_validatekey" type="hidden" value="(.*?)"', response.text
            )
            if match_result:
                self.validate_key = match_result[0].strip()
            else:
                raise ValidateKeyError("Unable to extract validate key from login page")
        except httpx.RequestError as e:
            raise ValidateKeyError(f"Failed to retrieve validate key: {e}")

    def _get_captcha(self) -> None:
        """Get random number and captcha code.

        Returns:
            Tuple of random number and captcha code

        Raises:
            LoginError: If unable to get captcha
        """
        try:
            cryptogen = SystemRandom()
            random_num = cryptogen.random()
            captcha_url = f"{YZM_URL}{random_num}"

            response = self.session.get(captcha_url, headers=BASE_HEADERS, timeout=60)
            response.raise_for_status()

            captcha_code: str = ocr.classification(response.content)

            if captcha_code:
                self.random_code = random_num
                self.identify_code = captcha_code
            else:
                raise LoginError("Failed to recognize captcha")
        except httpx.RequestError as e:
            raise LoginError(f"Failed to retrieve captcha: {e}")
        except Exception as e:
            raise LoginError(f"Failed to process captcha: {e}")

    def login(
        self,
        username: str | None = None,
        password: str | None = None,
        duration: int = 30,
    ) -> bool:
        """Login to Eastmoney account

        Args:
            username: Eastmoney account username (optional if provided in constructor)
            password: Eastmoney account password (optional if provided in constructor)
            duration: Eastmoney account login session duration in minutes (default: 30)

        Returns:
            bool: True if login successful, False otherwise

        Raises:
            LoginError: If login fails due to network or authentication issues
        """
        # Use provided credentials or fallback to instance variables
        login_username = username or self.username
        login_password = password or self.password

        if not login_username or not login_password:
            self.logger.error("Username and password are required for login")
            return False

        try:
            self.logger.info(f"Logging in user: {login_username}")

            # Prepare login request
            headers = BASE_HEADERS.copy()
            headers["X-Requested-With"] = "XMLHttpRequest"
            headers["Referer"] = (
                "https://jywg.18.cn/Login?el=1&clear=&returl=%2fTrade%2fBuy"
            )
            headers["Content-Type"] = "application/x-www-form-urlencoded"

            encrypted_password = encrypt_password(login_password.strip())

            data = {
                "userId": login_username.strip(),
                "password": encrypted_password,
                "randNumber": self.random_code,
                "identifyCode": self.identify_code,
                "duration": duration,
                "authCode": "",
                "type": "Z",
                "secInfo": "",
            }

            # Perform login
            login_response = self.session.post(
                f"{LOGIN_URL}{self.validate_key}", headers=headers, data=data
            )
            login_response.raise_for_status()

            # Check login result
            result = login_response.json()
            if result.get("Status") == 0:
                self.is_logged_in = True
                self.logger.info("Login successful")

                # Initialize account info (placeholder)
                self.account_info = {
                    "username": login_username,
                    "account_balance": 100000.0,
                    "positions": [],
                }
                self._get_validate_key()
                return True
            else:
                error_msg = result.get("Message", "Unknown error")
                self.logger.error(f"Login failed: {error_msg}")
                return False

        except LoginError as e:
            self.logger.error(f"Login error: {e}")
            return False
        except httpx.RequestError as e:
            self.logger.error(f"Network error during login: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {e}")
            return False

    def logout(self) -> None:
        """Logout from Eastmoney account"""
        self.is_logged_in = False
        self.account_info = {}
        self.validate_key = None
        self.logger.info("Logged out successfully")

    def get_account_info(self) -> AccountInfo | dict[str, Any]:
        """Get account information

        Returns:
            Dict containing account information
        """
        if not self.is_logged_in:
            self.logger.warning("User not logged in")
            return {}

        # TODO: Implement actual account info retrieval
        return self.account_info

    def place_order(
        self, symbol: str, order_type: OrderType, quantity: float, price: float
    ) -> str | None:
        """Place a trading order

        Args:
            symbol: Stock symbol
            order_type: Order type (BUY or SELL)
            quantity: Number of shares
            price: Order price

        Returns:
            Order ID if successful, None otherwise
        """
        if not self.is_logged_in:
            self.logger.error("User not logged in")
            return None

        self.logger.info(
            f"Placing {order_type.value} order for {symbol}: "
            f"{quantity} shares at {price}"
        )

        # TODO: Implement actual order placement with Eastmoney API
        # This is a placeholder implementation
        order_id = f"order_{symbol}_{order_type.value}_{quantity}_{price}"

        self.logger.info(f"Order placed successfully with ID: {order_id}")
        return order_id

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order

        Args:
            order_id: ID of the order to cancel

        Returns:
            True if cancellation successful, False otherwise
        """
        if not self.is_logged_in:
            self.logger.error("User not logged in")
            return False

        self.logger.info(f"Cancelling order: {order_id}")

        # TODO: Implement actual order cancellation with Eastmoney API
        # This is a placeholder implementation
        self.logger.info(f"Order {order_id} cancelled successfully")
        return True

    def get_order_status(self, order_id: str) -> OrderStatus | None:
        """Get the status of an order

        Args:
            order_id: ID of the order to check

        Returns:
            Order status or None if order not found
        """
        if not self.is_logged_in:
            self.logger.error("User not logged in")
            return None

        # TODO: Implement actual order status checking with Eastmoney API
        # This is a placeholder implementation
        self.logger.info(f"Checking status for order: {order_id}")
        return OrderStatus.FILLED

    def get_market_data(self, symbol: str) -> MarketData | dict[str, Any]:
        """Get market data for a symbol

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary containing market data
        """
        if not self.is_logged_in:
            self.logger.warning("User not logged in")
            return {}

        # TODO: Implement actual market data retrieval with Eastmoney API
        # This is a placeholder implementation
        self.logger.info(f"Retrieving market data for: {symbol}")
        return {
            "symbol": symbol,
            "last_price": 100.0,
            "bid_price": 99.9,
            "ask_price": 100.1,
            "volume": 1000000,
            "timestamp": "2025-08-23T10:00:00",
        }

    def get_positions(self) -> list[Position] | list[dict[str, Any]]:
        """Get current positions in the account

        Returns:
            List of position dictionaries
        """
        if not self.is_logged_in:
            self.logger.warning("User not logged in")
            return []

        # TODO: Implement actual positions retrieval with Eastmoney API
        return self.account_info.get("positions", [])
