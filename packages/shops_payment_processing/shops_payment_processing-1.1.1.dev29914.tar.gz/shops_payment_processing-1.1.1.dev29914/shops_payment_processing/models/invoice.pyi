from pydantic import BaseModel

class InvoiceBaseModel(BaseModel):
    chat_id: int
    order_id: str
    order_number: str
    payload: str
    amount: float
    currency: str
    payment_address: str
    payment_timeout: int | None

class InvoiceWithPaymentLinkMessageModel(InvoiceBaseModel):
    payment_link: str
