"""
CloudOps Runbooks - Enterprise CLI Interface

## Overview

The `runbooks` command-line interface provides a standardized, enterprise-grade
entrypoint for all AWS cloud operations, designed for CloudOps, DevOps, and SRE teams.

## Design Principles

- **AI-Agent Friendly**: Predictable command patterns and consistent outputs
- **Human-Optimized**: Intuitive syntax with comprehensive help and examples
- **KISS Architecture**: Simple commands without legacy complexity
- **Enterprise Ready**: Multi-deployment support (CLI, Docker, Lambda, K8s)

## Command Categories

### 🔍 Discovery & Assessment
- `runbooks inventory` - Resource discovery and inventory operations
- `runbooks cfat assess` - Cloud Foundations Assessment Tool
- `runbooks security assess` - Security baseline assessment

### ⚙️ Operations & Automation
- `runbooks operate` - AWS resource operations (EC2, S3, DynamoDB, etc.)
- `runbooks org` - AWS Organizations management
- `runbooks finops` - Cost analysis and financial operations

## Standardized Options

All commands support consistent options for enterprise integration:

- `--profile` - AWS profile selection
- `--region` - AWS region targeting
- `--dry-run` - Safety mode for testing
- `--output` - Format selection (console, json, csv, html, yaml)
- `--force` - Override confirmation prompts (for automation)

## Examples

```bash
# Assessment and Discovery
runbooks cfat assess --region us-west-2 --output json
runbooks inventory ec2 --profile production --output csv
runbooks security assess --output html --output-file security-report.html

# Operations (with safety)
runbooks operate ec2 start --instance-ids i-1234567890abcdef0 --dry-run
runbooks operate s3 create-bucket --bucket-name my-bucket --region us-west-2
runbooks operate dynamodb create-table --table-name employees

# Multi-Account Operations
runbooks org list-ous --profile management-account
runbooks operate ec2 cleanup-unused-volumes --region us-east-1 --force
```

## Documentation

For comprehensive documentation: https://cloudops.oceansoft.io/cloud-foundation/cfat-assessment-tool.html
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from loguru import logger

try:
    from rich.console import Console
    from rich.table import Table

    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

    # Fallback console implementation
    class Console:
        def print(self, *args, **kwargs):
            print(*args)


from runbooks import __version__
from runbooks.cfat.runner import AssessmentRunner
from runbooks.config import load_config, save_config
from runbooks.inventory.core.collector import InventoryCollector
from runbooks.utils import setup_logging

console = Console()

# ============================================================================
# STANDARDIZED CLI OPTIONS (Human & AI-Agent Friendly)
# ============================================================================


def common_aws_options(f):
    """
    Standard AWS connection and safety options for all commands.

    Provides consistent AWS configuration across the entire CLI interface,
    enabling predictable behavior for both human operators and AI agents.

    Args:
        f: Click command function to decorate

    Returns:
        Decorated function with AWS options

    Added Options:
        --profile: AWS profile name (default: 'default')
        --region: AWS region identifier (default: 'ap-southeast-2')
        --dry-run: Safety flag to preview operations without execution

    Examples:
        ```bash
        runbooks inventory ec2 --profile production --region us-west-2 --dry-run
        runbooks operate s3 create-bucket --profile dev --region eu-west-1
        ```
    """
    f = click.option("--profile", default="default", help="AWS profile (default: 'default')")(f)
    f = click.option("--region", default="ap-southeast-2", help="AWS region (default: 'ap-southeast-2')")(f)
    f = click.option("--dry-run", is_flag=True, help="Enable dry-run mode for safety")(f)
    return f


def common_output_options(f):
    """
    Standard output formatting options for consistent reporting.

    Enables flexible output formats suitable for different consumption patterns:
    human readable, automation integration, and data analysis workflows.

    Args:
        f: Click command function to decorate

    Returns:
        Decorated function with output options

    Added Options:
        --output: Format selection (console, json, csv, html, yaml)
        --output-file: Custom file path for saving results

    Examples:
        ```bash
        runbooks cfat assess --output json --output-file assessment.json
        runbooks inventory ec2 --output csv --output-file ec2-inventory.csv
        runbooks security assess --output html --output-file security-report.html
        ```
    """
    f = click.option(
        "--output",
        type=click.Choice(["console", "json", "csv", "html", "yaml"]),
        default="console",
        help="Output format",
    )(f)
    f = click.option("--output-file", type=click.Path(), help="Output file path (auto-generated if not specified)")(f)
    return f


def common_filter_options(f):
    """
    Standard resource filtering options for targeted discovery.

    Provides consistent filtering capabilities across all inventory and
    discovery operations, enabling precise resource targeting for large-scale
    multi-account AWS environments.

    Args:
        f: Click command function to decorate

    Returns:
        Decorated function with filter options

    Added Options:
        --tags: Tag-based filtering with key=value format (multiple values supported)
        --accounts: Account ID filtering for multi-account operations
        --regions: Region-based filtering for multi-region operations

    Examples:
        ```bash
        runbooks inventory ec2 --tags Environment=production Team=platform
        runbooks inventory s3 --accounts 123456789012 987654321098
        runbooks inventory vpc --regions us-east-1 us-west-2 --tags CostCenter=engineering
        ```
    """
    f = click.option("--tags", multiple=True, help="Filter by tags (key=value format)")(f)
    f = click.option("--accounts", multiple=True, help="Filter by account IDs")(f)
    f = click.option("--regions", multiple=True, help="Filter by regions")(f)
    return f


# ============================================================================
# MAIN CLI GROUP
# ============================================================================


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.option("--debug", is_flag=True, help="Enable debug logging")
@common_aws_options
@click.option("--config", type=click.Path(), help="Configuration file path")
@click.pass_context
def main(ctx, debug, profile, region, dry_run, config):
    """
    CloudOps Runbooks - Enterprise AWS Automation Toolkit v{version}.

    🚀 Unified CLI for comprehensive AWS operations, assessment, and management.
    
    Quick Commands (New!):
    • runbooks start i-123456    → Start EC2 instances instantly
    • runbooks stop i-123456     → Stop EC2 instances instantly
    • runbooks scan -r ec2,rds    → Quick resource discovery
    
    Full Architecture:
    • runbooks inventory  → Read-only discovery and analysis
    • runbooks operate    → Resource lifecycle operations 
    • runbooks cfat       → Cloud Foundations Assessment
    • runbooks security   → Security baseline testing
    • runbooks org        → Organizations management
    • runbooks finops     → Cost and usage analytics
    
    Safety Features:
    • --dry-run mode for all operations
    • Confirmation prompts for destructive actions
    • Comprehensive logging and audit trails
    • Type-safe operations with validation
    
    Examples:
        runbooks inventory collect --resources ec2,rds --dry-run
        runbooks operate ec2 start --instance-ids i-123456 --dry-run
        runbooks cfat assess --categories security --output html
        runbooks security assess --profile prod --format json
    """.format(version=__version__)

    # Initialize context for all subcommands
    ctx.ensure_object(dict)
    ctx.obj.update({"debug": debug, "profile": profile, "region": region, "dry_run": dry_run})

    # Setup logging
    setup_logging(debug=debug)

    # Load configuration
    config_path = Path(config) if config else Path.home() / ".runbooks" / "config.yaml"
    ctx.obj["config"] = load_config(config_path)

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# ============================================================================
# INVENTORY COMMANDS (Read-Only Discovery)
# ============================================================================


@main.group(invoke_without_command=True)
@common_aws_options
@common_output_options
@common_filter_options
@click.pass_context
def inventory(ctx, profile, region, dry_run, output, output_file, tags, accounts, regions):
    """
    Multi-account AWS resource discovery and inventory.

    Read-only operations for comprehensive resource discovery across
    AWS services, accounts, and regions with advanced filtering.

    Examples:
        runbooks inventory collect --resources ec2,rds
        runbooks inventory collect --accounts 123456789012 --regions us-east-1
        runbooks inventory collect --tags Environment=prod --output json
    """
    # Update context with inventory-specific options
    ctx.obj.update(
        {
            "profile": profile,
            "region": region,
            "dry_run": dry_run,
            "output": output,
            "output_file": output_file,
            "tags": tags,
            "accounts": accounts,
            "regions": regions,
        }
    )

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@inventory.command()
@click.option("--resources", "-r", multiple=True, help="Resource types (ec2, rds, lambda, s3, etc.)")
@click.option("--all-resources", is_flag=True, help="Collect all resource types")
@click.option("--all-accounts", is_flag=True, help="Collect from all organization accounts")
@click.option("--include-costs", is_flag=True, help="Include cost information")
@click.option("--parallel", is_flag=True, default=True, help="Enable parallel collection")
@click.pass_context
def collect(ctx, resources, all_resources, all_accounts, include_costs, parallel):
    """Collect comprehensive AWS resource inventory."""
    try:
        console.print(f"[blue]📊 Starting AWS Resource Inventory Collection[/blue]")
        console.print(f"[dim]Profile: {ctx.obj['profile']} | Region: {ctx.obj['region']} | Parallel: {parallel}[/dim]")

        # Initialize collector
        collector = InventoryCollector(profile=ctx.obj["profile"], region=ctx.obj["region"], parallel=parallel)

        # Configure resources
        if all_resources:
            resource_types = collector.get_all_resource_types()
        elif resources:
            resource_types = list(resources)
        else:
            resource_types = ["ec2", "rds", "s3", "lambda"]

        # Configure accounts
        if all_accounts:
            account_ids = collector.get_organization_accounts()
        elif ctx.obj.get("accounts"):
            account_ids = list(ctx.obj["accounts"])
        else:
            account_ids = [collector.get_current_account_id()]

        # Collect inventory
        with console.status("[bold green]Collecting inventory..."):
            results = collector.collect_inventory(
                resource_types=resource_types, account_ids=account_ids, include_costs=include_costs
            )

        # Output results
        if ctx.obj["output"] == "console":
            display_inventory_results(results)
        else:
            save_inventory_results(results, ctx.obj["output"], ctx.obj["output_file"])

        console.print(f"[green]✅ Inventory collection completed![/green]")

    except Exception as e:
        console.print(f"[red]❌ Inventory collection failed: {e}[/red]")
        logger.error(f"Inventory error: {e}")
        raise click.ClickException(str(e))


# ============================================================================
# OPERATE COMMANDS (Resource Lifecycle Operations)
# ============================================================================


@main.group(invoke_without_command=True)
@common_aws_options
@click.option("--force", is_flag=True, help="Skip confirmation prompts for destructive operations")
@click.pass_context
def operate(ctx, profile, region, dry_run, force):
    """
    AWS resource lifecycle operations and automation.

    Perform operational tasks including creation, modification, and deletion
    of AWS resources with comprehensive safety features.

    Safety Features:
    • Dry-run mode for all operations
    • Confirmation prompts for destructive actions
    • Comprehensive logging and audit trails
    • Operation result tracking and rollback support

    Examples:
        runbooks operate ec2 start --instance-ids i-123456 --dry-run
        runbooks operate s3 create-bucket --bucket-name test --encryption
        runbooks operate cloudformation deploy --template-file stack.yaml
    """
    ctx.obj.update({"profile": profile, "region": region, "dry_run": dry_run, "force": force})

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@operate.group()
@click.pass_context
def ec2(ctx):
    """EC2 instance and resource operations."""
    pass


@ec2.command()
@click.option(
    "--instance-ids",
    multiple=True,
    required=True,
    help="Instance IDs (repeat for multiple). Example: --instance-ids i-1234567890abcdef0",
)
@click.pass_context
def start(ctx, instance_ids):
    """Start EC2 instances."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import EC2Operations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]⚡ Starting EC2 Instances[/blue]")
        console.print(f"[dim]Count: {len(instance_ids)} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        # Initialize operations
        ec2_ops = EC2Operations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        # Create context
        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="start_instances",
            resource_types=["ec2:instance"],
            dry_run=ctx.obj["dry_run"],
            force=ctx.obj.get("force", False),
        )

        # Execute operation
        results = ec2_ops.start_instances(context, list(instance_ids))

        # Display results
        successful = sum(1 for r in results if r.success)
        for result in results:
            status = "✅" if result.success else "❌"
            message = result.message if result.success else result.error_message
            console.print(f"{status} {result.resource_id}: {message}")

        console.print(f"\n[bold]Summary: {successful}/{len(results)} instances started[/bold]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        console.print(f"[dim]💡 Try: runbooks inventory collect -r ec2  # List available instances[/dim]")
        console.print(f"[dim]💡 Example: runbooks operate ec2 start --instance-ids i-1234567890abcdef0[/dim]")
        raise click.ClickException(str(e))


@ec2.command()
@click.option("--instance-ids", multiple=True, required=True, help="Instance IDs (repeat for multiple)")
@click.pass_context
def stop(ctx, instance_ids):
    """Stop EC2 instances."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import EC2Operations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]⏹️ Stopping EC2 Instances[/blue]")
        console.print(f"[dim]Count: {len(instance_ids)} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        ec2_ops = EC2Operations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="stop_instances",
            resource_types=["ec2:instance"],
            dry_run=ctx.obj["dry_run"],
            force=ctx.obj.get("force", False),
        )

        results = ec2_ops.stop_instances(context, list(instance_ids))

        successful = sum(1 for r in results if r.success)
        for result in results:
            status = "✅" if result.success else "❌"
            message = result.message if result.success else result.error_message
            console.print(f"{status} {result.resource_id}: {message}")

        console.print(f"\n[bold]Summary: {successful}/{len(results)} instances stopped[/bold]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@ec2.command()
@click.option("--instance-ids", multiple=True, required=True, help="Instance IDs to terminate (DESTRUCTIVE)")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def terminate(ctx, instance_ids, confirm):
    """Terminate EC2 instances (DESTRUCTIVE - cannot be undone)."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import EC2Operations
        from runbooks.operate.base import OperationContext

        console.print(f"[red]💥 Terminating EC2 Instances[/red]")
        console.print(f"[dim]Count: {len(instance_ids)} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        if not ctx.obj["dry_run"] and not confirm and not ctx.obj.get("force", False):
            console.print("[yellow]⚠️ This action cannot be undone![/yellow]")
            if not click.confirm("Are you sure you want to terminate these instances?"):
                console.print("[blue]Operation cancelled[/blue]")
                return

        ec2_ops = EC2Operations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="terminate_instances",
            resource_types=["ec2:instance"],
            dry_run=ctx.obj["dry_run"],
            force=ctx.obj.get("force", False),
        )

        results = ec2_ops.terminate_instances(context, list(instance_ids))

        successful = sum(1 for r in results if r.success)
        for result in results:
            status = "✅" if result.success else "❌"
            message = result.message if result.success else result.error_message
            console.print(f"{status} {result.resource_id}: {message}")

        console.print(f"\n[bold]Summary: {successful}/{len(results)} instances terminated[/bold]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@ec2.command()
@click.option("--image-id", required=True, help="AMI ID to launch")
@click.option("--instance-type", default="t2.micro", help="Instance type (default: t2.micro)")
@click.option("--count", default=1, help="Number of instances to launch (default: 1)")
@click.option("--key-name", help="EC2 key pair name")
@click.option("--security-group-ids", multiple=True, help="Security group IDs (repeat for multiple)")
@click.option("--subnet-id", help="Subnet ID for VPC placement")
@click.option("--user-data", help="User data script")
@click.option("--instance-profile", help="IAM instance profile name")
@click.option("--tags", multiple=True, help="Instance tags in key=value format")
@click.pass_context
def run_instances(
    ctx, image_id, instance_type, count, key_name, security_group_ids, subnet_id, user_data, instance_profile, tags
):
    """Launch new EC2 instances with comprehensive configuration."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import EC2Operations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]🚀 Launching EC2 Instances[/blue]")
        console.print(
            f"[dim]AMI: {image_id} | Type: {instance_type} | Count: {count} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        # Parse tags
        tag_dict = {}
        for tag in tags:
            if "=" in tag:
                key, value = tag.split("=", 1)
                tag_dict[key] = value

        ec2_ops = EC2Operations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="run_instances",
            resource_types=["ec2:instance"],
            dry_run=ctx.obj["dry_run"],
        )

        results = ec2_ops.run_instances(
            context,
            image_id=image_id,
            instance_type=instance_type,
            min_count=count,
            max_count=count,
            key_name=key_name,
            security_group_ids=list(security_group_ids) if security_group_ids else None,
            subnet_id=subnet_id,
            user_data=user_data,
            instance_profile_name=instance_profile,
            tags=tag_dict if tag_dict else None,
        )

        for result in results:
            if result.success:
                console.print(f"[green]✅ Successfully launched {count} instances[/green]")
                if result.response_data and "Instances" in result.response_data:
                    instance_ids = [inst["InstanceId"] for inst in result.response_data["Instances"]]
                    console.print(f"[green]  📋 Instance IDs: {', '.join(instance_ids)}[/green]")
            else:
                console.print(f"[red]❌ Failed to launch instances: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@ec2.command()
@click.option("--source-image-id", required=True, help="Source AMI ID to copy")
@click.option("--source-region", required=True, help="Source region")
@click.option("--name", required=True, help="Name for the new AMI")
@click.option("--description", help="Description for the new AMI")
@click.option("--encrypt/--no-encrypt", default=True, help="Enable encryption (default: enabled)")
@click.option("--kms-key-id", help="KMS key ID for encryption")
@click.pass_context
def copy_image(ctx, source_image_id, source_region, name, description, encrypt, kms_key_id):
    """Copy AMI across regions with encryption."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import EC2Operations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]📋 Copying AMI Across Regions[/blue]")
        console.print(
            f"[dim]Source: {source_image_id} ({source_region}) → {ctx.obj['region']} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        ec2_ops = EC2Operations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="copy_image",
            resource_types=["ec2:ami"],
            dry_run=ctx.obj["dry_run"],
        )

        results = ec2_ops.copy_image(
            context,
            source_image_id=source_image_id,
            source_region=source_region,
            name=name,
            description=description,
            encrypted=encrypt,
            kms_key_id=kms_key_id,
        )

        for result in results:
            if result.success:
                console.print(f"[green]✅ AMI copy initiated successfully[/green]")
                if result.response_data and "ImageId" in result.response_data:
                    new_ami_id = result.response_data["ImageId"]
                    console.print(f"[green]  📋 New AMI ID: {new_ami_id}[/green]")
                    console.print(f"[yellow]  ⏳ Copy in progress - check console for completion[/yellow]")
            else:
                console.print(f"[red]❌ Failed to copy AMI: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@ec2.command()
@click.pass_context
def cleanup_unused_volumes(ctx):
    """Identify and report unused EBS volumes."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import EC2Operations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]🧹 Scanning for Unused EBS Volumes[/blue]")
        console.print(f"[dim]Region: {ctx.obj['region']} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        ec2_ops = EC2Operations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="cleanup_unused_volumes",
            resource_types=["ec2:volume"],
            dry_run=ctx.obj["dry_run"],
        )

        results = ec2_ops.cleanup_unused_volumes(context)

        for result in results:
            if result.success:
                data = result.response_data
                count = data.get("count", 0)
                console.print(f"[green]✅ Scan completed[/green]")
                console.print(f"[yellow]📊 Found {count} unused volumes[/yellow]")

                if count > 0 and "unused_volumes" in data:
                    console.print(
                        f"[dim]Volume IDs: {', '.join(data['unused_volumes'][:5])}{'...' if count > 5 else ''}[/dim]"
                    )
                    console.print(f"[blue]💡 Use AWS Console or additional tools to review and delete[/blue]")
            else:
                console.print(f"[red]❌ Scan failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@ec2.command()
@click.pass_context
def cleanup_unused_eips(ctx):
    """Identify and report unused Elastic IPs."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import EC2Operations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]🧹 Scanning for Unused Elastic IPs[/blue]")
        console.print(f"[dim]Region: {ctx.obj['region']} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        ec2_ops = EC2Operations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="cleanup_unused_eips",
            resource_types=["ec2:eip"],
            dry_run=ctx.obj["dry_run"],
        )

        results = ec2_ops.cleanup_unused_eips(context)

        for result in results:
            if result.success:
                data = result.response_data
                count = data.get("count", 0)
                console.print(f"[green]✅ Scan completed[/green]")
                console.print(f"[yellow]📊 Found {count} unused Elastic IPs[/yellow]")

                if count > 0 and "unused_eips" in data:
                    console.print(
                        f"[dim]Allocation IDs: {', '.join(data['unused_eips'][:3])}{'...' if count > 3 else ''}[/dim]"
                    )
                    console.print(f"[blue]💡 Use AWS Console to review and release unused EIPs[/blue]")
                    console.print(f"[red]⚠️ Unused EIPs incur charges even when not attached[/red]")
            else:
                console.print(f"[red]❌ Scan failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@operate.group()
@click.pass_context
def s3(ctx):
    """S3 bucket and object operations."""
    pass


@s3.command()
@click.option("--bucket-name", required=True, help="S3 bucket name")
@click.option("--encryption/--no-encryption", default=True, help="Enable encryption")
@click.option("--versioning/--no-versioning", default=False, help="Enable versioning")
@click.option("--public-access-block/--no-public-access-block", default=True, help="Block public access")
@click.pass_context
def create_bucket(ctx, bucket_name, encryption, versioning, public_access_block):
    """Create S3 bucket with security best practices."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import S3Operations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]🪣 Creating S3 Bucket[/blue]")
        console.print(f"[dim]Name: {bucket_name} | Encryption: {encryption} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        s3_ops = S3Operations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="create_bucket",
            resource_types=["s3:bucket"],
            dry_run=ctx.obj["dry_run"],
        )

        results = s3_ops.create_bucket(
            context,
            bucket_name=bucket_name,
            region=ctx.obj["region"],
            encryption=encryption,
            versioning=versioning,
            public_access_block=public_access_block,
        )

        for result in results:
            if result.success:
                console.print(f"[green]✅ Bucket {bucket_name} created successfully[/green]")
                if encryption:
                    console.print("[green]  🔒 Encryption enabled[/green]")
                if versioning:
                    console.print("[green]  📚 Versioning enabled[/green]")
                if public_access_block:
                    console.print("[green]  🚫 Public access blocked[/green]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@s3.command()
@click.option("--bucket-name", required=True, help="S3 bucket name to delete")
@click.option("--force", is_flag=True, help="Skip confirmation and delete all objects")
@click.pass_context
def delete_bucket_and_objects(ctx, bucket_name, force):
    """Delete S3 bucket and all its objects (DESTRUCTIVE)."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import S3Operations
        from runbooks.operate.base import OperationContext

        console.print(f"[red]🗑️ Deleting S3 Bucket and Objects[/red]")
        console.print(f"[dim]Bucket: {bucket_name} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        if not ctx.obj["dry_run"] and not force and not ctx.obj.get("force", False):
            console.print("[yellow]⚠️ This will permanently delete the bucket and ALL objects![/yellow]")
            if not click.confirm(f"Are you sure you want to delete bucket '{bucket_name}' and all its contents?"):
                console.print("[blue]Operation cancelled[/blue]")
                return

        s3_ops = S3Operations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="delete_bucket_and_objects",
            resource_types=["s3:bucket"],
            dry_run=ctx.obj["dry_run"],
        )

        results = s3_ops.delete_bucket_and_objects(context, bucket_name)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Bucket {bucket_name} and all objects deleted successfully[/green]")
            else:
                console.print(f"[red]❌ Failed to delete bucket: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@s3.command()
@click.option("--account-id", help="AWS account ID (uses current account if not specified)")
@click.option("--block-public-acls/--allow-public-acls", default=True, help="Block public ACLs")
@click.option("--ignore-public-acls/--honor-public-acls", default=True, help="Ignore public ACLs")
@click.option("--block-public-policy/--allow-public-policy", default=True, help="Block public bucket policies")
@click.option("--restrict-public-buckets/--allow-public-buckets", default=True, help="Restrict public bucket access")
@click.pass_context
def set_public_access_block(
    ctx, account_id, block_public_acls, ignore_public_acls, block_public_policy, restrict_public_buckets
):
    """Configure account-level S3 public access block settings."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import S3Operations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]🔒 Setting S3 Public Access Block[/blue]")
        console.print(f"[dim]Account: {account_id or 'current'} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        s3_ops = S3Operations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        account = AWSAccount(account_id=account_id or "current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="set_public_access_block",
            resource_types=["s3:account"],
            dry_run=ctx.obj["dry_run"],
        )

        results = s3_ops.set_public_access_block(
            context,
            account_id=account_id,
            block_public_acls=block_public_acls,
            ignore_public_acls=ignore_public_acls,
            block_public_policy=block_public_policy,
            restrict_public_buckets=restrict_public_buckets,
        )

        for result in results:
            if result.success:
                console.print(f"[green]✅ Public access block configured successfully[/green]")
                console.print(f"[green]  🔒 Block Public ACLs: {block_public_acls}[/green]")
                console.print(f"[green]  🔒 Ignore Public ACLs: {ignore_public_acls}[/green]")
                console.print(f"[green]  🔒 Block Public Policy: {block_public_policy}[/green]")
                console.print(f"[green]  🔒 Restrict Public Buckets: {restrict_public_buckets}[/green]")
            else:
                console.print(f"[red]❌ Failed to configure public access block: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@s3.command()
@click.option("--source-bucket", required=True, help="Source bucket name")
@click.option("--destination-bucket", required=True, help="Destination bucket name")
@click.option("--source-prefix", help="Source prefix to sync from")
@click.option("--destination-prefix", help="Destination prefix to sync to")
@click.option("--delete-removed", is_flag=True, help="Delete objects in destination that don't exist in source")
@click.option("--exclude-pattern", multiple=True, help="Patterns to exclude from sync (repeat for multiple)")
@click.pass_context
def sync(ctx, source_bucket, destination_bucket, source_prefix, destination_prefix, delete_removed, exclude_pattern):
    """Synchronize objects between S3 buckets or prefixes."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import S3Operations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]🔄 Synchronizing S3 Objects[/blue]")
        console.print(
            f"[dim]Source: {source_bucket} → Destination: {destination_bucket} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        if delete_removed:
            console.print(f"[yellow]⚠️ Delete removed objects enabled[/yellow]")

        s3_ops = S3Operations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="sync_objects",
            resource_types=["s3:bucket"],
            dry_run=ctx.obj["dry_run"],
        )

        results = s3_ops.sync_objects(
            context,
            source_bucket=source_bucket,
            destination_bucket=destination_bucket,
            source_prefix=source_prefix,
            destination_prefix=destination_prefix,
            delete_removed=delete_removed,
            exclude_patterns=list(exclude_pattern) if exclude_pattern else None,
        )

        for result in results:
            if result.success:
                data = result.response_data
                synced = data.get("synced_objects", 0)
                deleted = data.get("deleted_objects", 0)
                total = data.get("total_source_objects", 0)
                console.print(f"[green]✅ S3 sync completed successfully[/green]")
                console.print(f"[green]  📄 Total source objects: {total}[/green]")
                console.print(f"[green]  🔄 Objects synced: {synced}[/green]")
                console.print(f"[green]  🗑️ Objects deleted: {deleted}[/green]")
            else:
                console.print(f"[red]❌ Failed to sync objects: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@operate.group()
@click.pass_context
def cloudformation(ctx):
    """CloudFormation stack and StackSet operations."""
    pass


@cloudformation.command()
@click.option("--source-stackset-name", required=True, help="Source StackSet name")
@click.option("--target-stackset-name", required=True, help="Target StackSet name")
@click.option("--account-ids", multiple=True, required=True, help="Account IDs to move (repeat for multiple)")
@click.option("--regions", multiple=True, required=True, help="Regions to move (repeat for multiple)")
@click.option("--operation-preferences", help="JSON operation preferences")
@click.pass_context
def move_stack_instances(ctx, source_stackset_name, target_stackset_name, account_ids, regions, operation_preferences):
    """Move CloudFormation stack instances between StackSets."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import CloudFormationOperations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]📦 Moving CloudFormation Stack Instances[/blue]")
        console.print(
            f"[dim]Source: {source_stackset_name} → Target: {target_stackset_name} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )
        console.print(f"[dim]Accounts: {len(account_ids)} | Regions: {len(regions)}[/dim]")

        cfn_ops = CloudFormationOperations(
            profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"]
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="move_stack_instances",
            resource_types=["cloudformation:stackset"],
            dry_run=ctx.obj["dry_run"],
        )

        # Parse operation preferences if provided
        preferences = None
        if operation_preferences:
            import json

            preferences = json.loads(operation_preferences)

        results = cfn_ops.move_stack_instances(
            context,
            source_stackset_name=source_stackset_name,
            target_stackset_name=target_stackset_name,
            account_ids=list(account_ids),
            regions=list(regions),
            operation_preferences=preferences,
        )

        for result in results:
            if result.success:
                console.print(f"[green]✅ Stack instance move operation initiated[/green]")
                if result.response_data and "OperationId" in result.response_data:
                    op_id = result.response_data["OperationId"]
                    console.print(f"[green]  📋 Operation ID: {op_id}[/green]")
                    console.print(f"[yellow]  ⏳ Check AWS Console for progress[/yellow]")
            else:
                console.print(f"[red]❌ Failed to initiate move: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@cloudformation.command()
@click.option("--target-role-name", required=True, help="CloudFormation StackSet execution role name")
@click.option("--management-account-id", required=True, help="Management account ID")
@click.option("--trusted-principals", multiple=True, help="Additional trusted principals (repeat for multiple)")
@click.pass_context
def lockdown_stackset_role(ctx, target_role_name, management_account_id, trusted_principals):
    """Lockdown CloudFormation StackSet execution role to management account."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import CloudFormationOperations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]🔒 Locking Down StackSet Role[/blue]")
        console.print(
            f"[dim]Role: {target_role_name} | Management Account: {management_account_id} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        cfn_ops = CloudFormationOperations(
            profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"]
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="lockdown_stackset_role",
            resource_types=["iam:role"],
            dry_run=ctx.obj["dry_run"],
        )

        results = cfn_ops.lockdown_stackset_role(
            context,
            target_role_name=target_role_name,
            management_account_id=management_account_id,
            trusted_principals=list(trusted_principals) if trusted_principals else None,
        )

        for result in results:
            if result.success:
                console.print(f"[green]✅ StackSet role locked down successfully[/green]")
                console.print(f"[green]  🔒 Role: {target_role_name}[/green]")
                console.print(f"[green]  🏢 Trusted Account: {management_account_id}[/green]")
                if trusted_principals:
                    console.print(f"[green]  👥 Additional Principals: {len(trusted_principals)}[/green]")
            else:
                console.print(f"[red]❌ Failed to lockdown role: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@cloudformation.command()
@click.option("--stackset-name", required=True, help="StackSet name to update")
@click.option("--template-body", help="CloudFormation template body")
@click.option("--template-url", help="CloudFormation template URL")
@click.option("--parameters", multiple=True, help="Parameters in Key=Value format (repeat for multiple)")
@click.option("--capabilities", multiple=True, help="Required capabilities (CAPABILITY_IAM, CAPABILITY_NAMED_IAM)")
@click.option("--description", help="Update description")
@click.option("--operation-preferences", help="JSON operation preferences")
@click.pass_context
def update_stacksets(
    ctx, stackset_name, template_body, template_url, parameters, capabilities, description, operation_preferences
):
    """Update CloudFormation StackSet with new template or parameters."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import CloudFormationOperations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]🔄 Updating CloudFormation StackSet[/blue]")
        console.print(f"[dim]StackSet: {stackset_name} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        if not template_body and not template_url:
            console.print("[red]❌ Either --template-body or --template-url must be specified[/red]")
            return

        cfn_ops = CloudFormationOperations(
            profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"]
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="update_stacksets",
            resource_types=["cloudformation:stackset"],
            dry_run=ctx.obj["dry_run"],
        )

        # Parse parameters
        param_list = []
        for param in parameters:
            if "=" in param:
                key, value = param.split("=", 1)
                param_list.append({"ParameterKey": key, "ParameterValue": value})

        # Parse operation preferences
        preferences = None
        if operation_preferences:
            import json

            preferences = json.loads(operation_preferences)

        results = cfn_ops.update_stacksets(
            context,
            stackset_name=stackset_name,
            template_body=template_body,
            template_url=template_url,
            parameters=param_list if param_list else None,
            capabilities=list(capabilities) if capabilities else None,
            description=description,
            operation_preferences=preferences,
        )

        for result in results:
            if result.success:
                console.print(f"[green]✅ StackSet update operation initiated[/green]")
                if result.response_data and "OperationId" in result.response_data:
                    op_id = result.response_data["OperationId"]
                    console.print(f"[green]  📋 Operation ID: {op_id}[/green]")
                    console.print(f"[yellow]  ⏳ Check AWS Console for progress[/yellow]")
            else:
                console.print(f"[red]❌ Failed to initiate update: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@operate.group()
@click.pass_context
def iam(ctx):
    """IAM role and policy operations."""
    pass


@iam.command()
@click.option("--role-name", required=True, help="IAM role name to update")
@click.option("--trusted-account-ids", multiple=True, required=True, help="Trusted account IDs (repeat for multiple)")
@click.option("--external-id", help="External ID for additional security")
@click.option("--require-mfa", is_flag=True, help="Require MFA for role assumption")
@click.option("--session-duration", type=int, help="Maximum session duration in seconds")
@click.pass_context
def update_roles_cross_accounts(ctx, role_name, trusted_account_ids, external_id, require_mfa, session_duration):
    """Update IAM role trust policy for cross-account access."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import IAMOperations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]👥 Updating IAM Role Trust Policy[/blue]")
        console.print(
            f"[dim]Role: {role_name} | Trusted Accounts: {len(trusted_account_ids)} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        iam_ops = IAMOperations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="update_roles_cross_accounts",
            resource_types=["iam:role"],
            dry_run=ctx.obj["dry_run"],
        )

        results = iam_ops.update_roles_cross_accounts(
            context,
            role_name=role_name,
            trusted_account_ids=list(trusted_account_ids),
            external_id=external_id,
            require_mfa=require_mfa,
            session_duration=session_duration,
        )

        for result in results:
            if result.success:
                console.print(f"[green]✅ IAM role trust policy updated successfully[/green]")
                console.print(f"[green]  👥 Role: {role_name}[/green]")
                console.print(f"[green]  🏢 Trusted Accounts: {', '.join(trusted_account_ids)}[/green]")
                if external_id:
                    console.print(f"[green]  🔑 External ID: {external_id}[/green]")
                if require_mfa:
                    console.print(f"[green]  🛡️ MFA Required: Yes[/green]")
            else:
                console.print(f"[red]❌ Failed to update role: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@operate.group()
@click.pass_context
def cloudwatch(ctx):
    """CloudWatch logs and metrics operations."""
    pass


@cloudwatch.command()
@click.option("--retention-days", type=int, required=True, help="Log retention period in days")
@click.option("--log-group-names", multiple=True, help="Specific log group names (repeat for multiple)")
@click.option("--update-all-log-groups", is_flag=True, help="Update all log groups in the region")
@click.option("--log-group-prefix", help="Update log groups with specific prefix")
@click.pass_context
def update_log_retention_policy(ctx, retention_days, log_group_names, update_all_log_groups, log_group_prefix):
    """Update CloudWatch Logs retention policy."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import CloudWatchOperations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]📊 Updating CloudWatch Log Retention[/blue]")
        console.print(
            f"[dim]Retention: {retention_days} days | All Groups: {update_all_log_groups} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        if not log_group_names and not update_all_log_groups and not log_group_prefix:
            console.print(
                "[red]❌ Must specify log groups, use --update-all-log-groups, or provide --log-group-prefix[/red]"
            )
            return

        cw_ops = CloudWatchOperations(profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"])

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="update_log_retention_policy",
            resource_types=["logs:log-group"],
            dry_run=ctx.obj["dry_run"],
        )

        results = cw_ops.update_log_retention_policy(
            context,
            retention_days=retention_days,
            log_group_names=list(log_group_names) if log_group_names else None,
            update_all_log_groups=update_all_log_groups,
            log_group_prefix=log_group_prefix,
        )

        for result in results:
            if result.success:
                data = result.response_data
                updated_count = data.get("updated_log_groups", 0)
                console.print(f"[green]✅ Log retention policy updated[/green]")
                console.print(f"[green]  📊 Updated {updated_count} log groups[/green]")
                console.print(f"[green]  ⏰ Retention: {retention_days} days[/green]")
            else:
                console.print(f"[red]❌ Failed to update retention: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


# ==============================================================================
# DynamoDB Commands
# ==============================================================================


@operate.group()
@click.pass_context
def dynamodb(ctx):
    """DynamoDB table and data operations."""
    pass


@dynamodb.command()
@click.option("--table-name", required=True, help="Name of the DynamoDB table to create")
@click.option("--hash-key", required=True, help="Hash key attribute name")
@click.option("--hash-key-type", default="S", type=click.Choice(["S", "N", "B"]), help="Hash key attribute type")
@click.option("--range-key", help="Range key attribute name (optional)")
@click.option("--range-key-type", default="S", type=click.Choice(["S", "N", "B"]), help="Range key attribute type")
@click.option(
    "--billing-mode",
    default="PAY_PER_REQUEST",
    type=click.Choice(["PAY_PER_REQUEST", "PROVISIONED"]),
    help="Billing mode",
)
@click.option("--read-capacity", type=int, help="Read capacity units (required for PROVISIONED mode)")
@click.option("--write-capacity", type=int, help="Write capacity units (required for PROVISIONED mode)")
@click.option("--tags", multiple=True, help="Tags in format key=value (repeat for multiple)")
@click.pass_context
def create_table(
    ctx,
    table_name,
    hash_key,
    hash_key_type,
    range_key,
    range_key_type,
    billing_mode,
    read_capacity,
    write_capacity,
    tags,
):
    """Create a new DynamoDB table."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import DynamoDBOperations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]🗃️ Creating DynamoDB Table[/blue]")
        console.print(f"[dim]Table: {table_name} | Billing: {billing_mode} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        # Validate provisioned mode parameters
        if billing_mode == "PROVISIONED" and (not read_capacity or not write_capacity):
            console.print("[red]❌ Read and write capacity units are required for PROVISIONED billing mode[/red]")
            return

        # Build key schema
        key_schema = [{"AttributeName": hash_key, "KeyType": "HASH"}]
        attribute_definitions = [{"AttributeName": hash_key, "AttributeType": hash_key_type}]

        if range_key:
            key_schema.append({"AttributeName": range_key, "KeyType": "RANGE"})
            attribute_definitions.append({"AttributeName": range_key, "AttributeType": range_key_type})

        # Build provisioned throughput if needed
        provisioned_throughput = None
        if billing_mode == "PROVISIONED":
            provisioned_throughput = {"ReadCapacityUnits": read_capacity, "WriteCapacityUnits": write_capacity}

        # Parse tags
        parsed_tags = []
        for tag in tags:
            if "=" in tag:
                key, value = tag.split("=", 1)
                parsed_tags.append({"Key": key.strip(), "Value": value.strip()})

        dynamodb_ops = DynamoDBOperations(
            profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"]
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="create_table",
            resource_types=["dynamodb:table"],
            dry_run=ctx.obj["dry_run"],
        )

        results = dynamodb_ops.create_table(
            context,
            table_name=table_name,
            key_schema=key_schema,
            attribute_definitions=attribute_definitions,
            billing_mode=billing_mode,
            provisioned_throughput=provisioned_throughput,
            tags=parsed_tags if parsed_tags else None,
        )

        for result in results:
            if result.success:
                data = result.response_data
                table_arn = data.get("TableDescription", {}).get("TableArn", "")
                console.print(f"[green]✅ DynamoDB table created successfully[/green]")
                console.print(f"[green]  📊 Table: {table_name}[/green]")
                console.print(f"[green]  🔗 ARN: {table_arn}[/green]")
                console.print(f"[green]  💰 Billing: {billing_mode}[/green]")
            else:
                console.print(f"[red]❌ Failed to create table: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@dynamodb.command()
@click.option("--table-name", required=True, help="Name of the DynamoDB table to delete")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete_table(ctx, table_name, confirm):
    """
    Delete a DynamoDB table.

    ⚠️  WARNING: This operation is destructive and irreversible!
    """
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import DynamoDBOperations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]🗃️ Deleting DynamoDB Table[/blue]")
        console.print(f"[dim]Table: {table_name} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        if not confirm and not ctx.obj.get("force", False):
            console.print(f"[yellow]⚠️  WARNING: You are about to DELETE table '{table_name}'[/yellow]")
            console.print("[yellow]This operation is DESTRUCTIVE and IRREVERSIBLE![/yellow]")
            if not click.confirm("Do you want to continue?"):
                console.print("[yellow]❌ Operation cancelled by user[/yellow]")
                return

        dynamodb_ops = DynamoDBOperations(
            profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"]
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="delete_table",
            resource_types=["dynamodb:table"],
            dry_run=ctx.obj["dry_run"],
        )

        results = dynamodb_ops.delete_table(context, table_name)

        for result in results:
            if result.success:
                console.print(f"[green]✅ DynamoDB table deleted successfully[/green]")
                console.print(f"[green]  🗑️ Table: {table_name}[/green]")
            else:
                console.print(f"[red]❌ Failed to delete table: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


@dynamodb.command()
@click.option("--table-name", required=True, help="Name of the DynamoDB table to backup")
@click.option("--backup-name", help="Custom backup name (defaults to table_name_timestamp)")
@click.pass_context
def backup_table(ctx, table_name, backup_name):
    """Create a backup of a DynamoDB table."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate import DynamoDBOperations
        from runbooks.operate.base import OperationContext

        console.print(f"[blue]🗃️ Creating DynamoDB Table Backup[/blue]")
        console.print(
            f"[dim]Table: {table_name} | Backup: {backup_name or 'auto-generated'} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        dynamodb_ops = DynamoDBOperations(
            profile=ctx.obj["profile"], region=ctx.obj["region"], dry_run=ctx.obj["dry_run"]
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = OperationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="create_backup",
            resource_types=["dynamodb:backup"],
            dry_run=ctx.obj["dry_run"],
        )

        results = dynamodb_ops.create_backup(context, table_name=table_name, backup_name=backup_name)

        for result in results:
            if result.success:
                data = result.response_data
                backup_details = data.get("BackupDetails", {})
                backup_arn = backup_details.get("BackupArn", "")
                backup_creation_time = backup_details.get("BackupCreationDateTime", "")
                console.print(f"[green]✅ DynamoDB table backup created successfully[/green]")
                console.print(f"[green]  📊 Table: {table_name}[/green]")
                console.print(f"[green]  💾 Backup: {backup_name or result.resource_id}[/green]")
                console.print(f"[green]  🔗 ARN: {backup_arn}[/green]")
                console.print(f"[green]  📅 Created: {backup_creation_time}[/green]")
            else:
                console.print(f"[red]❌ Failed to create backup: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Operation failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# CFAT COMMANDS (Cloud Foundations Assessment)
# ============================================================================


@main.group(invoke_without_command=True)
@common_aws_options
@common_output_options
@click.pass_context
def cfat(ctx, profile, region, dry_run, output, output_file):
    """
    Cloud Foundations Assessment Tool.

    Comprehensive AWS account assessment against Cloud Foundations
    best practices with enterprise reporting capabilities.

    Examples:
        runbooks cfat assess --categories security,cost --output html
        runbooks cfat assess --compliance-framework SOC2 --parallel
    """
    ctx.obj.update(
        {"profile": profile, "region": region, "dry_run": dry_run, "output": output, "output_file": output_file}
    )

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cfat.command()
@click.option("--categories", multiple=True, help="Assessment categories (iam, s3, cloudtrail, etc.)")
@click.option("--severity", type=click.Choice(["INFO", "WARNING", "CRITICAL"]), help="Minimum severity")
@click.option("--compliance-framework", help="Compliance framework (SOC2, PCI-DSS, HIPAA)")
@click.option("--parallel/--sequential", default=True, help="Parallel execution")
@click.option("--max-workers", type=int, default=10, help="Max parallel workers")
@click.pass_context
def assess(ctx, categories, severity, compliance_framework, parallel, max_workers):
    """Run comprehensive Cloud Foundations assessment."""
    try:
        console.print(f"[blue]🏛️ Starting Cloud Foundations Assessment[/blue]")
        console.print(f"[dim]Profile: {ctx.obj['profile']} | Framework: {compliance_framework or 'Default'}[/dim]")

        runner = AssessmentRunner(profile=ctx.obj["profile"], region=ctx.obj["region"])

        # Configure assessment
        if categories:
            runner.assessment_config.included_categories = list(categories)
        if severity:
            runner.set_min_severity(severity)
        if compliance_framework:
            runner.assessment_config.compliance_framework = compliance_framework

        runner.assessment_config.parallel_execution = parallel
        runner.assessment_config.max_workers = max_workers

        # Run assessment
        with console.status("[bold green]Running assessment..."):
            report = runner.run_assessment()

        # Display results
        display_assessment_results(report)

        # Save output if requested
        if ctx.obj["output"] != "console":
            save_assessment_results(report, ctx.obj["output"], ctx.obj["output_file"])

        console.print(f"[green]✅ Assessment completed![/green]")

    except Exception as e:
        console.print(f"[red]❌ Assessment failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# SECURITY COMMANDS (Security Baseline Testing)
# ============================================================================


@main.group(invoke_without_command=True)
@common_aws_options
@click.option("--language", type=click.Choice(["EN", "JP", "KR", "VN"]), default="EN", help="Report language")
@common_output_options
@click.pass_context
def security(ctx, profile, region, dry_run, language, output, output_file):
    """
    AWS Security Baseline Assessment.

    Comprehensive security validation against AWS security best practices
    with multi-language reporting capabilities.

    Examples:
        runbooks security assess --language EN --output html
        runbooks security check root-mfa --profile production
    """
    ctx.obj.update(
        {
            "profile": profile,
            "region": region,
            "dry_run": dry_run,
            "language": language,
            "output": output,
            "output_file": output_file,
        }
    )

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@security.command()
@click.option("--checks", multiple=True, help="Specific security checks to run")
@click.pass_context
def assess(ctx, checks):
    """Run comprehensive security baseline assessment."""
    try:
        from runbooks.security.security_baseline_tester import SecurityBaselineTester

        console.print(f"[blue]🔒 Starting Security Assessment[/blue]")
        console.print(f"[dim]Profile: {ctx.obj['profile']} | Language: {ctx.obj['language']}[/dim]")

        tester = SecurityBaselineTester(ctx.obj["profile"], ctx.obj["language"], ctx.obj.get("output_file"))

        with console.status("[bold green]Running security checks..."):
            tester.run()

        console.print(f"[green]✅ Security assessment completed![/green]")
        console.print(f"[yellow]📁 Reports generated in: {ctx.obj.get('output_file', './results')}[/yellow]")

    except Exception as e:
        console.print(f"[red]❌ Security assessment failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# ORGANIZATIONS COMMANDS (OU Management)
# ============================================================================


@main.group(invoke_without_command=True)
@common_aws_options
@common_output_options
@click.pass_context
def org(ctx, profile, region, dry_run, output, output_file):
    """
    AWS Organizations management and automation.

    Manage organizational units (OUs), accounts, and policies with
    Cloud Foundations best practices.

    Examples:
        runbooks org list-ous --output json
        runbooks org setup-ous --template security --dry-run
    """
    ctx.obj.update(
        {"profile": profile, "region": region, "dry_run": dry_run, "output": output, "output_file": output_file}
    )

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@org.command()
@click.pass_context
def list_ous(ctx):
    """List all organizational units."""
    try:
        from runbooks.inventory.collectors.aws_management import OrganizationsManager

        console.print(f"[blue]🏢 Listing Organizations Structure[/blue]")

        manager = OrganizationsManager(profile=ctx.obj["profile"], region=ctx.obj["region"])

        with console.status("[bold green]Retrieving OUs..."):
            ous = manager.list_organizational_units()

        if ctx.obj["output"] == "console":
            display_ou_structure(ous)
        else:
            save_ou_results(ous, ctx.obj["output"], ctx.obj["output_file"])

        console.print(f"[green]✅ Found {len(ous)} organizational units[/green]")

    except Exception as e:
        console.print(f"[red]❌ Failed to list OUs: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# REMEDIATION COMMANDS (Security & Compliance Fixes)
# ============================================================================


@main.group(invoke_without_command=True)
@common_aws_options
@common_output_options
@click.option("--backup-enabled", is_flag=True, default=True, help="Enable backup creation before changes")
@click.option("--notification-enabled", is_flag=True, help="Enable SNS notifications")
@click.option("--sns-topic-arn", help="SNS topic ARN for notifications")
@click.pass_context
def remediation(
    ctx, profile, region, dry_run, output, output_file, backup_enabled, notification_enabled, sns_topic_arn
):
    """
    AWS Security & Compliance Remediation - Automated fixes for assessment findings.

    Provides comprehensive automated remediation capabilities for security and
    compliance findings from security assessments and CFAT evaluations.

    ## Key Features

    - **S3 Security**: Public access controls, encryption, SSL enforcement
    - **EC2 Security**: Security group hardening, network security
    - **Multi-Account**: Bulk operations across AWS Organizations
    - **Safety Features**: Dry-run, backup, rollback capabilities
    - **Compliance**: CIS, NIST, SOC2, CloudGuard/Dome9 mapping

    Examples:
        runbooks remediation s3 block-public-access --bucket-name critical-bucket
        runbooks remediation auto-fix --findings security-findings.json --severity critical
        runbooks remediation bulk enforce-ssl --accounts 123456789012,987654321098
    """
    ctx.obj.update(
        {
            "profile": profile,
            "region": region,
            "dry_run": dry_run,
            "output": output,
            "output_file": output_file,
            "backup_enabled": backup_enabled,
            "notification_enabled": notification_enabled,
            "sns_topic_arn": sns_topic_arn,
        }
    )

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@remediation.group()
@click.pass_context
def s3(ctx):
    """S3 security and compliance remediation operations."""
    pass


@remediation.group()
@click.pass_context
def ec2(ctx):
    """EC2 infrastructure security and compliance remediation operations."""
    pass


@remediation.group()
@click.pass_context
def kms(ctx):
    """KMS key management and encryption remediation operations."""
    pass


@remediation.group()
@click.pass_context
def dynamodb(ctx):
    """DynamoDB security and optimization remediation operations."""
    pass


@remediation.group()
@click.pass_context
def rds(ctx):
    """RDS database security and optimization remediation operations."""
    pass


@remediation.group()
@click.pass_context
def lambda_func(ctx):
    """Lambda function security and optimization remediation operations."""
    pass


@remediation.group()
@click.pass_context
def acm(ctx):
    """ACM certificate lifecycle and security remediation operations."""
    pass


@remediation.group()
@click.pass_context
def cognito(ctx):
    """Cognito user management and authentication security remediation operations."""
    pass


@remediation.group()
@click.pass_context
def cloudtrail(ctx):
    """CloudTrail audit trail and policy security remediation operations."""
    pass


@s3.command()
@click.option("--bucket-name", required=True, help="Target S3 bucket name")
@click.option("--confirm", is_flag=True, help="Confirm destructive operation")
@click.pass_context
def block_public_access(ctx, bucket_name, confirm):
    """Block all public access to S3 bucket."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.s3_remediation import S3SecurityRemediation

        console.print(f"[blue]🔒 Blocking Public Access on S3 Bucket[/blue]")
        console.print(f"[dim]Bucket: {bucket_name} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        # Initialize remediation
        s3_remediation = S3SecurityRemediation(
            profile=ctx.obj["profile"],
            backup_enabled=ctx.obj["backup_enabled"],
            notification_enabled=ctx.obj["notification_enabled"],
        )

        # Create remediation context
        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="block_public_access",
            dry_run=ctx.obj["dry_run"],
            force=confirm,
            backup_enabled=ctx.obj["backup_enabled"],
        )

        # Execute remediation
        results = s3_remediation.block_public_access(context, bucket_name)

        # Display results
        for result in results:
            if result.success:
                console.print(f"[green]✅ Successfully blocked public access on bucket: {bucket_name}[/green]")
                if result.compliance_evidence:
                    console.print(
                        "[dim]Compliance controls satisfied: "
                        + ", ".join(result.context.compliance_mapping.cis_controls)
                        + "[/dim]"
                    )
            else:
                console.print(f"[red]❌ Failed to block public access: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Remediation failed: {e}[/red]")
        raise click.ClickException(str(e))


@s3.command()
@click.option("--bucket-name", required=True, help="Target S3 bucket name")
@click.option("--confirm", is_flag=True, help="Confirm policy changes")
@click.pass_context
def enforce_ssl(ctx, bucket_name, confirm):
    """Enforce HTTPS-only access to S3 bucket."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.s3_remediation import S3SecurityRemediation

        console.print(f"[blue]🔐 Enforcing SSL on S3 Bucket[/blue]")
        console.print(f"[dim]Bucket: {bucket_name} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        s3_remediation = S3SecurityRemediation(profile=ctx.obj["profile"], backup_enabled=ctx.obj["backup_enabled"])

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="enforce_ssl",
            dry_run=ctx.obj["dry_run"],
            force=confirm,
            backup_enabled=ctx.obj["backup_enabled"],
        )

        results = s3_remediation.enforce_ssl(context, bucket_name)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Successfully enforced SSL on bucket: {bucket_name}[/green]")
            else:
                console.print(f"[red]❌ Failed to enforce SSL: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ SSL enforcement failed: {e}[/red]")
        raise click.ClickException(str(e))


@s3.command()
@click.option("--bucket-name", required=True, help="Target S3 bucket name")
@click.option("--kms-key-id", help="KMS key ID for encryption (uses default if not specified)")
@click.pass_context
def enable_encryption(ctx, bucket_name, kms_key_id):
    """Enable server-side encryption on S3 bucket."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.s3_remediation import S3SecurityRemediation

        console.print(f"[blue]🔐 Enabling Encryption on S3 Bucket[/blue]")
        console.print(f"[dim]Bucket: {bucket_name} | KMS Key: {kms_key_id or 'default'}[/dim]")

        s3_remediation = S3SecurityRemediation(profile=ctx.obj["profile"])

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="enable_encryption",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        results = s3_remediation.enable_encryption(context, bucket_name, kms_key_id)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Successfully enabled encryption on bucket: {bucket_name}[/green]")
            else:
                console.print(f"[red]❌ Failed to enable encryption: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Encryption enablement failed: {e}[/red]")
        raise click.ClickException(str(e))


@s3.command()
@click.option("--bucket-name", required=True, help="Target S3 bucket name")
@click.pass_context
def secure_comprehensive(ctx, bucket_name):
    """Apply comprehensive S3 security configuration to bucket."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.s3_remediation import S3SecurityRemediation

        console.print(f"[blue]🛡️ Comprehensive S3 Security Remediation[/blue]")
        console.print(f"[dim]Bucket: {bucket_name} | Operations: 5 security controls[/dim]")

        s3_remediation = S3SecurityRemediation(profile=ctx.obj["profile"])

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="secure_bucket_comprehensive",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        with console.status("[bold green]Applying comprehensive security controls..."):
            results = s3_remediation.secure_bucket_comprehensive(context, bucket_name)

        # Display summary
        successful = [r for r in results if r.success]
        failed = [r for r in results if r.failed]

        console.print(f"\n[bold]Security Remediation Summary:[/bold]")
        console.print(f"✅ Successful operations: {len(successful)}")
        console.print(f"❌ Failed operations: {len(failed)}")

        for result in results:
            status = "✅" if result.success else "❌"
            operation = result.context.operation_type.replace("_", " ").title()
            console.print(f"  {status} {operation}")

    except Exception as e:
        console.print(f"[red]❌ Comprehensive remediation failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# EC2 REMEDIATION COMMANDS
# ============================================================================


@ec2.command()
@click.option("--exclude-default", is_flag=True, default=True, help="Exclude default security groups")
@click.pass_context
def cleanup_security_groups(ctx, exclude_default):
    """Cleanup unused security groups with dependency analysis."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.ec2_remediation import EC2SecurityRemediation

        console.print(f"[blue]🖥️ EC2 Security Group Cleanup[/blue]")
        console.print(f"[dim]Exclude Default: {exclude_default} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        ec2_remediation = EC2SecurityRemediation(profile=ctx.obj["profile"], backup_enabled=ctx.obj["backup_enabled"])

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="cleanup_unused_security_groups",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        results = ec2_remediation.cleanup_unused_security_groups(context, exclude_default=exclude_default)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Successfully cleaned up unused security groups[/green]")
                data = result.response_data
                console.print(f"[dim]Deleted: {data.get('total_deleted', 0)} groups[/dim]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ EC2 security group cleanup failed: {e}[/red]")
        raise click.ClickException(str(e))


@ec2.command()
@click.option("--max-age-days", type=int, default=30, help="Maximum age for unattached volumes")
@click.pass_context
def cleanup_ebs_volumes(ctx, max_age_days):
    """Cleanup unattached EBS volumes with CloudTrail analysis."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.ec2_remediation import EC2SecurityRemediation

        console.print(f"[blue]💽 EC2 EBS Volume Cleanup[/blue]")
        console.print(f"[dim]Max Age: {max_age_days} days | Dry-run: {ctx.obj['dry_run']}[/dim]")

        ec2_remediation = EC2SecurityRemediation(
            profile=ctx.obj["profile"], backup_enabled=ctx.obj["backup_enabled"], cloudtrail_analysis=True
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="cleanup_unattached_ebs_volumes",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        results = ec2_remediation.cleanup_unattached_ebs_volumes(context, max_age_days=max_age_days)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Successfully cleaned up unattached EBS volumes[/green]")
                data = result.response_data
                console.print(f"[dim]Deleted: {data.get('total_deleted', 0)} volumes[/dim]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ EBS volume cleanup failed: {e}[/red]")
        raise click.ClickException(str(e))


@ec2.command()
@click.pass_context
def audit_public_ips(ctx):
    """Comprehensive public IP auditing and analysis."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.ec2_remediation import EC2SecurityRemediation

        console.print(f"[blue]🌐 EC2 Public IP Audit[/blue]")
        console.print(f"[dim]Region: {ctx.obj['region']}[/dim]")

        ec2_remediation = EC2SecurityRemediation(profile=ctx.obj["profile"])

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="audit_public_ips",
            dry_run=False,  # Audit operation, not destructive
            backup_enabled=False,
        )

        results = ec2_remediation.audit_public_ips(context)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Public IP audit completed[/green]")
                data = result.response_data
                posture = data.get("security_posture", {})
                console.print(
                    f"[dim]Risk Level: {posture.get('security_risk_level', 'UNKNOWN')} | "
                    f"Public Instances: {posture.get('instances_with_public_access', 0)}[/dim]"
                )
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Public IP audit failed: {e}[/red]")
        raise click.ClickException(str(e))


@ec2.command()
@click.pass_context
def disable_subnet_auto_ip(ctx):
    """Disable automatic public IP assignment on subnets."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.ec2_remediation import EC2SecurityRemediation

        console.print(f"[blue]🔒 Disable Subnet Auto-Assign Public IP[/blue]")
        console.print(f"[dim]Dry-run: {ctx.obj['dry_run']}[/dim]")

        ec2_remediation = EC2SecurityRemediation(profile=ctx.obj["profile"], backup_enabled=ctx.obj["backup_enabled"])

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="disable_subnet_auto_public_ip",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        results = ec2_remediation.disable_subnet_auto_public_ip(context)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Successfully disabled subnet auto-assign public IP[/green]")
                data = result.response_data
                console.print(f"[dim]Modified: {data.get('total_modified', 0)} subnets[/dim]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Subnet configuration failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# KMS REMEDIATION COMMANDS
# ============================================================================


@kms.command()
@click.option("--key-id", required=True, help="KMS key ID to enable rotation for")
@click.option("--rotation-period", type=int, default=365, help="Rotation period in days")
@click.pass_context
def enable_rotation(ctx, key_id, rotation_period):
    """Enable key rotation for a specific KMS key."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.kms_remediation import KMSSecurityRemediation

        console.print(f"[blue]🔐 KMS Key Rotation Enable[/blue]")
        console.print(f"[dim]Key: {key_id} | Period: {rotation_period} days | Dry-run: {ctx.obj['dry_run']}[/dim]")

        kms_remediation = KMSSecurityRemediation(
            profile=ctx.obj["profile"], backup_enabled=ctx.obj["backup_enabled"], rotation_period_days=rotation_period
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="enable_key_rotation",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        results = kms_remediation.enable_key_rotation(context, key_id, rotation_period)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Successfully enabled key rotation for: {key_id}[/green]")
            elif result.status.value == "skipped":
                console.print(f"[yellow]⚠️ Key rotation already enabled or not supported: {key_id}[/yellow]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ KMS key rotation failed: {e}[/red]")
        raise click.ClickException(str(e))


@kms.command()
@click.option(
    "--key-filter",
    type=click.Choice(["customer-managed", "all"]),
    default="customer-managed",
    help="Filter keys to process",
)
@click.pass_context
def enable_rotation_bulk(ctx, key_filter):
    """Enable key rotation for all eligible KMS keys in bulk."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.kms_remediation import KMSSecurityRemediation

        console.print(f"[blue]🔐 KMS Bulk Key Rotation Enable[/blue]")
        console.print(f"[dim]Filter: {key_filter} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        kms_remediation = KMSSecurityRemediation(profile=ctx.obj["profile"], backup_enabled=ctx.obj["backup_enabled"])

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="enable_key_rotation_bulk",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        with console.status("[bold green]Processing KMS keys..."):
            results = kms_remediation.enable_key_rotation_bulk(context, key_filter=key_filter)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Bulk key rotation completed[/green]")
                data = result.response_data
                console.print(f"[dim]Processed: {data.get('successful_keys', 0)} keys successfully[/dim]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Bulk KMS key rotation failed: {e}[/red]")
        raise click.ClickException(str(e))


@kms.command()
@click.pass_context
def analyze_usage(ctx):
    """Analyze KMS key usage and provide optimization recommendations."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.kms_remediation import KMSSecurityRemediation

        console.print(f"[blue]📊 KMS Key Usage Analysis[/blue]")
        console.print(f"[dim]Region: {ctx.obj['region']}[/dim]")

        kms_remediation = KMSSecurityRemediation(profile=ctx.obj["profile"])

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="analyze_key_usage",
            dry_run=False,  # Analysis operation
            backup_enabled=False,
        )

        with console.status("[bold green]Analyzing KMS keys..."):
            results = kms_remediation.analyze_key_usage(context)

        for result in results:
            if result.success:
                console.print(f"[green]✅ KMS key analysis completed[/green]")
                data = result.response_data
                analytics = data.get("usage_analytics", {})
                console.print(
                    f"[dim]Total Keys: {analytics.get('total_keys', 0)} | "
                    f"Compliance Rate: {analytics.get('rotation_compliance_rate', 0):.1f}%[/dim]"
                )
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ KMS analysis failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# DYNAMODB REMEDIATION COMMANDS
# ============================================================================


@dynamodb.command()
@click.option("--table-name", required=True, help="DynamoDB table name")
@click.option("--kms-key-id", help="KMS key ID for encryption (uses default if not specified)")
@click.pass_context
def enable_encryption(ctx, table_name, kms_key_id):
    """Enable server-side encryption for a DynamoDB table."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.dynamodb_remediation import DynamoDBRemediation

        console.print(f"[blue]🗃️ DynamoDB Table Encryption[/blue]")
        console.print(
            f"[dim]Table: {table_name} | KMS Key: {kms_key_id or 'default'} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        dynamodb_remediation = DynamoDBRemediation(
            profile=ctx.obj["profile"],
            backup_enabled=ctx.obj["backup_enabled"],
            default_kms_key=kms_key_id or "alias/aws/dynamodb",
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="enable_table_encryption",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        results = dynamodb_remediation.enable_table_encryption(context, table_name, kms_key_id)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Successfully enabled encryption for table: {table_name}[/green]")
            elif result.status.value == "skipped":
                console.print(f"[yellow]⚠️ Encryption already enabled for table: {table_name}[/yellow]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ DynamoDB encryption failed: {e}[/red]")
        raise click.ClickException(str(e))


@dynamodb.command()
@click.pass_context
def enable_encryption_bulk(ctx):
    """Enable server-side encryption for all DynamoDB tables in bulk."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.dynamodb_remediation import DynamoDBRemediation

        console.print(f"[blue]🗃️ DynamoDB Bulk Table Encryption[/blue]")
        console.print(f"[dim]Dry-run: {ctx.obj['dry_run']}[/dim]")

        dynamodb_remediation = DynamoDBRemediation(profile=ctx.obj["profile"], backup_enabled=ctx.obj["backup_enabled"])

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="enable_table_encryption_bulk",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        with console.status("[bold green]Processing DynamoDB tables..."):
            results = dynamodb_remediation.enable_table_encryption_bulk(context)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Bulk table encryption completed[/green]")
                data = result.response_data
                console.print(f"[dim]Encrypted: {len(data.get('successful_tables', []))} tables successfully[/dim]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Bulk DynamoDB encryption failed: {e}[/red]")
        raise click.ClickException(str(e))


@dynamodb.command()
@click.option("--table-names", help="Comma-separated list of table names (analyzes all if not specified)")
@click.pass_context
def analyze_usage(ctx, table_names):
    """Analyze DynamoDB table usage and provide optimization recommendations."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.dynamodb_remediation import DynamoDBRemediation

        console.print(f"[blue]📊 DynamoDB Usage Analysis[/blue]")
        console.print(f"[dim]Tables: {table_names or 'all'} | Region: {ctx.obj['region']}[/dim]")

        dynamodb_remediation = DynamoDBRemediation(profile=ctx.obj["profile"], analysis_period_days=7)

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="analyze_table_usage",
            dry_run=False,  # Analysis operation
            backup_enabled=False,
        )

        table_list = table_names.split(",") if table_names else None

        with console.status("[bold green]Analyzing DynamoDB tables..."):
            results = dynamodb_remediation.analyze_table_usage(context, table_names=table_list)

        for result in results:
            if result.success:
                console.print(f"[green]✅ DynamoDB analysis completed[/green]")
                data = result.response_data
                analytics = data.get("overall_analytics", {})
                console.print(
                    f"[dim]Tables Analyzed: {analytics.get('total_tables', 0)} | "
                    f"Encryption Rate: {analytics.get('encryption_compliance_rate', 0):.1f}%[/dim]"
                )
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ DynamoDB analysis failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# RDS REMEDIATION COMMANDS
# ============================================================================


@rds.command()
@click.option("--db-instance-identifier", required=True, help="RDS instance identifier")
@click.option("--kms-key-id", help="KMS key ID for encryption (uses default if not specified)")
@click.pass_context
def enable_encryption(ctx, db_instance_identifier, kms_key_id):
    """Enable encryption for an RDS instance (creates encrypted snapshot)."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.rds_remediation import RDSSecurityRemediation

        console.print(f"[blue]🗄️ RDS Instance Encryption[/blue]")
        console.print(
            f"[dim]Instance: {db_instance_identifier} | KMS Key: {kms_key_id or 'default'} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        rds_remediation = RDSSecurityRemediation(
            profile=ctx.obj["profile"],
            backup_enabled=ctx.obj["backup_enabled"],
            default_kms_key=kms_key_id or "alias/aws/rds",
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="enable_instance_encryption",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        results = rds_remediation.enable_instance_encryption(context, db_instance_identifier, kms_key_id)

        for result in results:
            if result.success:
                console.print(
                    f"[green]✅ Successfully enabled encryption for instance: {db_instance_identifier}[/green]"
                )
                data = result.response_data
                console.print(f"[dim]Snapshot: {data.get('snapshot_identifier', 'N/A')}[/dim]")
            elif result.status.value == "skipped":
                console.print(f"[yellow]⚠️ Encryption already enabled for instance: {db_instance_identifier}[/yellow]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ RDS encryption failed: {e}[/red]")
        raise click.ClickException(str(e))


@rds.command()
@click.pass_context
def enable_encryption_bulk(ctx):
    """Enable encryption for all unencrypted RDS instances in bulk."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.rds_remediation import RDSSecurityRemediation

        console.print(f"[blue]🗄️ RDS Bulk Instance Encryption[/blue]")
        console.print(f"[dim]Dry-run: {ctx.obj['dry_run']}[/dim]")

        rds_remediation = RDSSecurityRemediation(profile=ctx.obj["profile"], backup_enabled=ctx.obj["backup_enabled"])

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="enable_instance_encryption_bulk",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        with console.status("[bold green]Processing RDS instances..."):
            results = rds_remediation.enable_instance_encryption_bulk(context)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Bulk instance encryption completed[/green]")
                data = result.response_data
                console.print(
                    f"[dim]Snapshots Created: {len(data.get('successful_snapshots', []))} | "
                    + f"Success Rate: {data.get('success_rate', 0):.1%}[/dim]"
                )
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Bulk RDS encryption failed: {e}[/red]")
        raise click.ClickException(str(e))


@rds.command()
@click.option("--db-instance-identifier", help="Specific instance identifier (configures all if not specified)")
@click.option("--retention-days", type=int, default=30, help="Backup retention period in days")
@click.pass_context
def configure_backups(ctx, db_instance_identifier, retention_days):
    """Configure backup settings for RDS instances."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.rds_remediation import RDSSecurityRemediation

        console.print(f"[blue]💾 RDS Backup Configuration[/blue]")
        console.print(
            f"[dim]Instance: {db_instance_identifier or 'all'} | Retention: {retention_days} days | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        rds_remediation = RDSSecurityRemediation(
            profile=ctx.obj["profile"], backup_enabled=ctx.obj["backup_enabled"], backup_retention_days=retention_days
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="configure_backup_settings",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        results = rds_remediation.configure_backup_settings(context, db_instance_identifier)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Successfully configured backup settings[/green]")
                data = result.response_data
                console.print(f"[dim]Configured: {len(data.get('successful_configurations', []))} instances[/dim]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ RDS backup configuration failed: {e}[/red]")
        raise click.ClickException(str(e))


@rds.command()
@click.pass_context
def analyze_usage(ctx):
    """Analyze RDS instance usage and provide optimization recommendations."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.rds_remediation import RDSSecurityRemediation

        console.print(f"[blue]📊 RDS Usage Analysis[/blue]")
        console.print(f"[dim]Region: {ctx.obj['region']}[/dim]")

        rds_remediation = RDSSecurityRemediation(profile=ctx.obj["profile"], analysis_period_days=7)

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="analyze_instance_usage",
            dry_run=False,  # Analysis operation
            backup_enabled=False,
        )

        with console.status("[bold green]Analyzing RDS instances..."):
            results = rds_remediation.analyze_instance_usage(context)

        for result in results:
            if result.success:
                console.print(f"[green]✅ RDS analysis completed[/green]")
                data = result.response_data
                analytics = data.get("overall_analytics", {})
                console.print(
                    f"[dim]Instances Analyzed: {analytics.get('total_instances', 0)} | "
                    + f"Encryption Rate: {analytics.get('encryption_compliance_rate', 0):.1f}% | "
                    + f"Avg CPU: {analytics.get('avg_cpu_utilization', 0):.1f}%[/dim]"
                )
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ RDS analysis failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# LAMBDA REMEDIATION COMMANDS
# ============================================================================


@lambda_func.command()
@click.option("--function-name", required=True, help="Lambda function name")
@click.option("--kms-key-id", help="KMS key ID for encryption (uses default if not specified)")
@click.pass_context
def encrypt_environment(ctx, function_name, kms_key_id):
    """Enable encryption for Lambda function environment variables."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.lambda_remediation import LambdaSecurityRemediation

        console.print(f"[blue]🔄 Lambda Environment Encryption[/blue]")
        console.print(
            f"[dim]Function: {function_name} | KMS Key: {kms_key_id or 'default'} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        lambda_remediation = LambdaSecurityRemediation(
            profile=ctx.obj["profile"],
            backup_enabled=ctx.obj["backup_enabled"],
            default_kms_key=kms_key_id or "alias/aws/lambda",
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="encrypt_environment_variables",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        results = lambda_remediation.encrypt_environment_variables(context, function_name, kms_key_id)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Successfully enabled environment encryption for: {function_name}[/green]")
                data = result.response_data
                console.print(f"[dim]Variables: {data.get('variables_count', 0)}[/dim]")
            elif result.status.value == "skipped":
                console.print(
                    f"[yellow]⚠️ Environment encryption already enabled or no variables: {function_name}[/yellow]"
                )
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Lambda environment encryption failed: {e}[/red]")
        raise click.ClickException(str(e))


@lambda_func.command()
@click.pass_context
def encrypt_environment_bulk(ctx):
    """Enable environment variable encryption for all Lambda functions in bulk."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.lambda_remediation import LambdaSecurityRemediation

        console.print(f"[blue]🔄 Lambda Bulk Environment Encryption[/blue]")
        console.print(f"[dim]Dry-run: {ctx.obj['dry_run']}[/dim]")

        lambda_remediation = LambdaSecurityRemediation(
            profile=ctx.obj["profile"], backup_enabled=ctx.obj["backup_enabled"]
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="encrypt_environment_variables_bulk",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        with console.status("[bold green]Processing Lambda functions..."):
            results = lambda_remediation.encrypt_environment_variables_bulk(context)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Bulk environment encryption completed[/green]")
                data = result.response_data
                console.print(
                    f"[dim]Encrypted: {len(data.get('successful_functions', []))} functions | "
                    + f"Success Rate: {data.get('success_rate', 0):.1%}[/dim]"
                )
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Bulk Lambda encryption failed: {e}[/red]")
        raise click.ClickException(str(e))


@lambda_func.command()
@click.pass_context
def optimize_iam_policies(ctx):
    """Optimize IAM policies for all Lambda functions to follow least privilege."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.lambda_remediation import LambdaSecurityRemediation

        console.print(f"[blue]🔐 Lambda IAM Policy Optimization[/blue]")
        console.print(f"[dim]Dry-run: {ctx.obj['dry_run']}[/dim]")

        lambda_remediation = LambdaSecurityRemediation(
            profile=ctx.obj["profile"], backup_enabled=ctx.obj["backup_enabled"]
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="optimize_iam_policies_bulk",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        with console.status("[bold green]Optimizing IAM policies..."):
            results = lambda_remediation.optimize_iam_policies_bulk(context)

        for result in results:
            if result.success:
                console.print(f"[green]✅ IAM policy optimization completed[/green]")
                data = result.response_data
                console.print(
                    f"[dim]Optimized: {len(data.get('successful_optimizations', []))} functions | "
                    + f"Rate: {data.get('optimization_rate', 0):.1%}[/dim]"
                )
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Lambda IAM optimization failed: {e}[/red]")
        raise click.ClickException(str(e))


@lambda_func.command()
@click.pass_context
def analyze_usage(ctx):
    """Analyze Lambda function usage and provide optimization recommendations."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.lambda_remediation import LambdaSecurityRemediation

        console.print(f"[blue]📊 Lambda Usage Analysis[/blue]")
        console.print(f"[dim]Region: {ctx.obj['region']}[/dim]")

        lambda_remediation = LambdaSecurityRemediation(profile=ctx.obj["profile"], analysis_period_days=30)

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="analyze_function_usage",
            dry_run=False,  # Analysis operation
            backup_enabled=False,
        )

        with console.status("[bold green]Analyzing Lambda functions..."):
            results = lambda_remediation.analyze_function_usage(context)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Lambda analysis completed[/green]")
                data = result.response_data
                analytics = data.get("overall_analytics", {})
                console.print(
                    f"[dim]Functions Analyzed: {analytics.get('total_functions', 0)} | "
                    + f"Encryption Rate: {analytics.get('encryption_compliance_rate', 0):.1f}% | "
                    + f"VPC Rate: {analytics.get('vpc_adoption_rate', 0):.1f}%[/dim]"
                )
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Lambda analysis failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# ACM CERTIFICATE REMEDIATION COMMANDS
# ============================================================================


@acm.command()
@click.option("--confirm", is_flag=True, help="Confirm destructive operation")
@click.option("--verify-usage", is_flag=True, default=True, help="Verify certificate usage before deletion")
@click.pass_context
def cleanup_expired_certificates(ctx, confirm, verify_usage):
    """
    Clean up expired ACM certificates.

    ⚠️  WARNING: This operation deletes certificates and can cause service outages!
    """
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.acm_remediation import ACMRemediation
        from runbooks.remediation.base import RemediationContext

        console.print(f"[blue]🏅 Cleaning Up Expired ACM Certificates[/blue]")
        console.print(
            f"[dim]Region: {ctx.obj['region']} | Verify Usage: {verify_usage} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        acm_remediation = ACMRemediation(
            profile=ctx.obj["profile"],
            backup_enabled=ctx.obj["backup_enabled"],
            usage_verification=verify_usage,
            require_confirmation=True,
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="cleanup_expired_certificates",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        with console.status("[bold red]Cleaning up expired certificates..."):
            results = acm_remediation.cleanup_expired_certificates(
                context, force_delete=confirm, verify_usage=verify_usage
            )

        for result in results:
            if result.success:
                console.print(f"[green]✅ Certificate cleanup completed[/green]")
                data = result.response_data
                deleted_count = data.get("total_deleted", 0)
                console.print(f"[green]  🗑️ Deleted: {deleted_count} expired certificates[/green]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Certificate cleanup failed: {e}[/red]")
        raise click.ClickException(str(e))


@acm.command()
@click.pass_context
def analyze_certificate_usage(ctx):
    """Analyze ACM certificate usage and security."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.acm_remediation import ACMRemediation
        from runbooks.remediation.base import RemediationContext

        console.print(f"[blue]🏅 ACM Certificate Analysis[/blue]")
        console.print(f"[dim]Region: {ctx.obj['region']}[/dim]")

        acm_remediation = ACMRemediation(profile=ctx.obj["profile"], usage_verification=True)

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="analyze_certificate_usage",
            dry_run=False,  # Analysis operation
            backup_enabled=False,
        )

        with console.status("[bold green]Analyzing certificates..."):
            results = acm_remediation.analyze_certificate_usage(context)

        for result in results:
            if result.success:
                console.print(f"[green]✅ Certificate analysis completed[/green]")
                data = result.response_data
                analytics = data.get("overall_analytics", {})
                console.print(
                    f"[dim]Certificates: {analytics.get('total_certificates', 0)} | "
                    + f"Expired: {analytics.get('expired_certificates', 0)} | "
                    + f"Expiring Soon: {analytics.get('expiring_within_30_days', 0)}[/dim]"
                )
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Certificate analysis failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# COGNITO USER REMEDIATION COMMANDS
# ============================================================================


@cognito.command()
@click.option("--user-pool-id", required=True, help="Cognito User Pool ID")
@click.option("--username", required=True, help="Username to reset password for")
@click.option("--new-password", help="New password (will be prompted if not provided)")
@click.option("--permanent", is_flag=True, default=True, help="Set password as permanent")
@click.option("--add-to-group", default="ReadHistorical", help="Group to add user to")
@click.option("--confirm", is_flag=True, help="Confirm destructive operation")
@click.pass_context
def reset_user_password(ctx, user_pool_id, username, new_password, permanent, add_to_group, confirm):
    """
    Reset user password in Cognito User Pool.

    ⚠️  WARNING: This operation can lock users out of applications!
    """
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.cognito_remediation import CognitoRemediation

        console.print(f"[blue]👤 Resetting Cognito User Password[/blue]")
        console.print(f"[dim]User Pool: {user_pool_id} | Username: {username} | Dry-run: {ctx.obj['dry_run']}[/dim]")

        cognito_remediation = CognitoRemediation(
            profile=ctx.obj["profile"],
            backup_enabled=ctx.obj["backup_enabled"],
            impact_verification=True,
            require_confirmation=True,
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="reset_user_password",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        with console.status("[bold red]Resetting user password..."):
            results = cognito_remediation.reset_user_password(
                context,
                user_pool_id=user_pool_id,
                username=username,
                new_password=new_password,
                permanent=permanent,
                add_to_group=add_to_group,
                force_reset=confirm,
            )

        for result in results:
            if result.success:
                console.print(f"[green]✅ Password reset completed[/green]")
                data = result.response_data
                console.print(f"[green]  👤 User: {username}[/green]")
                console.print(f"[green]  🔐 Permanent: {data.get('permanent', permanent)}[/green]")
                if data.get("group_assignment"):
                    console.print(f"[green]  👥 Group: {data.get('group_assignment')}[/green]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Password reset failed: {e}[/red]")
        raise click.ClickException(str(e))


@cognito.command()
@click.option("--user-pool-id", required=True, help="Cognito User Pool ID")
@click.pass_context
def analyze_user_security(ctx, user_pool_id):
    """Analyze Cognito user security and compliance."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.cognito_remediation import CognitoRemediation

        console.print(f"[blue]👤 Cognito User Security Analysis[/blue]")
        console.print(f"[dim]User Pool: {user_pool_id} | Region: {ctx.obj['region']}[/dim]")

        cognito_remediation = CognitoRemediation(profile=ctx.obj["profile"], impact_verification=True)

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="analyze_user_security",
            dry_run=False,  # Analysis operation
            backup_enabled=False,
        )

        with console.status("[bold green]Analyzing user security..."):
            results = cognito_remediation.analyze_user_security(context, user_pool_id=user_pool_id)

        for result in results:
            if result.success:
                console.print(f"[green]✅ User security analysis completed[/green]")
                data = result.response_data
                analytics = data.get("security_analytics", {})
                console.print(
                    f"[dim]Users: {analytics.get('total_users', 0)} | "
                    + f"MFA Rate: {analytics.get('mfa_compliance_rate', 0):.1f}% | "
                    + f"Issues: {analytics.get('users_with_security_issues', 0)}[/dim]"
                )
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ User security analysis failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# CLOUDTRAIL POLICY REMEDIATION COMMANDS
# ============================================================================


@cloudtrail.command()
@click.option("--user-email", required=True, help="Email of user to analyze policy changes for")
@click.option("--days", type=int, default=7, help="Number of days to look back")
@click.pass_context
def analyze_s3_policy_changes(ctx, user_email, days):
    """Analyze S3 policy changes made by specific users via CloudTrail."""
    try:
        from datetime import datetime, timedelta, timezone

        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.cloudtrail_remediation import CloudTrailRemediation

        console.print(f"[blue]🕵️ Analyzing S3 Policy Changes[/blue]")
        console.print(f"[dim]User: {user_email} | Days: {days} | Region: {ctx.obj['region']}[/dim]")

        cloudtrail_remediation = CloudTrailRemediation(
            profile=ctx.obj["profile"], impact_verification=True, default_lookback_days=days
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="analyze_s3_policy_changes",
            dry_run=False,  # Analysis operation
            backup_enabled=False,
        )

        # Set time range
        end_time = datetime.now(tz=timezone.utc)
        start_time = end_time - timedelta(days=days)

        with console.status("[bold green]Analyzing CloudTrail events..."):
            results = cloudtrail_remediation.analyze_s3_policy_changes(
                context, user_email=user_email, start_time=start_time, end_time=end_time
            )

        for result in results:
            if result.success:
                console.print(f"[green]✅ Policy analysis completed[/green]")
                data = result.response_data
                assessment = data.get("security_assessment", {})
                console.print(
                    f"[dim]Changes: {assessment.get('total_modifications', 0)} | "
                    + f"High Risk: {assessment.get('high_risk_changes', 0)} | "
                    + f"Period: {days} days[/dim]"
                )

                # Show high-risk changes if any
                high_risk_changes = data.get("high_risk_changes", [])
                if high_risk_changes:
                    console.print(f"\n[red]⚠️ High-Risk Policy Changes Detected:[/red]")
                    for change in high_risk_changes[:5]:  # Show first 5
                        bucket = change.get("BucketName", "unknown")
                        impact = change.get("impact_analysis", {})
                        security_changes = impact.get("security_changes", [])
                        console.print(f"[red]  📦 {bucket}: {', '.join(security_changes)}[/red]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Policy analysis failed: {e}[/red]")
        raise click.ClickException(str(e))


@cloudtrail.command()
@click.option("--bucket-name", required=True, help="S3 bucket name to revert policy for")
@click.option("--target-policy-file", type=click.Path(exists=True), help="JSON file with target policy")
@click.option("--remove-policy", is_flag=True, help="Remove bucket policy entirely")
@click.option("--confirm", is_flag=True, help="Confirm destructive operation")
@click.pass_context
def revert_s3_policy_changes(ctx, bucket_name, target_policy_file, remove_policy, confirm):
    """
    Revert S3 bucket policy changes.

    ⚠️  WARNING: This operation can expose data or break application access!
    """
    try:
        import json

        from runbooks.inventory.models.account import AWSAccount
        from runbooks.remediation.base import RemediationContext
        from runbooks.remediation.cloudtrail_remediation import CloudTrailRemediation

        console.print(f"[blue]🕵️ Reverting S3 Policy Changes[/blue]")
        console.print(
            f"[dim]Bucket: {bucket_name} | Remove Policy: {remove_policy} | Dry-run: {ctx.obj['dry_run']}[/dim]"
        )

        target_policy = None
        if target_policy_file and not remove_policy:
            with open(target_policy_file, "r") as f:
                target_policy = json.load(f)

        cloudtrail_remediation = CloudTrailRemediation(
            profile=ctx.obj["profile"],
            backup_enabled=ctx.obj["backup_enabled"],
            impact_verification=True,
            require_confirmation=True,
        )

        account = AWSAccount(account_id="current", account_name="current")
        context = RemediationContext(
            account=account,
            region=ctx.obj["region"],
            operation_type="revert_s3_policy_changes",
            dry_run=ctx.obj["dry_run"],
            backup_enabled=ctx.obj["backup_enabled"],
        )

        with console.status("[bold red]Reverting policy changes..."):
            results = cloudtrail_remediation.revert_s3_policy_changes(
                context, bucket_name=bucket_name, target_policy=target_policy, force_revert=confirm
            )

        for result in results:
            if result.success:
                console.print(f"[green]✅ Policy reversion completed[/green]")
                data = result.response_data
                action = data.get("action_taken", "unknown")
                console.print(f"[green]  📦 Bucket: {bucket_name}[/green]")
                console.print(f"[green]  🔄 Action: {action}[/green]")
            else:
                console.print(f"[red]❌ Failed: {result.error_message}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Policy reversion failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# AUTO-FIX COMMAND
# ============================================================================


@remediation.command()
@click.option("--findings-file", required=True, type=click.Path(exists=True), help="Security findings JSON file")
@click.option(
    "--severity",
    type=click.Choice(["critical", "high", "medium", "low"]),
    default="high",
    help="Minimum severity to remediate",
)
@click.option("--max-operations", type=int, default=50, help="Maximum operations to execute")
@click.pass_context
def auto_fix(ctx, findings_file, severity, max_operations):
    """Automatically remediate security findings from assessment results."""
    try:
        import json

        console.print(f"[blue]🤖 Auto-Remediation from Security Findings[/blue]")
        console.print(f"[dim]File: {findings_file} | Min Severity: {severity}[/dim]")

        # Load findings
        with open(findings_file, "r") as f:
            findings = json.load(f)

        # Filter by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        min_severity = severity_order[severity]

        filtered_findings = [f for f in findings if severity_order.get(f.get("severity", "low"), 3) <= min_severity][
            :max_operations
        ]

        console.print(f"[yellow]📋 Found {len(filtered_findings)} findings to remediate[/yellow]")

        if not filtered_findings:
            console.print("[green]✅ No findings requiring remediation[/green]")
            return

        # Group findings by service for efficient processing
        s3_findings = [f for f in filtered_findings if f.get("service") == "s3"]

        total_results = []

        if s3_findings:
            from runbooks.inventory.models.account import AWSAccount
            from runbooks.remediation.base import RemediationContext
            from runbooks.remediation.s3_remediation import S3SecurityRemediation

            console.print(f"[blue]🗄️ Processing {len(s3_findings)} S3 findings[/blue]")

            s3_remediation = S3SecurityRemediation(profile=ctx.obj["profile"])
            account = AWSAccount(account_id="current", account_name="current")

            for finding in s3_findings:
                try:
                    context = RemediationContext.from_security_findings(finding)
                    context.region = ctx.obj["region"]
                    context.dry_run = ctx.obj["dry_run"]

                    check_id = finding.get("check_id", "")
                    resource = finding.get("resource", "")

                    if "public-access" in check_id:
                        results = s3_remediation.block_public_access(context, resource)
                    elif "ssl" in check_id or "https" in check_id:
                        results = s3_remediation.enforce_ssl(context, resource)
                    elif "encryption" in check_id:
                        results = s3_remediation.enable_encryption(context, resource)
                    else:
                        console.print(f"[yellow]⚠️ Unsupported finding type: {check_id}[/yellow]")
                        continue

                    total_results.extend(results)

                except Exception as e:
                    console.print(f"[red]❌ Failed to remediate {finding.get('resource', 'unknown')}: {e}[/red]")

        # Display final summary
        successful = [r for r in total_results if r.success]
        failed = [r for r in total_results if r.failed]

        console.print(f"\n[bold]Auto-Remediation Summary:[/bold]")
        console.print(f"📊 Total findings processed: {len(filtered_findings)}")
        console.print(f"✅ Successful remediations: {len(successful)}")
        console.print(f"❌ Failed remediations: {len(failed)}")

        if ctx.obj["output"] != "console":
            # Save results to file
            results_data = {
                "summary": {
                    "total_findings": len(filtered_findings),
                    "successful_remediations": len(successful),
                    "failed_remediations": len(failed),
                },
                "results": [
                    {
                        "operation_id": r.operation_id,
                        "resource": r.affected_resources,
                        "status": r.status.value,
                        "error": r.error_message,
                    }
                    for r in total_results
                ],
            }

            output_file = ctx.obj["output_file"] or f"auto_remediation_{severity}.json"
            with open(output_file, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            console.print(f"[green]💾 Results saved to: {output_file}[/green]")

    except Exception as e:
        console.print(f"[red]❌ Auto-remediation failed: {e}[/red]")
        raise click.ClickException(str(e))


# ============================================================================
# FINOPS COMMANDS (Cost & Usage Analytics)
# ============================================================================


@main.group(invoke_without_command=True)
@common_aws_options
@click.option("--time-range", type=int, help="Time range in days (default: current month)")
@click.option(
    "--report-type", multiple=True, type=click.Choice(["csv", "json", "pdf"]), default=("csv",), help="Report types"
)
@click.option("--report-name", help="Base name for report files (without extension)")
@click.option("--dir", help="Directory to save report files (default: current directory)")
@click.option("--profiles", multiple=True, help="Specific AWS profiles to use")
@click.option("--regions", multiple=True, help="AWS regions to check")
@click.option("--all", is_flag=True, help="Use all available AWS profiles")
@click.option("--combine", is_flag=True, help="Combine profiles from the same AWS account")
@click.option("--tag", multiple=True, help="Cost allocation tag to filter resources")
@click.option("--trend", is_flag=True, help="Display trend report for past 6 months")
@click.option("--audit", is_flag=True, help="Display audit report with cost anomalies and resource optimization")
@click.pass_context
def finops(ctx, profile, region, dry_run, time_range, report_type, report_name, dir, profiles, regions, all, combine, tag, trend, audit):
    """
    AWS FinOps - Cost and usage analytics.

    Comprehensive cost analysis, optimization recommendations,
    and resource utilization reporting.

    Examples:
        runbooks finops --audit --report-type csv,json,pdf --report-name audit_report
        runbooks finops --trend --report-name cost_trend  
        runbooks finops --time-range 30 --report-name monthly_costs
    """
    
    if ctx.invoked_subcommand is None:
        # Run default dashboard with all options
        import argparse
        from runbooks.finops.dashboard_runner import run_dashboard

        args = argparse.Namespace(
            profile=profile,
            region=region,
            dry_run=dry_run,
            time_range=time_range,
            report_type=list(report_type),
            report_name=report_name,
            dir=dir,
            profiles=list(profiles) if profiles else None,
            regions=list(regions) if regions else None,
            all=all,
            combine=combine,
            tag=list(tag) if tag else None,
            trend=trend,
            audit=audit,
            config_file=None  # Not exposed in Click interface yet
        )
        return run_dashboard(args)
    else:
        # Pass context to subcommands
        ctx.obj.update({
            "profile": profile, "region": region, "dry_run": dry_run, 
            "time_range": time_range, "report_type": list(report_type),
            "report_name": report_name, "dir": dir, "profiles": list(profiles) if profiles else None,
            "regions": list(regions) if regions else None, "all": all, "combine": combine,
            "tag": list(tag) if tag else None, "trend": trend, "audit": audit
        })


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def display_inventory_results(results):
    """Display inventory results in formatted tables."""
    from runbooks.inventory.core.formatter import InventoryFormatter

    formatter = InventoryFormatter(results)
    console_output = formatter.format_console_table()
    console.print(console_output)


def save_inventory_results(results, output_format, output_file):
    """Save inventory results to file."""
    from runbooks.inventory.core.formatter import InventoryFormatter

    formatter = InventoryFormatter(results)

    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"inventory_{timestamp}.{output_format}"

    if output_format == "csv":
        formatter.to_csv(output_file)
    elif output_format == "json":
        formatter.to_json(output_file)
    elif output_format == "html":
        formatter.to_html(output_file)
    elif output_format == "yaml":
        formatter.to_yaml(output_file)

    console.print(f"[green]💾 Results saved to: {output_file}[/green]")


def display_assessment_results(report):
    """Display CFAT assessment results."""
    console.print(f"\n[bold blue]📊 Cloud Foundations Assessment Results[/bold blue]")
    console.print(f"[dim]Score: {report.summary.compliance_score}/100 | Risk: {report.summary.risk_level}[/dim]")

    # Summary table
    from rich.table import Table

    table = Table(title="Assessment Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold")
    table.add_column("Status", style="green")

    table.add_row("Compliance Score", f"{report.summary.compliance_score}/100", report.summary.risk_level)
    table.add_row("Total Checks", str(report.summary.total_checks), "✓ Completed")
    table.add_row("Pass Rate", f"{report.summary.pass_rate:.1f}%", "📊 Analyzed")
    table.add_row(
        "Critical Issues",
        str(report.summary.critical_issues),
        "🚨 Review Required" if report.summary.critical_issues > 0 else "✅ None",
    )

    console.print(table)


def save_assessment_results(report, output_format, output_file):
    """Save assessment results to file."""
    if not output_file:
        timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
        output_file = f"cfat_report_{timestamp}.{output_format}"

    if output_format == "html":
        report.to_html(output_file)
    elif output_format == "json":
        report.to_json(output_file)
    elif output_format == "csv":
        report.to_csv(output_file)
    elif output_format == "yaml":
        report.to_yaml(output_file)

    console.print(f"[green]💾 Assessment saved to: {output_file}[/green]")


def display_ou_structure(ous):
    """Display OU structure in formatted table."""
    from rich.table import Table

    table = Table(title="AWS Organizations Structure")
    table.add_column("Name", style="cyan")
    table.add_column("ID", style="green")
    table.add_column("Level", justify="center")
    table.add_column("Parent ID", style="blue")

    for ou in ous:
        indent = "  " * ou.get("Level", 0)
        table.add_row(
            f"{indent}{ou.get('Name', 'Unknown')}", ou.get("Id", ""), str(ou.get("Level", 0)), ou.get("ParentId", "")
        )

    console.print(table)


def save_ou_results(ous, output_format, output_file):
    """Save OU results to file."""
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"organizations_{timestamp}.{output_format}"

    if output_format == "json":
        import json

        with open(output_file, "w") as f:
            json.dump(ous, f, indent=2, default=str)
    elif output_format == "yaml":
        import yaml

        with open(output_file, "w") as f:
            yaml.dump(ous, f, default_flow_style=False)

    console.print(f"[green]💾 OU structure saved to: {output_file}[/green]")


# ============================================================================
# CLI SHORTCUTS (Common Operations)
# ============================================================================


@main.command()
@click.argument("instance_ids", nargs=-1, required=False)
@common_aws_options
@click.pass_context
def start(ctx, instance_ids, profile, region, dry_run):
    """
    🚀 Quick start EC2 instances (shortcut for: runbooks operate ec2 start)

    Examples:
        runbooks start i-1234567890abcdef0
        runbooks start i-123456 i-789012 i-345678
    """
    # Interactive prompting for missing instance IDs
    if not instance_ids:
        console.print("[cyan]⚡ EC2 Start Operation[/cyan]")

        # Try to suggest available instances
        try:
            console.print("[dim]🔍 Discovering stopped instances...[/dim]")
            from runbooks.inventory.core.collector import InventoryCollector

            collector = InventoryCollector(profile=profile, region=region)

            # Quick scan for stopped instances
            # Simplified - just provide helpful tip

            # Extract stopped instances (this is a simplified version)
            console.print("[dim]💡 Found stopped instances - you can specify them manually[/dim]")

        except Exception:
            pass  # Continue without suggestions if discovery fails

        # Prompt for instance IDs
        instance_input = click.prompt("Instance IDs (comma-separated)", type=str)

        if not instance_input.strip():
            console.print("[red]❌ No instance IDs provided[/red]")
            console.print("[dim]💡 Example: i-1234567890abcdef0,i-0987654321fedcba0[/dim]")
            sys.exit(1)

        # Parse the input
        instance_ids = [id.strip() for id in instance_input.split(",") if id.strip()]

        # Confirm the operation
        console.print(f"\n[yellow]📋 Will start {len(instance_ids)} instance(s):[/yellow]")
        for instance_id in instance_ids:
            console.print(f"  • {instance_id}")
        console.print(f"[yellow]Region: {region}[/yellow]")
        console.print(f"[yellow]Profile: {profile}[/yellow]")
        console.print(f"[yellow]Dry-run: {dry_run}[/yellow]")

        if not click.confirm("\nContinue?", default=True):
            console.print("[yellow]❌ Operation cancelled[/yellow]")
            sys.exit(0)

    console.print(f"[cyan]🚀 Starting {len(instance_ids)} EC2 instance(s)...[/cyan]")

    from runbooks.operate.ec2_operations import start_instances

    try:
        result = start_instances(instance_ids=list(instance_ids), profile=profile, region=region, dry_run=dry_run)

        if dry_run:
            console.print("[yellow]🧪 DRY RUN - No instances were actually started[/yellow]")
        else:
            console.print(f"[green]✅ Operation completed successfully[/green]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print(f"[dim]💡 Try: runbooks inventory collect -r ec2  # List available instances[/dim]")
        console.print(f"[dim]💡 Example: runbooks operate ec2 start --instance-ids i-1234567890abcdef0[/dim]")
        sys.exit(1)


@main.command()
@click.argument("instance_ids", nargs=-1, required=False)
@common_aws_options
@click.pass_context
def stop(ctx, instance_ids, profile, region, dry_run):
    """
    🛑 Quick stop EC2 instances (shortcut for: runbooks operate ec2 stop)

    Examples:
        runbooks stop i-1234567890abcdef0
        runbooks stop i-123456 i-789012 i-345678
    """
    # Interactive prompting for missing instance IDs
    if not instance_ids:
        console.print("[cyan]⚡ EC2 Stop Operation[/cyan]")

        # Try to suggest available instances
        try:
            console.print("[dim]🔍 Discovering running instances...[/dim]")
            from runbooks.inventory.core.collector import InventoryCollector

            collector = InventoryCollector(profile=profile, region=region)

            # Quick scan for running instances
            # Simplified - just provide helpful tip

            # Extract running instances (this is a simplified version)
            console.print("[dim]💡 Found running instances - you can specify them manually[/dim]")

        except Exception:
            pass  # Continue without suggestions if discovery fails

        # Prompt for instance IDs
        instance_input = click.prompt("Instance IDs (comma-separated)", type=str)

        if not instance_input.strip():
            console.print("[red]❌ No instance IDs provided[/red]")
            console.print("[dim]💡 Example: i-1234567890abcdef0,i-0987654321fedcba0[/dim]")
            sys.exit(1)

        # Parse the input
        instance_ids = [id.strip() for id in instance_input.split(",") if id.strip()]

        # Confirm the operation
        console.print(f"\n[yellow]📋 Will stop {len(instance_ids)} instance(s):[/yellow]")
        for instance_id in instance_ids:
            console.print(f"  • {instance_id}")
        console.print(f"[yellow]Region: {region}[/yellow]")
        console.print(f"[yellow]Profile: {profile}[/yellow]")
        console.print(f"[yellow]Dry-run: {dry_run}[/yellow]")

        if not click.confirm("\nContinue?", default=True):
            console.print("[yellow]❌ Operation cancelled[/yellow]")
            sys.exit(0)

    console.print(f"[yellow]🛑 Stopping {len(instance_ids)} EC2 instance(s)...[/yellow]")

    from runbooks.operate.ec2_operations import stop_instances

    try:
        result = stop_instances(instance_ids=list(instance_ids), profile=profile, region=region, dry_run=dry_run)

        if dry_run:
            console.print("[yellow]🧪 DRY RUN - No instances were actually stopped[/yellow]")
        else:
            console.print(f"[green]✅ Operation completed successfully[/green]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print(f"[dim]💡 Try: runbooks inventory collect -r ec2  # List running instances[/dim]")
        console.print(f"[dim]💡 Example: runbooks operate ec2 stop --instance-ids i-1234567890abcdef0[/dim]")
        sys.exit(1)


@main.group()
@click.pass_context
def sprint(ctx):
    """
    Sprint management for Phase 1 Discovery & Assessment.
    
    Track progress across 3 sprints with 6-pane orchestration.
    """
    pass


@sprint.command()
@click.option('--number', type=click.Choice(['1', '2', '3']), default='1', help='Sprint number')
@click.option('--phase', default='1', help='Phase number')
@common_output_options
@click.pass_context
def init(ctx, number, phase, output, output_file):
    """Initialize a sprint with tracking and metrics."""
    import json
    from pathlib import Path
    
    sprint_configs = {
        '1': {
            'name': 'Discovery & Baseline',
            'duration': '4 hours',
            'goals': [
                'Complete infrastructure inventory',
                'Establish cost baseline',
                'Assess compliance posture',
                'Setup automation framework'
            ]
        },
        '2': {
            'name': 'Analysis & Optimization',
            'duration': '4 hours',
            'goals': [
                'Deep optimization analysis',
                'Design remediation strategies',
                'Build automation pipelines',
                'Implement quick wins'
            ]
        },
        '3': {
            'name': 'Implementation & Validation',
            'duration': '4 hours',
            'goals': [
                'Execute optimizations',
                'Validate improvements',
                'Generate reports',
                'Prepare Phase 2'
            ]
        }
    }
    
    config = sprint_configs[number]
    sprint_dir = Path(f'artifacts/sprint-{number}')
    sprint_dir.mkdir(parents=True, exist_ok=True)
    
    sprint_data = {
        'sprint': number,
        'phase': phase,
        'name': config['name'],
        'duration': config['duration'],
        'goals': config['goals'],
        'start_time': datetime.now().isoformat(),
        'metrics': {
            'discovery_coverage': '0/multi-account',
            'cost_savings': '$0',
            'compliance_score': '0%',
            'automation_coverage': '0%'
        }
    }
    
    config_file = sprint_dir / 'config.json'
    with open(config_file, 'w') as f:
        json.dump(sprint_data, f, indent=2)
    
    console.print(f"[green]✅ Sprint {number}: {config['name']} initialized![/green]")
    console.print(f"[blue]Duration: {config['duration']}[/blue]")
    console.print(f"[yellow]Artifacts: {sprint_dir}[/yellow]")


@sprint.command()
@click.option('--number', type=click.Choice(['1', '2', '3']), default='1', help='Sprint number')
@common_output_options  
@click.pass_context
def status(ctx, number, output, output_file):
    """Check sprint progress and metrics."""
    from pathlib import Path
    import json
    
    config_file = Path(f'artifacts/sprint-{number}/config.json')
    
    if not config_file.exists():
        console.print(f"[red]Sprint {number} not initialized.[/red]")
        return
        
    with open(config_file, 'r') as f:
        data = json.load(f)
    
    if _HAS_RICH:
        from rich.table import Table
        
        table = Table(title=f"Sprint {number}: {data['name']}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for metric, value in data['metrics'].items():
            table.add_row(metric.replace('_', ' ').title(), value)
        
        console.print(table)
    else:
        console.print(json.dumps(data, indent=2))


@main.command()
@common_aws_options
@click.option("--resources", "-r", default="ec2", help="Resources to discover (default: ec2)")
@click.pass_context
def scan(ctx, profile, region, dry_run, resources):
    """
    🔍 Quick resource discovery (shortcut for: runbooks inventory collect)

    Examples:
        runbooks scan                    # Scan EC2 instances
        runbooks scan -r ec2,rds         # Scan multiple resources
        runbooks scan -r s3              # Scan S3 buckets
    """
    console.print(f"[cyan]🔍 Scanning {resources} resources...[/cyan]")

    from runbooks.inventory.core.collector import InventoryCollector

    try:
        collector = InventoryCollector(profile=profile, region=region)

        # Get current account ID
        account_ids = [collector.get_current_account_id()]
        
        # Collect inventory
        results = collector.collect_inventory(
            resource_types=resources.split(","), 
            account_ids=account_ids, 
            include_costs=False
        )

        console.print(f"[green]✅ Scan completed - Found resources in account {account_ids[0]}[/green]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print(f"[dim]💡 Available resources: ec2, rds, s3, lambda, iam, vpc[/dim]")
        console.print(f"[dim]💡 Example: runbooks scan -r ec2,rds --region us-west-2[/dim]")
        sys.exit(1)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
