from _typeshed import Incomplete
from shops_payment_processing.logging_config import logger as logger
from shops_payment_processing.models.invoice import InvoiceWithPaymentLinkMessageModel as InvoiceWithPaymentLinkMessageModel
from shops_payment_processing.models.order import OrderResponseModel as OrderResponseModel, PaymentTypes as PaymentTypes
from shops_payment_processing.models.payment import PaymentMethodDBResponseModel as PaymentMethodDBResponseModel
from shops_payment_processing.models.shop import ShopDetailsModel as ShopDetailsModel
from shops_payment_processing.models.user import UserModel as UserModel
from shops_payment_processing.services.base import CreateInvoiceRequest as CreateInvoiceRequest
from shops_payment_processing.services.cloudpayments import CloudPaymentsAPI as CloudPaymentsAPI
from shops_payment_processing.services.life_pay import LifePayAPI as LifePayAPI
from shops_payment_processing.services.tkassa import TKassaAPI as TKassaAPI
from shops_payment_processing.services.yookassa import YooKassaAPI as YooKassaAPI
from shops_payment_processing.utils.link_generation import generate_web_app_order_link as generate_web_app_order_link

class InvoiceCreation:
    BASE_REDIRECT_URL: Incomplete
    BASE_CALLBACK_URL: Incomplete
    def __init__(self, base_redirect_url: str, base_callback_url: str) -> None: ...
    async def get_life_pay_sbp_payment_data(self, user: UserModel, order: OrderResponseModel, payment: PaymentMethodDBResponseModel, shop_details: ShopDetailsModel) -> InvoiceWithPaymentLinkMessageModel: ...
    async def get_yookassa_payment_data(self, user: UserModel, order: OrderResponseModel, payment: PaymentMethodDBResponseModel, shop_details: ShopDetailsModel) -> InvoiceWithPaymentLinkMessageModel: ...
    async def get_tkassa_payment_data(self, user: UserModel, order: OrderResponseModel, payment: PaymentMethodDBResponseModel, shop_details: ShopDetailsModel) -> InvoiceWithPaymentLinkMessageModel: ...
    async def get_cloudpayments_data(self, user: UserModel, order: OrderResponseModel, payment: PaymentMethodDBResponseModel, shop_details: ShopDetailsModel) -> InvoiceWithPaymentLinkMessageModel: ...
    async def get_invoice_data(self, payment_type: PaymentMethodDBResponseModel, user: UserModel, order: OrderResponseModel, shop_details: ShopDetailsModel) -> InvoiceWithPaymentLinkMessageModel | None: ...
