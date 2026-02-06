import asyncio
import os
from dotenv import load_dotenv
from src.graph import create_graph

# 确保在测试前加载环境变量
load_dotenv()

async def main():
    print("Initializing Research Graph...")
    app = create_graph()
    
    task = "分析 DeepSeek MoE 架构的核心优势"
    print(f"\nStarting research task: {task}\n")
    
    initial_state = {
        "task": task,
        "sub_queries": [],
        "notes": [],
        "report_content": "",
        "review_count": 0,
        "feedback": None
    }
    
    # 使用 ainvoke 异步调用
    result = await app.ainvoke(initial_state)
    
    print("\n\n=== Final Report ===\n")
    print(result.get("report_content"))
    
    print("\n\n=== Execution Stats ===")
    print(f"Total Notes: {len(result.get('notes', []))}")
    print(f"Review Loops: {result.get('review_count')}")

if __name__ == "__main__":
    asyncio.run(main())
