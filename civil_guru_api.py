from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Literal

import asyncio
import json
import logging
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


# ==================================================
# Logging
# ==================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==================================================
# Lifespan
# ==================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Civil Guru API Starting...")
    yield
    logger.info("Civil Guru API Shutting Down...")


# ==================================================
# FastAPI App
# ==================================================

app = FastAPI(
    title="Civil Guru API",
    version="1.0.0",
    lifespan=lifespan
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# Models
# ==================================================

class AgentResponse(BaseModel):
    agent_name: str
    query: str
    answer: str

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    latency_ms: int = Field(
        ge=0
    )

    status: Literal[
        "success",
        "partial",
        "failed"
    ]


class QueryRequest(BaseModel):
    query: str = Field(
        min_length=5,
        max_length=500,
        description="User query"
    )

    agents: list[str] = Field(
        min_length=1,
        description="List of agents to run"
    )


class QueryResponse(BaseModel):
    query: str
    results: list[AgentResponse]
    total_latency_ms: int        
    agents_invoked: int          


# ==================================================
# Simulated Agent
# ==================================================

async def simulate_agent(
    agent_name: str,
    query: str
) -> AgentResponse:

    start = time.perf_counter()

    await asyncio.sleep(1.5)

    latency_ms = int(
        (time.perf_counter() - start) * 1000
    )

    confidence = 0.90
    status = "success"

    return AgentResponse(
        agent_name=agent_name,
        query=query,
        answer=f"{agent_name} processed: {query}",
        confidence=confidence,
        latency_ms=latency_ms,
        status=status
    )


# ==================================================
# Health Endpoint
# ==================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat()
    }


# ==================================================
# Query Endpoint
# ==================================================

@app.post(
    "/query",
    response_model=QueryResponse
)
async def query_agents(
    request: QueryRequest
):

    try:

        tasks = [
            simulate_agent(
                agent_name,
                request.query
            )
            for agent_name in request.agents
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

        responses: list[AgentResponse] = []

        for result in results:

            if isinstance(result, Exception):

                logger.error(
                    f"Agent failed: {result}"
                )

                responses.append(
                    AgentResponse(
                        agent_name="Unknown",
                        query=request.query,
                        answer="Agent failed",
                        confidence=0.0,
                        latency_ms=0,
                        status="failed"
                    )
                )

            else:
                responses.append(result)

        return QueryResponse(
            query=request.query,
            results=responses
        )

    except Exception:

        logger.exception(
            "Query endpoint failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error. Check server logs."
        )


# ==================================================
# Streaming Endpoint (SSE)
# ==================================================

@app.post("/query/stream")
async def stream_query(
    request: QueryRequest
):

    async def event_generator():

        response_text = (
            f"Civil Guru response for: {request.query}"
        )

        tokens = response_text.split()

        for token in tokens:

            payload = {
                "token": token
            }

            yield (
                f"data: {json.dumps(payload)}\n\n"
            )

            await asyncio.sleep(0.05)

        yield (
            f"data: {json.dumps({'done': True})}\n\n"
        )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"   # prevents nginx from buffering your stream
        }
    )


# ==================================================
# Run Locally
# ==================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "civil_guru_api:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )

