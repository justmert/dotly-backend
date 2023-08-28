import requests
import os
import time
from time import (
    sleep,
)
import logging
import tools.log_config as log_config

logger = logging.getLogger(__name__)


class SubSquidActor:
    @property
    def get_session(
        self,
    ):
        return self.session

    def __init__(
        self,
        session=None,
    ):
        self.subsquid_explorer_endpoint = "https://squid.subsquid.io/gs-explorer-polkadot/graphql"
        self.subsquid_stats_endpoint = "https://squid.subsquid.io/gs-stats-polkadot/graphql"
        self.subsquid_main_endpoint = "https://squid.subsquid.io/gs-main-polkadot/graphql"

        self.subsquid_graphql_headers = {
            "Accept": "*/*",
        }
        self.session = session
        if not self.session:
            self.session = requests.Session()

    def _subscan_graphql_make_query(
        self,
        endpoint,
        query,
        variables=None,
    ):
        logger.info(f". [=] Fetching data from Graphql API from {endpoint}")
        self.session.headers.update(self.subsquid_graphql_headers)
        response = self.session.post(
            endpoint,
            json={
                "query": query,
                "variables": variables,
            },
        )

        if response.status_code in (
            301,
            302,
        ):
            response = self.session.post(
                response.headers["location"],
                json={
                    "query": query,
                    "variables": variables,
                },
            )

        if response.status_code != 200:
            logger.error(f". [-] Failed to retrieve from API. Status code: {response.status_code} - {response.text}")
            logger.info(f". [#] Graphql endpoint: {endpoint}")
            logger.info(f". [#] Query: {query}")
            logger.info(f". [#] Variables: {variables}")

            return None

        return response.json()

    def subscan_explorer_graphql(
        self,
        _query,
        variables=None,
    ):
        return self._subscan_graphql_make_query(
            endpoint=self.subsquid_explorer_endpoint,
            query=_query,
            variables=variables,
        )

    def subscan_stats_graphql(
        self,
        _query,
        variables=None,
    ):
        return self._subscan_graphql_make_query(
            endpoint=self.subsquid_stats_endpoint,
            query=_query,
            variables=variables,
        )

    def subscan_main_graphql(
        self,
        _query,
        variables=None,
    ):
        return self._subscan_graphql_make_query(
            endpoint=self.subsquid_main_endpoint,
            query=_query,
            variables=variables,
        )
