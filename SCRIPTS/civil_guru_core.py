import asyncio
import functools
import logging
import random
import time
from typing import Any, Callable, Literal, TypeVar

from pydantic import BaseModel, Field, field_validator, model_validator

# ==================================================
# Logging
# ==================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

# ==================================================
# Pydantic Model
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
    ] = "success"

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Answer cannot be empty")

        return value

    @model_validator(mode="after")
    def validate_status_confidence(self):
        if self.status == "failed":
            self.confidence = 0.0

        return self

    def summary(self) -> str:
        return (
            f"[{self.agent_name}] "
            f"status={self.status} | "
            f"confidence={self.confidence:.0%} | "
            f"latency={self.latency_ms}ms"
        )


# ==================================================
# Retry Decorator
# ==================================================


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0
):
    def decorator(func: F) -> F:

        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                wait = delay

                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)

                    except Exception as e:
                        if attempt == max_attempts - 1:
                            raise

                        logger.warning(
                            f"{func.__name__} | "
                            f"{type(e).__name__}: {e} | "
                            f"retrying in {wait:.1f}s"
                        )

                        await asyncio.sleep(wait)
                        wait *= backoff

            return async_wrapper  # type: ignore

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            wait = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise

                    logger.warning(
                        f"{func.__name__} | "
                        f"{type(e).__name__}: {e} | "
                        f"retrying in {wait:.1f}s"
                    )

                    time.sleep(wait)
                    wait *= backoff

        return sync_wrapper  # type: ignore

    return decorator


# ==================================================
# Timed Decorator
# ==================================================


def timed(func: F) -> F:

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()

            result = await func(*args, **kwargs)

            elapsed_ms = (
                time.perf_counter() - start
            ) * 1000

            label = args[0] if args else func.__name__

            logger.info(
                f"{func.__name__}[{label}] "
                f"took {elapsed_ms:.1f}ms"
            )

            return result

        return async_wrapper  # type: ignore

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()

        result = func(*args, **kwargs)

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        label = args[0] if args else func.__name__

        logger.info(
            f"{func.__name__}[{label}] "
            f"took {elapsed_ms:.1f}ms"
        )

        return result

    return sync_wrapper  # type: ignore


# ==================================================
# Simulated Agent
# ==================================================


@retry(max_attempts=3, delay=1.0, backoff=2.0)
@timed
async def simulate_agent(
    agent_name: str,
    query: str
) -> AgentResponse:

    start = time.perf_counter()

    # Simulate LLM latency
    sleep_time = random.uniform(1.0, 3.0)

    await asyncio.sleep(sleep_time)

    latency_ms = int(
        (time.perf_counter() - start) * 1000
    )

    confidence = round(
        random.uniform(0.60, 0.99),
        2
    )

    status = (
        "partial"
        if confidence < 0.75
        else "success"
    )

    return AgentResponse(
        agent_name=agent_name,
        query=query,
        answer=f"{agent_name} processed '{query}'",
        confidence=confidence,
        latency_ms=latency_ms,
        status=status
    )


# ==================================================
# Concurrent Runner
# ==================================================


async def run_agents_concurrent(
    query: str
) -> list[AgentResponse]:

    results = await asyncio.gather(
        simulate_agent(
            "Syllabus Mapper",
            query
        ),
        simulate_agent(
            "Fact Checker",
            query
        ),
        simulate_agent(
            "Answer Generator",
            query
        ),
        return_exceptions=True
    )

    responses: list[AgentResponse] = []

    for result in results:

        if isinstance(result, Exception):

            responses.append(
                AgentResponse(
                    agent_name="Unknown",
                    query=query,
                    answer="Agent failed",
                    confidence=0.0,
                    latency_ms=0,
                    status="failed"
                )
            )

        else:
            responses.append(result)

    return responses


# ==================================================
# Main
# ==================================================


if __name__ == "__main__":

    print("\nRunning Civil Guru Agents...\n")

    responses = asyncio.run(
        run_agents_concurrent(
            "What is Article 370?"
        )
    )

    print("\n=== Agent Results ===\n")

    for response in responses:
        print(response.summary())