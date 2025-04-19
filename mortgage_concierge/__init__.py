"""
Main entrypoint for the Mortgage Advisor ADK service.
Run with:
    uvicorn main:app --reload --port 8008
"""
import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Load environment variables from .env
load_dotenv()

# ADK imports
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.services import InMemorySessionService
from google.adk.runners import Runner

# Import application components from agent module
from agent import session_service, runner

# FastAPI application
app = FastAPI()

class SessionCreateRequest(BaseModel):
    state: dict = {}

@app.post("/apps/{app_name}/users/{user_id}/sessions/{session_id}")
async def create_session(app_name: str, user_id: str, session_id: str, body: SessionCreateRequest):
    try:
        session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            initial_state=body.state,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    session = session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    return session.dict()

class RunRequest(BaseModel):
    app_name: str
    user_id: str
    session_id: str
    new_message: dict
    streaming: bool = False

@app.post("/run")
async def run(request: RunRequest):
    # Execute agent turn and collect all events
    try:
        event_stream = runner.run_async(
            request.new_message,
            request.user_id,
            request.session_id,
            request.app_name,
        )
        events = []
        async for evt in event_stream:
            events.append(evt.to_dict())
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run_sse")
async def run_sse(request: RunRequest):
    # Server-Sent Events stream of events
    async def event_generator():
        try:
            stream = runner.run_async(
                request.new_message,
                request.user_id,
                request.session_id,
                request.app_name,
                streaming=request.streaming,
            )
            async for evt in stream:
                yield f"data: {json.dumps(evt.to_dict())}\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")