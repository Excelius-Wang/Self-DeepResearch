import json
import asyncio
import uuid
from typing import List, Optional, Dict
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel import Session, select, col

from src.graph import create_graph
from src.database import create_db_and_tables, engine, get_session
from src.db_models import ResearchSession

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Self-DeepResearch API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    task: str = Field(..., min_length=5, max_length=300, description="Research task description")
    max_loops: int = Field(3, ge=1, le=5, description="Max research loops (depth)")

class HistorySummary(BaseModel):
    """Lightweight history item for list view"""
    id: int
    task: str
    created_at: datetime
    notes_count: int

    class Config:
        from_attributes = True

# Global semaphore for concurrency control
MAX_CONCURRENT_RESEARCH = 2
research_semaphore = asyncio.Semaphore(MAX_CONCURRENT_RESEARCH)

# Track active research tasks for cancellation
active_tasks: Dict[str, asyncio.Event] = {}

# Queue tracking for position info
waiting_queue: List[str] = []

# Friendly error messages
ERROR_MESSAGES = {
    "api_error": "AI service temporarily unavailable. Please try again.",
    "search_error": "Unable to search. Please check your network connection.",
    "timeout": "Request timed out. Try reducing research depth.",
    "rate_limit": "Too many requests. Please wait a moment and try again.",
    "invalid_response": "Received invalid response from AI. Please try again.",
    "network_error": "Network error occurred. Please check your connection.",
}

def get_friendly_error(error: Exception) -> str:
    """Map exception to friendly error message"""
    error_str = str(error).lower()
    if "rate" in error_str or "limit" in error_str:
        return ERROR_MESSAGES["rate_limit"]
    if "timeout" in error_str:
        return ERROR_MESSAGES["timeout"]
    if "network" in error_str or "connection" in error_str:
        return ERROR_MESSAGES["network_error"]
    if "api" in error_str or "key" in error_str:
        return ERROR_MESSAGES["api_error"]
    if "search" in error_str or "tavily" in error_str:
        return ERROR_MESSAGES["search_error"]
    return f"An error occurred: {str(error)[:100]}"

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/history", response_model=List[HistorySummary])
async def get_history(session: Session = Depends(get_session)):
    """Get history list with summary only (no full report content)"""
    statement = select(ResearchSession).order_by(col(ResearchSession.created_at).desc())
    results = session.exec(statement)
    summaries = []
    for item in results.all():
        notes = item.notes if hasattr(item, 'notes') else []
        summaries.append(HistorySummary(
            id=item.id,
            task=item.task,
            created_at=item.created_at,
            notes_count=len(notes) if notes else 0
        ))
    return summaries

@app.get("/history/{session_id}", response_model=ResearchSession)
async def get_history_item(session_id: int, session: Session = Depends(get_session)):
    item = session.get(ResearchSession, session_id)
    if not item:
        raise HTTPException(status_code=404, detail="Session not found")
    return item

@app.delete("/history/{session_id}")
async def delete_history_item(session_id: int, session: Session = Depends(get_session)):
    item = session.get(ResearchSession, session_id)
    if not item:
        raise HTTPException(status_code=404, detail="Session not found")
    session.delete(item)
    session.commit()
    return {"status": "deleted"}

@app.post("/research/{session_id}/cancel")
async def cancel_research(session_id: str):
    """Cancel an ongoing research task"""
    if session_id in active_tasks:
        active_tasks[session_id].set()
        return {"status": "cancelling"}
    return {"status": "not_found"}

