import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from src.logger import logger
from src.config import config

class BitrixClient:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url.rstrip('/')
        self.session = self._build_session()

    def _build_session(self):
        retry_strategy = Retry(
            total=10,
            backoff_factor=1,  # 1s, 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s, 512s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def call(self, method: str, params: dict = None):
        url = f"{self.webhook_url}/{method}"
        try:
            response = self.session.post(url, json=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Bitrix24 API: {e}", extra={"method": method, "params": params})
            raise

    def get_deals(self, start_date: str = None):
        """
        Fetches deals from Bitrix24 using pagination and filtering.
        Sorts by DATE_MODIFY ASC to ensure kontiguity.
        Uses start=-1 for optimized pagination.
        """
        method = "crm.deal.list"
        params = {
            "select": ["*", "UF_*"],
            "order": {"DATE_MODIFY": "ASC"},
            "filter": {},
            "start": -1
        }

        if start_date:
            params["filter"][">DATE_MODIFY"] = start_date
            logger.info(f"Fetching deals modified after {start_date}")
        else:
            logger.info("Fetching all deals (full sync)")

        total_fetched = 0
        while True:
            result = self.call(method, params)
            records = result.get("result", [])
            next_offset = result.get("next")

            for record in records:
                yield record
                total_fetched += 1

            if next_offset:
                params["start"] = next_offset
                logger.info(f"Fetched {total_fetched} records. Continuing with offset {next_offset}")
            else:
                logger.info(f"Finished fetching deals. Total: {total_fetched}")
                break
