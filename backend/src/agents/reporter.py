from typing import Dict, AsyncIterator
from langchain_core.messages import SystemMessage, HumanMessage
from src.core.llm import get_llm
from src.prompts import REPORTER_PROMPT
from src.models import ResearchState


async def reporter_node(state: ResearchState) -> Dict:
    """
    Reporter Agent: 撰写最终报告 (使用流式输出)
    使用 astream 替代 ainvoke 实现真正的流式输出
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

    # 使用 astream 进行流式输出，添加 tags 以便在 main.py 中捕获
    report_content = ""
    async for chunk in llm.astream(messages, config={"tags": ["reporter"]}):
        if chunk.content:
            report_content += chunk.content

    print("--- [Reporter] Report generated successfully ---")
    return {"report_content": report_content}
