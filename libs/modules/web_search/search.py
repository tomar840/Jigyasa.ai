import concurrent.futures
import re
from queue import Queue
from typing import Optional

import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from readability import Document


class WebSearcher:
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"
        }
        self.session = requests.Session()
        self.session.headers.update(headers)

    def get_clean_text_from_url(self, url: str, timeout: int = 2) -> Optional[str]:
        """Extract clean text from the specified url.

        Args:
            url (str): url to fetch the cleaned text
            timeout (int, optional): timeout (in seconds). Defaults to 2.

        Raises:
            Exception: raise exception if status code is not 200

        Returns:
            Optional[str]: cleaned text
        """
        try:
            response = self.session.get(url, timeout=timeout)
            if response.status_code != 200:
                raise Exception(
                    f"HTTP error {response.status_code}: {response.reason} for URL {url}"
                )
            document = Document(response.text)
            html_content = document.summary()
            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text(separator="")
            text = re.sub(r"\n\s*\n\s*\n*", " \n\n ", text)
            return text.strip()
        except requests.exceptions.RequestException:
            return None
        except Exception:
            return None

    def google_search(
        self,
        search_term: str,
        api_key: str,
        cse_id: str,
        num_results: int = 2,
        **kwargs,
    ) -> str:
        """Get search results from google search api.

        Args:
            search_term (str): search query
            api_key (str): API key to use in google search API
            cse_id (str): CSE id for custom google search
            num_results (int, optional): number of results to fetch. Defaults to 2.

        Returns:
            str: search results
        """
        service = build("customsearch", "v1", developerKey=api_key)
        res = (
            service.cse()
            .list(q=search_term, cx=cse_id, num=num_results, **kwargs)
            .execute()
        )
        return res["items"]

    def form_articles(
        self, search_queries: list[str], gs_api_key: str, gs_cse_id: str
    ) -> str:
        """Form the articles from the search queries.

        Args:
            search_queries (str): search queries
            gs_api_key (str): API key to use in google search API
            gs_cse_id (str): CSE id for custom google search

        Returns:
            str: formatted articles.
        """
        articles = ""
        article_idx = 1

        search_queries = [s for s in search_queries if s != "not_needed"]

        # len(SEARCH_QUERIES) can be one of [1, 2, 3] only
        max_local_articles = 6 // len(search_queries)

        num_results_for_search = 10 if len(search_queries) == 1 else 5

        for qry in search_queries:
            local_article_idx = 0
            results = self.google_search(
                qry, gs_api_key, gs_cse_id, num_results=num_results_for_search
            )
            urls = [result["link"] for result in results]

            for url in urls:
                content = self.get_clean_text_from_url(url)
                if content:
                    content = content[:3500]
                    articles += f"""<ARTICLE {article_idx}>\n{content}\n<\ARTICLE {article_idx}>\n\n"""
                    article_idx += 1
                    local_article_idx += 1
                    if local_article_idx == max_local_articles:
                        break

            if article_idx > 6:
                break

        # Remove exiting [citation] marks from scraped articles
        articles = re.sub(r"\[\d+\]", "", articles)

        return articles

    def form_articles_mp(
        self, search_queries: list[str], gs_api_key: str, gs_cse_id: str
    ) -> tuple[str, dict[int, any]]:
        """Get article map.

        Args:
            search_queries (list[str]): search queries
            gs_api_key (str): API key to use in google search API
            gs_cse_id (str): CSE id for custom google search

        Returns:
            tuple[str, dict[int, any]]: formatted articles and query index map
        """
        articles_queue = Queue()
        article_idx = 1  # Start indexing from 1

        search_queries = [s for s in search_queries if s != "not_needed"]

        max_local_articles = 6 // len(search_queries)
        num_results_for_search = 10 if len(search_queries) == 1 else 5

        def process_query(qry):
            results = self.google_search(
                qry, gs_api_key, gs_cse_id, num_results=num_results_for_search
            )
            urls = [result["link"] for result in results]

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_url = {
                    executor.submit(self.get_clean_text_from_url, url): url
                    for url in urls
                }
                local_article_idx = 0

                for future in concurrent.futures.as_completed(future_to_url):
                    if local_article_idx >= max_local_articles:
                        break
                    try:
                        content = future.result()
                        if content:
                            content = content[:3500]  # Limit content size
                            articles_queue.put((content, future_to_url[future]))
                            local_article_idx += 1
                    except Exception as exc:
                        print(f"{future_to_url[future]} generated an exception: {exc}")

        # Process each query in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_query, search_queries)

        # Collect all articles from the queue and build index to URL map
        artciles = ""
        idx_to_url = {}
        while not articles_queue.empty():
            content, url = articles_queue.get()
            artciles += (
                f"<ARTICLE {article_idx}>\n{content}\n</ARTICLE {article_idx}>\n\n"
            )
            idx_to_url[article_idx] = url
            article_idx += 1

        # Remove existing [citation] marks from scraped articles
        artciles = re.sub(r"\[\d+\]", "", artciles)

        return artciles, idx_to_url
