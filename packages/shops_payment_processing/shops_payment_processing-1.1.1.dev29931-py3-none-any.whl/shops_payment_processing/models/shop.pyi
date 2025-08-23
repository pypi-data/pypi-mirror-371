from pydantic import BaseModel

class ShopDetailsModel(BaseModel):
    shop_id: str
    shop_name: str
    friendly_name: str
    shop_language: str
    contact_phone: str | None
    contact_email: str
