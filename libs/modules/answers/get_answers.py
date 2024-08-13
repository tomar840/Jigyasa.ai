import datetime
import json
import os

from dotenv import load_dotenv

from libs.modules.model_inference.engine import LLMEngine
from libs.modules.prompts.model_prompts import (
    CHAT_TEMPLATE, QUERY_REPHRASE_COMPLETION_PROMPT,
    REPHRASE_QUERY_FOR_SEARCH_SYSTEM_PROMPT, RESPONSE_FORMATION_SYSTEM_PROMPT,
    USER_QUERY_ANSWER_COMPLETION_PROMPT)
from libs.modules.web_search.search import WebSearcher

load_dotenv()

GS_API_KEY = os.getenv("GS_API_KEY")
GS_CSE_ID = os.getenv("GS_CSE_ID")

# Initialize LLM Engine and Web Searcher
llm_engine = LLMEngine()
web_search = WebSearcher()

# To keep chat history
chat_history = []


def generate_stream_response(user_query):
    global chat_history

    # Get rephrased search queries
    rephrased_search_queries = llm_engine.forward(
        REPHRASE_QUERY_FOR_SEARCH_SYSTEM_PROMPT.format(
            CHAT_HISTORY="\n".join(chat_history),
            CURRENT_DATE=datetime.date.today().strftime("%B %-d, %Y"),
        ),
        QUERY_REPHRASE_COMPLETION_PROMPT.format(QUERY=user_query),
    )

    try:
        rephrased_search_queries = eval(rephrased_search_queries)
        if type(rephrased_search_queries) != list:
            raise Exception("Could not parse rephrased queries.")
        rephrased_search_queries = rephrased_search_queries[:3]
    except Exception:
        yield json.dumps(
            {
                "message": {
                    "content": "Jigyasa: Cannot answer this query at this moment."
                }
            }
        ) + "\n"
        return

    # Web search and form articles
    search_articles_formed, idx_url_mapping = web_search.form_articles_mp(
        rephrased_search_queries, GS_API_KEY, GS_CSE_ID
    )

    # Fetch model response
    query_response_stream = llm_engine.forward(
        RESPONSE_FORMATION_SYSTEM_PROMPT.format(
            ARTICLES=search_articles_formed,
            CURRENT_DATE=datetime.date.today().strftime("%B %-d, %Y"),
        ),
        USER_QUERY_ANSWER_COMPLETION_PROMPT.format(QUERY=user_query),
        stream=True,
    )

    streamed_response_list = []
    for chunk in query_response_stream:
        streamed_response_list.append(chunk["message"]["content"])
        yield json.dumps({"message": {"content": streamed_response_list[-1]}}) + "\n"

    query_response_stream = "".join(streamed_response_list)

    # Update chat history
    chat_history.append(
        CHAT_TEMPLATE.format(
            USER_QUERY=user_query, ASSISTANT_RESPONSE=query_response_stream
        )
    )

    if len(chat_history) > 2:
        chat_history = chat_history[1:]

    # Send sources information
    for idx, url in idx_url_mapping.items():
        yield json.dumps({"message": {"content": f"[{idx}] - {url}"}}) + "\n"
