from __future__ import annotations

import logging
from typing import Any, Literal
import time

import httpx
from lxml.html import HTMLParser as LHTMLParser
from lxml.html import document_fromstring
from lxml.etree import _Element # For type hinting

from .exceptions import SearXNGSearchException, RequestException, ParsingException
from .utils import _normalize, _normalize_url, json_loads

logger = logging.getLogger("searxng_search.SearXNGSearch")

class SearXNGSearch:
    """
    SearXNGSearch class to get search results from a local or LAN SearXNG instance.
    """

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str] | None = None,
        timeout: int | None = 30, # Increased timeout for potential network latency
        verify: bool = True,
        retries: int = 3, # retries: Number of retry attempts for failed requests
        backoff_factor: float = 0.5, # backoff_factor: Factor for exponential backoff delay
    ) -> None:
        """
        Initialize the SearXNGSearch object.

        Args:
            base_url (str): The base URL of your SearXNG instance (e.g., "http://localhost:8080" or "http://192.168.1.100:8080").
            headers (dict, optional): Dictionary of headers for the HTTP client. Defaults to None.
            timeout (int, optional): Timeout value for the HTTP client in seconds. Defaults to 30.
            verify (bool): SSL verification when making the request. Defaults to True.
            retries (int): Number of times to retry a failed HTTP request. Defaults to 3.
            backoff_factor (float): A factor by which to multiply the retry delay. The delay will be
                                    `backoff_factor * (2 ** (retry_count - 1))`. Defaults to 0.5.
        """

        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url
        self.headers = headers if headers else {}
        self.headers["User-Agent"] = "SearXNG-Search-Client/1.0" # Custom User-Agent
        self.timeout = timeout
        self.retries = retries
        self.backoff_factor = backoff_factor
        self.client = httpx.Client(
            headers=self.headers,
            timeout=self.timeout,
            verify=verify,
            follow_redirects=True, # SearXNG might redirect
        )

    def __enter__(self) -> SearXNGSearch:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: Any | None = None,
    ) -> None:
        self.client.close() # Ensure httpx client is closed

    def _get_url(
        self,
        method: Literal["POST", "GET"],
        path: str,
        params: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Helper to make HTTP requests to the SearXNG instance."""
        url = self.base_url + path.lstrip('/')
        for attempt in range(self.retries + 1): # +1 to include the initial attempt
            try:
                resp = self.client.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    json=json,
                    headers=headers,
                )
                resp.raise_for_status() # Raise an exception for 4xx/5xx responses
                return resp
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                # Log the error for the current attempt
                if isinstance(e, httpx.HTTPStatusError):
                    logger.warning(f"HTTP error (status {e.response.status_code}) for {url} (Attempt {attempt + 1}/{self.retries + 1}): {e.response.text}")
                else:
                    logger.warning(f"Request error for {url} (Attempt {attempt + 1}/{self.retries + 1}): {e}")

                # If this is the last attempt, re-raise the exception
                if attempt == self.retries:
                    logger.error(f"All {self.retries + 1} attempts failed for {url}.")
                    if isinstance(e, httpx.HTTPStatusError):
                        raise RequestException(f"HTTP error: {e.response.status_code} for {url}") from e
                    else:
                        raise RequestException(f"Request failed for {url}") from e

                # Calculate sleep time for next retry (exponential backoff)
                sleep_time = self.backoff_factor * (2 ** attempt)
                logger.info(f"Retrying {url} in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            except Exception as e:
                # Catch any other unexpected exceptions immediately, no retry for these
                logger.error(f"An unexpected error occurred for {url} during attempt {attempt + 1}: {e}")
                raise SearXNGSearchException(f"Unexpected error: {e}") from e

    def text(
        self,
        keywords: str,
        category: str = "general", # SearXNG categories
        language: str = "en-US", # SearXNG language parameter
        pageno: int = 1, # SearXNG supports pagination
        format: Literal["json", "html"] = "json", # SearXNG's preferred output format
        max_results: int | None = None, # Not directly controlled by SearXNG's API, but for post-filtering
        safesearch: Literal[0, 1, 2] = 0, # SearXNG supports safe search
    ) -> list[dict[str, str]]:
        """
        SearXNG text search.

        Args:
            keywords (str): keywords for query.
            category (str): SearXNG category, e.g., "general", "images", "videos", "news", "science", "it", etc. Defaults to "general".
            language (str): SearXNG language parameter, e.g., "en-US", "zh-CN". Defaults to "en-US".
            pageno (int): Page number for results. Defaults to 1.
            format (Literal["json", "html"]): Desired output format from SearXNG. Defaults to "json".
            max_results (int, optional): Max number of results to return. If None, returns all results from the requested page.
            safesearch (Literal[0, 1, 2]): Filter search results based on safe search level.
                                            0: Off, 1: Moderate, 2: Strict. Defaults to 0.

        Returns:
            List of dictionaries with search results.

        Raises:
            SearXNGSearchException: Base exception for searxng_search errors.
            RequestException: Raised for HTTP request errors.
            ParsingException: Raised when parsing SearXNG's response fails.
        """
        if not keywords.strip():
            raise ValueError("The 'keywords' argument is mandatory and cannot be empty.")

        params = {
            "q": keywords,
            "category": category,
            "language": language,
            "pageno": str(pageno),
            "format": format,
            "safesearch": str(safesearch),
        }

        results: list[dict[str, str]] = []

        try:
            resp = self._get_url("POST", "/search", params=params)

            if format == "json":
                data = json_loads(resp.content)
                # SearXNG JSON response structure example:
                # {
                #   "results": [
                #     {"title": "...", "url": "...", "content": "..."},
                #     ...
                #   ],
                #   "suggestions": [...],
                #   "answers": [...],
                #   "number_of_results": ...,
                #   "query": "..."
                # }
                for item in data.get("results", []):
                    title = _normalize(item.get("title", ""))
                    href = _normalize_url(item.get("url", ""))
                    body = _normalize(item.get("content", ""))
                    results.append({
                        "title": title,
                        "href": href,
                        "body": body,
                    })
                    if max_results and len(results) >= max_results:
                        break # Stop if max_results reached
            elif format == "html":
                # Parsing HTML from SearXNG is more complex and depends on its rendering.
                # This is a basic example; you'd need to inspect SearXNG's HTML structure.
                tree = document_fromstring(resp.content, LHTMLParser(remove_blank_text=True))
                # Example XPath, adjust based on your SearXNG instance's HTML
                elements = tree.xpath('//*[@id="urls"]/article')
                for e in elements:
                    title_elem = e.xpath('./h3/a/text()')
                    href_elem = e.xpath('./h3/a/@href')
                    body_elem = e.xpath('./p[@class="content"]//text()')

                    title = _normalize(title_elem[0]) if title_elem else ""
                    href = _normalize_url(href_elem[0]) if href_elem else ""
                    body = _normalize("".join(body_elem)) if body_elem else ""

                    if href: # Only add if URL is present
                        results.append({
                            "title": title,
                            "href": href,
                            "body": body,
                        })
                        if max_results and len(results) >= max_results:
                            break
            else:
                raise ValueError("Unsupported format. Choose 'json' or 'html'.")

        except Exception as e:
            logger.error(f"Failed to get text search results for '{keywords}': {e}")
            raise ParsingException(f"Failed to parse SearXNG response for '{keywords}'") from e

        return results
