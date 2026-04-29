import time
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from agent import agent_app

logger = logging.getLogger("api.chat_router")
chat_router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    session_id: str = Field(
        ..., description="Unique ID to maintain chat context across turns."
    )
    message: str = Field(..., description="The user's input message.")


class ChatResponse(BaseModel):
    response: str
    processing_time_ms: float = Field(
        ..., description="Time taken to generate the response in milliseconds."
    )
    timestamp: str = Field(..., description="UTC timestamp of the response.")


@chat_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Standard endpoint that waits for the full response before returning."""
    start_time = time.time()
    logger.info(
        f"Received request | Session: {request.session_id} | Message: '{request.message}'"
    )

    try:
        config = {"configurable": {"thread_id": request.session_id}}
        logger.info(f"Invoking LangGraph agent for session '{request.session_id}'...")

        events = await agent_app.ainvoke(
            {"messages": [("user", request.message)]}, config=config
        )

        final_message = events["messages"][-1].content
        end_time = time.time()
        processing_time = round((end_time - start_time) * 1000, 2)

        logger.info(f"Response generated successfully in {processing_time}ms.")

        return ChatResponse(
            response=final_message,
            processing_time_ms=processing_time,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    except Exception as e:
        logger.error(
            f"Error processing request for session '{request.session_id}': {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Internal server error during agent execution."
        )


@chat_router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """Streams the agent's response token-by-token for responsive UX."""
    logger.info(
        f"Received streaming request | Session: {request.session_id} | Message: '{request.message}'"
    )

    async def event_stream():
        config = {"configurable": {"thread_id": request.session_id}}
        try:
            async for event in agent_app.astream_events(
                {"messages": [("user", request.message)]}, config=config, version="v2"
            ):
                if event["event"] == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        yield f"data: {json.dumps({'token': chunk.content})}\n\n"

        except Exception as e:
            logger.error(
                f"Streaming error for session '{request.session_id}': {str(e)}",
                exc_info=True,
            )
            yield f"data: {json.dumps({'error': 'Internal server error during streaming.'})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
