# azure-waf-deployer/azure_waf_deployer/__init__.py
"""
Azure WAF Deployer - A comprehensive package for deploying WAF-enabled infrastructure on Azure
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .deployer import WAFDeployer
from .templates import TemplateManager
from .config import WAFConfig

__all__ = ["WAFDeployer", "TemplateManager", "WAFConfig"]


# azure-waf-deployer/azure_waf_deployer/deployer.py
"""
Main deployment class for Azure WAF infrastructure
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.core.exceptions import AzureError

from .templates import TemplateManager
from .config import WAFConfig
from .exceptions import WAFDeploymentError

logger = logging.getLogger(__name__)


class WAFDeployer:
    """Azure WAF deployment manager"""
    
    def __init__(self, subscription_id: str, credential: Optional[Any] = None):
        """
        Initialize WAF Deployer
        
        Args:
            subscription_id: Azure subscription ID
            credential: Azure credential object (defaults to DefaultAzureCredential)
        """
        self.subscription_id = subscription_id
        self.credential = credential or DefaultAzureCredential()
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)
        self.network_client = NetworkManagementClient(self.credential, subscription_id)
        self.template_manager = TemplateManager()
        
    def deploy_application_gateway_waf(
        self,
        resource_group: str,
        config: WAFConfig,
        template_type: str = "application_gateway"
    ) -> Dict[str, Any]:
        """
        Deploy Application Gateway with WAF
        
        Args:
            resource_group: Resource group name
            config: WAF configuration
            template_type: Template type to use
            
        Returns:
            Deployment result dictionary
        """
        try:
            logger.info(f"Starting Application Gateway WAF deployment in {resource_group}")
            
            # Get template and parameters
            template = self.template_manager.get_template(template_type)
            parameters = config.get_deployment_parameters()
            
            # Create resource group if it doesn't exist
            self._ensure_resource_group(resource_group, config.location)
            
            # Deploy ARM template
            deployment_name = f"waf-deployment-{config.name}"
            deployment_operation = self.resource_client.deployments.begin_create_or_update(
                resource_group_name=resource_group,
                deployment_name=deployment_name,
                parameters={
                    'properties': {
                        'template': template,
                        'parameters': parameters,
                        'mode': 'Incremental'
                    }
                }
            )
            
            # Wait for completion
            result = deployment_operation.result()
            logger.info(f"Deployment completed successfully: {deployment_name}")
            
            return {
                'deployment_name': deployment_name,
                'status': 'Success',
                'outputs': result.properties.outputs if result.properties.outputs else {},
                'resource_group': resource_group
            }
            
        except AzureError as e:
            logger.error(f"Azure deployment error: {str(e)}")
            raise WAFDeploymentError(f"Failed to deploy WAF: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during deployment: {str(e)}")
            raise WAFDeploymentError(f"Deployment failed: {str(e)}")
    
    def deploy_front_door_waf(
        self,
        resource_group: str,
        config: WAFConfig,
        template_type: str = "front_door"
    ) -> Dict[str, Any]:
        """
        Deploy Azure Front Door with WAF
        
        Args:
            resource_group: Resource group name
            config: WAF configuration
            template_type: Template type to use
            
        Returns:
            Deployment result dictionary
        """
        try:
            logger.info(f"Starting Front Door WAF deployment in {resource_group}")
            
            template = self.template_manager.get_template(template_type)
            parameters = config.get_deployment_parameters()
            
            self._ensure_resource_group(resource_group, config.location)
            
            deployment_name = f"frontdoor-waf-deployment-{config.name}"
            deployment_operation = self.resource_client.deployments.begin_create_or_update(
                resource_group_name=resource_group,
                deployment_name=deployment_name,
                parameters={
                    'properties': {
                        'template': template,
                        'parameters': parameters,
                        'mode': 'Incremental'
                    }
                }
            )
            
            result = deployment_operation.result()
            logger.info(f"Front Door deployment completed: {deployment_name}")
            
            return {
                'deployment_name': deployment_name,
                'status': 'Success',
                'outputs': result.properties.outputs if result.properties.outputs else {},
                'resource_group': resource_group
            }
            
        except AzureError as e:
            logger.error(f"Azure Front Door deployment error: {str(e)}")
            raise WAFDeploymentError(f"Failed to deploy Front Door WAF: {str(e)}")
    
    def validate_template(self, resource_group: str, config: WAFConfig, template_type: str) -> bool:
        """
        Validate ARM template before deployment
        
        Args:
            resource_group: Resource group name
            config: WAF configuration
            template_type: Template type to validate
            
        Returns:
            True if template is valid
        """
        try:
            template = self.template_manager.get_template(template_type)
            parameters = config.get_deployment_parameters()
            
            validation = self.resource_client.deployments.validate(
                resource_group_name=resource_group,
                deployment_name="validation-test",
                parameters={
                    'properties': {
                        'template': template,
                        'parameters': parameters,
                        'mode': 'Incremental'
                    }
                }
            )
            
            if validation.error:
                logger.error(f"Template validation failed: {validation.error}")
                return False
                
            logger.info("Template validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Template validation error: {str(e)}")
            return False
    
    def _ensure_resource_group(self, resource_group: str, location: str):
        """Ensure resource group exists"""
        try:
            self.resource_client.resource_groups.get(resource_group)
            logger.info(f"Resource group {resource_group} already exists")
        except:
            logger.info(f"Creating resource group {resource_group}")
            self.resource_client.resource_groups.create_or_update(
                resource_group,
                {'location': location}
            )
    
    def get_deployment_status(self, resource_group: str, deployment_name: str) -> Dict[str, Any]:
        """Get deployment status"""
        try:
            deployment = self.resource_client.deployments.get(resource_group, deployment_name)
            return {
                'name': deployment.name,
                'provisioning_state': deployment.properties.provisioning_state,
                'timestamp': deployment.properties.timestamp,
                'outputs': deployment.properties.outputs
            }
        except Exception as e:
            logger.error(f"Error getting deployment status: {str(e)}")
            return {'error': str(e)}


