import json
import asyncio
from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel import Session, select

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

# Global semaphore for concurrency control
MAX_CONCURRENT_RESEARCH = 2
research_semaphore = asyncio.Semaphore(MAX_CONCURRENT_RESEARCH)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/history", response_model=List[ResearchSession])
async def get_history(session: Session = Depends(get_session)):
    statement = select(ResearchSession).order_by(ResearchSession.created_at.desc())
    results = session.exec(statement)
    # Return summary (without full report content to save bandwidth if list is long)
    # But for now returning full object is fine for small scale
    return results.all()

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

@app.post("/research/stream")
async def stream_research(request: ResearchRequest):
    # Try to acquire semaphore
    try:
        await asyncio.wait_for(research_semaphore.acquire(), timeout=0.1)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=429, detail="Too many concurrent research tasks. Please try again later.")

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

    async def event_generator():
        sent_notes_count = 0
        full_report_content = ""
        accumulated_notes = []
        
        try:
            async for event in graph.astream_events(initial_state, version="v1"):
                kind = event["event"]
                name = event["name"]
                data = event["data"]
                
                # --- 1. Planner ---
                if kind == "on_chain_end" and name == "planner":
                    output = data.get("output")
                    if output and "sub_queries" in output:
                        yield f"data: {json.dumps({'type': 'planner', 'content': output['sub_queries']})}\n\n"

                # --- 2. Researcher ---
                if kind == "on_tool_start" and name == "search":
                    query = data.get("input", {}).get("query")
                    if query:
                        yield f"data: {json.dumps({'type': 'researcher', 'action': 'searching', 'query': query})}\n\n"
                        
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
                if kind == "on_chain_end" and name == "reviewer":
                    output = data.get("output")
                    if output:
                        feedback = output.get("feedback")
                        yield f"data: {json.dumps({'type': 'reviewer', 'feedback': feedback})}\n\n"

                # --- 4. Reporter ---
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
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        finally:
            research_semaphore.release()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
