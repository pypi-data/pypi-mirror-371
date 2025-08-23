"""
Enterprise-Grade EC2 Operations Module.

Comprehensive EC2 resource management with Lambda support, environment configuration,
SNS notifications, and full compatibility with original AWS Cloud Foundations scripts.

Migrated and enhanced from:
- aws/ec2_terminate_instances.py (with Lambda handler)
- aws/ec2_start_stop_instances.py (with state management)
- aws/ec2_run_instances.py (with block device mappings)
- aws/ec2_copy_image_cross-region.py (with image creation)
- aws/ec2_ebs_snapshots_delete.py (with safety checks)
- aws/ec2_unused_volumes.py (with SNS notifications)
- aws/ec2_unused_eips.py (with comprehensive scanning)

Author: CloudOps DevOps Engineer
Date: 2025-01-21
Version: 2.0.0 - Enterprise Enhancement
"""

import base64
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from loguru import logger

from runbooks.operate.base import BaseOperation, OperationContext, OperationResult, OperationStatus


class EC2Operations(BaseOperation):
    """
    Enterprise-grade EC2 resource operations and lifecycle management.

    Handles all EC2-related operational tasks including instance management,
    volume operations, AMI operations, resource cleanup, and notifications.
    Supports environment variable configuration and AWS Lambda execution.
    """

    service_name = "ec2"
    supported_operations = {
        "start_instances",
        "stop_instances",
        "terminate_instances",
        "run_instances",
        "copy_image",
        "create_image",
        "delete_snapshots",
        "cleanup_unused_volumes",
        "cleanup_unused_eips",
        "reboot_instances",
    }
    requires_confirmation = True

    def __init__(
        self,
        profile: Optional[str] = None,
        region: Optional[str] = None,
        dry_run: bool = False,
        sns_topic_arn: Optional[str] = None,
    ):
        """
        Initialize EC2 operations with enhanced configuration support.

        Args:
            profile: AWS profile name (can be overridden by AWS_PROFILE env var)
            region: AWS region (can be overridden by AWS_REGION env var)
            dry_run: Dry run mode (can be overridden by DRY_RUN env var)
            sns_topic_arn: SNS topic for notifications (can be overridden by SNS_TOPIC_ARN env var)
        """
        # Environment variable support for Lambda/Container deployment
        self.profile = profile or os.getenv("AWS_PROFILE")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.dry_run = dry_run or os.getenv("DRY_RUN", "false").lower() == "true"
        self.sns_topic_arn = sns_topic_arn or os.getenv("SNS_TOPIC_ARN")

        super().__init__(self.profile, self.region, self.dry_run)

        # Initialize SNS client for notifications
        self.sns_client = None
        if self.sns_topic_arn:
            self.sns_client = self.get_client("sns", self.region)

    def validate_sns_arn(self, arn: str) -> None:
        """
        Validates the format of the SNS Topic ARN.

        Args:
            arn: SNS Topic ARN

        Raises:
            ValueError: If the ARN format is invalid
        """
        if not arn.startswith("arn:aws:sns:"):
            raise ValueError(f"Invalid SNS Topic ARN: {arn}")
        logger.info(f"✅ Valid SNS ARN: {arn}")

    def validate_regions(self, source_region: str, dest_region: str) -> None:
        """
        Validates AWS regions for cross-region operations.

        Args:
            source_region: Source AWS region
            dest_region: Destination AWS region

        Raises:
            ValueError: If regions are invalid
        """
        session = boto3.session.Session()
        valid_regions = session.get_available_regions("ec2")

        if source_region not in valid_regions:
            raise ValueError(f"Invalid source region: {source_region}")
        if dest_region not in valid_regions:
            raise ValueError(f"Invalid destination region: {dest_region}")
        logger.info(f"Validated AWS regions: {source_region} -> {dest_region}")

    def send_sns_notification(self, subject: str, message: str) -> None:
        """
        Send SNS notification if configured.

        Args:
            subject: Notification subject
            message: Notification message
        """
        if self.sns_client and self.sns_topic_arn:
            try:
                self.sns_client.publish(TopicArn=self.sns_topic_arn, Subject=subject, Message=message)
                logger.info(f"SNS notification sent: {subject}")
            except ClientError as e:
                logger.warning(f"Failed to send SNS notification: {e}")

    def get_default_block_device_mappings(self, volume_size: int = 20, encrypted: bool = True) -> List[Dict]:
        """
        Get default block device mappings with modern EBS configuration.

        Args:
            volume_size: EBS volume size in GB
            encrypted: Whether to encrypt the EBS volume

        Returns:
            Block device mappings configuration
        """
        return [
            {
                "DeviceName": "/dev/xvda",  # Root volume device
                "Ebs": {
                    "DeleteOnTermination": True,  # Clean up after instance termination
                    "VolumeSize": volume_size,  # Set volume size in GB
                    "VolumeType": "gp3",  # Modern, faster storage
                    "Encrypted": encrypted,  # Encrypt the EBS volume
                },
            },
        ]

    def execute_operation(self, context: OperationContext, operation_type: str, **kwargs) -> List[OperationResult]:
        """Execute EC2 operation."""
        self.validate_context(context)

        if operation_type == "start_instances":
            return self.start_instances(context, kwargs.get("instance_ids", []))
        elif operation_type == "stop_instances":
            return self.stop_instances(context, kwargs.get("instance_ids", []))
        elif operation_type == "terminate_instances":
            return self.terminate_instances(context, kwargs.get("instance_ids", []))
        elif operation_type == "run_instances":
            return self.run_instances(context, **kwargs)
        elif operation_type == "copy_image":
            return self.copy_image(context, **kwargs)
        elif operation_type == "create_image":
            return self.create_image(context, **kwargs)
        elif operation_type == "delete_snapshots":
            return self.delete_snapshots(context, kwargs.get("snapshot_ids", []))
        elif operation_type == "cleanup_unused_volumes":
            return self.cleanup_unused_volumes(context)
        elif operation_type == "cleanup_unused_eips":
            return self.cleanup_unused_eips(context)
        elif operation_type == "reboot_instances":
            return self.reboot_instances(context, kwargs.get("instance_ids", []))
        else:
            raise ValueError(f"Unsupported operation: {operation_type}")

    def start_instances(self, context: OperationContext, instance_ids: List[str]) -> List[OperationResult]:
        """Start EC2 instances."""
        ec2_client = self.get_client("ec2", context.region)
        results = []

        for instance_id in instance_ids:
            result = self.create_operation_result(context, "start_instances", "ec2:instance", instance_id)

            try:
                if context.dry_run:
                    logger.info(f"[DRY-RUN] Would start instance {instance_id}")
                    result.mark_completed(OperationStatus.DRY_RUN)
                else:
                    response = self.execute_aws_call(ec2_client, "start_instances", InstanceIds=[instance_id])
                    result.response_data = response
                    result.mark_completed(OperationStatus.SUCCESS)
                    logger.info(f"Successfully started instance {instance_id}")

            except ClientError as e:
                error_msg = f"Failed to start instance {instance_id}: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)

            results.append(result)

        return results

    def stop_instances(self, context: OperationContext, instance_ids: List[str]) -> List[OperationResult]:
        """Stop EC2 instances."""
        ec2_client = self.get_client("ec2", context.region)
        results = []

        for instance_id in instance_ids:
            result = self.create_operation_result(context, "stop_instances", "ec2:instance", instance_id)

            try:
                if context.dry_run:
                    logger.info(f"[DRY-RUN] Would stop instance {instance_id}")
                    result.mark_completed(OperationStatus.DRY_RUN)
                else:
                    response = self.execute_aws_call(ec2_client, "stop_instances", InstanceIds=[instance_id])
                    result.response_data = response
                    result.mark_completed(OperationStatus.SUCCESS)
                    logger.info(f"Successfully stopped instance {instance_id}")

            except ClientError as e:
                error_msg = f"Failed to stop instance {instance_id}: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)

            results.append(result)

        return results

    def terminate_instances(self, context: OperationContext, instance_ids: List[str]) -> List[OperationResult]:
        """
        Terminate EC2 instances (DESTRUCTIVE) with enhanced validation and notifications.

        Based on original aws/ec2_terminate_instances.py with enterprise enhancements.
        """
        # Enhanced validation from original file
        if not instance_ids or instance_ids == [""]:
            logger.error("No instance IDs provided for termination.")
            raise ValueError("Instance IDs cannot be empty.")

        ec2_client = self.get_client("ec2", context.region)
        results = []
        terminated_instances = []

        logger.info(f"Terminating instances: {', '.join(instance_ids)} in region {context.region}...")

        for instance_id in instance_ids:
            result = self.create_operation_result(context, "terminate_instances", "ec2:instance", instance_id)

            try:
                if not self.confirm_operation(context, instance_id, "terminate"):
                    result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                    results.append(result)
                    continue

                if context.dry_run:
                    logger.info(f"[DRY-RUN] No actual termination performed for {instance_id}")
                    result.mark_completed(OperationStatus.DRY_RUN)
                else:
                    response = self.execute_aws_call(ec2_client, "terminate_instances", InstanceIds=[instance_id])

                    # Enhanced logging from original file
                    for instance in response["TerminatingInstances"]:
                        logger.info(
                            f"Instance {instance['InstanceId']} state changed to {instance['CurrentState']['Name']}"
                        )

                    terminated_instances.append(instance_id)
                    result.response_data = response
                    result.mark_completed(OperationStatus.SUCCESS)
                    logger.info(f"Successfully terminated instance {instance_id}")

            except ClientError as e:
                error_msg = f"AWS Client Error: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)
            except BotoCoreError as e:
                error_msg = f"BotoCore Error: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)

            results.append(result)

        # Send SNS notification if configured
        if terminated_instances:
            message = f"Successfully terminated instances: {', '.join(terminated_instances)}"
            self.send_sns_notification("EC2 Instances Terminated", message)
            logger.info(message)
        elif not context.dry_run:
            logger.info("No instances terminated.")

        return results

    def run_instances(
        self,
        context: OperationContext,
        image_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        min_count: Optional[int] = None,
        max_count: Optional[int] = None,
        key_name: Optional[str] = None,
        security_group_ids: Optional[List[str]] = None,
        subnet_id: Optional[str] = None,
        user_data: Optional[str] = None,
        instance_profile_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        volume_size: int = 20,
        enable_monitoring: bool = False,
        enable_encryption: bool = True,
    ) -> List[OperationResult]:
        """
        Launch EC2 instances with comprehensive configuration.

        Enhanced from original aws/ec2_run_instances.py with environment variable support,
        block device mappings, monitoring, and enterprise-grade configuration.
        """
        # Environment variable support from original file
        image_id = image_id or os.getenv("AMI_ID", "ami-03f052ebc3f436d52")  # Default RHEL 9
        instance_type = instance_type or os.getenv("INSTANCE_TYPE", "t2.micro")
        min_count = min_count or int(os.getenv("MIN_COUNT", "1"))
        max_count = max_count or int(os.getenv("MAX_COUNT", "1"))
        key_name = key_name or os.getenv("KEY_NAME", "EC2Test")

        # Parse security groups and subnet from environment
        if not security_group_ids:
            env_sg = os.getenv("SECURITY_GROUP_IDS", "")
            security_group_ids = env_sg.split(",") if env_sg else []

        subnet_id = subnet_id or os.getenv("SUBNET_ID")

        # Parse tags from environment variable
        if not tags:
            env_tags = os.getenv("TAGS", '{"Project":"CloudOps", "Environment":"Dev"}')
            try:
                tags = json.loads(env_tags)
            except json.JSONDecodeError:
                tags = {"Project": "CloudOps", "Environment": "Dev"}

        # Enhanced validation from original file
        if not subnet_id:
            raise ValueError("Missing required SUBNET_ID for VPC deployment")
        if not security_group_ids:
            raise ValueError("Missing required SECURITY_GROUP_IDS for VPC deployment")

        logger.info("✅ Environment variables validated successfully.")

        ec2_client = self.get_client("ec2", context.region)

        result = self.create_operation_result(
            context, "run_instances", "ec2:instance", f"{min_count}-{max_count} instances"
        )

        try:
            logger.info(f"Launching {min_count}-{max_count} instances of type {instance_type} with AMI {image_id}...")

            if context.dry_run:
                logger.info(f"[DRY-RUN] Would launch {min_count}-{max_count} instances of {image_id}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            # Enhanced parameters from original file
            launch_params = {
                "BlockDeviceMappings": self.get_default_block_device_mappings(volume_size, enable_encryption),
                "ImageId": image_id,
                "InstanceType": instance_type,
                "MinCount": min_count,
                "MaxCount": max_count,
                "Monitoring": {"Enabled": enable_monitoring},
                "KeyName": key_name,
                "SubnetId": subnet_id,
                "SecurityGroupIds": security_group_ids,
            }

            # Optional parameters
            if user_data:
                launch_params["UserData"] = base64.b64encode(user_data.encode()).decode()
            if instance_profile_name:
                launch_params["IamInstanceProfile"] = {"Name": instance_profile_name}

            # Enhanced tagging from original file
            if tags:
                tag_specifications = [
                    {"ResourceType": "instance", "Tags": [{"Key": k, "Value": v} for k, v in tags.items()]}
                ]
                launch_params["TagSpecifications"] = tag_specifications

            response = self.execute_aws_call(ec2_client, "run_instances", **launch_params)
            instance_ids = [inst["InstanceId"] for inst in response["Instances"]]

            logger.info(f"Launched Instances: {instance_ids}")

            # Apply additional tags if needed (from original file approach)
            if tags:
                try:
                    ec2_client.create_tags(
                        Resources=instance_ids,
                        Tags=[{"Key": k, "Value": v} for k, v in tags.items()],
                    )
                    logger.info(f"✅ Applied tags to instances: {instance_ids}")
                except ClientError as e:
                    logger.warning(f"Failed to apply additional tags: {e}")

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully launched {len(instance_ids)} instances")

            # SNS notification
            message = f"Successfully launched {len(instance_ids)} instances: {', '.join(instance_ids)}"
            self.send_sns_notification("EC2 Instances Launched", message)

        except ClientError as e:
            error_msg = f"AWS Client Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except BotoCoreError as e:
            error_msg = f"BotoCore Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def copy_image(
        self,
        context: OperationContext,
        source_image_id: str,
        source_region: str,
        name: str,
        description: Optional[str] = None,
        encrypted: bool = True,
        kms_key_id: Optional[str] = None,
    ) -> List[OperationResult]:
        """
        Copy AMI across regions with encryption and validation.

        Enhanced from original aws/ec2_copy_image_cross-region.py.
        """
        # Validate regions using original file logic
        self.validate_regions(source_region, context.region)

        ec2_client = self.get_client("ec2", context.region)

        result = self.create_operation_result(
            context, "copy_image", "ec2:ami", f"{source_image_id}:{source_region}->{context.region}"
        )

        try:
            if context.dry_run:
                logger.info(f"[DRY-RUN] Would copy AMI {source_image_id} from {source_region}")
                result.mark_completed(OperationStatus.DRY_RUN)
                return [result]

            copy_params = {
                "SourceImageId": source_image_id,
                "SourceRegion": source_region,
                "Name": name,
                "Encrypted": encrypted,
            }

            if description:
                copy_params["Description"] = description
            if kms_key_id and encrypted:
                copy_params["KmsKeyId"] = kms_key_id

            response = self.execute_aws_call(ec2_client, "copy_image", **copy_params)
            new_image_id = response["ImageId"]

            result.response_data = response
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(f"Successfully initiated AMI copy. New AMI ID: {new_image_id}")

            # SNS notification
            message = f"AMI {source_image_id} copied from {source_region} to {context.region}. New AMI: {new_image_id}"
            self.send_sns_notification("EC2 AMI Copied", message)

        except ClientError as e:
            error_msg = f"AWS Client Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except BotoCoreError as e:
            error_msg = f"BotoCore Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def create_image(
        self, context: OperationContext, instance_ids: List[str], image_name_prefix: Optional[str] = None
    ) -> List[OperationResult]:
        """
        Create AMI images from EC2 instances.

        Based on original aws/ec2_copy_image_cross-region.py image creation functionality.
        """
        # Environment variable support
        image_name_prefix = image_name_prefix or os.getenv("IMAGE_NAME_PREFIX", "Demo-Boto")

        if not instance_ids:
            raise ValueError("No instance IDs provided for image creation.")

        ec2_resource = boto3.resource("ec2", region_name=context.region)
        results = []
        created_images = []

        for instance_id in instance_ids:
            result = self.create_operation_result(context, "create_image", "ec2:ami", instance_id)

            try:
                instance = ec2_resource.Instance(instance_id)
                image_name = f"{image_name_prefix}-{instance_id}"

                logger.info(f"Creating image for instance {instance_id} with name '{image_name}'...")

                if context.dry_run:
                    logger.info(f"[DRY-RUN] Image creation for {instance_id} skipped.")
                    result.mark_completed(OperationStatus.DRY_RUN)
                else:
                    image = instance.create_image(Name=image_name, Description=f"Image for {instance_id}")
                    created_images.append(image.id)

                    result.response_data = {"ImageId": image.id, "ImageName": image_name}
                    result.mark_completed(OperationStatus.SUCCESS)
                    logger.info(f"Created image: {image.id}")

            except ClientError as e:
                error_msg = f"AWS Client Error: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)
            except BotoCoreError as e:
                error_msg = f"BotoCore Error: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)

            results.append(result)

        # SNS notification
        if created_images:
            message = f"Successfully created {len(created_images)} AMI images: {', '.join(created_images)}"
            self.send_sns_notification("EC2 AMI Images Created", message)
            logger.info(message)

        return results

    def delete_snapshots(
        self, context: OperationContext, snapshot_ids: List[str], delete_owned_only: bool = True
    ) -> List[OperationResult]:
        """Delete EBS snapshots with safety checks."""
        ec2_client = self.get_client("ec2", context.region)
        results = []

        for snapshot_id in snapshot_ids:
            result = self.create_operation_result(context, "delete_snapshots", "ec2:snapshot", snapshot_id)

            try:
                if not self.confirm_operation(context, snapshot_id, "delete EBS snapshot"):
                    result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                    results.append(result)
                    continue

                if context.dry_run:
                    logger.info(f"[DRY-RUN] Would delete snapshot {snapshot_id}")
                    result.mark_completed(OperationStatus.DRY_RUN)
                    results.append(result)
                    continue

                self.execute_aws_call(ec2_client, "delete_snapshot", SnapshotId=snapshot_id)
                result.mark_completed(OperationStatus.SUCCESS)
                logger.info(f"Successfully deleted snapshot {snapshot_id}")

            except ClientError as e:
                error_msg = f"Failed to delete snapshot {snapshot_id}: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)

            results.append(result)

        return results

    def cleanup_unused_volumes(self, context: OperationContext) -> List[OperationResult]:
        """
        Identify unused EBS volumes with detailed reporting and SNS notifications.

        Enhanced from original aws/ec2_unused_volumes.py with comprehensive scanning.
        """
        ec2_client = self.get_client("ec2", context.region)

        result = self.create_operation_result(context, "cleanup_unused_volumes", "ec2:volume", "scan")

        try:
            logger.info("🔍 Fetching all EBS volumes...")

            # Get all volumes (not just available ones for comprehensive reporting)
            volumes_response = self.execute_aws_call(ec2_client, "describe_volumes")

            unused_volumes = []

            # Enhanced loop with detailed analysis from original file
            for vol in volumes_response["Volumes"]:
                if len(vol.get("Attachments", [])) == 0:  # Unattached volumes
                    # Enhanced volume details from original file
                    volume_details = {
                        "VolumeId": vol["VolumeId"],
                        "Size": vol["Size"],
                        "State": vol["State"],
                        "Encrypted": vol.get("Encrypted", False),
                        "VolumeType": vol.get("VolumeType", "unknown"),
                        "CreateTime": str(vol["CreateTime"]),
                    }
                    unused_volumes.append(volume_details)

                    # Debug logging from original file
                    logger.debug(f"Unattached Volume: {json.dumps(volume_details, default=str)}")

            result.response_data = {
                "unused_volumes": unused_volumes,
                "count": len(unused_volumes),
                "total_scanned": len(volumes_response["Volumes"]),
            }
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(
                f"✅ Found {len(unused_volumes)} unused volumes out of {len(volumes_response['Volumes'])} total volumes"
            )

            # SNS notification with detailed report from original file
            if unused_volumes:
                message = f"Found {len(unused_volumes)} unused EBS volumes in {context.region}:\n"
                for vol in unused_volumes[:10]:  # Limit to first 10 for readability
                    message += f"- {vol['VolumeId']} ({vol['Size']}GB, {vol['VolumeType']}, {vol['State']})\n"
                if len(unused_volumes) > 10:
                    message += f"... and {len(unused_volumes) - 10} more volumes"

                self.send_sns_notification("Unused EBS Volumes Found", message)

        except ClientError as e:
            error_msg = f"❌ AWS Client Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except BotoCoreError as e:
            error_msg = f"❌ BotoCore Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except Exception as e:
            error_msg = f"❌ Unexpected error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def cleanup_unused_eips(self, context: OperationContext) -> List[OperationResult]:
        """
        Identify unused Elastic IPs with detailed reporting and SNS notifications.

        Enhanced from original aws/ec2_unused_eips.py with comprehensive scanning.
        """
        ec2_client = self.get_client("ec2", context.region)

        result = self.create_operation_result(context, "cleanup_unused_eips", "ec2:eip", "scan")

        try:
            logger.info("🔍 Fetching all Elastic IP addresses...")

            addresses_response = self.execute_aws_call(ec2_client, "describe_addresses")
            unassociated_eips = []
            eip_details = []

            for address in addresses_response["Addresses"]:
                # Enhanced analysis from original file
                if "InstanceId" not in address and "NetworkInterfaceId" not in address:
                    eip_info = {
                        "AllocationId": address.get("AllocationId", "N/A"),
                        "PublicIp": address.get("PublicIp", "N/A"),
                        "Domain": address.get("Domain", "classic"),
                        "AssociationId": address.get("AssociationId"),
                    }
                    unassociated_eips.append(address.get("AllocationId", address.get("PublicIp")))
                    eip_details.append(eip_info)

                    # Debug logging from original file
                    logger.debug(f"Unassociated EIP: {json.dumps(eip_info, default=str)}")

            result.response_data = {
                "unused_eips": unassociated_eips,
                "eip_details": eip_details,
                "count": len(unassociated_eips),
                "total_scanned": len(addresses_response["Addresses"]),
            }
            result.mark_completed(OperationStatus.SUCCESS)
            logger.info(
                f"✅ Found {len(unassociated_eips)} unused EIPs out of {len(addresses_response['Addresses'])} total EIPs"
            )

            # SNS notification with detailed report
            if unassociated_eips:
                message = f"Found {len(unassociated_eips)} unused Elastic IPs in {context.region}:\n"
                for eip in eip_details[:10]:  # Limit to first 10 for readability
                    message += f"- {eip['PublicIp']} ({eip['AllocationId']}, {eip['Domain']})\n"
                if len(eip_details) > 10:
                    message += f"... and {len(eip_details) - 10} more EIPs"

                self.send_sns_notification("Unused Elastic IPs Found", message)

        except ClientError as e:
            error_msg = f"❌ AWS Client Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except BotoCoreError as e:
            error_msg = f"❌ BotoCore Error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)
        except Exception as e:
            error_msg = f"❌ Unexpected error: {e}"
            logger.error(error_msg)
            result.mark_completed(OperationStatus.FAILED, error_msg)

        return [result]

    def reboot_instances(self, context: OperationContext, instance_ids: List[str]) -> List[OperationResult]:
        """Reboot EC2 instances."""
        ec2_client = self.get_client("ec2", context.region)
        results = []

        for instance_id in instance_ids:
            result = self.create_operation_result(context, "reboot_instances", "ec2:instance", instance_id)

            try:
                if not self.confirm_operation(context, instance_id, "reboot"):
                    result.mark_completed(OperationStatus.CANCELLED, "Operation cancelled by user")
                    results.append(result)
                    continue

                if context.dry_run:
                    logger.info(f"[DRY-RUN] Would reboot instance {instance_id}")
                    result.mark_completed(OperationStatus.DRY_RUN)
                else:
                    response = self.execute_aws_call(ec2_client, "reboot_instances", InstanceIds=[instance_id])

                    result.response_data = response
                    result.mark_completed(OperationStatus.SUCCESS)
                    logger.info(f"Successfully rebooted instance {instance_id}")

            except ClientError as e:
                error_msg = f"Failed to reboot instance {instance_id}: {e}"
                logger.error(error_msg)
                result.mark_completed(OperationStatus.FAILED, error_msg)

            results.append(result)

        return results


