from pydantic import BaseModel
from shops_payment_processing.models.order import PaymentTypes as PaymentTypes

class Metadata(BaseModel):
    key: str
    value: list[str]

class PaymentMethodModel(BaseModel):
    name: str
    type: PaymentTypes
    payment_data: str | None
    meta: list[Metadata] | None
    class Config:
        use_enum_values: bool

class PaymentMethodDBResponseModel(PaymentMethodModel):
    id: str
