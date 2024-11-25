from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cachetools import TTLCache
from server.interactive_query_handler import InteractiveQueryHandler  # Import your class

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

interactive_engine = None
cache = TTLCache(maxsize=1000, ttl=3600)


@app.on_event("startup")
def startup_event():
    """
    Load configuration and initialize InteractiveQueryHandler.
    """
    global interactive_engine
    config_path = "config/config.yaml"
    try:
        print("Loading configuration...")
        interactive_engine = InteractiveQueryHandler(config_path)
        interactive_engine.init_global_rag_chain()
        print("InteractiveQueryHandler initialized successfully.")
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        raise RuntimeError("Server failed to start due to initialization error.")


@app.post("/query")
async def query(request: QueryRequest):
    """
    Handle a query across all loaded documents.
    """
    global interactive_engine, cache

    cache_key = request.query
    try:
        if cache_key in cache:
            return {"query": request.query, "response": cache[cache_key]}

        response = interactive_engine.invoke_query(request.query)
        cache[cache_key] = response
        return {"query": request.query, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
