"""Eastmoney Trading Library

Unofficial library for interacting with Eastmoney trading services.
"""

from .trading import Order, OrderStatus, OrderType, TradingAgent

__all__ = ["TradingAgent", "Order", "OrderType", "OrderStatus"]