# azure-waf-deployer/azure_waf_deployer/config.py
"""
Configuration management for WAF deployments
"""

import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class CustomRule:
    """Custom WAF rule configuration"""
    name: str
    priority: int
    rule_type: str
    action: str
    match_conditions: List[Dict[str, Any]]
    enabled: bool = True

@dataclass
class ManagedRuleSet:
    """Managed rule set configuration"""
    rule_set_type: str
    rule_set_version: str
    exclusions: List[Dict[str, Any]] = field(default_factory=list)
    rule_group_overrides: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class WAFConfig:
    """WAF configuration class"""
    name: str
    location: str
    sku_tier: str = "WAF_v2"
    sku_name: str = "WAF_v2"
    capacity: int = 2
    waf_mode: str = "Prevention"  # Detection or Prevention
    
    # Managed rules
    managed_rule_sets: List[ManagedRuleSet] = field(default_factory=lambda: [
        ManagedRuleSet("Microsoft_DefaultRuleSet", "2.1"),
        ManagedRuleSet("Microsoft_BotManagerRuleSet", "1.0")
    ])
    
    # Custom rules
    custom_rules: List[CustomRule] = field(default_factory=list)
    
    # Network configuration
    vnet_name: str = ""
    subnet_name: str = ""
    public_ip_name: str = ""
    
    # Backend configuration
    backend_pools: List[Dict[str, Any]] = field(default_factory=list)
    
    # SSL configuration
    ssl_certificates: List[Dict[str, Any]] = field(default_factory=list)
    
    # Additional settings
    enable_http2: bool = True
    request_timeout: int = 20
    
    @classmethod
    def from_yaml(cls, file_path: str) -> 'WAFConfig':
        """Load configuration from YAML file"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    def to_yaml(self, file_path: str):
        """Save configuration to YAML file"""
        with open(file_path, 'w') as f:
            yaml.dump(self.__dict__, f, default_flow_style=False)
    
    def get_deployment_parameters(self) -> Dict[str, Any]:
        """Convert config to ARM template parameters"""
        return {
            "applicationGatewayName": {"value": self.name},
            "location": {"value": self.location},
            "skuTier": {"value": self.sku_tier},
            "skuName": {"value": self.sku_name},
            "capacity": {"value": self.capacity},
            "wafMode": {"value": self.waf_mode},
            "managedRuleSets": {"value": [
                {
                    "ruleSetType": mrs.rule_set_type,
                    "ruleSetVersion": mrs.rule_set_version,
                    "exclusions": mrs.exclusions,
                    "ruleGroupOverrides": mrs.rule_group_overrides
                } for mrs in self.managed_rule_sets
            ]},
            "customRules": {"value": [
                {
                    "name": rule.name,
                    "priority": rule.priority,
                    "ruleType": rule.rule_type,
                    "action": rule.action,
                    "matchConditions": rule.match_conditions,
                    "enabled": rule.enabled
                } for rule in self.custom_rules
            ]},
            "vnetName": {"value": self.vnet_name},
            "subnetName": {"value": self.subnet_name},
            "publicIpName": {"value": self.public_ip_name},
            "backendPools": {"value": self.backend_pools},
            "sslCertificates": {"value": self.ssl_certificates},
            "enableHttp2": {"value": self.enable_http2},
            "requestTimeout": {"value": self.request_timeout}
        }


# azure-waf-deployer/azure_waf_deployer/exceptions.py
"""
Custom exceptions for WAF deployment
"""

class WAFDeploymentError(Exception):
    """Raised when WAF deployment fails"""
    pass

class TemplateError(Exception):
    """Raised when template operations fail"""
    pass

class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
    pass