"""
Deployment related request and response models.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class CreateDeploymentRequest(BaseModel):
    """Request to create a deployment."""
    model_version_id: str


class CreateDeploymentResponse(BaseModel):
    """Response from deployment creation."""
    deployment_id: str


class CreateDeploymentKeyRequest(BaseModel):
    """Request to create a deployment key."""
    deployment_id: str
    description: str = ""
    days_until_expiry: int = 90


class CreateDeploymentKeyResponse(BaseModel):
    """Response from deployment key creation."""
    deploy_key: UUID


class DeploymentInfo(BaseModel):
    """Information about a deployment."""
    deployment_id: str
    model_id: str
    version_iud: str  # Note: keeping as provided, though likely typo for version_id
    created_by: str
    created: datetime
    active: bool
    ip_blocking: bool


class DeployKeyInfo(BaseModel):
    """Information about a deploy key."""
    key_id: str
    deployment_id: str
    description: str
    created: datetime
    expires: datetime
    created_by: str
    active: bool