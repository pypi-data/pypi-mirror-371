"""
Core PoI Receipt class for representing proof-of-intent documents.
"""

import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from .exceptions import PoIError


class PoIReceipt(BaseModel):
    """
    Proof-of-Intent receipt containing all necessary information about an agent's action.
    
    This class represents a cryptographically signed document that proves an agent's
    intent before taking action. It includes metadata about the agent, action,
    target resource, and declared objective.
    """
    
    # Core receipt information
    receipt_id: str = Field(..., description="Unique identifier for the receipt")
    timestamp: str = Field(..., description="Creation timestamp in ISO 8601 format")
    version: str = Field(default="1.0", description="PoI receipt version")
    
    # Agent information
    agent_id: str = Field(..., description="Identifier of the agent taking action")
    agent_type: Optional[str] = Field(None, description="Type/category of the agent")
    agent_version: Optional[str] = Field(None, description="Version of the agent")
    
    # Action information
    action: str = Field(..., description="Type of action being performed")
    target_resource: str = Field(..., description="Resource being accessed or modified")
    declared_objective: str = Field(..., description="Stated purpose of the action")
    
    # Security and risk context
    risk_context: str = Field(default="medium", description="Risk level assessment")
    expiration_time: str = Field(..., description="When the receipt expires (ISO 8601)")
    
    # Additional context
    additional_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Additional context information"
    )
    
    # Cryptographic information
    signature: Optional[str] = Field(None, description="Cryptographic signature")
    signature_algorithm: Optional[str] = Field(None, description="Algorithm used for signing")
    certificate_chain: Optional[List[str]] = Field(
        default_factory=list,
        description="Certificate chain for validation"
    )
    
    # Agent lineage and delegation
    parent_agent_id: Optional[str] = Field(None, description="Parent agent if delegated")
    delegation_chain: Optional[List[str]] = Field(
        default_factory=list,
        description="Chain of agent delegations"
    )
    
    # Compliance and audit
    compliance_tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Compliance and regulatory tags"
    )
    audit_trail: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Audit trail information"
    )
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
    
    @validator('receipt_id')
    def validate_receipt_id(cls, v):
        """Validate receipt ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Receipt ID cannot be empty")
        return v.strip()
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError("Timestamp must be in ISO 8601 format")
    
    @validator('expiration_time')
    def validate_expiration_time(cls, v):
        """Validate expiration time format."""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError("Expiration time must be in ISO 8601 format")
    
    @validator('risk_context')
    def validate_risk_context(cls, v):
        """Validate risk context values."""
        valid_risks = ['low', 'medium', 'high', 'critical']
        if v.lower() not in valid_risks:
            raise ValueError(f"Risk context must be one of: {', '.join(valid_risks)}")
        return v.lower()
    
    @classmethod
    def create(
        cls,
        agent_id: str,
        action: str,
        target_resource: str,
        declared_objective: str,
        **kwargs
    ) -> 'PoIReceipt':
        """
        Create a new PoI receipt with default values.
        
        Args:
            agent_id: Identifier of the agent
            action: Type of action being performed
            target_resource: Resource being accessed
            declared_objective: Stated purpose of the action
            **kwargs: Additional fields to set
            
        Returns:
            New PoI receipt instance
        """
        now = datetime.now(timezone.utc)
        
        # Generate unique receipt ID
        receipt_id = f"poi_{uuid.uuid4().hex[:16]}"
        
        # Set default timestamp
        timestamp = now.isoformat()
        
        # Set default expiration (1 hour from now)
        expiration_hours = kwargs.pop('expiration_hours', 1)
        expiration_time = (now.replace(tzinfo=timezone.utc) + 
                          timedelta(hours=expiration_hours)).isoformat()
        
        # Set default values
        defaults = {
            'receipt_id': receipt_id,
            'timestamp': timestamp,
            'expiration_time': expiration_time,
            'version': '1.0',
            'risk_context': 'medium',
            'additional_context': {},
            'compliance_tags': [],
            'audit_trail': [],
            'delegation_chain': [],
            'certificate_chain': [],
        }
        
        # Update with provided kwargs
        defaults.update(kwargs)
        
        return cls(
            agent_id=agent_id,
            action=action,
            target_resource=target_resource,
            declared_objective=declared_objective,
            **defaults
        )
    
    def is_expired(self) -> bool:
        """
        Check if the receipt has expired.
        
        Returns:
            True if expired, False otherwise
        """
        try:
            expiration = datetime.fromisoformat(self.expiration_time.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            return now > expiration
        except (ValueError, TypeError):
            # If we can't parse the expiration time, consider it expired
            return True
    
    def time_until_expiration(self) -> Optional[float]:
        """
        Get time until expiration in seconds.
        
        Returns:
            Seconds until expiration, or None if expired
        """
        try:
            expiration = datetime.fromisoformat(self.expiration_time.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            delta = expiration - now
            if delta.total_seconds() > 0:
                return delta.total_seconds()
            return None
        except (ValueError, TypeError):
            return None
    
    def add_audit_entry(self, action: str, details: Dict[str, Any]) -> None:
        """
        Add an entry to the audit trail.
        
        Args:
            action: Action being audited
            details: Details about the action
        """
        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'action': action,
            'details': details
        }
        self.audit_trail.append(entry)
    
    def add_compliance_tag(self, tag: str) -> None:
        """
        Add a compliance tag.
        
        Args:
            tag: Compliance tag to add
        """
        if tag not in self.compliance_tags:
            self.compliance_tags.append(tag)
    
    def set_signature(self, signature: str, algorithm: str) -> None:
        """
        Set the cryptographic signature.
        
        Args:
            signature: Cryptographic signature
            algorithm: Algorithm used for signing
        """
        self.signature = signature
        self.signature_algorithm = algorithm
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert receipt to dictionary.
        
        Returns:
            Dictionary representation of the receipt
        """
        return self.model_dump()
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """
        Convert receipt to JSON string.
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON string representation of the receipt
        """
        return self.model_dump_json(indent=indent)
    
    def get_signature_data(self) -> str:
        """
        Get the data that should be signed.
        
        Returns:
            String representation of signable data
        """
        # Create a copy without signature fields for signing
        signable_data = self.model_dump()
        signable_data.pop('signature', None)
        signable_data.pop('signature_algorithm', None)
        signable_data.pop('certificate_chain', None)
        
        # Sort keys for consistent signing
        return json.dumps(signable_data, sort_keys=True, separators=(',', ':'))
    
    def __str__(self) -> str:
        """String representation of the receipt."""
        return f"PoIReceipt(id={self.receipt_id}, agent={self.agent_id}, action={self.action})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the receipt."""
        return (f"PoIReceipt(receipt_id='{self.receipt_id}', "
                f"agent_id='{self.agent_id}', action='{self.action}', "
                f"target_resource='{self.target_resource}')")
