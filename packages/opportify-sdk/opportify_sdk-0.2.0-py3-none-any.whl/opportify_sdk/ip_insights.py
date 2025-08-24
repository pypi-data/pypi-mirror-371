# src/ip_insights.py
import openapi_client
from openapi_client.configuration import Configuration as ApiConfiguration
from openapi_client.api_client import ApiClient
from openapi_client.api.ip_insights_api import IPInsightsApi
from openapi_client.models.analyze_ip_request import AnalyzeIpRequest
from openapi_client.models.batch_analyze_ips_request import BatchAnalyzeIpsRequest
from openapi_client.exceptions import ApiException

class IpInsights:
    def __init__(self, api_key: str):
        """
        Initialize the IpInsights class with the provided API key.

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
        Analyze the IP address based on the provided parameters.

        :param params: Dictionary containing parameters for IP analysis.
        :return: The analysis result as a dictionary.
        :raises Exception: If an API exception occurs.
        """
        params = self._normalize_request(params)

        # Configure the host and create the API client instance
        self.config.host = f"{self.host}/insights/{self.version}"
        api_client = ApiClient(configuration=self.config)
        api_client.configuration.debug = self.debug_mode
        self.api_instance = IPInsightsApi(api_client)

        # Prepare the AnalyzeIpRequest object
        analyze_ip_request = AnalyzeIpRequest(**params)

        try:
            result = self.api_instance.analyze_ip(analyze_ip_request)
            return result.to_dict()
        except ApiException as e:
            raise Exception(f"API exception: {e.reason}")

    def batch_analyze(self, params: dict) -> dict:
        """
        Start a batch analysis of multiple IP addresses.

        :param params: Dictionary containing parameters for batch IP analysis.
                      Should include "ips" (list of IPs) and optionally "enable_ai".
        :return: The batch job information as a dictionary (job_id, status, etc.).
        :raises Exception: If an API exception occurs.
        """
        params = self._normalize_batch_request(params)

        # Configure the host and create the API client instance
        self.config.host = f"{self.host}/insights/{self.version}"
        api_client = ApiClient(configuration=self.config)
        api_client.configuration.debug = self.debug_mode
        self.api_instance = IPInsightsApi(api_client)

        # Prepare the BatchAnalyzeIpsRequest object
        batch_analyze_ips_request = BatchAnalyzeIpsRequest(**params)

        try:
            result = self.api_instance.batch_analyze_ips(batch_analyze_ips_request)
            return result.to_dict()
        except ApiException as e:
            raise Exception(f"API exception: {e.reason}")

    def get_batch_status(self, job_id: str) -> dict:
        """
        Get the status of a batch IP analysis job.

        :param job_id: The unique identifier of the batch job.
        :return: The batch job status as a dictionary.
        :raises Exception: If an API exception occurs.
        """
        # Configure the host and create the API client instance
        self.config.host = f"{self.host}/insights/{self.version}"
        api_client = ApiClient(configuration=self.config)
        api_client.configuration.debug = self.debug_mode
        self.api_instance = IPInsightsApi(api_client)

        try:
            result = self.api_instance.get_ip_batch_status(job_id)
            return result.to_dict()
        except ApiException as e:
            raise Exception(f"API exception: {e.reason}")

    def set_host(self, host: str) -> "IpInsights":
        """
        Set the host.

        :param host: The host URL.
        :return: The current instance for chaining.
        """
        self.host = host
        return self

    def set_version(self, version: str) -> "IpInsights":
        """
        Set the version.

        :param version: The API version.
        :return: The current instance for chaining.
        """
        self.version = version
        return self

    def set_debug_mode(self, debug_mode: bool) -> "IpInsights":
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
        normalized["ip"] = str(params["ip"])

        if "enableAi" in params:
            params["enable_ai"] = params.pop("enableAi")

        normalized["enable_ai"] = bool(params.get("enable_ai", False))

        return normalized

    def _normalize_batch_request(self, params: dict) -> dict:
        """
        Normalize the batch request parameters.

        :param params: The raw parameters.
        :return: Normalized parameters.
        """
        normalized = {}
        
        # Ensure ips is a list of strings
        if "ips" not in params:
            raise ValueError("'ips' parameter is required for batch analysis")
        
        ips = params["ips"]
        if not isinstance(ips, list):
            raise ValueError("'ips' parameter must be a list")
        
        normalized["ips"] = [str(ip) for ip in ips]

        # Handle enableAi parameter name conversion
        if "enableAi" in params:
            params["enable_ai"] = params.pop("enableAi")

        normalized["enable_ai"] = bool(params.get("enable_ai", False))

        return normalized
