from typing import Dict, List, Set
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.callbacks import AsyncCallbackHandler
from src.core.llm import get_llm
from src.tools.search import search_tool
from src.prompts import RESEARCHER_PROMPT
from src.models import ResearchState, Note


def dedupe_notes(notes: List[Note]) -> List[Note]:
    """
    去重 notes，基于 source_url
    """
    seen_urls: Set[str] = set()
    unique: List[Note] = []
    for note in notes:
        if note.source_url not in seen_urls:
            seen_urls.add(note.source_url)
            unique.append(note)
    return unique


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
    Researcher Agent: 逐个处理查询并生成笔记
    改为顺序执行以便在 main.py 中通过 astream_events 逐步发送进度
    """
    print(f"--- [Researcher] Processing {len(state['sub_queries'])} queries sequentially ---")

    all_notes = list(state.get("notes", []))

    for idx, query in enumerate(state['sub_queries']):
        print(f"--- [Researcher] Query {idx + 1}/{len(state['sub_queries'])}: {query} ---")
        notes = await process_query(query, state['task'])
        all_notes.extend(notes)

    # 去重 notes
    all_notes = dedupe_notes(all_notes)
    print(f"--- [Researcher] Total unique notes: {len(all_notes)} ---")

    return {"notes": all_notes}
