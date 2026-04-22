import logging
import json
import os
import datetime

from httplib2 import Http, ProxyInfo
from typing import List, Union
from urllib.parse import urlparse, urlunparse, urlencode

from constants import *
from oauth_helper import BasicAuth, OAuth


class ApiClient:
    ucc_basic_auth: str = "basic"
    logger: logging.Logger
    auth: [BasicAuth, OAuth]
    results_per_page: int = 100

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def ensure_https(self, url: str) -> str:
        url = url.rstrip('/')
        parsed = urlparse(url)

        # Case 1: No scheme > add https://
        if not parsed.scheme:
            return "https://" + url

        # Case 2: http:// > convert to https://
        if parsed.scheme == "http":
            new_parsed = parsed._replace(scheme="https")
            return urlunparse(new_parsed)

        # Case 3: https:// > leave unchanged
        return url

    def to_string(self, dt: datetime) -> str:
        format = "%Y-%m-%dT%H:%M:%S.%f"
        return dt.strftime(format)

    def to_datetime(self, dt_string: str) -> datetime:
        format = "%Y-%m-%dT%H:%M:%S.%f"
        return datetime.datetime.strptime(dt_string, format)

    def _get(self, url: str, query_params: dict) -> List:
        raise NotImplementedError("Please Implement this method")


