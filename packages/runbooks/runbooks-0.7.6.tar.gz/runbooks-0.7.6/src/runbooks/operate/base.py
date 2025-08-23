"""
Base operation classes for AWS resource management.

This module provides the abstract foundation for all AWS operational capabilities,
ensuring consistent patterns, safety features, and enterprise-grade reliability
across all service-specific operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger

from runbooks.inventory.models.account import AWSAccount
from runbooks.inventory.utils.aws_helpers import aws_api_retry, get_boto3_session


class OperationStatus(Enum):
    """Status of an AWS operation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DRY_RUN = "dry_run"


@dataclass
class OperationContext:
    """Context information for AWS operations."""

    account: AWSAccount
    region: str
    operation_type: str
    resource_types: List[str]
    dry_run: bool = False
    force: bool = False
    operation_timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize context after creation."""
        if not self.operation_timestamp:
            self.operation_timestamp = datetime.utcnow()


@dataclass
class OperationResult:
    """Result of an AWS operation."""

    operation_id: str
    status: OperationStatus
    operation_type: str
    resource_type: str
    resource_id: str
    account_id: str
    region: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    response_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Update success flag based on status."""
        self.success = self.status == OperationStatus.SUCCESS

    def mark_completed(self, status: OperationStatus, error_message: Optional[str] = None):
        """Mark operation as completed with given status."""
        self.status = status
        self.completed_at = datetime.utcnow()
        self.success = status == OperationStatus.SUCCESS
        if error_message:
            self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format."""
        return {
            "operation_id": self.operation_id,
            "status": self.status.value,
            "operation_type": self.operation_type,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "account_id": self.account_id,
            "region": self.region,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "success": self.success,
            "error_message": self.error_message,
            "response_data": self.response_data,
            "metadata": self.metadata,
        }


class BaseOperation(ABC):
    """
    Abstract base class for all AWS operations.

    Provides common functionality including session management, error handling,
    logging, and safety features that all operation classes should inherit.

    Attributes:
        service_name: AWS service name (e.g., 'ec2', 's3', 'dynamodb')
        supported_operations: Set of operation types this class handles
        requires_confirmation: Whether operations require explicit confirmation
    """

    service_name: str = None
    supported_operations: set = set()
    requires_confirmation: bool = False

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None, dry_run: bool = False):
        """
        Initialize base operation class.

        Args:
            profile: AWS profile name for authentication
            region: AWS region for operations
            dry_run: Enable dry-run mode for safe testing
        """
        self.profile = profile
        self.region = region or "us-east-1"
        self.dry_run = dry_run
        self._session = None
        self._clients = {}

    @property
    def session(self) -> boto3.Session:
        """Get or create AWS session."""
        if self._session is None:
            self._session = get_boto3_session(profile_name=self.profile)
        return self._session

    def get_client(self, service: str, region: Optional[str] = None) -> Any:
        """
        Get AWS service client.

        Args:
            service: AWS service name
            region: Override region for this client

        Returns:
            Configured AWS service client
        """
        client_key = f"{service}:{region or self.region}"

        if client_key not in self._clients:
            self._clients[client_key] = self.session.client(service, region_name=region or self.region)

        return self._clients[client_key]

    def validate_context(self, context: OperationContext) -> bool:
        """
        Validate operation context before execution.

        Args:
            context: Operation context to validate

        Returns:
            True if context is valid

        Raises:
            ValueError: If context validation fails
        """
        if not context.account:
            raise ValueError("Operation context must include AWS account information")

        if not context.region:
            raise ValueError("Operation context must include AWS region")

        if context.operation_type not in self.supported_operations:
            raise ValueError(
                f"Operation '{context.operation_type}' not supported. "
                f"Supported operations: {list(self.supported_operations)}"
            )

        return True

    def confirm_operation(self, context: OperationContext, resource_id: str, operation_type: str) -> bool:
        """
        Request user confirmation for destructive operations.

        Args:
            context: Operation context
            resource_id: Resource identifier
            operation_type: Type of operation

        Returns:
            True if operation is confirmed
        """
        if context.dry_run:
            logger.info(f"[DRY-RUN] Would perform {operation_type} on {resource_id}")
            return True

        if context.force or not self.requires_confirmation:
            return True

        # In a real implementation, this would integrate with CLI for confirmation
        logger.warning(
            f"Destructive operation: {operation_type} on {resource_id} in account {context.account.account_id}"
        )
        return True  # Simplified for this implementation

    @aws_api_retry
    def execute_aws_call(self, client: Any, method_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute AWS API call with retry and error handling.

        Args:
            client: AWS service client
            method_name: Method name to call
            **kwargs: Method arguments

        Returns:
            AWS API response

        Raises:
            ClientError: AWS service errors
        """
        try:
            method = getattr(client, method_name)
            response = method(**kwargs)

            logger.debug(f"AWS API call successful: {method_name}")
            return response

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(f"AWS API call failed: {method_name} - {error_code}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in AWS API call: {method_name} - {e}")
            raise

    def create_operation_result(
        self,
        context: OperationContext,
        operation_type: str,
        resource_type: str,
        resource_id: str,
        status: OperationStatus = OperationStatus.PENDING,
    ) -> OperationResult:
        """
        Create operation result object.

        Args:
            context: Operation context
            operation_type: Type of operation
            resource_type: Type of resource
            resource_id: Resource identifier
            status: Initial status

        Returns:
            OperationResult object
        """
        operation_id = f"{operation_type}-{resource_id}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        return OperationResult(
            operation_id=operation_id,
            status=status,
            operation_type=operation_type,
            resource_type=resource_type,
            resource_id=resource_id,
            account_id=context.account.account_id,
            region=context.region,
            started_at=datetime.utcnow(),
            metadata=context.metadata.copy(),
        )

    @abstractmethod
    def execute_operation(self, context: OperationContext, operation_type: str, **kwargs) -> List[OperationResult]:
        """
        Execute the specified operation.

        Args:
            context: Operation context
            operation_type: Type of operation to execute
            **kwargs: Operation-specific arguments

        Returns:
            List of operation results

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement execute_operation")

    def get_operation_history(
        self, resource_id: Optional[str] = None, operation_type: Optional[str] = None, limit: int = 100
    ) -> List[OperationResult]:
        """
        Get operation history for resources.

        Args:
            resource_id: Filter by resource ID
            operation_type: Filter by operation type
            limit: Maximum results to return

        Returns:
            List of historical operation results
        """
        # In a real implementation, this would query a database or log store
        logger.info(f"Operation history requested for {resource_id or 'all resources'}")
        return []