@app.post("/research/stream")
async def stream_research(request: ResearchRequest):
    session_id = str(uuid.uuid4())
    cancel_event = asyncio.Event()
    active_tasks[session_id] = cancel_event

    # Check queue position
    queue_position = len(waiting_queue)

    # Try to acquire semaphore
    try:
        await asyncio.wait_for(research_semaphore.acquire(), timeout=0.1)
    except asyncio.TimeoutError:
        # Add to waiting queue
        waiting_queue.append(session_id)
        queue_position = len(waiting_queue)

        async def queued_generator():
            try:
                # Notify client about queue position
                yield f"data: {json.dumps({'type': 'queued', 'position': queue_position, 'session_id': session_id})}\n\n"

                # Wait for semaphore
                await research_semaphore.acquire()
                waiting_queue.remove(session_id)

                # Check if cancelled while waiting
                if cancel_event.is_set():
                    yield f"data: {json.dumps({'type': 'cancelled'})}\n\n"
                    return

                # Continue with normal flow
                async for event in _run_research(request, session_id, cancel_event):
                    yield event
            finally:
                if session_id in waiting_queue:
                    waiting_queue.remove(session_id)
                research_semaphore.release()
                if session_id in active_tasks:
                    del active_tasks[session_id]

        return StreamingResponse(queued_generator(), media_type="text/event-stream")

    async def event_generator():
        try:
            async for event in _run_research(request, session_id, cancel_event):
                yield event
        finally:
            research_semaphore.release()
            if session_id in active_tasks:
                del active_tasks[session_id]

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def _run_research(request: ResearchRequest, session_id: str, cancel_event: asyncio.Event):
    """Core research logic with streaming events"""
    graph = create_graph()
    initial_state = {
        "task": request.task,
        "sub_queries": [],
        "notes": [],
        "report_content": "",
        "review_count": 0,
        "max_loops": request.max_loops,
        "feedback": None
    }

    sent_notes_count = 0
    full_report_content = ""
    accumulated_notes = []
    current_loop = 0
    current_phase = "planner"

    # Send session ID to client
    yield f"data: {json.dumps({'type': 'session_start', 'session_id': session_id})}\n\n"

    try:
        async for event in graph.astream_events(initial_state, version="v1"):
            # Check for cancellation
            if cancel_event.is_set():
                yield f"data: {json.dumps({'type': 'cancelled'})}\n\n"
                return

            kind = event["event"]
            name = event["name"]
            data = event["data"]

            # --- 1. Planner ---
            if kind == "on_chain_start" and name == "planner":
                current_phase = "planner"
                yield f"data: {json.dumps({'type': 'progress', 'current_loop': current_loop, 'max_loops': request.max_loops, 'phase': 'planner', 'message': 'Planning research strategy...'})}\n\n"

            if kind == "on_chain_end" and name == "planner":
                output = data.get("output")
                if output and "sub_queries" in output:
                    yield f"data: {json.dumps({'type': 'planner', 'content': output['sub_queries']})}\n\n"

            # --- 2. Researcher ---
            if kind == "on_chain_start" and name == "researcher":
                current_phase = "researcher"
                yield f"data: {json.dumps({'type': 'progress', 'current_loop': current_loop + 1, 'max_loops': request.max_loops, 'phase': 'researcher', 'message': 'Searching and analyzing information...'})}\n\n"

            if kind == "on_chain_end" and name == "researcher":
                output = data.get("output")
                if output and "notes" in output:
                    current_notes = output["notes"]
                    new_notes = current_notes[sent_notes_count:]
                    if new_notes:
                        formatted_notes = [
                            {"title": n.source_title, "url": n.source_url, "content": n.content[:200] + "..."}
                            for n in new_notes
                        ]
                        accumulated_notes.extend(formatted_notes)
                        yield f"data: {json.dumps({'type': 'researcher', 'action': 'notes', 'data': formatted_notes})}\n\n"
                        sent_notes_count = len(current_notes)

            # --- 3. Reviewer ---
            if kind == "on_chain_start" and name == "reviewer":
                current_phase = "reviewer"
                yield f"data: {json.dumps({'type': 'progress', 'current_loop': current_loop + 1, 'max_loops': request.max_loops, 'phase': 'reviewer', 'message': 'Reviewing research quality...'})}\n\n"

            # Capture streaming reviewer chunks
            if kind == "on_chat_model_stream" and "reviewer" in event.get("tags", []):
                chunk = data.get("chunk")
                if chunk:
                    content = chunk.content
                    if content:
                        yield f"data: {json.dumps({'type': 'reviewer_chunk', 'content': content})}\n\n"

            if kind == "on_chain_end" and name == "reviewer":
                output = data.get("output")
                if output:
                    feedback = output.get("feedback")
                    new_queries = output.get("sub_queries", [])
                    yield f"data: {json.dumps({'type': 'reviewer', 'feedback': feedback, 'has_more_queries': len(new_queries) > 0})}\n\n"
                    if new_queries:
                        current_loop += 1

            # --- 4. Reporter ---
            if kind == "on_chain_start" and name == "reporter":
                current_phase = "reporter"
                yield f"data: {json.dumps({'type': 'progress', 'current_loop': current_loop + 1, 'max_loops': request.max_loops, 'phase': 'reporter', 'message': 'Writing final report...'})}\n\n"

            # Capture streaming report chunks
            if kind == "on_chat_model_stream" and "reporter" in event.get("tags", []):
                chunk = data.get("chunk")
                if chunk:
                    content = chunk.content
                    if content:
                        full_report_content += content
                        yield f"data: {json.dumps({'type': 'report_chunk', 'content': content})}\n\n"

        # --- Save to DB ---
        if full_report_content:
            try:
                with Session(engine) as session:
                    db_session = ResearchSession(
                        task=request.task,
                        report_content=full_report_content,
                        notes_json=json.dumps(accumulated_notes)
                    )
                    session.add(db_session)
                    session.commit()
                    session.refresh(db_session)
                    # Yield the saved ID so frontend can update URL or state
                    yield f"data: {json.dumps({'type': 'saved', 'id': db_session.id})}\n\n"
            except Exception as e:
                print(f"Error saving to DB: {e}")
                # Don't fail the stream just because save failed, but log it

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        print(f"Stream Error: {e}")
        friendly_error = get_friendly_error(e)
        yield f"data: {json.dumps({'type': 'error', 'content': friendly_error})}\n\n"
