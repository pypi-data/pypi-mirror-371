"""
PoI Receipt Generator for creating and signing proof-of-intent documents.
"""

import os
import base64
from pathlib import Path
from typing import Optional, Dict, Any, Union
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate
from .receipt import PoIReceipt
from .config import PoIConfig
from .exceptions import PoIGenerationError, PoICryptographicError, PoIConfigurationError


class PoIGenerator:
    """
    Generator for creating and cryptographically signing PoI receipts.
    
    This class handles the creation of proof-of-intent receipts and their
    cryptographic signing using RSA or ECDSA algorithms.
    """
    
    def __init__(
        self,
        private_key_path: Optional[str] = None,
        certificate_path: Optional[str] = None,
        config: Optional[PoIConfig] = None
    ):
        """
        Initialize the PoI generator.
        
        Args:
            private_key_path: Path to private key file
            certificate_path: Path to certificate file
            config: Configuration object
        """
        self.config = config or PoIConfig()
        self.private_key = None
        self.certificate = None
        self.signature_algorithm = self.config.get_signature_algorithm()
        
        # Load cryptographic materials
        self._load_private_key(private_key_path)
        self._load_certificate(certificate_path)
    
    def _load_private_key(self, key_path: Optional[str] = None) -> None:
        """
        Load the private key for signing.
        
        Args:
            key_path: Path to private key file
        """
        key_path = key_path or self.config.get_private_key_path()
        
        if not key_path:
            # Generate a temporary key for demo purposes
            self._generate_temp_key()
            return
        
        try:
            with open(key_path, 'rb') as key_file:
                key_data = key_file.read()
                self.private_key = load_pem_private_key(key_data, password=None)
        except Exception as e:
            raise PoIConfigurationError(
                f"Failed to load private key from {key_path}: {e}",
                config_key="private_key_path"
            )
    
    def _load_certificate(self, cert_path: Optional[str] = None) -> None:
        """
        Load the certificate for validation.
        
        Args:
            cert_path: Path to certificate file
        """
        cert_path = cert_path or self.config.get_certificate_path()
        
        if not cert_path:
            return
        
        try:
            with open(cert_path, 'rb') as cert_file:
                cert_data = cert_file.read()
                self.certificate = load_pem_x509_certificate(cert_data)
        except Exception as e:
            raise PoIConfigurationError(
                f"Failed to load certificate from {cert_path}: {e}",
                config_key="certificate_path"
            )
    
    def _generate_temp_key(self) -> None:
        """Generate a temporary RSA key for demo purposes."""
        try:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.signature_algorithm = 'rsa'
        except Exception as e:
            raise PoICryptographicError(
                f"Failed to generate temporary key: {e}",
                operation="key_generation"
            )
    
    def generate_receipt(
        self,
        agent_id: str,
        action: str,
        target_resource: str,
        declared_objective: str,
        **kwargs
    ) -> PoIReceipt:
        """
        Generate a new PoI receipt.
        
        Args:
            agent_id: Identifier of the agent
            action: Type of action being performed
            target_resource: Resource being accessed
            declared_objective: Stated purpose of the action
            **kwargs: Additional fields to set
            
        Returns:
            Generated and signed PoI receipt
        """
        try:
            # Create receipt
            receipt = PoIReceipt.create(
                agent_id=agent_id,
                action=action,
                target_resource=target_resource,
                declared_objective=declared_objective,
                **kwargs
            )
            
            # Sign the receipt
            self.sign_receipt(receipt)
            
            return receipt
            
        except Exception as e:
            raise PoIGenerationError(
                f"Failed to generate receipt: {e}",
                details={
                    'agent_id': agent_id,
                    'action': action,
                    'target_resource': target_resource,
                    'declared_objective': declared_objective
                }
            )
    
    def sign_receipt(self, receipt: PoIReceipt) -> None:
        """
        Cryptographically sign a PoI receipt.
        
        Args:
            receipt: Receipt to sign
        """
        if not self.private_key:
            raise PoICryptographicError(
                "No private key available for signing",
                operation="signing"
            )
        
        try:
            # Get the data to sign
            signable_data = receipt.get_signature_data()
            
            # Create signature
            if self.signature_algorithm.lower() == 'rsa':
                signature = self._sign_with_rsa(signable_data)
            elif self.signature_algorithm.lower() == 'ecdsa':
                signature = self._sign_with_ecdsa(signable_data)
            else:
                raise PoICryptographicError(
                    f"Unsupported signature algorithm: {self.signature_algorithm}",
                    operation="signing"
                )
            
            # Encode signature
            signature_b64 = base64.b64encode(signature).decode('utf-8')
            
            # Set signature on receipt
            receipt.set_signature(signature_b64, self.signature_algorithm)
            
        except Exception as e:
            raise PoICryptographicError(
                f"Failed to sign receipt: {e}",
                operation="signing"
            )
    
    def _sign_with_rsa(self, data: str) -> bytes:
        """
        Sign data using RSA.
        
        Args:
            data: Data to sign
            
        Returns:
            RSA signature
        """
        if not isinstance(self.private_key, rsa.RSAPrivateKey):
            raise PoICryptographicError(
                "Private key is not an RSA key",
                operation="rsa_signing"
            )
        
        return self.private_key.sign(
            data.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    
    def _sign_with_ecdsa(self, data: str) -> bytes:
        """
        Sign data using ECDSA.
        
        Args:
            data: Data to sign
            
        Returns:
            ECDSA signature
        """
        if not isinstance(self.private_key, ec.EllipticCurvePrivateKey):
            raise PoICryptographicError(
                "Private key is not an ECDSA key",
                operation="ecdsa_signing"
            )
        
        return self.private_key.sign(
            data.encode('utf-8'),
            ec.ECDSA(hashes.SHA256())
        )
    
    def generate_receipt_from_dict(self, receipt_data: Dict[str, Any]) -> PoIReceipt:
        """
        Generate a receipt from a dictionary.
        
        Args:
            receipt_data: Dictionary containing receipt data
            
        Returns:
            Generated and signed PoI receipt
        """
        try:
            # Extract required fields
            required_fields = ['agent_id', 'action', 'target_resource', 'declared_objective']
            for field in required_fields:
                if field not in receipt_data:
                    raise PoIGenerationError(f"Missing required field: {field}")
            
            # Create receipt
            receipt = PoIReceipt(**receipt_data)
            
            # Sign the receipt
            self.sign_receipt(receipt)
            
            return receipt
            
        except Exception as e:
            raise PoIGenerationError(
                f"Failed to generate receipt from dict: {e}",
                details={'receipt_data': receipt_data}
            )
    
    def batch_generate_receipts(
        self,
        receipt_specs: list[Dict[str, Any]]
    ) -> list[PoIReceipt]:
        """
        Generate multiple receipts in batch.
        
        Args:
            receipt_specs: List of receipt specifications
            
        Returns:
            List of generated receipts
        """
        receipts = []
        
        for spec in receipt_specs:
            try:
                receipt = self.generate_receipt_from_dict(spec)
                receipts.append(receipt)
            except Exception as e:
                # Log error but continue with other receipts
                print(f"Warning: Failed to generate receipt: {e}")
                continue
        
        return receipts
    
    def get_public_key_pem(self) -> Optional[str]:
        """
        Get the public key in PEM format.
        
        Returns:
            Public key as PEM string, or None if not available
        """
        if not self.private_key:
            return None
        
        try:
            if isinstance(self.private_key, rsa.RSAPrivateKey):
                public_key = self.private_key.public_key()
            elif isinstance(self.private_key, ec.EllipticCurvePrivateKey):
                public_key = self.private_key.public_key()
            else:
                return None
            
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return pem.decode('utf-8')
            
        except Exception:
            return None
    
    def validate_receipt_structure(self, receipt: PoIReceipt) -> bool:
        """
        Validate the structure of a receipt.
        
        Args:
            receipt: Receipt to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # This will raise validation errors if invalid
            receipt.model_dump()
            return True
        except Exception:
            return False
    
    def __repr__(self) -> str:
        """String representation of the generator."""
        has_key = "Yes" if self.private_key else "No"
        has_cert = "Yes" if self.certificate else "No"
        return f"PoIGenerator(private_key={has_key}, certificate={has_cert}, algorithm={self.signature_algorithm})"
