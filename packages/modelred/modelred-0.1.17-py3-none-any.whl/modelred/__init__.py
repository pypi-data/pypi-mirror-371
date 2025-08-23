"""
ModelRed Python SDK

Enterprise-ready Python SDK for ModelRed AI security testing platform.
Provides both synchronous and asynchronous clients with comprehensive
error handling, subscription limit awareness, and full API coverage.
"""

import asyncio
import aiohttp
import requests
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path

__version__ = "3.0.0"
__author__ = "ModelRed Team"
__email__ = "support@modelred.ai"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("modelred")

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================


class ModelProvider(Enum):
    """Supported AI model providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    REST = "rest"


class AssessmentStatus(Enum):
    """Assessment execution status"""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(Enum):
    """Assessment priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SubscriptionTier(Enum):
    """Subscription tier levels"""

    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class Model:
    """Represents a registered AI model"""

    id: str
    modelId: str
    provider: str
    modelName: str
    displayName: str
    description: Optional[str] = None
    isActive: bool = True
    lastTested: Optional[datetime] = None
    testCount: int = 0
    createdAt: Optional[datetime] = None
    createdByUser: Optional[Dict[str, Any]] = None


@dataclass
class Assessment:
    """Represents a security assessment"""

    id: str
    modelId: str
    status: AssessmentStatus
    testTypes: List[str]
    priority: Priority
    progress: int = 0
    results: Optional[Dict[str, Any]] = None
    errorMessage: Optional[str] = None
    createdAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    estimatedDuration: Optional[int] = None


@dataclass
class UsageStats:
    """Current usage statistics and limits"""

    models: int
    modelsLimit: int
    assessments: int
    assessmentsLimit: int
    apiAccess: bool
    tier: SubscriptionTier
    warnings: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SubscriptionInfo:
    """Detailed subscription information"""

    subscription: Optional[Dict[str, Any]]
    tier: SubscriptionTier
    usage: Dict[str, int]
    limits: Dict[str, Union[int, bool, List[str]]]
    warnings: List[Dict[str, Any]]


@dataclass
class ApiKey:
    """Represents an API key"""

    id: str
    name: str
    key: str
    isActive: bool
    expiresAt: Optional[datetime] = None
    lastUsed: Optional[datetime] = None
    createdAt: Optional[datetime] = None


# ============================================================================
# EXCEPTIONS
# ============================================================================