class PexipClient(ApiClient):
    http: Http = None
    proxy_info: ProxyInfo = None
    base_url: str = str()

    def __init__(self, logger: logging.Logger, account: dict, proxy_config: dict = None) -> None:
        super().__init__(logger)
        hostname = account.get("hostname")
        auth_type = account.get("auth_type")
        if auth_type == self.ucc_basic_auth:
            self.auth = BasicAuth(logger, account)
        else:
            self.auth = OAuth(logger, account, proxy_config)

        if proxy_config:
            self.proxy_info = self.auth.getProxyDetails(proxy_config)

        self.http = Http(proxy_info=self.proxy_info)
        self.base_url = self.ensure_https(hostname)

    def _get(self, url: str, query_params: dict = {}) -> List:
        """
        GET data via REST API.

        :param url: URL to call to fetch data.
        :param query_params: Query parameters to be added to the call.
        :return: List of results.
        """
        items = []
        offset = 0
        header = self.auth.get_header()
        header["Accept"] = "application/json"

        params = {
            "limit": self.results_per_page,
            "offset": offset
        }
        params.update(query_params)

        self.logger.debug(f"Request Query Parameters: {params}")

        # Adding Query Params to the URL
        url += f"/?{urlencode(params)}"

        while True:
            response, content = self.http.request(
                url,
                method="GET",
                headers=header
            )
            if response.status != 200:
                self.logger.error(f"Error {response.status} occurred - {response.reason}")
                raise Exception(f"[{response.status}] {response.reason}")

            content = json.loads(content)
            results = content["objects"]
            if results:
                items.extend(results)

            next_page_url = content["meta"]["next"]
            if next_page_url is None:
                break

            url = f"{self.base_url}{next_page_url}"

        return items

        # next = url to next page
        # previous = url to previous page
        # limit = max amount of objects per page (10000 max)
        # offset = indicates the object to start with
        # total_count = total number of objects
        # e.g. next page: /api/admin/configuration/v1/conference_alias/?offset=20

    def get_conference_data(
        self,
        start_time: datetime,
        service_types: List = [],
        service_name: str = None,
        duration: int = -1,
        active_conference_only: bool = False
    ) -> List:
        """
        Get conferences data.

        :param start_time: To filter based on conferences start time.
        :param service_types: Specify to filter based on conferences service types.
        :param service_name: Specify to filter based on conference service name.
        :param duration: Specify to filter based on conference duration.
        :param active_conference_only: Specify to fetch active conferences only. Historical data will be fetched otherwise.
        :return: List of all conferences data
        """
        result = []
        status_endpoint = f"{self.base_url}/{STATUS_RESOURCES}"
        history_endpoint = f"{self.base_url}/{HISTORY_RESOURCES}"

        api_resource = status_endpoint if active_conference_only else history_endpoint
        url = f"{api_resource}/conference"
        q_params = {
            "start_time__gte": self.to_string(start_time)
        }

        if service_name:
            q_params["name"] = service_name
        if duration > 0:
            q_params["duration"] = duration

        try:
            active_txt = " active " if active_conference_only else " "
            if not service_types:
                self.logger.info(f"Getting{active_txt}conferences data")
                return self._get(url, q_params)

            for service_type in service_types:
                self.logger.info(f"Getting{active_txt}conferences data \
                    with service type '{service_type}'")
                q_params["service_type"] = service_type
                response = self._get(url, q_params)
                result.extend(response)
            return result

        except Exception as e:
            self.logger.error(f"Error fetching{active_txt}conferences: {str(e)}")
            return []

    def _get_alarms(self,
        params: dict,
        alarm_levels: List = [],
        alarm_names: List = []
    ) -> List:
        """
        Get alarms filtered by parameters.

        :param params: Query parameters to be added to the API call.
        :param alarm_levels: Specify to filter based on alarm levels.
        :param alarm_names: Specify to filter based on alarm names.
        :return: List of fetched alarms.
        """
        self.logger.debug(f"Current query parameters: {params} and alarm levels {alarm_levels}")
        result = []
        history_endpoint = f"{self.base_url}/{HISTORY_RESOURCES}"

        url = f"{history_endpoint}/alarm"

        try:
            if not alarm_levels:
                if alarm_names:
                    for name in alarm_names:
                        self.logger.info(f"Getting '{name}' alarms")
                        params["name"] = name.lower().replace(" ", "_")
                        response = self._get(url, q_params)
                        result.extend(response)
                    return result

                self.logger.info("Getting all alarms")
                return self._get(url, params)

            for level in alarm_levels:
                msg = f"Getting alarms with level '{level}'"
                params["level"] = level

                if alarm_names:
                    for name in alarm_names:
                        params["name"] = name.lower().replace(" ", "_")
                        self.logger.info(f"{msg} and name '{name}'")
                        response = self._get(url, params)
                        result.extend(response)
                    continue

                self.logger.info(msg)
                response = self._get(url, params)
                result.extend(response)

            return result

        except Exception as e:
            raise Exception(f"Error occurred while getting alarms - {str(e)}")

    def get_alarms(self,
        from_time: datetime,
        alarm_levels: List = [],
        alarm_names: List = []
    ) -> List:
        """
        Get alarms.

        :param from_time: To filter based on time.
        :param alarm_levels: Specify to filter based on alarm levels.
        :param alarm_names: Specify to filter based on alarm names.
        :return: List of retrieved alarms.
        """
        result = []

        # Removing empty strings from lists
        alarm_levels = [x for x in alarm_levels if x.strip()]
        alarm_names = [x for x in alarm_names if x.strip()]

        # Get alarms filtered by time
        for time_filter in ["time_raised", "time_lowered"]:
            q_params = {
                f"{time_filter}__gte": self.to_string(from_time)
            }
            alarms = self._get_alarms(q_params, alarm_levels, alarm_names)
            if alarms:
                result.extend(alarms)

        # Remove duplicates i.e. alarm time_raised & time_lowered in the time range
        unique_alarms = list({a["id"] : a for a in result }.values())
        return unique_alarms

    def get_participants_data(
        self,
        end_time: datetime,
        call_directions: List = [],
        duration: int = -1
    ) -> List:
        """
        Get participants data.

        :param end_time: To filter based on time of ended calls.
        :param call_directions: Specify to filter based on call direction.
        :param duration: Specify to filter based on calls duration.
        :return: List of all participants data
        """
        result = []
        history_endpoint = f"{self.base_url}/{HISTORY_RESOURCES}"

        url = f"{history_endpoint}/participant"
        q_params = {
            "end_time__gte": self.to_string(end_time)
        }
        if duration > 0:
            q_params["duration"] = duration

        try:
            if not call_directions:
                self.logger.info("Getting call participants data")
                return self._get(url, q_params)

            for call_direction in call_directions:
                self.logger.info(f"Getting call participants data \
                    with call direction '{call_direction}'")
                q_params["call_direction"] = call_direction
                response = self._get(url, q_params)
                result.extend(response)
            return result

        except Exception as e:
            self.logger.error(f"Error fetching call participants: {str(e)}")
            return []
