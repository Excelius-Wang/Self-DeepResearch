import asyncio
from typing import Dict, List
from langchain_core.messages import SystemMessage, HumanMessage
from src.core.llm import get_llm
from src.tools.search import search_tool
from src.prompts import RESEARCHER_PROMPT
from src.models import ResearchState, Note

async def process_query(query: str, task: str) -> List[Note]:
    """
    处理单个查询：搜索 -> 摘要
    """
    print(f"--- [Researcher] Searching: {query} ---")
    results = await search_tool.search(query, max_results=3)
    
    if not results:
        return []
        
    context = ""
    for idx, res in enumerate(results):
        context += f"Result {idx+1}:\nTitle: {res.get('title')}\nURL: {res.get('url')}\nContent: {res.get('content')}\n\n"
        
    llm = get_llm()
    messages = [
        SystemMessage(content=RESEARCHER_PROMPT.format(task=task, query=query, content=context)),
        HumanMessage(content="请提取笔记。")
    ]
    
    try:
        # 异步调用 LLM
        response = await llm.ainvoke(messages)
        content = response.content
        
        primary_source = results[0]
        note = Note(
            content=content,
            source_url=primary_source.get('url', ''),
            source_title=primary_source.get('title', 'Unknown Source'),
            relevance=0.9
        )
        return [note]
    except Exception as e:
        print(f"Error processing query {query}: {e}")
        return []

async def researcher_node(state: ResearchState) -> Dict:
    """
    Researcher Agent: 异步并发执行搜索并生成笔记
    """
    print(f"--- [Researcher] Processing {len(state['sub_queries'])} queries concurrently ---")
    
    tasks = [process_query(q, state['task']) for q in state['sub_queries']]
    results = await asyncio.gather(*tasks)
    
    new_notes = []
    for res in results:
        new_notes.extend(res)
            
    all_notes = state.get("notes", []) + new_notes
    print(f"--- [Researcher] Added {len(new_notes)} notes. Total: {len(all_notes)} ---")
    
    return {"notes": all_notes}
