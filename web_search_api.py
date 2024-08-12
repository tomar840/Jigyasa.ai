from googleapiclient.discovery import build
import requests
from readability import Document
from bs4 import BeautifulSoup
import re
import concurrent.futures
from queue import Queue


class WebSearcher:
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"
        }
        self.session = requests.Session()
        self.session.headers.update(headers)

    def get_clean_text_from_url(self, url, timeout=2):
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
        except requests.exceptions.RequestException as e:
            # print(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            # print(f"Failed to process {url}: {e}")
            return None

    def google_search(self, search_term, api_key, cse_id, num_results=2, **kwargs):
        service = build("customsearch", "v1", developerKey=api_key)
        res = (
            service.cse()
            .list(q=search_term, cx=cse_id, num=num_results, **kwargs)
            .execute()
        )
        return res["items"]

    def form_articles(self, SEARCH_QUERIES, gs_api_key, gs_cse_id):
        ARTICLES = ""
        article_idx = 1

        SEARCH_QUERIES = [s for s in SEARCH_QUERIES if s != "not_needed"]

        # len(SEARCH_QUERIES) can be one of [1, 2, 3] only
        max_local_articles = 6 // len(SEARCH_QUERIES)

        num_results_for_search = 10 if len(SEARCH_QUERIES) == 1 else 5

        for qry in SEARCH_QUERIES:
            local_article_idx = 0
            results = self.google_search(
                qry, gs_api_key, gs_cse_id, num_results=num_results_for_search
            )
            urls = [result["link"] for result in results]

            for url in urls:
                content = self.get_clean_text_from_url(url)
                if content:
                    content = content[:3500]
                    ARTICLES += f"""<ARTICLE {article_idx}>\n{content}\n<\ARTICLE {article_idx}>\n\n"""
                    article_idx += 1
                    local_article_idx += 1
                    if local_article_idx == max_local_articles:
                        break

            if article_idx > 6:
                break

        # Remove exiting [citation] marks from scraped articles
        ARTICLES = re.sub(r"\[\d+\]", "", ARTICLES)

        return ARTICLES

    def form_articles_mp(self, SEARCH_QUERIES, gs_api_key, gs_cse_id):
        articles_queue = Queue()
        article_idx = 1  # Start indexing from 1

        SEARCH_QUERIES = [s for s in SEARCH_QUERIES if s != "not_needed"]

        max_local_articles = 6 // len(SEARCH_QUERIES)
        num_results_for_search = 10 if len(SEARCH_QUERIES) == 1 else 5

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
            executor.map(process_query, SEARCH_QUERIES)

        # Collect all articles from the queue and build index to URL map
        ARTICLES = ""
        idx_to_url = {}
        while not articles_queue.empty():
            content, url = articles_queue.get()
            ARTICLES += (
                f"<ARTICLE {article_idx}>\n{content}\n</ARTICLE {article_idx}>\n\n"
            )
            idx_to_url[article_idx] = url
            article_idx += 1

        # Remove existing [citation] marks from scraped articles
        ARTICLES = re.sub(r"\[\d+\]", "", ARTICLES)

        return ARTICLES, idx_to_url
