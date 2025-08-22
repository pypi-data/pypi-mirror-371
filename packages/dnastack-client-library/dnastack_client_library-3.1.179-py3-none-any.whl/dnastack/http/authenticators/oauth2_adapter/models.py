from typing import Optional

from pydantic import BaseModel

from dnastack.common.model_mixin import JsonModelMixin as HashableModel


GRANT_TYPE_TOKEN_EXCHANGE = 'urn:ietf:params:oauth:grant-type:token-exchange'


class OAuth2Authentication(BaseModel, HashableModel):
    """OAuth2 Authentication Information"""
    authorization_endpoint: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]
    device_code_endpoint: Optional[str]
    grant_type: str
    personal_access_endpoint: Optional[str]
    personal_access_email: Optional[str]
    personal_access_token: Optional[str]
    redirect_url: Optional[str]
    resource_url: str
    scope: Optional[str]
    token_endpoint: Optional[str]
    type: str = 'oauth2'
    subject_token: Optional[str]
    subject_token_type: Optional[str]
    requested_token_type: Optional[str]
    audience: Optional[str]
    cloud_provider: Optional[str]  # Currently supported: 'gcp'