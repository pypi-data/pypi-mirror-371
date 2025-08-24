# packages/python/whatsextract/__init__.py
from __future__ import annotations

from typing import List, Dict, Optional, Any, Iterable, Callable
import os
import time
import json
import hmac
import hashlib
import requests
import asyncio
import aiohttp
from dataclasses import dataclass

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # Optional at runtime


__all__ = [
    "WhatsExtract",
    "ExtractionResult",
    "validate_webhook_signature",
]

__version__ = "1.0.0"

DEFAULT_BASE_URL = os.getenv("WE_BASE_URL", "http://localhost:8000")


@dataclass
class ExtractionResult:
    index: int
    data: Optional[Dict[str, Any]]
    status: str
    error: Optional[str]

    def ok(self) -> bool:
        return self.status == "success"


class WhatsExtract:
    """
    WhatsExtract API Client (sync + async)

    Example:
        client = WhatsExtract(api_key="your_api_key", base_url="http://127.0.0.1:8000")
        r = client.extract("Contact me at john@example.com")
        print(r["email"])
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        if not isinstance(api_key, str) or len(api_key) < 12:
            raise ValueError("Invalid API key")
        self.api_key = api_key
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    # -------------- internal helpers --------------
    def _retry_request(
        self,
        method: str,
        path: str,
        json_body: Optional[Dict[str, Any]] = None,
        *,
        allow_404: bool = False,
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        tries = 0
        while True:
            tries += 1
            try:
                resp = self._session.request(
                    method=method,
                    url=url,
                    json=json_body,
                    timeout=self.timeout,
                )
                if (resp.status_code == 404 and allow_404) or (200 <= resp.status_code < 300):
                    return resp

                # Retry 429 and 5xx; raise for others
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    raise requests.HTTPError(
                        f"{resp.status_code} {resp.text}", response=resp
                    )
                resp.raise_for_status()
                return resp
            except requests.HTTPError:
                if tries > self.max_retries:
                    raise
                backoff = min(1.0 * tries, 4.0)
                time.sleep(backoff)

    # -------------- public sync methods --------------
    def extract(self, message: str, mode: str = "lite") -> Dict[str, Any]:
        out = self.batch_extract([message], mode=mode)
        item = out[0]
        if not item.ok():
            raise RuntimeError(item.error or "Extraction failed")
        return item.data or {}

    def batch_extract(
        self,
        messages: List[str],
        mode: str = "lite",
        skip_errors: bool = True,
        webhook_url: Optional[str] = None,
        chunk_size: int = 100,
        progress_callback: Optional[Callable[[Dict[str, int]], None]] = None,
    ) -> List[ExtractionResult]:
        if not messages:
            raise ValueError("messages must not be empty")
        if chunk_size < 1 or chunk_size > 100:
            chunk_size = 100

        results: List[ExtractionResult] = []
        processed = 0
        total = len(messages)

        for i in range(0, total, chunk_size):
            chunk = messages[i : i + chunk_size]
            body: Dict[str, Any] = {
                "messages": chunk,
                "mode": mode,
                "skip_errors": skip_errors,
            }
            if webhook_url:
                if not webhook_url.startswith("https://"):
                    raise ValueError("webhook_url must be HTTPS")
                body["webhook_url"] = webhook_url

            resp = self._retry_request("POST", "/v2/batch", json_body=body)
            data = resp.json()

            # map chunk indices to global indices
            for item in data.get("results", []):
                results.append(
                    ExtractionResult(
                        index=i + int(item["index"]),
                        data=item.get("data"),
                        status=str(item.get("status")),
                        error=item.get("error"),
                    )
                )
                processed += 1
                if progress_callback:
                    progress_callback({"processed": processed, "total": total})

        # keep order
        results.sort(key=lambda r: r.index)
        return results

    def configure_webhook(
        self,
        webhook_url: str,
        events: Optional[List[str]] = None,
        secret: Optional[str] = None,
        active: bool = True,
    ) -> Dict[str, Any]:
        if not webhook_url.startswith("https://"):
            raise ValueError("webhook_url must be HTTPS")
        body = {
            "webhook_url": webhook_url,
            "events": events
            or ["extraction.completed", "batch.completed", "quota.exceeded"],
            "secret": secret,
            "active": bool(active),
        }
        resp = self._retry_request("POST", "/v2/webhooks", json_body=body)
        return resp.json()

    def get_usage(self) -> Dict[str, Any]:
        resp = self._retry_request("GET", "/v2/usage")
        return resp.json()

    @staticmethod
    def validate_message(message: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Stateless helper that does not need an instance (no auth required by API).
        """
        url_base = (base_url or DEFAULT_BASE_URL).rstrip("/")
        resp = requests.post(
            f"{url_base}/v2/validate",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            json={"message": message},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    # -------------- async API --------------
    async def extract_async(self, message: str, mode: str = "lite") -> Dict[str, Any]:
        arr = await self.batch_extract_async([message], mode=mode)
        item = arr[0]
        if not item.ok():
            raise RuntimeError(item.error or "Extraction failed")
        return item.data or {}

    async def batch_extract_async(
        self,
        messages: List[str],
        mode: str = "lite",
        skip_errors: bool = True,
        webhook_url: Optional[str] = None,
        chunk_size: int = 100,
        progress_callback: Optional[Callable[[Dict[str, int]], None]] = None,
    ) -> List[ExtractionResult]:
        if not messages:
            raise ValueError("messages must not be empty")
        if chunk_size < 1 or chunk_size > 100:
            chunk_size = 100

        results: List[ExtractionResult] = []
        processed = 0
        total = len(messages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as sess:
            for i in range(0, total, chunk_size):
                chunk = messages[i : i + chunk_size]
                body: Dict[str, Any] = {
                    "messages": chunk,
                    "mode": mode,
                    "skip_errors": skip_errors,
                }
                if webhook_url:
                    if not webhook_url.startswith("https://"):
                        raise ValueError("webhook_url must be HTTPS")
                    body["webhook_url"] = webhook_url

                tries = 0
                while True:
                    tries += 1
                    async with sess.post(f"{self.base_url}/v2/batch", json=body) as r:
                        if r.status == 429 or 500 <= r.status < 600:
                            if tries > self.max_retries:
                                text = await r.text()
                                raise RuntimeError(f"HTTP {r.status} {text}")
                            await asyncio.sleep(min(1.0 * tries, 4.0))
                            continue
                        if r.status < 200 or r.status >= 300:
                            text = await r.text()
                            raise RuntimeError(f"HTTP {r.status} {text}")
                        data = await r.json()
                        break

                for item in data.get("results", []):
                    results.append(
                        ExtractionResult(
                            index=i + int(item["index"]),
                            data=item.get("data"),
                            status=str(item.get("status")),
                            error=item.get("error"),
                        )
                    )
                    processed += 1
                    if progress_callback:
                        progress_callback({"processed": processed, "total": total})

        results.sort(key=lambda r: r.index)
        return results

    # -------------- DataFrame helper --------------
    def extract_from_dataframe(
        self,
        df: "pd.DataFrame",
        column: str,
        add_columns: bool = True,
        mode: str = "lite",
        chunk_size: int = 100,
    ) -> "pd.DataFrame":
        if pd is None:
            raise RuntimeError("pandas not installed")
        if column not in df.columns:
            raise KeyError(f"Column '{column}' not found")

        messages: List[str] = df[column].astype(str).tolist()
        results = self.batch_extract(messages, mode=mode, chunk_size=chunk_size)

        emails: List[Optional[str]] = []
        phones: List[Optional[str]] = []
        names: List[Optional[str]] = []
        confidences: List[Optional[float]] = []

        for r in results:
            d = r.data or {}
            emails.append(d.get("email"))
            phones.append(d.get("phone"))
            names.append(d.get("name"))
            confidences.append(d.get("confidence"))

        if add_columns:
            df = df.copy()
            df["we_email"] = emails
            df["we_phone"] = phones
            df["we_name"] = names
            df["we_confidence"] = confidences
            return df
        else:
            return pd.DataFrame(
                {
                    "email": emails,
                    "phone": phones,
                    "name": names,
                    "confidence": confidences,
                }
            )


# -------------- Webhook utilities --------------
def validate_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """
    Verify HMAC SHA-256 signature sent in header "X-WhatsExtract-Signature".

    signature format: "sha256=<hex>"
    """
    if not signature or not signature.startswith("sha256="):
        return False
    mac = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    expected = f"sha256={mac}"
    # timing-safe compare
    a = expected.encode("utf-8")
    b = signature.encode("utf-8")
    if len(a) != len(b):
        return False
    return hmac.compare_digest(a, b)