# Lambda handlers to append to ec2_operations.py

# ==============================
# AWS LAMBDA HANDLERS
# ==============================


def lambda_handler_terminate_instances(event, context):
    """
    AWS Lambda handler for terminating EC2 instances.

    Based on original aws/ec2_terminate_instances.py Lambda handler.
    """
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate.base import OperationContext

        instance_ids = event.get("instance_ids", os.getenv("INSTANCE_IDS", "").split(","))
        region = event.get("region", os.getenv("AWS_REGION", "us-east-1"))

        if not instance_ids or instance_ids == [""]:
            logger.error("No instance IDs provided in the Lambda event or environment.")
            raise ValueError("Instance IDs are required to terminate EC2 instances.")

        ec2_ops = EC2Operations()
        account = AWSAccount(account_id="current", account_name="lambda-execution")
        operation_context = OperationContext(
            account=account,
            region=region,
            operation_type="terminate_instances",
            resource_types=["ec2:instance"],
            dry_run=False,
        )

        results = ec2_ops.terminate_instances(operation_context, instance_ids)
        terminated_instances = [r.resource_id for r in results if r.success]

        return {
            "statusCode": 200,
            "body": {
                "message": "Instances terminated successfully.",
                "terminated_instances": terminated_instances,
            },
        }
    except Exception as e:
        logger.error(f"Lambda function failed: {e}")
        return {"statusCode": 500, "body": {"message": str(e)}}


