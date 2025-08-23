"""
Advanced Configuration Management System
Handles configuration loading, validation, and management for SQLMap AI.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


@dataclass
class AIProviderConfig:
    """AI Provider configuration"""
    name: str
    enabled: bool = True
    api_key_env: str = ""
    model: str = ""
    max_tokens: int = 4096
    timeout: int = 30
    rate_limit: float = 1.0
    priority: int = 1


@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 30
    max_requests_per_hour: int = 500
    max_concurrent_scans: int = 3
    allowed_domains: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    enable_audit_logging: bool = True
    safe_mode: bool = True
    require_confirmation: bool = True


@dataclass
class SQLMapConfig:
    """SQLMap execution configuration"""
    default_timeout: int = 120
    max_timeout: int = 600
    default_threads: int = 5
    max_threads: int = 20
    default_risk: int = 1
    max_risk: int = 2
    default_level: int = 1
    max_level: int = 3
    enable_tamper_scripts: bool = True
    custom_tamper_scripts: List[str] = field(default_factory=list)


@dataclass
class ReportingConfig:
    """Reporting configuration"""
    default_format: str = "html"
    enable_pdf: bool = True
    enable_json: bool = True
    enable_charts: bool = True
    output_directory: str = "reports"
    auto_save: bool = True
    include_raw_data: bool = False
    compress_reports: bool = False


@dataclass
class UIConfig:
    """User interface configuration"""
    enable_colors: bool = True
    show_banner: bool = True
    verbose_output: bool = False
    interactive_mode: bool = False
    confirm_dangerous_operations: bool = True
    progress_indicators: bool = True


@dataclass
class AppConfig:
    """Main application configuration"""
    version: str = "2.0.0"
    debug: bool = False
    log_level: str = "INFO"
    config_version: str = "1.0"
    
    # Sub-configurations
    ai_providers: Dict[str, AIProviderConfig] = field(default_factory=dict)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    sqlmap: SQLMapConfig = field(default_factory=SQLMapConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """Advanced configuration manager"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else Path("config.yaml")
        self.env_file = Path(".env")
        self.config: AppConfig = AppConfig()
        
        # Load environment variables
        if self.env_file.exists():
            load_dotenv(self.env_file)
        
        # Initialize default AI providers
        self._initialize_default_ai_providers()
        
        # Load configuration
        self.load_config()
    
    def _initialize_default_ai_providers(self):
        """Initialize default AI provider configurations"""
        default_providers = {
            "groq": AIProviderConfig(
                name="groq",
                enabled=bool(os.getenv("GROQ_API_KEY")),
                api_key_env="GROQ_API_KEY",
                model="qwen/qwen3-32b",
                max_tokens=4096,
                timeout=30,
                rate_limit=0.5,
                priority=1
            ),
            "openai": AIProviderConfig(
                name="openai",
                enabled=bool(os.getenv("OPENAI_API_KEY")),
                api_key_env="OPENAI_API_KEY",
                model="gpt-4o-mini",
                max_tokens=4096,
                timeout=30,
                rate_limit=1.0,
                priority=2
            ),
            "anthropic": AIProviderConfig(
                name="anthropic",
                enabled=bool(os.getenv("ANTHROPIC_API_KEY")),
                api_key_env="ANTHROPIC_API_KEY",
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                timeout=30,
                rate_limit=1.0,
                priority=3
            ),
            "local": AIProviderConfig(
                name="local",
                enabled=os.getenv("ENABLE_LOCAL_LLM", "false").lower() == "true",
                api_key_env="",
                model=os.getenv("LOCAL_MODEL", "microsoft/DialoGPT-medium"),
                max_tokens=512,
                timeout=60,
                rate_limit=0.1,
                priority=4
            )
        }
        
        self.config.ai_providers = default_providers
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                logger.info(f"Loading configuration from {self.config_file}")
                
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    if self.config_file.suffix.lower() in ['.yaml', '.yml']:
                        data = yaml.safe_load(f)
                    else:
                        data = json.load(f)
                
                # Merge with existing config
                self._merge_config(data)
                logger.info("Configuration loaded successfully")
                return True
            else:
                logger.info(f"Configuration file {self.config_file} not found, using defaults")
                # Create default config file
                self.save_config()
                return False
                
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            # Convert config to dictionary
            config_dict = asdict(self.config)
            
            # Ensure output directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                if self.config_file.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def _merge_config(self, data: Dict[str, Any]):
        """Merge loaded configuration data with current config"""
        
        # Update AI providers
        if 'ai_providers' in data:
            for name, provider_data in data['ai_providers'].items():
                if name in self.config.ai_providers:
                    # Update existing provider
                    for key, value in provider_data.items():
                        if hasattr(self.config.ai_providers[name], key):
                            setattr(self.config.ai_providers[name], key, value)
                else:
                    # Create new provider
                    self.config.ai_providers[name] = AIProviderConfig(
                        name=name,
                        **provider_data
                    )
        
        # Update security config
        if 'security' in data:
            for key, value in data['security'].items():
                if hasattr(self.config.security, key):
                    setattr(self.config.security, key, value)
        
        # Update SQLMap config
        if 'sqlmap' in data:
            for key, value in data['sqlmap'].items():
                if hasattr(self.config.sqlmap, key):
                    setattr(self.config.sqlmap, key, value)
        
        # Update reporting config
        if 'reporting' in data:
            for key, value in data['reporting'].items():
                if hasattr(self.config.reporting, key):
                    setattr(self.config.reporting, key, value)
        
        # Update UI config
        if 'ui' in data:
            for key, value in data['ui'].items():
                if hasattr(self.config.ui, key):
                    setattr(self.config.ui, key, value)
        
        # Update main config
        main_keys = ['version', 'debug', 'log_level', 'config_version']
        for key in main_keys:
            if key in data:
                setattr(self.config, key, data[key])
        
        # Update custom settings
        if 'custom_settings' in data:
            self.config.custom_settings.update(data['custom_settings'])
    
    def get_ai_provider_config(self, provider_name: str) -> Optional[AIProviderConfig]:
        """Get AI provider configuration"""
        return self.config.ai_providers.get(provider_name)
    
    def get_enabled_ai_providers(self) -> List[AIProviderConfig]:
        """Get list of enabled AI providers sorted by priority"""
        enabled = [p for p in self.config.ai_providers.values() if p.enabled]
        return sorted(enabled, key=lambda x: x.priority)
    
    def update_ai_provider(self, provider_name: str, **kwargs) -> bool:
        """Update AI provider configuration"""
        if provider_name not in self.config.ai_providers:
            return False
        
        provider = self.config.ai_providers[provider_name]
        for key, value in kwargs.items():
            if hasattr(provider, key):
                setattr(provider, key, value)
        
        return True
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate AI providers
        enabled_providers = self.get_enabled_ai_providers()
        if not enabled_providers:
            issues.append("No AI providers are enabled")
        
        for provider in enabled_providers:
            if provider.api_key_env and not os.getenv(provider.api_key_env):
                issues.append(f"Missing API key for {provider.name}: {provider.api_key_env}")
        
        # Validate security settings
        if self.config.security.max_requests_per_minute <= 0:
            issues.append("Invalid rate limit: max_requests_per_minute must be > 0")
        
        if self.config.security.max_concurrent_scans <= 0:
            issues.append("Invalid concurrent scans: max_concurrent_scans must be > 0")
        
        # Validate SQLMap settings
        if self.config.sqlmap.default_timeout <= 0:
            issues.append("Invalid timeout: default_timeout must be > 0")
        
        if self.config.sqlmap.max_threads <= 0:
            issues.append("Invalid threads: max_threads must be > 0")
        
        # Validate reporting settings
        valid_formats = ['html', 'pdf', 'json']
        if self.config.reporting.default_format not in valid_formats:
            issues.append(f"Invalid report format: {self.config.reporting.default_format}")
        
        # Validate output directory
        try:
            output_dir = Path(self.config.reporting.output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create output directory: {e}")
        
        return issues
    
    def get_sqlmap_defaults(self) -> Dict[str, Any]:
        """Get default SQLMap options based on configuration"""
        return {
            'timeout': self.config.sqlmap.default_timeout,
            'threads': self.config.sqlmap.default_threads,
            'risk': self.config.sqlmap.default_risk,
            'level': self.config.sqlmap.default_level,
            'tamper_scripts': self.config.sqlmap.custom_tamper_scripts if self.config.sqlmap.enable_tamper_scripts else []
        }
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration"""
        return self.config.security
    
    def get_reporting_config(self) -> ReportingConfig:
        """Get reporting configuration"""
        return self.config.reporting
    
    def get_ui_config(self) -> UIConfig:
        """Get UI configuration"""
        return self.config.ui
    
    def set_custom_setting(self, key: str, value: Any):
        """Set custom application setting"""
        self.config.custom_settings[key] = value
    
    def get_custom_setting(self, key: str, default: Any = None) -> Any:
        """Get custom application setting"""
        return self.config.custom_settings.get(key, default)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = AppConfig()
        self._initialize_default_ai_providers()
        logger.info("Configuration reset to defaults")
    
    def export_config(self, export_path: str, include_sensitive: bool = False) -> bool:
        """Export configuration to file"""
        try:
            config_dict = asdict(self.config)
            
            # Remove sensitive data if requested
            if not include_sensitive:
                for provider in config_dict.get('ai_providers', {}).values():
                    if 'api_key_env' in provider:
                        provider['api_key_env'] = "[REDACTED]"
            
            export_file = Path(export_path)
            with open(export_file, 'w', encoding='utf-8') as f:
                if export_file.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for display"""
        enabled_providers = [p.name for p in self.get_enabled_ai_providers()]
        
        return {
            "version": self.config.version,
            "config_file": str(self.config_file),
            "enabled_ai_providers": enabled_providers,
            "security_mode": "Safe" if self.config.security.safe_mode else "Advanced",
            "default_report_format": self.config.reporting.default_format,
            "max_concurrent_scans": self.config.security.max_concurrent_scans,
            "default_timeout": self.config.sqlmap.default_timeout,
            "audit_logging": self.config.security.enable_audit_logging,
            "debug_mode": self.config.debug
        }


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> AppConfig:
    """Get current application configuration"""
    return config_manager.config


def save_config() -> bool:
    """Save current configuration"""
    return config_manager.save_config()


def validate_config() -> List[str]:
    """Validate current configuration"""
    return config_manager.validate_config()