class ModelRedError(Exception):
    """Base exception for ModelRed SDK"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response or {}


class AuthenticationError(ModelRedError):
    """Authentication failed - invalid API key"""

    pass


class AuthorizationError(ModelRedError):
    """Authorization failed - insufficient permissions"""

    pass


class SubscriptionLimitError(ModelRedError):
    """Subscription limit exceeded"""

    def __init__(self, message: str, tier: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.tier = tier


class ValidationError(ModelRedError):
    """Invalid input data"""

    pass


class NotFoundError(ModelRedError):
    """Resource not found"""

    pass


class ConflictError(ModelRedError):
    """Resource conflict (e.g., duplicate model ID)"""

    pass


class RateLimitError(ModelRedError):
    """Rate limit exceeded"""

    pass


class ServerError(ModelRedError):
    """Server-side error"""

    pass


class NetworkError(ModelRedError):
    """Network connectivity issues"""

    pass


# ============================================================================
# PROVIDER CONFIGURATION HELPERS
# ============================================================================


class ProviderConfig:
    """Helper class for creating provider configurations"""

    @staticmethod
    def openai(
        api_key: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create OpenAI provider configuration"""
        config = {
            "api_key": api_key or os.getenv("OPENAI_API_KEY"),
            "model_name": model_name,
        }
        if base_url:
            config["base_url"] = base_url
        if organization:
            config["organization"] = organization
        return config

    @staticmethod
    def anthropic(
        api_key: Optional[str] = None, model_name: str = "claude-3-sonnet-20240229"
    ) -> Dict[str, Any]:
        """Create Anthropic provider configuration"""
        return {
            "api_key": api_key or os.getenv("ANTHROPIC_API_KEY"),
            "model_name": model_name,
        }

    @staticmethod
    def azure(
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None,
        api_version: str = "2024-06-01",
    ) -> Dict[str, Any]:
        """Create Azure OpenAI provider configuration"""
        return {
            "api_key": api_key or os.getenv("AZURE_OPENAI_API_KEY"),
            "endpoint": endpoint or os.getenv("AZURE_OPENAI_ENDPOINT"),
            "deployment_name": deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            "api_version": api_version,
        }

    @staticmethod
    def huggingface(
        model_name: str,
        api_key: Optional[str] = None,
        use_inference_api: bool = True,
        endpoint_url: Optional[str] = None,
        task: str = "text-generation",
    ) -> Dict[str, Any]:
        """Create Hugging Face provider configuration"""
        config = {
            "model_name": model_name,
            "use_inference_api": use_inference_api,
            "task": task,
        }
        if api_key:
            config["api_key"] = api_key
        elif os.getenv("HUGGINGFACE_API_TOKEN"):
            config["api_key"] = os.getenv("HUGGINGFACE_API_TOKEN")
        if endpoint_url:
            config["endpoint_url"] = endpoint_url
        return config

    @staticmethod
    def rest_api(
        uri: str,
        name: Optional[str] = None,
        key_env_var: str = "REST_API_KEY",
        api_key: Optional[str] = None,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        req_template: str = "$INPUT",
        req_template_json_object: Optional[Dict[str, Any]] = None,
        response_json: bool = True,
        response_json_field: str = "text",
        request_timeout: int = 20,
        ratelimit_codes: Optional[List[int]] = None,
        skip_codes: Optional[List[int]] = None,
        verify_ssl: Union[bool, str] = True,
        proxies: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create REST API provider configuration for custom model endpoints

        Args:
            uri: The API endpoint URL (required)
            name: Optional name for the REST API configuration
            key_env_var: Environment variable name for API key (default: "REST_API_KEY")
            api_key: API key for authentication (optional)
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
            headers: Custom HTTP headers as dict
            req_template: Request template string (use $INPUT for prompts, $KEY for API key)
            req_template_json_object: JSON template as dict (overrides req_template)
            response_json: Whether response is JSON format
            response_json_field: JSON field path for response text (e.g., "text", "choices.0.message.content")
            request_timeout: Request timeout in seconds (1-300)
            ratelimit_codes: HTTP status codes to treat as rate limits (default: [429])
            skip_codes: HTTP status codes to skip/ignore (default: [])
            verify_ssl: SSL verification - True, False, or path to cert file
            proxies: Proxy configuration as dict (e.g., {"http": "http://proxy:8080"})

        Returns:
            Dict containing the REST API configuration

        Example:
            config = ProviderConfig.rest_api(
                uri="https://api.example.com/v1/completions",
                method="POST",
                headers={"Authorization": "Bearer your-token"},
                req_template_json_object={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "$INPUT"}],
                    "max_tokens": 150
                },
                response_json_field="choices.0.message.content",
                request_timeout=30
            )
        """
        config = {
            "uri": uri,
            "method": method,
            "headers": headers or {},
            "req_template": req_template,
            "response_json": response_json,
            "response_json_field": response_json_field,
            "request_timeout": request_timeout,
            "ratelimit_codes": ratelimit_codes or [429],
            "skip_codes": skip_codes or [],
            "verify_ssl": verify_ssl,
        }

        # Add optional fields only if provided
        if name is not None:
            config["name"] = name
        if key_env_var != "REST_API_KEY":
            config["key_env_var"] = key_env_var
        if api_key is not None:
            config["api_key"] = api_key
        if req_template_json_object is not None:
            config["req_template_json_object"] = req_template_json_object
        if proxies is not None:
            config["proxies"] = proxies

        return config


# ============================================================================
# BASE CLIENT
# ============================================================================


class BaseClient:
    """Base client with common functionality"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("MODELRED_API_KEY")
        if not self.api_key:
            raise ValidationError(
                "API key required. Set MODELRED_API_KEY environment variable or pass api_key parameter."
            )

        if not self.api_key.startswith("mr_"):
            raise ValidationError(
                "Invalid API key format. API key must start with 'mr_'"
            )

        self.base_url = base_url or os.getenv(
            "MODELRED_BASE_URL", "https://app.modelred.ai"
        )
        self.logger = logger

    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"ModelRed-Python-SDK/{__version__}",
        }

    def _handle_response_error(
        self, status_code: int, response_data: Dict[str, Any]
    ) -> None:
        """Handle API response errors with proper exception mapping"""
        error_message = response_data.get("error", f"API error: {status_code}")

        if status_code == 401:
            raise AuthenticationError(error_message, status_code, response_data)
        elif status_code == 403:
            tier = response_data.get("tier")
            if any(
                keyword in error_message.lower()
                for keyword in ["limit", "subscription", "tier", "upgrade"]
            ):
                raise SubscriptionLimitError(
                    error_message, tier, status_code=status_code, response=response_data
                )
            else:
                raise AuthorizationError(error_message, status_code, response_data)
        elif status_code == 404:
            raise NotFoundError(error_message, status_code, response_data)
        elif status_code == 409:
            raise ConflictError(error_message, status_code, response_data)
        elif status_code == 422:
            raise ValidationError(error_message, status_code, response_data)
        elif status_code == 429:
            raise RateLimitError(error_message, status_code, response_data)
        elif status_code >= 500:
            raise ServerError(error_message, status_code, response_data)
        else:
            raise ModelRedError(error_message, status_code, response_data)

    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string to datetime object"""
        if not dt_string:
            return None
        try:
            return datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None


# ============================================================================
# SYNCHRONOUS CLIENT
# ============================================================================


class ModelRed(BaseClient):
    """Synchronous ModelRed client for AI security testing"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        super().__init__(api_key, base_url)
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self._get_headers())

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}/api{endpoint}"

        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)

            try:
                response_data = response.json()
            except ValueError:
                response_data = {"error": response.text}

            if response.status_code >= 400:
                self._handle_response_error(response.status_code, response_data)

            return response_data

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}")

    # ========================================================================
    # MODELS API
    # ========================================================================

    def create_model(
        self,
        model_id: str,
        provider: Union[str, ModelProvider],
        display_name: str,
        provider_config: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Model:
        """Create a new AI model for security testing"""
        if isinstance(provider, ModelProvider):
            provider = provider.value

        payload = {
            "modelId": model_id,
            "provider": provider,
            "displayName": display_name,
            "providerConfig": provider_config,
        }
        if description:
            payload["description"] = description

        response = self._make_request("POST", "/models", json=payload)
        return self._parse_model(response["data"])

    def list_models(self) -> List[Model]:
        """List all registered models"""
        response = self._make_request("GET", "/models")
        return [self._parse_model(model_data) for model_data in response["data"]]

    def get_model(self, model_id: str) -> Model:
        """Get details of a specific model"""
        response = self._make_request("GET", f"/models/{model_id}")
        return self._parse_model(response["data"])

    def delete_model(self, model_id: str) -> bool:
        """Delete a registered model"""
        response = self._make_request("DELETE", f"/models/{model_id}")
        return response.get("success", True)

    def _parse_model(self, data: Dict[str, Any]) -> Model:
        """Parse model data from API response"""
        return Model(
            id=data["id"],
            modelId=data["modelId"],
            provider=data["provider"],
            modelName=data["modelName"],
            displayName=data["displayName"],
            description=data.get("description"),
            isActive=data.get("isActive", True),
            lastTested=self._parse_datetime(data.get("lastTested")),
            testCount=data.get("testCount", 0),
            createdAt=self._parse_datetime(data.get("createdAt")),
            createdByUser=data.get("createdByUser"),
        )

    # ========================================================================
    # ASSESSMENTS API
    # ========================================================================

    def create_assessment(
        self,
        model_id: str,
        test_types: List[str],
        priority: Union[str, Priority] = Priority.MEDIUM,
    ) -> Assessment:
        """Create a new security assessment"""
        if isinstance(priority, Priority):
            priority = priority.value

        payload = {
            "modelId": model_id,
            "testTypes": test_types,
            "priority": priority,
        }

        response = self._make_request("POST", "/assessments", json=payload)
        return self._parse_assessment(response["data"])

    def get_assessment(self, assessment_id: str) -> Assessment:
        """Get assessment details and status"""
        response = self._make_request("GET", f"/assessments/{assessment_id}")
        return self._parse_assessment(response["data"])

    def list_assessments(self, limit: Optional[int] = None) -> List[Assessment]:
        """List recent assessments"""
        params = {}
        if limit:
            params["limit"] = limit

        response = self._make_request("GET", "/assessments", params=params)
        return [
            self._parse_assessment(assessment_data)
            for assessment_data in response["data"]
        ]

    def wait_for_completion(
        self,
        assessment_id: str,
        timeout_minutes: int = 60,
        poll_interval: int = 10,
        progress_callback: Optional[Callable[[Assessment], None]] = None,
    ) -> Assessment:
        """Wait for assessment completion with progress updates"""
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60

        while time.time() - start_time < timeout_seconds:
            assessment = self.get_assessment(assessment_id)

            if progress_callback:
                progress_callback(assessment)

            if assessment.status in [
                AssessmentStatus.COMPLETED,
                AssessmentStatus.FAILED,
                AssessmentStatus.CANCELLED,
            ]:
                return assessment

            time.sleep(poll_interval)

        raise ModelRedError(f"Assessment timeout after {timeout_minutes} minutes")

    def _parse_assessment(self, data: Dict[str, Any]) -> Assessment:
        """Parse assessment data from API response"""
        return Assessment(
            id=data["id"],
            modelId=data["modelId"],
            status=AssessmentStatus(data["status"]),
            testTypes=data.get("testTypes", []),
            priority=Priority(data.get("priority", "medium")),
            progress=data.get("progress", 0),
            results=data.get("results"),
            errorMessage=data.get("errorMessage"),
            createdAt=self._parse_datetime(data.get("createdAt")),
            completedAt=self._parse_datetime(data.get("completedAt")),
            estimatedDuration=data.get("estimatedDuration"),
        )

    # ========================================================================
    # SUBSCRIPTION API
    # ========================================================================

    def get_subscription_info(self, organization_id: str) -> SubscriptionInfo:
        """Get detailed subscription information"""
        response = self._make_request("GET", f"/subscription/{organization_id}")

        return SubscriptionInfo(
            subscription=response.get("subscription"),
            tier=SubscriptionTier(response["tier"]),
            usage=response["usage"],
            limits=response["limits"],
            warnings=response.get("warnings", []),
        )

    def get_usage_stats(self) -> UsageStats:
        """Get current usage statistics (simplified)"""
        # This would need to be implemented based on your dashboard API
        response = self._make_request("GET", "/dashboard")

        return UsageStats(
            models=response.get("modelsCount", 0),
            modelsLimit=response.get("modelsLimit", 0),
            assessments=response.get("assessmentsCount", 0),
            assessmentsLimit=response.get("assessmentsLimit", 0),
            apiAccess=response.get("hasApiAccess", False),
            tier=SubscriptionTier(response.get("tier", "free")),
            warnings=response.get("warnings", []),
        )

    # ========================================================================
    # API KEYS MANAGEMENT
    # ========================================================================

    def create_api_key(self, name: str, expires_at: Optional[str] = None) -> ApiKey:
        """Create a new API key"""
        payload = {"name": name}
        if expires_at:
            payload["expiresAt"] = expires_at

        response = self._make_request("POST", "/keys", json=payload)
        return self._parse_api_key(response["data"])

    def list_api_keys(self) -> List[ApiKey]:
        """List all API keys"""
        response = self._make_request("GET", "/keys")
        return [self._parse_api_key(key_data) for key_data in response["data"]]

    def delete_api_key(self, key_id: str) -> bool:
        """Delete an API key"""
        response = self._make_request("DELETE", f"/keys/{key_id}")
        return response.get("success", True)

    def _parse_api_key(self, data: Dict[str, Any]) -> ApiKey:
        """Parse API key data from response"""
        return ApiKey(
            id=data["id"],
            name=data["name"],
            key=data.get("key", ""),  # Only returned on creation
            isActive=data.get("isActive", True),
            expiresAt=self._parse_datetime(data.get("expiresAt")),
            lastUsed=self._parse_datetime(data.get("lastUsed")),
            createdAt=self._parse_datetime(data.get("createdAt")),
        )

    # ========================================================================
    # CONVENIENCE METHODS
    # ========================================================================

    def create_openai_model(
        self,
        model_id: str,
        display_name: str,
        api_key: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Model:
        """Convenience method to create an OpenAI model"""
        config = ProviderConfig.openai(api_key, model_name, base_url, organization)
        return self.create_model(
            model_id, ModelProvider.OPENAI, display_name, config, description
        )

    def create_anthropic_model(
        self,
        model_id: str,
        display_name: str,
        api_key: Optional[str] = None,
        model_name: str = "claude-3-sonnet-20240229",
        description: Optional[str] = None,
    ) -> Model:
        """Convenience method to create an Anthropic model"""
        config = ProviderConfig.anthropic(api_key, model_name)
        return self.create_model(
            model_id, ModelProvider.ANTHROPIC, display_name, config, description
        )

    def create_azure_model(
        self,
        model_id: str,
        display_name: str,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None,
        api_version: str = "2024-06-01",
        description: Optional[str] = None,
    ) -> Model:
        """Convenience method to create an Azure OpenAI model"""
        config = ProviderConfig.azure(api_key, endpoint, deployment_name, api_version)
        return self.create_model(
            model_id, ModelProvider.AZURE, display_name, config, description
        )

    def run_assessment_sync(
        self,
        model_id: str,
        test_types: List[str],
        priority: Union[str, Priority] = Priority.MEDIUM,
        wait_for_completion: bool = False,
        timeout_minutes: int = 60,
        progress_callback: Optional[Callable[[Assessment], None]] = None,
    ) -> Assessment:
        """Run assessment with optional waiting for completion"""
        assessment = self.create_assessment(model_id, test_types, priority)

        if wait_for_completion:
            assessment = self.wait_for_completion(
                assessment.id, timeout_minutes, progress_callback=progress_callback
            )

        return assessment


# ============================================================================
# ASYNCHRONOUS CLIENT
# ============================================================================


class AsyncModelRed(BaseClient):
    """Asynchronous ModelRed client for AI security testing"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        super().__init__(api_key, base_url)
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self._get_headers(),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """Make async HTTP request with error handling"""
        if not self.session:
            raise RuntimeError(
                "Client not initialized. Use 'async with AsyncModelRed() as client:'"
            )

        url = f"{self.base_url}/api{endpoint}"

        try:
            async with self.session.request(method, url, **kwargs) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = {"error": await response.text()}

                if response.status >= 400:
                    self._handle_response_error(response.status, response_data)

                return response_data

        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {str(e)}")

    # ========================================================================
    # ASYNC MODELS API
    # ========================================================================

    async def create_model(
        self,
        model_id: str,
        provider: Union[str, ModelProvider],
        display_name: str,
        provider_config: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Model:
        """Create a new AI model for security testing"""
        if isinstance(provider, ModelProvider):
            provider = provider.value

        payload = {
            "modelId": model_id,
            "provider": provider,
            "displayName": display_name,
            "providerConfig": provider_config,
        }
        if description:
            payload["description"] = description

        response = await self._make_request("POST", "/models", json=payload)
        return self._parse_model(response["data"])

    async def list_models(self) -> List[Model]:
        """List all registered models"""
        response = await self._make_request("GET", "/models")
        return [self._parse_model(model_data) for model_data in response["data"]]

    async def get_model(self, model_id: str) -> Model:
        """Get details of a specific model"""
        response = await self._make_request("GET", f"/models/{model_id}")
        return self._parse_model(response["data"])

    async def delete_model(self, model_id: str) -> bool:
        """Delete a registered model"""
        response = await self._make_request("DELETE", f"/models/{model_id}")
        return response.get("success", True)

    def _parse_model(self, data: Dict[str, Any]) -> Model:
        """Parse model data from API response"""
        return Model(
            id=data["id"],
            modelId=data["modelId"],
            provider=data["provider"],
            modelName=data["modelName"],
            displayName=data["displayName"],
            description=data.get("description"),
            isActive=data.get("isActive", True),
            lastTested=self._parse_datetime(data.get("lastTested")),
            testCount=data.get("testCount", 0),
            createdAt=self._parse_datetime(data.get("createdAt")),
            createdByUser=data.get("createdByUser"),
        )

    # ========================================================================
    # ASYNC ASSESSMENTS API
    # ========================================================================

    async def create_assessment(
        self,
        model_id: str,
        test_types: List[str],
        priority: Union[str, Priority] = Priority.MEDIUM,
    ) -> Assessment:
        """Create a new security assessment"""
        if isinstance(priority, Priority):
            priority = priority.value

        payload = {
            "modelId": model_id,
            "testTypes": test_types,
            "priority": priority,
        }

        response = await self._make_request("POST", "/assessments", json=payload)
        return self._parse_assessment(response["data"])

    async def get_assessment(self, assessment_id: str) -> Assessment:
        """Get assessment details and status"""
        response = await self._make_request("GET", f"/assessments/{assessment_id}")
        return self._parse_assessment(response["data"])

    async def list_assessments(self, limit: Optional[int] = None) -> List[Assessment]:
        """List recent assessments"""
        params = {}
        if limit:
            params["limit"] = limit

        response = await self._make_request("GET", "/assessments", params=params)
        return [
            self._parse_assessment(assessment_data)
            for assessment_data in response["data"]
        ]

    async def wait_for_completion(
        self,
        assessment_id: str,
        timeout_minutes: int = 60,
        poll_interval: int = 10,
        progress_callback: Optional[Callable[[Assessment], None]] = None,
    ) -> Assessment:
        """Wait for assessment completion with progress updates"""
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60

        while time.time() - start_time < timeout_seconds:
            assessment = await self.get_assessment(assessment_id)

            if progress_callback:
                progress_callback(assessment)

            if assessment.status in [
                AssessmentStatus.COMPLETED,
                AssessmentStatus.FAILED,
                AssessmentStatus.CANCELLED,
            ]:
                return assessment

            await asyncio.sleep(poll_interval)

        raise ModelRedError(f"Assessment timeout after {timeout_minutes} minutes")

    def _parse_assessment(self, data: Dict[str, Any]) -> Assessment:
        """Parse assessment data from API response"""
        return Assessment(
            id=data["id"],
            modelId=data["modelId"],
            status=AssessmentStatus(data["status"]),
            testTypes=data.get("testTypes", []),
            priority=Priority(data.get("priority", "medium")),
            progress=data.get("progress", 0),
            results=data.get("results"),
            errorMessage=data.get("errorMessage"),
            createdAt=self._parse_datetime(data.get("createdAt")),
            completedAt=self._parse_datetime(data.get("completedAt")),
            estimatedDuration=data.get("estimatedDuration"),
        )

    # ========================================================================
    # ASYNC SUBSCRIPTION API
    # ========================================================================

    async def get_subscription_info(self, organization_id: str) -> SubscriptionInfo:
        """Get detailed subscription information"""
        response = await self._make_request("GET", f"/subscription/{organization_id}")

        return SubscriptionInfo(
            subscription=response.get("subscription"),
            tier=SubscriptionTier(response["tier"]),
            usage=response["usage"],
            limits=response["limits"],
            warnings=response.get("warnings", []),
        )

    async def get_usage_stats(self) -> UsageStats:
        """Get current usage statistics"""
        response = await self._make_request("GET", "/dashboard")

        return UsageStats(
            models=response.get("modelsCount", 0),
            modelsLimit=response.get("modelsLimit", 0),
            assessments=response.get("assessmentsCount", 0),
            assessmentsLimit=response.get("assessmentsLimit", 0),
            apiAccess=response.get("hasApiAccess", False),
            tier=SubscriptionTier(response.get("tier", "free")),
            warnings=response.get("warnings", []),
        )

    # ========================================================================
    # ASYNC API KEYS MANAGEMENT
    # ========================================================================

    async def create_api_key(
        self, name: str, expires_at: Optional[str] = None
    ) -> ApiKey:
        """Create a new API key"""
        payload = {"name": name}
        if expires_at:
            payload["expiresAt"] = expires_at

        response = await self._make_request("POST", "/keys", json=payload)
        return self._parse_api_key(response["data"])

    async def list_api_keys(self) -> List[ApiKey]:
        """List all API keys"""
        response = await self._make_request("GET", "/keys")
        return [self._parse_api_key(key_data) for key_data in response["data"]]

    async def delete_api_key(self, key_id: str) -> bool:
        """Delete an API key"""
        response = await self._make_request("DELETE", f"/keys/{key_id}")
        return response.get("success", True)

    def _parse_api_key(self, data: Dict[str, Any]) -> ApiKey:
        """Parse API key data from response"""
        return ApiKey(
            id=data["id"],
            name=data["name"],
            key=data.get("key", ""),
            isActive=data.get("isActive", True),
            expiresAt=self._parse_datetime(data.get("expiresAt")),
            lastUsed=self._parse_datetime(data.get("lastUsed")),
            createdAt=self._parse_datetime(data.get("createdAt")),
        )

    # ========================================================================
    # ASYNC CONVENIENCE METHODS
    # ========================================================================

    async def create_openai_model(
        self,
        model_id: str,
        display_name: str,
        api_key: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Model:
        """Convenience method to create an OpenAI model"""
        config = ProviderConfig.openai(api_key, model_name, base_url, organization)
        return await self.create_model(
            model_id, ModelProvider.OPENAI, display_name, config, description
        )

    async def create_anthropic_model(
        self,
        model_id: str,
        display_name: str,
        api_key: Optional[str] = None,
        model_name: str = "claude-3-sonnet-20240229",
        description: Optional[str] = None,
    ) -> Model:
        """Convenience method to create an Anthropic model"""
        config = ProviderConfig.anthropic(api_key, model_name)
        return await self.create_model(
            model_id, ModelProvider.ANTHROPIC, display_name, config, description
        )

    async def create_azure_model(
        self,
        model_id: str,
        display_name: str,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment_name: Optional[str] = None,
        api_version: str = "2024-06-01",
        description: Optional[str] = None,
    ) -> Model:
        """Convenience method to create an Azure OpenAI model"""
        config = ProviderConfig.azure(api_key, endpoint, deployment_name, api_version)
        return await self.create_model(
            model_id, ModelProvider.AZURE, display_name, config, description
        )

    async def run_assessment(
        self,
        model_id: str,
        test_types: List[str],
        priority: Union[str, Priority] = Priority.MEDIUM,
        wait_for_completion: bool = False,
        timeout_minutes: int = 60,
        progress_callback: Optional[Callable[[Assessment], None]] = None,
    ) -> Assessment:
        """Run assessment with optional waiting for completion"""
        assessment = await self.create_assessment(model_id, test_types, priority)

        if wait_for_completion:
            assessment = await self.wait_for_completion(
                assessment.id, timeout_minutes, progress_callback=progress_callback
            )

        return assessment


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Main clients
    "ModelRed",
    "AsyncModelRed",
    # Data classes
    "Model",
    "Assessment",
    "UsageStats",
    "SubscriptionInfo",
    "ApiKey",
    # Enums
    "ModelProvider",
    "AssessmentStatus",
    "Priority",
    "SubscriptionTier",
    # Exceptions
    "ModelRedError",
    "AuthenticationError",
    "AuthorizationError",
    "SubscriptionLimitError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    # Helpers
    "ProviderConfig",
]
