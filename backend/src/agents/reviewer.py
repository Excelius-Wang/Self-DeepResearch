import json
from typing import Dict
from langchain_core.messages import SystemMessage, HumanMessage
from src.core.llm import get_llm
from src.prompts import REVIEWER_PROMPT
from src.models import ResearchState

async def reviewer_node(state: ResearchState) -> Dict:
    """
    Reviewer Agent: 审查笔记质量并决定下一步 (异步)
    """
    current_loop = state.get("review_count", 0)
    max_loops = state.get("max_loops", 3)
    print(f"--- [Reviewer] Loop {current_loop + 1} / {max_loops} ---")
    
    if current_loop >= max_loops:
        print("--- [Reviewer] Max loops reached. Proceeding to report. ---")
        return {"review_count": current_loop + 1, "feedback": "Max loops reached", "sub_queries": []}

    notes_text = ""
    for idx, note in enumerate(state['notes']):
        notes_text += f"[{idx+1}] {note.source_title}: {note.content[:200]}...\n"

    llm = get_llm(json_mode=True)
    
    messages = [
        SystemMessage(content=REVIEWER_PROMPT.format(task=state['task'], notes=notes_text)),
        HumanMessage(content="请审查并给出决策。")
    ]
    
    response = await llm.ainvoke(messages)
    
    try:
        result = json.loads(response.content)
        satisfactory = result.get("satisfactory", False)
        feedback = result.get("feedback", "")
        new_queries = result.get("new_queries", [])
        
        print(f"--- [Reviewer] Satisfactory: {satisfactory}, Feedback: {feedback} ---")
        
        if satisfactory:
            return {"review_count": current_loop + 1, "feedback": feedback, "sub_queries": []}
        else:
            print(f"--- [Reviewer] New queries: {new_queries} ---")
            return {"review_count": current_loop + 1, "feedback": feedback, "sub_queries": new_queries}
            
    except Exception as e:
        print(f"Error parsing reviewer output: {e}")
        return {"review_count": current_loop + 1, "feedback": "Error parsing output", "sub_queries": []}
