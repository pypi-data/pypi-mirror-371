"""Tests for the Eastmoney Trading Agent"""

import os
from unittest.mock import MagicMock, patch

from emta.trading import OrderStatus, OrderType, TradingAgent


class TestTradingAgent:
    """Tests for the TradingAgent class"""

    def test_init(self):
        """Test TradingAgent initialization"""
        agent = TradingAgent()
        assert agent.username is None
        assert agent.password is None
        assert agent.is_logged_in is False
        assert agent.validate_key is None

    def test_init_with_credentials(self):
        """Test TradingAgent initialization with credentials"""
        agent = TradingAgent("test_user", "test_pass")
        assert agent.username == "test_user"
        assert agent.password == "test_pass"

    def test_login(self):
        agent = TradingAgent(
            os.getenv("EM_USERNAME", ""),
            os.getenv("EM_PASSWORD", ""),
        )
        result = agent.login()
        assert result is True
        assert len("79e54fcd-2306-46d0-981f-e3f5d3439173") == len(
            agent.validate_key or ""
        )

    @patch("emta.trading.TradingAgent._get_validate_key")
    @patch("emta.trading.TradingAgent._get_captcha")
    @patch("emta.trading.httpx.Client.post")
    def test_login_success(self, mock_post, mock_captcha, mock_validate_key):
        """Test successful login"""
        # Mock the validate key
        mock_validate_key.return_value = (
            None  # _get_validate_key sets self.validate_key directly
        )

        # Mock the captcha
        mock_captcha.return_value = (0.123456, "1234")

        # Mock the login response
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": 0, "Message": "Success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        agent = TradingAgent("test_user", "test_pass")
        # Set validate_key directly since _get_validate_key sets it internally
        agent.validate_key = "test_validate_key"
        result = agent.login()

        assert result is True
        assert agent.is_logged_in is True
        assert agent.validate_key == "test_validate_key"
        assert "account_balance" in agent.account_info

    def test_login_failure_missing_credentials(self):
        """Test login failure when credentials are missing"""
        agent = TradingAgent()
        result = agent.login()
        assert result is False
        assert agent.is_logged_in is False

    @patch("emta.trading.TradingAgent._get_validate_key")
    @patch("emta.trading.TradingAgent._get_captcha")
    @patch("emta.trading.httpx.Client.post")
    def test_login_failure_api_error(self, mock_post, mock_captcha, mock_validate_key):
        """Test login failure due to API error"""
        # Mock the validate key
        mock_validate_key.return_value = "test_validate_key"

        # Mock the captcha
        mock_captcha.return_value = (0.123456, "1234")

        # Mock the login response with error
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Status": -1,
            "Message": "Invalid credentials",
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        agent = TradingAgent("test_user", "test_pass")
        result = agent.login()

        assert result is False
        assert agent.is_logged_in is False

    @patch("emta.trading.TradingAgent._get_validate_key")
    @patch("emta.trading.TradingAgent._get_captcha")
    @patch("emta.trading.httpx.Client.post")
    def test_logout(self, mock_post, mock_captcha, mock_validate_key):
        """Test logout functionality"""
        # Mock the validate key
        mock_validate_key.return_value = "test_validate_key"

        # Mock the captcha
        mock_captcha.return_value = (0.123456, "1234")

        # Mock the login response
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": 0, "Message": "Success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        agent = TradingAgent("test_user", "test_pass")
        agent.login()
        assert agent.is_logged_in is True

        agent.logout()
        assert agent.is_logged_in is False
        assert agent.validate_key is None
        assert agent.account_info == {}
        assert agent.validate_key is None

    @patch("emta.trading.TradingAgent._get_validate_key")
    @patch("emta.trading.TradingAgent._get_captcha")
    @patch("emta.trading.httpx.Client.post")
    def test_get_account_info(self, mock_post, mock_captcha, mock_validate_key):
        """Test getting account information"""
        # Mock the validate key
        mock_validate_key.return_value = "test_validate_key"

        # Mock the captcha
        mock_captcha.return_value = (0.123456, "1234")

        # Mock the login response
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": 0, "Message": "Success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        agent = TradingAgent("test_user", "test_pass")
        agent.login()

        account_info = agent.get_account_info()
        assert isinstance(account_info, dict)
        assert "username" in account_info
        assert "account_balance" in account_info

    def test_get_account_info_not_logged_in(self):
        """Test getting account info when not logged in"""
        agent = TradingAgent()
        account_info = agent.get_account_info()
        assert account_info == {}

    @patch("emta.trading.TradingAgent._get_validate_key")
    @patch("emta.trading.TradingAgent._get_captcha")
    @patch("emta.trading.httpx.Client.post")
    def test_place_order(self, mock_post, mock_captcha, mock_validate_key):
        """Test placing an order"""
        # Mock the validate key
        mock_validate_key.return_value = "test_validate_key"

        # Mock the captcha
        mock_captcha.return_value = (0.123456, "1234")

        # Mock the login response
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": 0, "Message": "Success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        agent = TradingAgent("test_user", "test_pass")
        agent.login()

        order_id = agent.place_order("SH600000", OrderType.BUY, 100, 12.5)
        assert order_id is not None
        assert isinstance(order_id, str)

    def test_place_order_not_logged_in(self):
        """Test placing an order when not logged in"""
        agent = TradingAgent()
        order_id = agent.place_order("SH600000", OrderType.BUY, 100, 12.5)
        assert order_id is None

    @patch("emta.trading.TradingAgent._get_validate_key")
    @patch("emta.trading.TradingAgent._get_captcha")
    @patch("emta.trading.httpx.Client.post")
    def test_cancel_order(self, mock_post, mock_captcha, mock_validate_key):
        """Test cancelling an order"""
        # Mock the validate key
        mock_validate_key.return_value = "test_validate_key"

        # Mock the captcha
        mock_captcha.return_value = (0.123456, "1234")

        # Mock the login response
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": 0, "Message": "Success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        agent = TradingAgent("test_user", "test_pass")
        agent.login()

        result = agent.cancel_order("test_order_id")
        assert result is True

    def test_cancel_order_not_logged_in(self):
        """Test cancelling an order when not logged in"""
        agent = TradingAgent()
        result = agent.cancel_order("test_order_id")
        assert result is False

    @patch("emta.trading.TradingAgent._get_validate_key")
    @patch("emta.trading.TradingAgent._get_captcha")
    @patch("emta.trading.httpx.Client.post")
    def test_get_order_status(self, mock_post, mock_captcha, mock_validate_key):
        """Test getting order status"""
        # Mock the validate key
        mock_validate_key.return_value = "test_validate_key"

        # Mock the captcha
        mock_captcha.return_value = (0.123456, "1234")

        # Mock the login response
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": 0, "Message": "Success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        agent = TradingAgent("test_user", "test_pass")
        agent.login()

        status = agent.get_order_status("test_order_id")
        assert status is not None
        assert isinstance(status, OrderStatus)

    def test_get_order_status_not_logged_in(self):
        """Test getting order status when not logged in"""
        agent = TradingAgent()
        status = agent.get_order_status("test_order_id")
        assert status is None

    @patch("emta.trading.TradingAgent._get_validate_key")
    @patch("emta.trading.TradingAgent._get_captcha")
    @patch("emta.trading.httpx.Client.post")
    def test_get_market_data(self, mock_post, mock_captcha, mock_validate_key):
        """Test getting market data"""
        # Mock the validate key
        mock_validate_key.return_value = "test_validate_key"

        # Mock the captcha
        mock_captcha.return_value = (0.123456, "1234")

        # Mock the login response
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": 0, "Message": "Success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        agent = TradingAgent("test_user", "test_pass")
        agent.login()

        market_data = agent.get_market_data("SH600000")
        assert isinstance(market_data, dict)
        assert "symbol" in market_data
        assert "last_price" in market_data

    def test_get_market_data_not_logged_in(self):
        """Test getting market data when not logged in"""
        agent = TradingAgent()
        market_data = agent.get_market_data("SH600000")
        assert market_data == {}

    @patch("emta.trading.TradingAgent._get_validate_key")
    @patch("emta.trading.TradingAgent._get_captcha")
    @patch("emta.trading.httpx.Client.post")
    def test_get_positions(self, mock_post, mock_captcha, mock_validate_key):
        """Test getting positions"""
        # Mock the validate key
        mock_validate_key.return_value = "test_validate_key"

        # Mock the captcha
        mock_captcha.return_value = (0.123456, "1234")

        # Mock the login response
        mock_response = MagicMock()
        mock_response.json.return_value = {"Status": 0, "Message": "Success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        agent = TradingAgent("test_user", "test_pass")
        agent.login()

        positions = agent.get_positions()
        assert isinstance(positions, list)

    def test_get_positions_not_logged_in(self):
        """Test getting positions when not logged in"""
        agent = TradingAgent()
        positions = agent.get_positions()
        assert positions == []
