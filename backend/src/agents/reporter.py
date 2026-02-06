from typing import Dict
from langchain_core.messages import SystemMessage, HumanMessage
from src.core.llm import get_llm
from src.prompts import REPORTER_PROMPT
from src.models import ResearchState

async def reporter_node(state: ResearchState) -> Dict:
    """
    Reporter Agent: 撰写最终报告 (异步)
    """
    print(f"--- [Reporter] Generating final report based on {len(state['notes'])} notes ---")
    
    notes_text = ""
    for idx, note in enumerate(state['notes']):
        notes_text += f"Source [{idx+1}]: {note.source_title} ({note.source_url})\nContent: {note.content}\n\n"
        
    llm = get_llm()
    
    messages = [
        SystemMessage(content=REPORTER_PROMPT.format(task=state['task'], notes=notes_text)),
        HumanMessage(content="请撰写报告。")
    ]
    
    # 关键修改：添加 tags=["reporter"] 以便在 main.py 中通过 astream_events 捕获
    response = await llm.ainvoke(messages, config={"tags": ["reporter"]})
    report = response.content
    
    print("--- [Reporter] Report generated successfully ---")
    return {"report_content": report}
