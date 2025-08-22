import abc
import dataclasses
import httpx
import time
from typing import Any, Dict, Optional, Union

from fastapi import HTTPException
from shops_payment_processing.logging_config import logger


@dataclasses.dataclass
class CreateInvoiceRequest:
    """Data Transfer Object for invoice creation request."""
    shop_name: str
    order_id: str
    order_number: str
    amount: float
    currency: str = "RUB"
    description: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    redirect_url: Optional[str] = None
    items: Optional[list] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclasses.dataclass
class CreateInvoiceResponse:
    """Data Transfer Object for invoice creation response."""
    payment_id: str
    payment_url: Optional[str] = None
    status: str = "pending"
    raw_response: Optional[Dict[str, Any]] = None


@dataclasses.dataclass
class PaymentStatusResponse:
    """Data Transfer Object for payment status response."""
    payment_id: str
    status: str
    amount: float
    currency: str = "RUB"
    paid: bool = False
    refunded: bool = False
    created_at: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclasses.dataclass
class RefundRequest:
    """Data Transfer Object for refund request."""
    payment_id: str
    amount: Optional[float] = None  # If None, full refund
    reason: Optional[str] = None


@dataclasses.dataclass
class RefundResponse:
    """Data Transfer Object for refund response."""
    refund_id: str
    payment_id: str
    status: str
    amount: float
    currency: str = "RUB"
    raw_response: Optional[Dict[str, Any]] = None


class BasePaymentsAPI(abc.ABC):
    """Abstract base class for payment API implementations."""
    
    def __init__(self, **kwargs):
        """Initialize the payment API with configuration."""
        self.url = kwargs.get("url", "")
        self.timeout = kwargs.get("timeout", 30)
        self.max_retries = kwargs.get("max_retries", 3)
        self.retry_delay = kwargs.get("retry_delay", 1)
    
    async def _make_request(
        self, 
        method: str, 
        url: str, 
        headers: Optional[Dict[str, str]] = None, 
        json: Optional[Dict[str, Any]] = None,
        auth: Optional[httpx.Auth] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with retries and error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: HTTP headers
            json: JSON payload
            auth: Authentication
            **kwargs: Additional arguments for httpx
            
        Returns:
            Response JSON
            
        Raises:
            HTTPException: If the request fails after retries
        """
        headers = headers or {}
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
            
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    logger.info(f"Making {method} request to {url}")
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=json,
                        auth=auth,
                        **kwargs
                    )
                    
                    if response.status_code >= 200 and response.status_code < 300:
                        return response.json()
                    
                    logger.warning(f"Request failed with status {response.status_code}: {response.text}")
                    last_error = HTTPException(status_code=response.status_code, detail=response.text)
                    
            except Exception as e:
                logger.warning(f"Request failed with error: {str(e)}")
                last_error = HTTPException(status_code=500, detail=str(e))
                
            retries += 1
            if retries < self.max_retries:
                wait_time = self.retry_delay * (2 ** (retries - 1))  # Exponential backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                
        # If we get here, all retries failed
        logger.error(f"All retries failed for {method} request to {url}")
        raise last_error or HTTPException(status_code=500, detail="Request failed after retries")
    
    @abc.abstractmethod
    async def create_invoice(self, req: CreateInvoiceRequest) -> CreateInvoiceResponse:
        """
        Create a payment invoice.
        
        Args:
            req: Invoice creation request
            
        Returns:
            Invoice creation response
        """
        pass
    
    @abc.abstractmethod
    async def get_payment_status(self, payment_id: str) -> PaymentStatusResponse:
        """
        Get the status of a payment.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment status response
        """
        pass
    
    @abc.abstractmethod
    async def refund(self, req: RefundRequest) -> RefundResponse:
        """
        Refund a payment.
        
        Args:
            req: Refund request
            
        Returns:
            Refund response
        """
        pass