from _typeshed import Incomplete
from shops_payment_processing.logging_config import logger as logger
from shops_payment_processing.models.order import OrderResponseModel as OrderResponseModel

class YooKassaAPI:
    account_id: Incomplete
    secret_key: Incomplete
    url: str
    def __init__(self, account_id: str, secret_key: str) -> None: ...
    async def create_sbp_invoice(self, shop_name: str, order: OrderResponseModel, redirect_url: str, receipt_email: str): ...
