from langgraph.graph import StateGraph, END
from src.models import ResearchState
from src.agents.planner import planner_node
from src.agents.researcher import researcher_node
from src.agents.reviewer import reviewer_node
from src.agents.reporter import reporter_node

def should_continue(state: ResearchState):
    """
    Reviewer 之后的条件判断逻辑
    """
    # 如果 Reviewer 生成了新的 queries，则继续 Research
    if state.get("sub_queries") and len(state["sub_queries"]) > 0:
        print("--- [Graph] Decision: Continue Research ---")
        return "researcher"
    
    # 否则（满意 或 次数耗尽），生成报告
    print("--- [Graph] Decision: Generate Report ---")
    return "reporter"

def create_graph():
    """
    构建 LangGraph 工作流
    """
    workflow = StateGraph(ResearchState)
    
    # 1. 添加节点
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("reporter", reporter_node)
    
    # 2. 定义边
    # Start -> Planner
    workflow.set_entry_point("planner")
    
    # Planner -> Researcher
    workflow.add_edge("planner", "researcher")
    
    # Researcher -> Reviewer
    workflow.add_edge("researcher", "reviewer")
    
    # Reviewer -> (Researcher OR Reporter)
    workflow.add_conditional_edges(
        "reviewer",
        should_continue,
        {
            "researcher": "researcher",
            "reporter": "reporter"
        }
    )
    
    # Reporter -> End
    workflow.add_edge("reporter", END)
    
    # 3. 编译图
    app = workflow.compile()
    return app
