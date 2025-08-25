# azure-waf-deployer/azure_waf_deployer/cli.py
"""
Command-line interface for Azure WAF deployer
"""

import click
import logging
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .deployer import WAFDeployer
from .config import WAFConfig
from .exceptions import WAFDeploymentError, ConfigurationError

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(verbose):
    """Azure WAF Deployer - Deploy WAF-enabled infrastructure on Azure"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')


@main.command()
@click.option('--subscription-id', required=True, help='Azure subscription ID')
@click.option('--resource-group', required=True, help='Resource group name')
@click.option('--config', '-c', required=True, help='Configuration file path')
@click.option('--template-type', default='application_gateway', 
              type=click.Choice(['application_gateway', 'front_door']),
              help='Template type to deploy')
@click.option('--validate-only', is_flag=True, help='Only validate template, don\'t deploy')
def deploy(subscription_id, resource_group, config, template_type, validate_only):
    """Deploy WAF-enabled infrastructure"""
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading configuration...", total=None)
            
            # Load configuration
            config = WAFConfig.from_yaml(config)
            progress.update(task, description="Initializing deployer...")
            
            # Initialize deployer
            deployer = WAFDeployer(subscription_id)
            
            if validate_only:
                progress.update(task, description="Validating template...")
                is_valid = deployer.validate_template(resource_group, config, template_type)
                if is_valid:
                    console.print("✅ Template validation successful!", style="green")
                else:
                    console.print("❌ Template validation failed!", style="red")
                    return
            else:
                progress.update(task, description=f"Deploying {template_type}...")
                
                if template_type == 'application_gateway':
                    result = deployer.deploy_application_gateway_waf(resource_group, config, template_type)
                elif template_type == 'front_door':
                    result = deployer.deploy_front_door_waf(resource_group, config, template_type)
                
                progress.update(task, description="Deployment complete!")
                
                # Display results
                console.print(f"✅ Deployment successful!", style="green")
                console.print(f"Deployment name: {result['deployment_name']}")
                console.print(f"Resource group: {result['resource_group']}")
                
                if result.get('outputs'):
                    console.print("\nOutputs:")
                    for key, value in result['outputs'].items():
                        console.print(f"  {key}: {value['value']}")
                        
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        raise click.Abort()


@main.command()
@click.option('--name', required=True, help='WAF configuration name')
@click.option('--location', required=True, help='Azure region')
@click.option('--output', '-o', required=True, help='Output configuration file')
def init(name, location, output):
    """Initialize a new WAF configuration file"""
    try:
        config = WAFConfig(name=name, location=location)
        config.to_yaml(output)
        console.print(f"✅ Configuration file created: {output}", style="green")
    except Exception as e:
        console.print(f"❌ Error creating configuration: {str(e)}", style="red")
        raise click.Abort()


@main.command()
@click.option('--subscription-id', required=True, help='Azure subscription ID')
@click.option('--resource-group', required=True, help='Resource group name')
@click.option('--deployment-name', required=True, help='Deployment name')
def status(subscription_id, resource_group, deployment_name):
    """Check deployment status"""
    try:
        deployer = WAFDeployer(subscription_id)
        result = deployer.get_deployment_status(resource_group, deployment_name)
        
        if 'error' in result:
            console.print(f"❌ Error: {result['error']}", style="red")
        else:
            table = Table(title="Deployment Status")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Name", result['name'])
            table.add_row("Status", result['provisioning_state'])
            table.add_row("Timestamp", str(result['timestamp']))
            
            console.print(table)
            
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        raise click.Abort()


@main.command()
def list_templates():
    """List available templates"""
    try:
        from .templates import TemplateManager
        manager = TemplateManager()
        templates = manager.list_templates()
        
        table = Table(title="Available Templates")
        table.add_column("Template Name", style="cyan")
        table.add_column("Description", style="magenta")
        
        descriptions = {
            'application_gateway': 'Application Gateway with WAF v2',
            'front_door': 'Azure Front Door with WAF',
            'api_management': 'API Management with WAF'
        }
        
        for template in templates:
            desc = descriptions.get(template, 'WAF enabled template')
            table.add_row(template, desc)
            
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        raise click.Abort()


if __name__ == '__main__':
    main()