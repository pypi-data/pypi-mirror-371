from annotated_types import Ge as Ge
from enum import Enum
from pydantic import BaseModel
from pydantic_core.core_schema import ValidationInfo as ValidationInfo
from typing import Annotated

class PaymentTypes(str, Enum):
    manual_payment_request = 'ManualPaymentRequest'
    external_card_payment_provider = 'ExternalCardPaymentProvider'
    crypto_ton = 'CryptoTON'
    xtr = 'XTR'
    life_pay = 'LifePay'
    yookassa = 'yookassa'
    tkassa = 'tkassa'
    cloud_payments = 'CloudPayments'

class DBProductInBasketV2(BaseModel):
    id: str
    unique_id: str
    extra_option_ids: list[str]

class MetaBaseModel(BaseModel):
    metadata: dict

class BaseProductResponseModel(MetaBaseModel):
    id: str
    name: str
    description: str
    price: float
    final_price: float
    currency: str
    preview_url: list[str]
    stock_qty: int
    orders_qty: int
    def set_final_price(cls, value, values: ValidationInfo): ...

class ProductsInBasket(BaseProductResponseModel):
    count_in_basket: int

class UserBasketResponseModel(BaseModel):
    id: str | None
    user_id: str | None
    order_id: str | None
    products_id: list[DBProductInBasketV2]
    coupon: str | None
    coupon_discount: Annotated[float, None]
    amount: Annotated[float, None]
    preview_url: str
    products: list[ProductsInBasket]

class ExtraFieldPayload(BaseModel):
    name: str
    value: str

class OrderDeliveryTypeModel(BaseModel):
    name: str
    address: str | None
    amount: float | None
    extra_fields_payload: list[ExtraFieldPayload] | None

class OrderResponseModel(UserBasketResponseModel):
    id: str
    delivery: OrderDeliveryTypeModel
    basket: UserBasketResponseModel
    user_id: str | None
    basket_id: str | None
    status: str | None
    order_number: str
    process_key: int | None
    coupon: str | None
    user_contact_number: str | None