def lambda_handler_run_instances(event, context):
    """AWS Lambda handler for launching EC2 instances."""
    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate.base import OperationContext

        region = event.get("region", os.getenv("AWS_REGION", "us-east-1"))

        ec2_ops = EC2Operations()
        account = AWSAccount(account_id="current", account_name="lambda-execution")
        operation_context = OperationContext(
            account=account,
            region=region,
            operation_type="run_instances",
            resource_types=["ec2:instance"],
            dry_run=False,
        )

        kwargs = {
            "image_id": event.get("image_id"),
            "instance_type": event.get("instance_type"),
            "min_count": event.get("min_count"),
            "max_count": event.get("max_count"),
            "key_name": event.get("key_name"),
            "security_group_ids": event.get("security_group_ids"),
            "subnet_id": event.get("subnet_id"),
            "tags": event.get("tags"),
        }

        results = ec2_ops.run_instances(operation_context, **kwargs)

        if results and results[0].success:
            instance_ids = [inst["InstanceId"] for inst in results[0].response_data["Instances"]]
            return {
                "statusCode": 200,
                "body": {"message": "Instances launched successfully.", "instance_ids": instance_ids},
            }
        else:
            return {"statusCode": 500, "body": {"message": "Failed to launch instances"}}

    except Exception as e:
        logger.error(f"Lambda Handler Error: {e}")
        return {"statusCode": 500, "body": {"error": str(e)}}


