import json
from typing import List, Dict
from langchain_core.messages import SystemMessage, HumanMessage
from src.core.llm import get_llm
from src.prompts import PLANNER_PROMPT
from src.models import ResearchState

async def planner_node(state: ResearchState) -> Dict:
    """
    Planner Agent: 分析任务并生成初始搜索查询 (异步)
    """
    print(f"--- [Planner] Start planning for: {state['task']} ---")
    
    llm = get_llm(json_mode=True)
    
    messages = [
        SystemMessage(content=PLANNER_PROMPT.format(task=state['task'])),
        HumanMessage(content="请开始规划。")
    ]
    
    response = await llm.ainvoke(messages)
    try:
        result = json.loads(response.content)
        queries = result.get("queries", [])
        print(f"--- [Planner] Generated queries: {queries} ---")
        return {"sub_queries": queries, "notes": [], "review_count": 0}
    except Exception as e:
        print(f"Error parsing planner output: {e}")
        return {"sub_queries": [state['task']], "notes": [], "review_count": 0}
