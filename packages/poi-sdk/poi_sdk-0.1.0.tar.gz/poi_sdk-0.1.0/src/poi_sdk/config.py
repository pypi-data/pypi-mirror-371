"""
Configuration management for the Proof-of-Intent SDK.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from .exceptions import PoIConfigurationError


class PoIConfig:
    """Configuration manager for the PoI SDK."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self._config = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Load from file if provided
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    if file_config and 'poi' in file_config:
                        self._config.update(file_config['poi'])
            except Exception as e:
                raise PoIConfigurationError(
                    f"Failed to load configuration file: {e}",
                    config_key="config_file"
                )
        
        # Override with environment variables
        self._load_env_config()
        
        # Set defaults
        self._set_defaults()
    
    def _load_env_config(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'POI_PRIVATE_KEY_PATH': 'keys.private_key_path',
            'POI_CERTIFICATE_PATH': 'keys.certificate_path',
            'POI_PUBLIC_KEY_PATH': 'keys.public_key_path',
            'POI_DEFAULT_EXPIRATION_HOURS': 'defaults.expiration_hours',
            'POI_RISK_THRESHOLD': 'defaults.risk_threshold',
            'POI_SIGNATURE_ALGORITHM': 'defaults.signature_algorithm',
            'POI_CLOCK_SKEW_TOLERANCE': 'validation.clock_skew_tolerance_seconds',
            'POI_REQUIRE_CERTIFICATE_VALIDATION': 'validation.require_certificate_validation',
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_config(config_key, value)
    
    def _set_nested_config(self, key_path: str, value: Any) -> None:
        """Set a nested configuration value."""
        keys = key_path.split('.')
        current = self._config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string values to appropriate types
        if keys[-1] in ['expiration_hours', 'clock_skew_tolerance_seconds']:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
        elif keys[-1] == 'require_certificate_validation':
            value = str(value).lower() in ('true', '1', 'yes', 'on')
        
        current[keys[-1]] = value
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        defaults = {
            'keys': {
                'private_key_path': None,
                'certificate_path': None,
                'public_key_path': None,
            },
            'defaults': {
                'expiration_hours': 1,
                'risk_threshold': 'medium',
                'signature_algorithm': 'rsa',
            },
            'validation': {
                'clock_skew_tolerance_seconds': 300,  # 5 minutes
                'require_certificate_validation': True,
            }
        }
        
        for section, values in defaults.items():
            if section not in self._config:
                self._config[section] = {}
            for key, value in values.items():
                if key not in self._config[section]:
                    self._config[section][key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated path to configuration value
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        current = self._config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def get_private_key_path(self) -> Optional[str]:
        """Get the private key path."""
        return self.get('keys.private_key_path')
    
    def get_certificate_path(self) -> Optional[str]:
        """Get the certificate path."""
        return self.get('keys.certificate_path')
    
    def get_public_key_path(self) -> Optional[str]:
        """Get the public key path."""
        return self.get('keys.public_key_path')
    
    def get_default_expiration_hours(self) -> int:
        """Get the default expiration time in hours."""
        return self.get('defaults.expiration_hours', 1)
    
    def get_risk_threshold(self) -> str:
        """Get the default risk threshold."""
        return self.get('defaults.risk_threshold', 'medium')
    
    def get_signature_algorithm(self) -> str:
        """Get the signature algorithm."""
        return self.get('defaults.signature_algorithm', 'rsa')
    
    def get_clock_skew_tolerance(self) -> int:
        """Get the clock skew tolerance in seconds."""
        return self.get('validation.clock_skew_tolerance_seconds', 300)
    
    def require_certificate_validation(self) -> bool:
        """Check if certificate validation is required."""
        return self.get('validation.require_certificate_validation', True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self._config.copy()
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"PoIConfig(config_path={self.config_path})"
