# azure-waf-deployer/azure_waf_deployer/templates.py
"""
Template management for Azure WAF deployments
"""

import json
from typing import Dict, Any
from pathlib import Path
import pkg_resources

from .exceptions import TemplateError


class TemplateManager:
    """Manages ARM and Bicep templates for WAF deployments"""
    
    def __init__(self):
        self.template_path = Path(__file__).parent / "templates"
    
    def get_template(self, template_name: str) -> Dict[str, Any]:
        """
        Get ARM template by name
        
        Args:
            template_name: Name of the template
            
        Returns:
            ARM template as dictionary
        """
        try:
            template_file = f"{template_name}.json"
            template_content = pkg_resources.resource_string(
                'azure_waf_deployer', 
                f'templates/{template_file}'
            ).decode('utf-8')
            return json.loads(template_content)
        except Exception as e:
            raise TemplateError(f"Failed to load template {template_name}: {str(e)}")
    
    def list_templates(self) -> list:
        """List available templates"""
        try:
            templates_dir = Path(pkg_resources.resource_filename('azure_waf_deployer', 'templates'))
            return [f.stem for f in templates_dir.glob("*.json")]
        except Exception as e:
            raise TemplateError(f"Failed to list templates: {str(e)}")


# azure-waf-deployer/azure_waf_deployer/templates/application_gateway.json
{
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "applicationGatewayName": {
            "type": "string",
            "metadata": {
                "description": "Name of the Application Gateway"
            }
        },
        "location": {
            "type": "string",
            "defaultValue": "[resourceGroup().location]",
            "metadata": {
                "description": "Location for all resources"
            }
        },
        "skuTier": {
            "type": "string",
            "defaultValue": "WAF_v2",
            "allowedValues": [
                "WAF_v2",
                "Standard_v2"
            ],
            "metadata": {
                "description": "SKU tier for the Application Gateway"
            }
        },
        "skuName": {
            "type": "string",
            "defaultValue": "WAF_v2",
            "allowedValues": [
                "WAF_v2",
                "Standard_v2"
            ],
            "metadata": {
                "description": "SKU name for the Application Gateway"
            }
        },
        "capacity": {
            "type": "int",
            "defaultValue": 2,
            "minValue": 1,
            "maxValue": 32,
            "metadata": {
                "description": "Capacity (instance count) of Application Gateway"
            }
        },
        "wafMode": {
            "type": "string",
            "defaultValue": "Prevention",
            "allowedValues": [
                "Detection",
                "Prevention"
            ],
            "metadata": {
                "description": "WAF mode"
            }
        },
        "vnetName": {
            "type": "string",
            "defaultValue": "[concat(parameters('applicationGatewayName'), '-vnet')]",
            "metadata": {
                "description": "Virtual network name"
            }
        },
        "subnetName": {
            "type": "string",
            "defaultValue": "appgw-subnet",
            "metadata": {
                "description": "Subnet name for Application Gateway"
            }
        },
        "publicIpName": {
            "type": "string",
            "defaultValue": "[concat(parameters('applicationGatewayName'), '-pip')]",
            "metadata": {
                "description": "Public IP name"
            }
        },
        "backendPools": {
            "type": "array",
            "defaultValue": [],
            "metadata": {
                "description": "Backend pools configuration"
            }
        },
        "managedRuleSets": {
            "type": "array",
            "defaultValue": [
                {
                    "ruleSetType": "Microsoft_DefaultRuleSet",
                    "ruleSetVersion": "2.1"
                },
                {
                    "ruleSetType": "Microsoft_BotManagerRuleSet",
                    "ruleSetVersion": "1.0"
                }
            ],
            "metadata": {
                "description": "Managed rule sets"
            }
        },
        "customRules": {
            "type": "array",
            "defaultValue": [],
            "metadata": {
                "description": "Custom WAF rules"
            }
        },
        "enableHttp2": {
            "type": "bool",
            "defaultValue": true,
            "metadata": {
                "description": "Enable HTTP2 support"
            }
        },
        "requestTimeout": {
            "type": "int",
            "defaultValue": 20,
            "metadata": {
                "description": "Request timeout in seconds"
            }
        }
    },
    "variables": {
        "wafPolicyName": "[concat(parameters('applicationGatewayName'), '-wafpolicy')]",
        "vnetAddressPrefix": "10.0.0.0/16",
        "subnetAddressPrefix": "10.0.1.0/24",
        "publicIPRef": "[resourceId('Microsoft.Network/publicIPAddresses', parameters('publicIpName'))]",
        "subnetRef": "[resourceId('Microsoft.Network/virtualNetworks/subnets', parameters('vnetName'), parameters('subnetName'))]",
        "wafPolicyRef": "[resourceId('Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies', variables('wafPolicyName'))]"
    },
    "resources": [
        {
            "type": "Microsoft.Network/virtualNetworks",
            "apiVersion": "2022-07-01",
            "name": "[parameters('vnetName')]",
            "location": "[parameters('location')]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        "[variables('vnetAddressPrefix')]"
                    ]
                },
                "subnets": [
                    {
                        "name": "[parameters('subnetName')]",
                        "properties": {
                            "addressPrefix": "[variables('subnetAddressPrefix')]"
                        }
                    }
                ]
            }
        },
        {
            "type": "Microsoft.Network/publicIPAddresses",
            "apiVersion": "2022-07-01",
            "name": "[parameters('publicIpName')]",
            "location": "[parameters('location')]",
            "sku": {
                "name": "Standard",
                "tier": "Regional"
            },
            "properties": {
                "publicIPAllocationMethod": "Static"
            }
        },
        {
            "type": "Microsoft.Network/ApplicationGatewayWebApplicationFirewallPolicies",
            "apiVersion": "2022-07-01",
            "name": "[variables('wafPolicyName')]",
            "location": "[parameters('location')]",
            "properties": {
                "policySettings": {
                    "mode": "[parameters('wafMode')]",
                    "state": "Enabled",
                    "maxRequestBodySizeInKb": 128,
                    "fileUploadLimitInMb": 100,
                    "requestBodyCheck": true
                },
                "managedRules": {
                    "managedRuleSets": "[parameters('managedRuleSets')]"
                },
                "customRules": "[parameters('customRules')]"
            }
        },
        {
            "type": "Microsoft.Network/applicationGateways",
            "apiVersion": "2022-07-01",
            "name": "[parameters('applicationGatewayName')]",
            "location": "[parameters('location')]",
            "dependsOn": [
                "[variables('wafPolicyRef')]",
                "[variables('publicIPRef')]",
                "[variables('subnetRef')]"
            ],
            "properties": {
                "sku": {
                    "name": "[parameters('skuName')]",
                    "tier": "[parameters('skuTier')]"
                },
                "autoscaleConfiguration": {
                    "minCapacity": 1,
                    "maxCapacity": 32
                },
                "gatewayIPConfigurations": [
                    {
                        "name": "appGatewayIpConfig",
                        "properties": {
                            "subnet": {
                                "id": "[variables('subnetRef')]"
                            }
                        }
                    }
                ],
                "frontendIPConfigurations": [
                    {
                        "name": "appGatewayFrontendIP",
                        "properties": {
                            "publicIPAddress": {
                                "id": "[variables('publicIPRef')]"
                            }
                        }
                    }
                ],
                "frontendPorts": [
                    {
                        "name": "port_80",
                        "properties": {
                            "port": 80
                        }
                    },
                    {
                        "name": "port_443",
                        "properties": {
                            "port": 443
                        }
                    }
                ],
                "backendAddressPools": "[if(empty(parameters('backendPools')), createArray(createObject('name', 'defaultBackendPool', 'properties', createObject())), parameters('backendPools'))]",
                "backendHttpSettingsCollection": [
                    {
                        "name": "defaultHttpSettings",
                        "properties": {
                            "port": 80,
                            "protocol": "Http",
                            "cookieBasedAffinity": "Disabled",
                            "requestTimeout": "[parameters('requestTimeout')]"
                        }
                    }
                ],
                "httpListeners": [
                    {
                        "name": "defaultListener",
                        "properties": {
                            "frontendIPConfiguration": {
                                "id": "[resourceId('Microsoft.Network/applicationGateways/frontendIPConfigurations', parameters('applicationGatewayName'), 'appGatewayFrontendIP')]"
                            },
                            "frontendPort": {
                                "id": "[resourceId('Microsoft.Network/applicationGateways/frontendPorts', parameters('applicationGatewayName'), 'port_80')]"
                            },
                            "protocol": "Http"
                        }
                    }
                ],
                "requestRoutingRules": [
                    {
                        "name": "defaultRule",
                        "properties": {
                            "ruleType": "Basic",
                            "priority": 100,
                            "httpListener": {
                                "id": "[resourceId('Microsoft.Network/applicationGateways/httpListeners', parameters('applicationGatewayName'), 'defaultListener')]"
                            },
                            "backendAddressPool": {
                                "id": "[resourceId('Microsoft.Network/applicationGateways/backendAddressPools', parameters('applicationGatewayName'), if(empty(parameters('backendPools')), 'defaultBackendPool', parameters('backendPools')[0].name))]"
                            },
                            "backendHttpSettings": {
                                "id": "[resourceId('Microsoft.Network/applicationGateways/backendHttpSettingsCollection', parameters('applicationGatewayName'), 'defaultHttpSettings')]"
                            }
                        }
                    }
                ],
                "enableHttp2": "[parameters('enableHttp2')]",
                "firewallPolicy": {
                    "id": "[variables('wafPolicyRef')]"
                }
            }
        }
    ],
    "outputs": {
        "applicationGatewayId": {
            "type": "string",
            "value": "[resourceId('Microsoft.Network/applicationGateways', parameters('applicationGatewayName'))]"
        },
        "publicIPAddress": {
            "type": "string",
            "value": "[reference(variables('publicIPRef')).ipAddress]"
        },
        "wafPolicyId": {
            "type": "string",
            "value": "[variables('wafPolicyRef')]"
        },
        "fqdn": {
            "type": "string",
            "value": "[reference(variables('publicIPRef')).dnsSettings.fqdn]"
        }
    }
}