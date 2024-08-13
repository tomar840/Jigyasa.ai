from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from libs.modules.answers.get_answers import generate_stream_response

app = FastAPI()


@app.get("/query")
async def query(request: Request):
    user_query = request.query_params.get("query", None)
    if not user_query:
        return {"error": "Query parameter is missing."}

    return StreamingResponse(
        generate_stream_response(user_query), media_type="application/json"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
