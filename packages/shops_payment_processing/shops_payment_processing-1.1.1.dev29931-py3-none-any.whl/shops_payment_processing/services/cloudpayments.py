import base64
from typing import Dict
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


class CloudPaymentsAPI(BasePaymentsAPI):
    def __init__(self, account_id: str, password: str, **kwargs):
        super().__init__(url="https://api.cloudpayments.ru", **kwargs)
        self.account_id = account_id
        self.password = password

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

    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for CloudPayments API."""
        auth_string = f"{self.account_id}:{self.password}"
        auth_bytes = auth_string.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')

        return {
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64_auth}"
        }

    async def create_invoice_legacy(
            self,
            shop_name: str,
            order: OrderResponseModel,
            redirect_url: str,
            receipt_email: str
    ):
        """Legacy method for backward compatibility."""
        customer_phone = order.user_contact_number if order.user_contact_number else None

        # Build receipt items
        receipt_items = await self._build_receipt_items(order)

        request_body = {
            "Amount": order.basket.amount,
            "Currency": "RUB",
            "Description": f"Заказ {order.order_number}",
            "RequireConfirmation": True,
            "SendEmail": False,
            "InvoiceId": order.order_number,
            "AccountId": order.user_id
        }

        if customer_phone:
            request_body["Phone"] = customer_phone
            request_body["SendSms"] = True

        headers = await self._get_auth_headers()

        logger.info(f"Creating Cloud Payment invoice for order {order.id}")
        response = await self._make_request(
            method="POST",
            url=f"{self.url}/orders/create",
            json=request_body,
            headers=headers,
        )
        return response

    async def create_invoice(self, req: CreateInvoiceRequest) -> CreateInvoiceResponse:
        """Create a payment invoice using the standardized DTO."""
        request_body = {
            "Amount": req.amount,
            "Currency": req.currency,
            "Description": req.description or f"Заказ {req.order_number}",
            "RequireConfirmation": True,
            "SendEmail": False,
            "InvoiceId": req.order_id,
            "AccountId": req.metadata.get("user_id") if req.metadata else None
        }

        if req.customer_phone:
            request_body["Phone"] = req.customer_phone
            request_body["SendSms"] = True

        headers = await self._get_auth_headers()

        logger.info(f"Creating Cloud Payment invoice for order {req.order_id}")
        response = await self._make_request(
            method="POST",
            url=f"{self.url}/orders/create",
            json=request_body,
            headers=headers,
        )
        return CreateInvoiceResponse(
            payment_id=response.get("Model", {}).get("Id", ""),
            payment_url=response.get("Model", {}).get("Url", ""),
            status=response.get("Model", {}).get("Status", ""),
            raw_response=response
        )

    async def get_payment_status(self, payment_id: str) -> PaymentStatusResponse:
        """Get the status of a payment."""
        headers = await self._get_auth_headers()

        response = await self._make_request(
            method="POST",
            url=f"{self.url}/orders/status",
            json={"Id": payment_id},
            headers=headers,
        )

        return PaymentStatusResponse(
            payment_id=payment_id,
            status=response.get("Status", "unknown"),
            amount=float(response.get("Amount", 0)) / 100,  # Convert from kopecks to rubles
            currency=response.get("Currency", "RUB"),
            paid=response.get("Status") == "Completed",
            refunded=False,  # CloudPayments doesn't provide this directly
            created_at=response.get("CreatedDate"),
            raw_response=response
        )

    async def refund(self, req: RefundRequest) -> RefundResponse:
        """Refund a payment."""
        headers = await self._get_auth_headers()

        request_body = {
            "Id": req.payment_id,
            "Amount": req.amount
        }

        response = await self._make_request(
            method="POST",
            url=f"{self.url}/orders/refund",
            json=request_body,
            headers=headers,
        )

        return RefundResponse(
            refund_id=response.get("RefundId", ""),
            payment_id=req.payment_id,
            status="completed" if response.get("Success") else "failed",
            amount=req.amount or 0,
            currency="RUB",
            raw_response=response
        )
