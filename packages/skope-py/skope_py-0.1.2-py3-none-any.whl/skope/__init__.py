from typing import List, Optional, Dict, Any, Literal
import requests
from pydantic import BaseModel

# Request Models
class CreateEventRequest(BaseModel):
    user_id: str
    unit: str
    value: Optional[float] = None
    properties: Optional[Dict[str, str]] = None

# Response Models
class Unit(BaseModel):
    id: str
    created_at: str
    organization_id: str
    type: Literal["usage", "recurring"]
    name: str
    tag: str
    archived_at: Optional[str] = None

class PricingRule(BaseModel):
    id: str
    created_at: str
    price: Optional[float] = None
    limit: Optional[int] = None
    unit_id: Optional[str] = None
    plan_id: Optional[str] = None
    relationship_id: Optional[str] = None
    multiplier: Optional[int] = None
    aggregation_type: Optional[Literal["SUM", "LAST", "COUNT"]] = None
    effective_from: Optional[str] = None
    effective_to: Optional[str] = None
    rates: Optional[Dict[str, float]] = None
    rate_field: Optional[str] = None

class PricingRuleWithUnit(PricingRule):
    unit: Unit

class Event(BaseModel):
    id: str
    created_at: str
    pricing_rule_id: str
    value: float
    properties: Optional[Dict[str, str]] = None
    raw_event_data: Optional[Dict[str, Any]] = None

class EventDetails(Event):
    pricing_rule: PricingRuleWithUnit
    user_name: str

class Invoice(BaseModel):
    id: str
    created_at: str
    issued_at: Optional[str] = None
    due_at: Optional[str] = None
    paid_at: Optional[str] = None
    voided_at: Optional[str] = None
    relationship_id: str
    status: Literal["draft", "issued", "paid", "overdue", "void"]
    amount: float
    period_start: str
    period_end: str
    source: Literal["skope", "stripe"]
    source_invoice_id: Optional[str] = None

class InvoiceWithUserName(Invoice):
    user_name: Optional[str] = None

class PricingRuleUsage(BaseModel):
    used: int
    remaining: int
    limit: int

class EventsAPI:
    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url

    def create(self, events: List[CreateEventRequest]) -> Dict[str, Any]:
        """Upload multiple events to Skope in batch.
        
        Args:
            events: List of CreateEventRequest objects to upload
            
        Returns:
            Dict containing the upload response
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.post(
            f"{self.base_url}/v1/events",
            json=[event.model_dump() for event in events]
        )
        response.raise_for_status()
        return response.json()

    def get(self, user_id: Optional[str] = None) -> List[EventDetails]:
        """Get events from Skope.
        
        Args:
            user_id: Optional user ID to filter events for specific user
            
        Returns:
            List of EventDetails objects
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        params = {"user_id": user_id} if user_id else {}
        response = self.session.get(
            f"{self.base_url}/v1/events",
            params=params
        )
        response.raise_for_status()
        data = response.json()["data"]
        return [EventDetails(**event) for event in data]

class InvoicesAPI:
    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url

    def get(self, user_id: Optional[str] = None) -> List[InvoiceWithUserName]:
        """Get invoices from Skope.
        
        Args:
            user_id: Optional user ID to filter invoices for specific user
            
        Returns:
            List of InvoiceWithUserName objects
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        params = {"user_id": user_id} if user_id else {}
        response = self.session.get(
            f"{self.base_url}/v1/invoices",
            params=params
        )
        response.raise_for_status()
        data = response.json()["data"]
        return [InvoiceWithUserName(**invoice) for invoice in data]

class PricingRulesAPI:
    def __init__(self, session: requests.Session, base_url: str):
        self.session = session
        self.base_url = base_url

    def get(self, user_id: Optional[str] = None) -> List[PricingRuleWithUnit]:
        """Get pricing rules from Skope.
        
        Args:
            user_id: Optional user ID to filter pricing rules for specific user
            
        Returns:
            List of PricingRuleWithUnit objects
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        params = {"user_id": user_id} if user_id else {}
        response = self.session.get(
            f"{self.base_url}/v1/pricing-rules",
            params=params
        )
        response.raise_for_status()
        data = response.json()["data"]
        return [PricingRuleWithUnit(**rule) for rule in data]

    def get_usage(self, user_id: str, unit: str) -> PricingRuleUsage:
        """Get pricing rule usage for a specific user and unit.
        
        Args:
            user_id: User ID to get usage for
            unit: Unit to get usage for
            
        Returns:
            PricingRuleUsage object
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.session.get(
            f"{self.base_url}/v1/pricing-rules/usage",
            params={"user_id": user_id, "unit": unit}
        )
        response.raise_for_status()
        data = response.json()["data"]
        return PricingRuleUsage(**data)

class Skope:
    def __init__(self, api_key: str, base_url: str = "https://api.useskope.com"):
        """Initialize the Skope client.
        
        Args:
            api_key: Your Skope API key
            base_url: The base URL of the Skope API (default: https://api.useskope.com)
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        })
        
        # Initialize namespaced APIs
        self.events = EventsAPI(self.session, self.base_url)
        self.invoices = InvoicesAPI(self.session, self.base_url)
        self.pricing_rules = PricingRulesAPI(self.session, self.base_url)
