# src/email_insights.py
import openapi_client
from openapi_client.configuration import Configuration as ApiConfiguration
from openapi_client.api_client import ApiClient
from openapi_client.api.email_insights_api import EmailInsightsApi
from openapi_client.models.analyze_email_request import AnalyzeEmailRequest
from openapi_client.models.batch_analyze_emails_request import BatchAnalyzeEmailsRequest
from openapi_client.exceptions import ApiException

class EmailInsights:
    def __init__(self, api_key: str):
        """
        Initialize the EmailInsights class with the provided API key.

        :param api_key: The API key for authentication.
        """
        self.config = ApiConfiguration()
        self.config.api_key = {"opportifyToken": api_key}
        self.host = "https://api.opportify.ai"
        self.version = "v1"
        self.debug_mode = False
        self.api_instance = None

    def analyze(self, params: dict) -> dict:
        """
        Analyze the email with the given parameters.

        :param params: Dictionary containing parameters for email analysis.
        :return: The analysis result as a dictionary.
        :raises Exception: If an API exception occurs.
        """
        params = self._normalize_request(params)

        # Configure the host and create the API client instance
        self.config.host = f"{self.host}/insights/{self.version}"
        api_client = ApiClient(configuration=self.config)
        api_client.configuration.debug = self.debug_mode
        self.api_instance = EmailInsightsApi(api_client)

        # Prepare the AnalyzeEmailRequest object
        analyze_email_request = AnalyzeEmailRequest(**params)

        try:
            result = self.api_instance.analyze_email(analyze_email_request)
            return result.to_dict()
        except ApiException as e:
            raise Exception(f"API exception: {e.reason}")

    def batch_analyze(self, params: dict) -> dict:
        """
        Start a batch analysis of multiple email addresses.

        :param params: Dictionary containing parameters for batch email analysis.
                      Should include "emails" (list of emails) and optionally "enable_ai" and "enable_auto_correction".
        :return: The batch job information as a dictionary (job_id, status, etc.).
        :raises Exception: If an API exception occurs.
        """
        params = self._normalize_batch_request(params)

        # Configure the host and create the API client instance
        self.config.host = f"{self.host}/insights/{self.version}"
        api_client = ApiClient(configuration=self.config)
        api_client.configuration.debug = self.debug_mode
        self.api_instance = EmailInsightsApi(api_client)

        # Prepare the BatchAnalyzeEmailsRequest object
        batch_analyze_emails_request = BatchAnalyzeEmailsRequest(**params)

        try:
            result = self.api_instance.batch_analyze_emails(batch_analyze_emails_request)
            return result.to_dict()
        except ApiException as e:
            raise Exception(f"API exception: {e.reason}")

    def get_batch_status(self, job_id: str) -> dict:
        """
        Get the status of a batch email analysis job.

        :param job_id: The unique identifier of the batch job.
        :return: The batch job status as a dictionary.
        :raises Exception: If an API exception occurs.
        """
        # Configure the host and create the API client instance
        self.config.host = f"{self.host}/insights/{self.version}"
        api_client = ApiClient(configuration=self.config)
        api_client.configuration.debug = self.debug_mode
        self.api_instance = EmailInsightsApi(api_client)

        try:
            result = self.api_instance.get_email_batch_status(job_id)
            return result.to_dict()
        except ApiException as e:
            raise Exception(f"API exception: {e.reason}")

    def set_host(self, host: str) -> "EmailInsights":
        """
        Set the host.

        :param host: The host URL.
        :return: The current instance for chaining.
        """
        self.host = host
        return self

    def set_version(self, version: str) -> "EmailInsights":
        """
        Set the version.

        :param version: The API version.
        :return: The current instance for chaining.
        """
        self.version = version
        return self

    def set_debug_mode(self, debug_mode: bool) -> "EmailInsights":
        """
        Set the debug mode.

        :param debug_mode: Enable or disable debug mode.
        :return: The current instance for chaining.
        """
        self.debug_mode = debug_mode
        return self

    def _normalize_request(self, params: dict) -> dict:
        """
        Normalize the request parameters.

        :param params: The raw parameters.
        :return: Normalized parameters.
        """
        normalized = {}
        normalized["email"] = str(params["email"])

        if "enableAi" in params:
            params["enable_ai"] = params.pop("enableAi")

        if "enableAutoCorrection" in params:
            params["enable_auto_correction"] = bool(params.pop("enableAutoCorrection"))

        normalized["enable_ai"] = bool(params.get("enable_ai", False))
        normalized["enable_auto_correction"] = bool(params.get("enable_auto_correction", False))

        return normalized

    def _normalize_batch_request(self, params: dict) -> dict:
        """
        Normalize the batch request parameters.

        :param params: The raw parameters.
        :return: Normalized parameters.
        """
        normalized = {}
        
        # Ensure emails is a list of strings
        if "emails" not in params:
            raise ValueError("'emails' parameter is required for batch analysis")
        
        emails = params["emails"]
        if not isinstance(emails, list):
            raise ValueError("'emails' parameter must be a list")
        
        normalized["emails"] = [str(email) for email in emails]

        # Handle enableAi parameter name conversion
        if "enableAi" in params:
            params["enable_ai"] = params.pop("enableAi")

        # Handle enableAutoCorrection parameter name conversion
        if "enableAutoCorrection" in params:
            params["enable_auto_correction"] = bool(params.pop("enableAutoCorrection"))

        normalized["enable_ai"] = bool(params.get("enable_ai", False))
        normalized["enable_auto_correction"] = bool(params.get("enable_auto_correction", False))

        return normalized