# CLI Support
def main():
    """Main entry point for standalone execution."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ec2_operations.py <operation>")
        print("Operations: terminate, run, cleanup-volumes, cleanup-eips")
        sys.exit(1)

    operation = sys.argv[1]

    try:
        from runbooks.inventory.models.account import AWSAccount
        from runbooks.operate.base import OperationContext

        ec2_ops = EC2Operations()
        account = AWSAccount(account_id="current", account_name="cli-execution")
        operation_context = OperationContext(
            account=account,
            region=os.getenv("AWS_REGION", "us-east-1"),
            operation_type=operation,
            resource_types=["ec2"],
            dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
        )

        if operation == "terminate":
            instance_ids = os.getenv("INSTANCE_IDS", "").split(",")
            if not instance_ids or instance_ids == [""]:
                raise ValueError("INSTANCE_IDS environment variable is required")
            results = ec2_ops.terminate_instances(operation_context, instance_ids)

        elif operation == "run":
            results = ec2_ops.run_instances(operation_context)

        elif operation == "cleanup-volumes":
            results = ec2_ops.cleanup_unused_volumes(operation_context)

        elif operation == "cleanup-eips":
            results = ec2_ops.cleanup_unused_eips(operation_context)

        else:
            raise ValueError(f"Unknown operation: {operation}")

        for result in results:
            if result.success:
                print(f"✅ {result.operation_type} completed successfully")
            else:
                print(f"❌ {result.operation_type} failed: {result.error_message}")

    except Exception as e:
        logger.error(f"Error during operation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
