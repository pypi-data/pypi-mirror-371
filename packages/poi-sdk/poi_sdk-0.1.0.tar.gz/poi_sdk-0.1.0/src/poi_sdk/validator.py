"""
PoI Receipt Validator for verifying proof-of-intent documents.
"""

import base64
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec, utils
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.x509 import load_pem_x509_certificate
from .receipt import PoIReceipt
from .config import PoIConfig
from .exceptions import (
    PoIValidationError, 
    PoICryptographicError, 
    PoIExpirationError,
    PoISignatureError
)


class PoIValidator:
    """
    Validator for verifying PoI receipts.
    
    This class handles the validation of proof-of-intent receipts including
    signature verification, expiration checks, and structural validation.
    """
    
    def __init__(
        self,
        public_key_path: Optional[str] = None,
        certificate_path: Optional[str] = None,
        config: Optional[PoIConfig] = None
    ):
        """
        Initialize the PoI validator.
        
        Args:
            public_key_path: Path to public key file
            certificate_path: Path to certificate file
            config: Configuration object
        """
        self.config = config or PoIConfig()
        self.public_key = None
        self.certificate = None
        
        # Load cryptographic materials
        self._load_public_key(public_key_path)
        self._load_certificate(certificate_path)
    
    def _load_public_key(self, key_path: Optional[str] = None) -> None:
        """
        Load the public key for verification.
        
        Args:
            key_path: Path to public key file
        """
        key_path = key_path or self.config.get_public_key_path()
        
        if not key_path:
            return
        
        try:
            with open(key_path, 'rb') as key_file:
                key_data = key_file.read()
                self.public_key = load_pem_public_key(key_data)
        except Exception as e:
            raise PoICryptographicError(
                f"Failed to load public key from {key_path}: {e}",
                operation="public_key_loading"
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
            raise PoICryptographicError(
                f"Failed to load certificate from {cert_path}: {e}",
                operation="certificate_loading"
            )
    
    def validate_receipt(self, receipt: PoIReceipt) -> bool:
        """
        Validate a PoI receipt.
        
        Args:
            receipt: Receipt to validate
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            PoIValidationError: If validation fails
        """
        try:
            # Check expiration
            self.check_expiration(receipt)
            
            # Validate structure
            if not self.validate_receipt_structure(receipt):
                raise PoIValidationError(
                    "Receipt structure validation failed",
                    receipt_id=receipt.receipt_id
                )
            
            # Verify signature if available
            if receipt.signature and receipt.signature_algorithm:
                if not self.verify_signature(receipt):
                    raise PoISignatureError(
                        "Signature verification failed",
                        receipt_id=receipt.receipt_id,
                        signature=receipt.signature
                    )
            
            # Validate certificate chain if available
            if receipt.certificate_chain and self.config.require_certificate_validation():
                if not self.validate_certificate_chain(receipt):
                    raise PoIValidationError(
                        "Certificate chain validation failed",
                        receipt_id=receipt.receipt_id
                    )
            
            return True
            
        except (PoIExpirationError, PoIValidationError, PoISignatureError):
            # Re-raise these specific errors
            raise
        except Exception as e:
            raise PoIValidationError(
                f"Unexpected validation error: {e}",
                receipt_id=getattr(receipt, 'receipt_id', 'unknown')
            )
    
    def check_expiration(self, receipt: PoIReceipt) -> None:
        """
        Check if a receipt has expired.
        
        Args:
            receipt: Receipt to check
            
        Raises:
            PoIExpirationError: If receipt has expired
        """
        if receipt.is_expired():
            raise PoIExpirationError(
                "Receipt has expired",
                receipt_id=receipt.receipt_id,
                expiration_time=receipt.expiration_time
            )
    
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
    
    def verify_signature(self, receipt: PoIReceipt) -> bool:
        """
        Verify the cryptographic signature of a receipt.
        
        Args:
            receipt: Receipt to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not receipt.signature or not receipt.signature_algorithm:
            return False
        
        if not self.public_key:
            # If no public key available, we can't verify
            return False
        
        try:
            # Decode signature
            signature_bytes = base64.b64decode(receipt.signature)
            
            # Get data that was signed
            signable_data = receipt.get_signature_data()
            
            # Verify signature based on algorithm
            if receipt.signature_algorithm.lower() == 'rsa':
                return self._verify_rsa_signature(signable_data, signature_bytes)
            elif receipt.signature_algorithm.lower() == 'ecdsa':
                return self._verify_ecdsa_signature(signable_data, signature_bytes)
            else:
                return False
                
        except Exception:
            return False
    
    def _verify_rsa_signature(self, data: str, signature: bytes) -> bool:
        """
        Verify RSA signature.
        
        Args:
            data: Data that was signed
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not isinstance(self.public_key, rsa.RSAPublicKey):
            return False
        
        try:
            self.public_key.verify(
                signature,
                data.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def _verify_ecdsa_signature(self, data: str, signature: bytes) -> bool:
        """
        Verify ECDSA signature.
        
        Args:
            data: Data that was signed
            signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not isinstance(self.public_key, ec.EllipticCurvePublicKey):
            return False
        
        try:
            self.public_key.verify(
                signature,
                data.encode('utf-8'),
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception:
            return False
    
    def validate_certificate_chain(self, receipt: PoIReceipt) -> bool:
        """
        Validate the certificate chain of a receipt.
        
        Args:
            receipt: Receipt to validate
            
        Returns:
            True if certificate chain is valid, False otherwise
        """
        if not receipt.certificate_chain:
            return False
        
        try:
            # For now, we'll do basic validation
            # In a production system, you'd want more sophisticated chain validation
            for cert_pem in receipt.certificate_chain:
                try:
                    cert = load_pem_x509_certificate(cert_pem.encode('utf-8'))
                    # Check if certificate is not expired
                    if cert.not_valid_after < datetime.now(timezone.utc):
                        return False
                except Exception:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def validate_receipt_batch(self, receipts: List[PoIReceipt]) -> Dict[str, bool]:
        """
        Validate multiple receipts in batch.
        
        Args:
            receipts: List of receipts to validate
            
        Returns:
            Dictionary mapping receipt IDs to validation results
        """
        results = {}
        
        for receipt in receipts:
            try:
                is_valid = self.validate_receipt(receipt)
                results[receipt.receipt_id] = is_valid
            except Exception as e:
                results[receipt.receipt_id] = False
                # Log error for debugging
                print(f"Validation failed for receipt {receipt.receipt_id}: {e}")
        
        return results
    
    def get_validation_summary(self, receipts: List[PoIReceipt]) -> Dict[str, Any]:
        """
        Get a summary of validation results for multiple receipts.
        
        Args:
            receipts: List of receipts to validate
            
        Returns:
            Validation summary dictionary
        """
        validation_results = self.validate_receipt_batch(receipts)
        
        total_receipts = len(receipts)
        valid_receipts = sum(validation_results.values())
        invalid_receipts = total_receipts - valid_receipts
        
        summary = {
            'total_receipts': total_receipts,
            'valid_receipts': valid_receipts,
            'invalid_receipts': invalid_receipts,
            'validation_rate': valid_receipts / total_receipts if total_receipts > 0 else 0,
            'results': validation_results
        }
        
        return summary
    
    def check_clock_skew(self, receipt: PoIReceipt) -> bool:
        """
        Check if receipt timestamp is within acceptable clock skew tolerance.
        
        Args:
            receipt: Receipt to check
            
        Returns:
            True if within tolerance, False otherwise
        """
        try:
            receipt_time = datetime.fromisoformat(receipt.timestamp.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            
            tolerance_seconds = self.config.get_clock_skew_tolerance()
            time_diff = abs((receipt_time - now).total_seconds())
            
            return time_diff <= tolerance_seconds
            
        except Exception:
            return False
    
    def __repr__(self) -> str:
        """String representation of the validator."""
        has_pub_key = "Yes" if self.public_key else "No"
        has_cert = "Yes" if self.certificate else "No"
        return f"PoIValidator(public_key={has_pub_key}, certificate={has_cert})"
