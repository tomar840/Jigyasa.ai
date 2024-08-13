import json
import time

import requests
import streamlit as st


# Function to call the backend API (assuming it runs locally on port 8000)
def query_backend(user_query):
    url = "http://localhost:8000/query"
    params = {"query": user_query}
    response = requests.get(url, params=params, stream=True)

    for line in response.iter_lines():
        if line:
            decoded_line = line.decode("utf-8")
            yield json.loads(decoded_line)["message"]["content"]


# Custom CSS for wider response box and star animation
st.markdown(
    """
    <style>
    .stTextInput > div > div > input {
        width: 100%;
        padding: 10px;
    }

    .stButton > button {
        width: 100%;
        padding: 10px;
    }

    .stMarkdown > div {
        width: 100%;
    }

    .response-area {
        width: 100%;
        padding: 15px;
        border-radius: 10px;
        background-color: #f0f0f5;
        color: #333;
        font-size: 1.1em;
    }

    .star {
        width: 20px;
        height: 20px;
        background-image: url('https://path-to-your-bluish-star-image.png');
        background-size: cover;
        animation: glow 1s infinite alternate;
    }

    @keyframes glow {
        from {
            box-shadow: 0 0 5px #00F;
        }
        to {
            box-shadow: 0 0 20px #00F;
        }
    }

    .star-container {
        display: flex;
        align-items: center;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .response-with-star {
        display: flex;
        align-items: flex-start;
    }

    .star {
        margin-right: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def main():
    st.markdown(
        "<h1 style='text-align: center; color: white;'>Where knowledge begins</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h3 style='text-align: center;'>Jigyasa.ai</h3>", unsafe_allow_html=True
    )

    # Center the input field and button
    user_query = st.text_input("Ask anything...", "")
    submit_button = st.button("➤")

    if submit_button and user_query:
        # Show a dynamic glowing star during response fetching
        star_placeholder = st.empty()
        star_placeholder.markdown(
            '<div class="star-container"><div class="star"></div></div>',
            unsafe_allow_html=True,
        )

        # Show the progress bar
        progress_bar = st.progress(0)

        # Display a placeholder for the streamed response
        response_placeholder = st.empty()

        # Simulate fetching the response and update the progress bar
        response_text = ""
        for i, response_chunk in enumerate(query_backend(user_query)):
            response_text += response_chunk
            response_placeholder.markdown(
                f'<div class="response-with-star"><div class="star"></div><div class="response-area">{response_text}</div></div>',
                unsafe_allow_html=True,
            )
            progress_bar.progress(min(i / 10, 1.0))
            time.sleep(0.1)  # Simulate delay in receiving streamed chunks

        progress_bar.empty()  # Remove the progress bar when done
        star_placeholder.empty()  # Remove the star animation once done


if __name__ == "__main__":
    main()
