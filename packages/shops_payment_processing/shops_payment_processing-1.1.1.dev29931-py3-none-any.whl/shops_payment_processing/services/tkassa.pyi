from _typeshed import Incomplete
from shops_payment_processing.logging_config import logger as logger
from shops_payment_processing.models.order import OrderResponseModel as OrderResponseModel

class TKassaAPI:
    terminal_id: Incomplete
    terminal_password: Incomplete
    url: str
    def __init__(self, terminal_id: str, terminal_password: str) -> None: ...
    async def create_sbp_invoice(self, shop_name: str, order: OrderResponseModel, redirect_url: str, receipt_email: str): ...
