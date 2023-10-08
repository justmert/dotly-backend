import requests
import os
import time
from time import (
    sleep,
)
import logging
import tools.log_config as log_config

logger = logging.getLogger(__name__)


class SubscanActor:
    @property
    def get_session(
        self,
    ):
        return self.session

    def __init__(
        self,
        session=None,
    ):
        self.subscan_rest_endpoint = "https://polkadot.api.subscan.io/api/"
        self.subscan_rest_headers = {
            "Accept": "*/*",
            "x-api-key": os.environ["SUBSCAN_API_KEY"],
        }
        self.session = session
        if not self.session:
            self.session = requests.Session()

    def subscan_rest_make_request(
        self,
        url,
        variables=None,
        data=None,
        max_page_fetch=float("inf"),
    ):
        url = f"{self.subscan_rest_endpoint}{url}"
        logger.info(f". [=] Fetching data from REST API from {url}")

        result = []
        current_fetch_count = 0
        while url and (current_fetch_count < max_page_fetch):
            logger.info(f". page {current_fetch_count + 1}/{max_page_fetch} of {url}")
            self.session.headers.update(self.subscan_rest_headers)
            response = self.session.post(
                url,
                params=variables,
                json=data,
            )

            if response.status_code == 200:
                json_response = response.json()
                url = response.links.get(
                    "next",
                    {},
                ).get(
                    "url",
                    None,
                )
                if max_page_fetch == 1:
                    return json_response

                if isinstance(
                    json_response,
                    list,
                ):
                    result.extend(json_response)

                else:
                    result.append(json_response)

                if url is None:
                    if current_fetch_count == 0:
                        return json_response

                current_fetch_count += 1

            elif response.status_code == 401:  # Unauthorized
                logger.error(
                    f" [-] Failed to retrieve from API. Status code: {response.status_code} - {response.text}. Please check your api key."
                )
                break

            elif response.status_code == 404:  # Not found
                logger.error(
                    f" [-] Failed to retrieve from API. Status code: {response.status_code} - {response.text}. Please check your endpoint."
                )
                break

            elif response.status_code == 429:  # Too many requests
                logger.warning(f" [-] Rate limit exceeded.")
                # get retry-after header
                retry_after = response.headers.get(
                    "retry-after",
                    None,
                )
                try:
                    if retry_after is not None:
                        retry_after = int(retry_after)
                        self.rate_limit_wait(retry_after)
                        continue
                except:
                    pass

            elif response.status_code in [
                500,
                502,
                503,
                504,
            ]:  # Internal server error
                logger.error(
                    f" [-] Failed to retrieve from API. Status code: {response.status_code} - {response.text}. Internal server error, see https://subscan.statuspage.io/"
                )
                break

            else:
                logger.error(f" [-] Failed to retrieve from API. Status code: {response.status_code} - {response.text}")
                logger.info(f" [#] Rest endpoint: {url}")
                logger.info(f" [#] Variables: {variables}")
                break
        return result

    def rate_limit_wait(
        self,
        retry_after,
    ):
        logger.warning(f". [-] Waiting for {retry_after} seconds which is {round(retry_after / 60, 2)} minutes.")
        time.sleep(retry_after)
