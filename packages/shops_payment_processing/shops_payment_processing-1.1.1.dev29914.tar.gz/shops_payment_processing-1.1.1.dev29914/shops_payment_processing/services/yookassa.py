import httpx
import random
from typing import Dict, Any, Optional

from fastapi import HTTPException
from shops_payment_processing.logging_config import logger
from shops_payment_processing.models.order import OrderResponseModel
from shops_payment_processing.services.base import (
    BasePaymentsAPI,
    CreateInvoiceRequest,
    CreateInvoiceResponse,
    PaymentStatusResponse,
    RefundRequest,
    RefundResponse,
)

class YooKassaAPI(BasePaymentsAPI):
    def __init__(self, account_id: str, secret_key: str, **kwargs):
        super().__init__(url="https://api.yookassa.ru/v3", **kwargs)
        self.account_id = account_id
        self.secret_key = secret_key

    async def _build_receipt_items(self, order: OrderResponseModel, currency: str = "RUB") -> list:
        """Build receipt items from order products."""
        receipt_items = []
        for product in order.basket.products:
            item = {
                "description": product.name,
                "quantity": f"{product.count_in_basket:.2f}",
                "amount": {
                    "value": f"{round(product.final_price):.2f}",
                    "currency": currency,
                },
                "vat_code": "2",  # Replace with the actual VAT code as needed
                "payment_mode": "full_payment",  # Adjust if payment mode varies
                "payment_subject": "commodity",  # Adjust if payment subject varies
                "country_of_origin_code": "RU"  # Assuming this exists
            }
            receipt_items.append(item)

        if order.delivery.amount and order.delivery.amount > 0:
            item = {
                "description": order.delivery.name,
                "quantity": "1",
                "amount": {
                    "value": f"{round(order.delivery.amount):.2f}",
                    "currency": currency,
                },
                "vat_code": "2",  # Replace with the actual VAT code as needed
                "payment_mode": "full_payment",  # Adjust if payment mode varies
                "payment_subject": "commodity",  # Adjust if payment subject varies
                "country_of_origin_code": "RU"  # Assuming this exists
            }
            receipt_items.append(item)

        return receipt_items

    async def create_sbp_invoice_legacy(self, shop_name: str, order: OrderResponseModel, redirect_url: str, receipt_email: str):
        """Legacy method for backward compatibility."""
        value = f"{round(order.basket.amount, 2):.2f}"
        currency = "RUB"
        customer_phone = order.user_contact_number.replace("+", "") if order.user_contact_number else None

        # Build receipt items
        receipt_items = await self._build_receipt_items(order, currency)

        # Build the request payload
        request_body = {
            "amount": {
                "value": value,
                "currency": currency,
            },
            "confirmation": {
                "type": "redirect",
                "return_url": redirect_url
            },
            "capture": True,
            "description": f"Заказ {order.order_number}",
            "metadata": {
                "orderId": order.id,
                "orderNumber": order.order_number
            },
            "receipt": {
                "items": receipt_items
            }
        }

        # Add customer phone if available
        if customer_phone:
            request_body["receipt"]["customer"] = {"phone": customer_phone}  # type: ignore
        else:
            request_body["receipt"]["customer"] = {"email": receipt_email}  # type: ignore

        # Prepare authentication
        auth = httpx.BasicAuth(self.account_id, self.secret_key)

        # Set the Idempotence-Key header using the order ID
        headers = {
            "Idempotence-Key": f"{str(order.id)}:{random.randint(1000, 9999)}",
            "Content-Type": "application/json"
        }

        logger.info(f"Creating YooKassa payment for order {order.id}")
        response = await self._make_request(
            method="POST",
            url=f"{self.url}/payments",
            auth=auth,
            json=request_body,
            headers=headers
        )

        return response

    async def create_invoice(self, req: CreateInvoiceRequest) -> CreateInvoiceResponse:
        """Create a payment invoice using the standardized DTO."""
        value = f"{round(req.amount, 2):.2f}"
        currency = req.currency

        # Build the request payload
        request_body = {
            "amount": {
                "value": value,
                "currency": currency,
            },
            "confirmation": {
                "type": "redirect",
                "return_url": req.redirect_url or ""
            },
            "capture": True,
            "description": req.description or f"Заказ {req.order_number}",
            "metadata": req.metadata or {
                "orderId": req.order_id,
                "orderNumber": req.order_number
            }
        }

        # Add receipt if items are provided
        if req.items:
            request_body["receipt"] = {
                "items": req.items
            }

            # Add customer info
            if req.customer_phone:
                request_body["receipt"]["customer"] = {"phone": req.customer_phone.replace("+", "")}  # type: ignore
            elif req.customer_email:
                request_body["receipt"]["customer"] = {"email": req.customer_email}  # type: ignore

        # Prepare authentication
        auth = httpx.BasicAuth(self.account_id, self.secret_key)

        # Set the Idempotence-Key header using the order ID
        headers = {
            "Idempotence-Key": f"{req.order_id}:{random.randint(1000, 9999)}",
            "Content-Type": "application/json"
        }

        logger.info(f"Creating YooKassa payment for order {req.order_id}")
        response = await self._make_request(
            method="POST",
            url=f"{self.url}/payments",
            auth=auth,
            json=request_body,
            headers=headers
        )

        return CreateInvoiceResponse(
            payment_id=response.get("id", ""),
            payment_url=response.get("confirmation", {}).get("confirmation_url", ""),
            status=response.get("status", "pending"),
            raw_response=response
        )

    async def get_payment_status(self, payment_id: str) -> PaymentStatusResponse:
        """Get the status of a payment."""
        # Prepare authentication
        auth = httpx.BasicAuth(self.account_id, self.secret_key)

        # Set the Idempotence-Key header
        headers = {
            "Idempotence-Key": f"status_{payment_id}:{random.randint(1000, 9999)}",
            "Content-Type": "application/json"
        }

        response = await self._make_request(
            method="GET",
            url=f"{self.url}/payments/{payment_id}",
            auth=auth,
            headers=headers
        )

        # Map YooKassa status to our standard status
        status_mapping = {
            "pending": "pending",
            "waiting_for_capture": "authorized",
            "succeeded": "completed",
            "canceled": "cancelled"
        }

        status = status_mapping.get(response.get("status", ""), "unknown")

        return PaymentStatusResponse(
            payment_id=payment_id,
            status=status,
            amount=float(response.get("amount", {}).get("value", 0)),
            currency=response.get("amount", {}).get("currency", "RUB"),
            paid=status == "completed",
            refunded=response.get("refunded_amount") is not None,
            created_at=response.get("created_at"),
            raw_response=response
        )

    async def refund(self, req: RefundRequest) -> RefundResponse:
        """Refund a payment."""
        # Prepare the refund request body
        request_body = {
            "payment_id": req.payment_id,
            "description": req.reason or "Customer request"
        }

        # Add amount if specified
        if req.amount is not None:
            request_body["amount"] = { # type: ignore
                "value": f"{round(req.amount, 2):.2f}",
                "currency": "RUB"
            }

        # Prepare authentication
        auth = httpx.BasicAuth(self.account_id, self.secret_key)

        # Set the Idempotence-Key header
        headers = {
            "Idempotence-Key": f"refund_{req.payment_id}:{random.randint(1000, 9999)}",
            "Content-Type": "application/json"
        }

        response = await self._make_request(
            method="POST",
            url=f"{self.url}/refunds",
            auth=auth,
            json=request_body,
            headers=headers
        )

        return RefundResponse(
            refund_id=response.get("id", ""),
            payment_id=req.payment_id,
            status=response.get("status", "unknown"),
            amount=float(response.get("amount", {}).get("value", 0)),
            currency=response.get("amount", {}).get("currency", "RUB"),
            raw_response=response
        )
