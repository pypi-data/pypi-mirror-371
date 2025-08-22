import httpx
from typing import Dict, Any, Optional

from shops_payment_processing.logging_config import logger
from shops_payment_processing.models.order import UserBasketResponseModel
from shops_payment_processing.models.order import OrderResponseModel
from shops_payment_processing.services.base import (
    BasePaymentsAPI,
    CreateInvoiceRequest,
    CreateInvoiceResponse,
    PaymentStatusResponse,
    RefundRequest,
    RefundResponse,
)

def configure_description(basket: UserBasketResponseModel):
    """
    Configure description for sbp order in format: "1. Капучино 150мл x 1.0 = 3.00"
    """
    description = ""
    count = 1
    for product in basket.products:
        description += \
            f"{count}. {product.name} x {round(product.count_in_basket, 1)} = {round(product.count_in_basket * product.final_price, 2)}\n"
        count += 1
    return description


class LifePayAPI(BasePaymentsAPI):
    def __init__(self, callback_base_url: str, **kwargs):
        super().__init__(url='https://api.life-pay.ru/v1', **kwargs)
        self.CALLBACK_BASE_URL = callback_base_url
        self.login = kwargs.get("login", "")
        self.api_key = kwargs.get("api_key", "")

    async def create_sbp_invoice_legacy(self,
                                 shop_name: str,
                                 login: str,
                                 api_key: str,
                                 order: OrderResponseModel):
        """Legacy method for backward compatibility."""
        extra_data = {}
        if order.user_contact_number:
            extra_data['customer_phone'] = order.user_contact_number.replace("+", "")

        payload = {
            "apikey": api_key,
            "login": login,
            "amount": order.basket.amount,
            "description": configure_description(order.basket),
            "currency": "RUB",
            "callback_url": f"{self.CALLBACK_BASE_URL}/life-pay/{shop_name}/events/?order_id={order.id}",
            **extra_data
        }

        logger.debug(f"Creating SBP invoice for order {order.id} {login} {api_key[:3]}")
        response = await self._make_request(
            method="POST",
            url=f"{self.url}/bill",
            json=payload
        )

        return response

    async def create_invoice(self, req: CreateInvoiceRequest) -> CreateInvoiceResponse:
        """Create a payment invoice using the standardized DTO."""
        extra_data = {}
        if req.customer_phone:
            extra_data['customer_phone'] = req.customer_phone.replace("+", "")
        if req.customer_email:
            extra_data['customer_email'] = req.customer_email

        # Use stored credentials or from metadata
        login = self.login
        api_key = self.api_key

        if req.metadata:
            login = req.metadata.get("login", login)
            api_key = req.metadata.get("api_key", api_key)

        if not login or not api_key:
            raise ValueError("Login and API key are required for LifePay")

        payload = {
            "apikey": api_key,
            "login": login,
            "amount": req.amount,
            "description": req.description or f"Заказ {req.order_number}",
            "currency": req.currency,
            "callback_url": f"{self.CALLBACK_BASE_URL}/life-pay/{req.shop_name}/events/?order_id={req.order_id}",
            **extra_data
        }

        logger.debug(f"Creating SBP invoice for order {req.order_id}")
        response = await self._make_request(
            method="POST",
            url=f"{self.url}/bill",
            json=payload
        )

        return CreateInvoiceResponse(
            payment_id=response.get("id", ""),
            payment_url=response.get("payment_url", ""),
            status="pending",
            raw_response=response
        )

    async def get_payment_status(self, payment_id: str) -> PaymentStatusResponse:
        """Get the status of a payment."""
        if not self.login or not self.api_key:
            raise ValueError("Login and API key are required for LifePay")

        payload = {
            "apikey": self.api_key,
            "login": self.login,
            "id": payment_id
        }

        response = await self._make_request(
            method="POST",
            url=f"{self.url}/bill/status",
            json=payload
        )

        # Map LifePay status to our standard status
        status_mapping = {
            "waiting": "pending",
            "paid": "completed",
            "expired": "expired",
            "canceled": "cancelled"
        }

        status = status_mapping.get(response.get("status", ""), "unknown")

        return PaymentStatusResponse(
            payment_id=payment_id,
            status=status,
            amount=float(response.get("amount", 0)),
            currency=response.get("currency", "RUB"),
            paid=status == "completed",
            refunded=False,  # LifePay doesn't provide this directly
            created_at=response.get("created_at"),
            raw_response=response
        )

    async def refund(self, req: RefundRequest) -> RefundResponse:
        """Refund a payment."""
        if not self.login or not self.api_key:
            raise ValueError("Login and API key are required for LifePay")

        payload = {
            "apikey": self.api_key,
            "login": self.login,
            "id": req.payment_id,
            "amount": req.amount,  # If None, LifePay will do a full refund
            "reason": req.reason or "Customer request"
        }

        response = await self._make_request(
            method="POST",
            url=f"{self.url}/bill/refund",
            json=payload
        )

        return RefundResponse(
            refund_id=response.get("refund_id", ""),
            payment_id=req.payment_id,
            status="completed" if response.get("success") else "failed",
            amount=req.amount or float(response.get("amount", 0)),
            currency="RUB",
            raw_response=response
        )
