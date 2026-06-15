import time
import requests
from typing import Dict, Any, Generator, Optional
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bitrix_gcp.logging_config import logger
from bitrix_gcp.errors import BitrixAPIError

class BitrixClient:
    def __init__(self, webhook_url: str, timeout: int = 60):
        self.webhook_url = webhook_url.rstrip("/")
        self.timeout = timeout
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        retry_strategy = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.webhook_url}/{method}"
        try:
            response = self.session.post(url, json=params, timeout=self.timeout)
            if response.status_code == 503:
                logger.warning("Bitrix query limit exceeded (503). Retrying after 5s delay...")
                time.sleep(5)
                return self._call(method, params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise BitrixAPIError(f"API Error: {str(e)}")

    def get_entities(self, entity_type: str, watermark_field: str = "DATE_MODIFY",
                     start_date: Optional[str] = None) -> Generator[Dict[str, Any], None, None]:
        if entity_type == "activities":
            method = "crm.activity.list"
        else:
            method = f"crm.{entity_type}.list"

        params = {
            "select": ["*", "UF_*"],
            "order": {watermark_field: "ASC"},
            "filter": {},
            "start": -1
        }
        if start_date:
            params["filter"][f">{watermark_field}"] = start_date

        total = 0
        while True:
            result = self._call(method, params)
            records = result.get("result", [])
            next_offset = result.get("next")
            for record in records:
                yield record
                total += 1
            if next_offset:
                params["start"] = next_offset
                logger.info(f"Fetched {total} {entity_type} records. Next offset: {next_offset}")
            else:
                break
