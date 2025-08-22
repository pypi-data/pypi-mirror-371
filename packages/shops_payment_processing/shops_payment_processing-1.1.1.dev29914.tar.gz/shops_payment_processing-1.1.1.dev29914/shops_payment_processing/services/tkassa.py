import hashlib
import httpx
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


class TKassaAPI(BasePaymentsAPI):
    def __init__(self, terminal_id: str, terminal_password: str, **kwargs):
        super().__init__(url="https://securepay.tinkoff.ru/v2", **kwargs)
        self.terminal_id = terminal_id
        self.terminal_password = terminal_password


    async def _build_receipt_items(self, order: OrderResponseModel) -> list:
        """Build receipt items from order products."""
        receipt_items = []
        for product in order.basket.products:
            item = {
                "Name": product.name,
                "Price": int(product.final_price * 100),
                "Quantity": product.count_in_basket,
                "Amount": int(product.final_price * 100) * product.count_in_basket,
                "PaymentMethod": "full_payment",  # Adjust if payment method varies
                "PaymentObject": "commodity",  # Adjust if payment object varies
                "Tax": "none"  # Replace with actual tax if needed
            }
            receipt_items.append(item)

        if order.delivery.amount and order.delivery.amount > 0:
            item = {
                "Name": order.delivery.name,
                "Price": int(order.delivery.amount * 100),
                "Quantity": 1,
                "Amount": int(order.delivery.amount * 100),
                "PaymentMethod": "full_payment",  # Adjust if payment method varies
                "PaymentObject": "commodity",  # Adjust if payment object varies
                "Tax": "none"  # Replace with actual tax if needed
            }
            receipt_items.append(item)

        if order.basket.coupon_discount and order.basket.coupon_discount != 0:
            item = {
                "Name": "Скидка",
                "Price": int(order.basket.coupon_discount * 100) * -1,
                "Quantity": 1,
                "Amount": int(order.basket.coupon_discount * 100) * -1,
                "PaymentMethod": "full_payment",  # Adjust if payment method varies
                "PaymentObject": "commodity",  # Adjust if payment object varies
                "Tax": "none"  # Replace with actual tax if needed
            }
            receipt_items.append(item)

        return receipt_items

    async def _generate_token(self, params: Dict[str, Any]) -> str:
        """Generate token for TKassa API."""
        # Add password to params
        params_with_password = params.copy()
        params_with_password["Password"] = self.terminal_password

        # Sort params
        sorted_params = sorted(params_with_password.items(), key=lambda x: x[0])

        # Build token source string
        concatenated_values = ''.join(str(value) for key, value in sorted_params)

        # Build token
        return hashlib.sha256(concatenated_values.encode('utf-8')).hexdigest()

    async def create_sbp_invoice_legacy(self, shop_name: str, order: OrderResponseModel, redirect_url: str, receipt_email: str):
        """Legacy method for backward compatibility."""
        value = int(order.basket.amount * 100)
        customer_phone = order.user_contact_number if order.user_contact_number else None
        order_id = order.id

        # Build receipt items
        receipt_items = await self._build_receipt_items(order)

        # Prepare params for token generation
        token_params = {
            "TerminalKey": self.terminal_id,
            "Amount": str(value),
            "OrderId": order_id,
            "Description": f"Заказ {order.order_number}"
        }

        # Generate token
        token = await self._generate_token(token_params)

        request_body = {
            "TerminalKey": self.terminal_id,
            "Amount": value,
            "OrderId": order_id,
            "Description": f"Заказ {order.order_number}",
            "Token": token,
            "DATA": {
                "orderId": order.id,
                "orderNumber": order.order_number
            },
            "Receipt": {
                "Items": receipt_items,
                "Taxation": "osn"  # Replace with actual taxation if needed
            }
        }

        if customer_phone:
            request_body["Receipt"]["Phone"] = customer_phone  # type: ignore
        else:
            request_body["Receipt"]["Email"] = receipt_email  # type: ignore

        headers = {
            "Content-Type": "application/json"
        }

        logger.info(f"Creating Tkassa payment for order {order.id}")
        response = await self._make_request(
            method="POST",
            url=f"{self.url}/Init",
            json=request_body,
            headers=headers
        )

        return response

    async def create_invoice(self, req: CreateInvoiceRequest) -> CreateInvoiceResponse:
        """Create a payment invoice using the standardized DTO."""
        value = int(req.amount * 100)

        # Prepare params for token generation
        token_params = {
            "TerminalKey": self.terminal_id,
            "Amount": str(value),
            "OrderId": req.order_id,
            "Description": req.description or f"Заказ {req.order_number}"
        }

        # Generate token
        token = await self._generate_token(token_params)

        request_body = {
            "TerminalKey": self.terminal_id,
            "Amount": value,
            "OrderId": req.order_id,
            "Description": req.description or f"Заказ {req.order_number}",
            "Token": token,
            "DATA": {
                "orderId": req.order_id,
                "orderNumber": req.order_number
            }
        }

        # Add receipt if items are provided
        if req.items:
            request_body["Receipt"] = {
                "Items": req.items,
                "Taxation": "osn"  # Replace with actual taxation if needed
            }

            if req.customer_phone:
                request_body["Receipt"]["Phone"] = req.customer_phone  # type: ignore
            elif req.customer_email:
                request_body["Receipt"]["Email"] = req.customer_email  # type: ignore

        headers = {
            "Content-Type": "application/json"
        }

        logger.info(f"Creating Tkassa payment for order {req.order_id}")
        response = await self._make_request(
            method="POST",
            url=f"{self.url}/Init",
            json=request_body,
            headers=headers
        )

        return CreateInvoiceResponse(
            payment_id=response.get("PaymentId", ""),
            payment_url=response.get("PaymentURL", ""),
            status="pending",
            raw_response=response
        )

    async def get_payment_status(self, payment_id: str) -> PaymentStatusResponse:
        """Get the status of a payment."""
        # Prepare params for token generation
        token_params = {
            "TerminalKey": self.terminal_id,
            "PaymentId": payment_id
        }

        # Generate token
        token = await self._generate_token(token_params)

        request_body = {
            "TerminalKey": self.terminal_id,
            "PaymentId": payment_id,
            "Token": token
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = await self._make_request(
            method="POST",
            url=f"{self.url}/GetState",
            json=request_body,
            headers=headers
        )

        # Map TKassa status to our standard status
        status_mapping = {
            "NEW": "pending",
            "FORM_SHOWED": "pending",
            "AUTHORIZED": "authorized",
            "CONFIRMED": "completed",
            "REVERSED": "cancelled",
            "REFUNDED": "refunded",
            "PARTIAL_REFUNDED": "partially_refunded",
            "REJECTED": "failed"
        }

        status = status_mapping.get(response.get("Status", ""), "unknown")

        return PaymentStatusResponse(
            payment_id=payment_id,
            status=status,
            amount=float(response.get("Amount", 0)) / 100,  # Convert from kopecks to rubles
            currency="RUB",
            paid=status in ["completed", "authorized"],
            refunded=status in ["refunded", "partially_refunded"],
            created_at=None,  # TKassa doesn't provide this directly
            raw_response=response
        )

    async def refund(self, req: RefundRequest) -> RefundResponse:
        """Refund a payment."""
        amount = int((req.amount or 0) * 100)  # Convert to kopecks

        # Prepare params for token generation
        token_params = {
            "TerminalKey": self.terminal_id,
            "PaymentId": req.payment_id
        }

        if amount > 0:
            token_params["Amount"] = str(amount)

        # Generate token
        token = await self._generate_token(token_params)

        request_body = {
            "TerminalKey": self.terminal_id,
            "PaymentId": req.payment_id,
            "Token": token
        }

        if amount > 0:
            request_body["Amount"] = amount # type: ignore

        headers = {
            "Content-Type": "application/json"
        }

        response = await self._make_request(
            method="POST",
            url=f"{self.url}/Cancel",
            json=request_body,
            headers=headers
        )

        return RefundResponse(
            refund_id=response.get("PaymentId", ""),  # TKassa uses the same ID
            payment_id=req.payment_id,
            status="completed" if response.get("Success") else "failed",
            amount=float(response.get("Amount", amount)) / 100,  # Convert from kopecks to rubles
            currency="RUB",
            raw_response=response
        )
