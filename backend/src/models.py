from typing import List, TypedDict, Optional
from pydantic import BaseModel, Field

class Note(BaseModel):
    """
    存储单次搜索/阅读的核心发现
    """
    content: str = Field(description="从网页中提取的关键信息摘要")
    source_url: str = Field(description="来源网页的URL")
    source_title: str = Field(description="来源网页的标题")
    relevance: float = Field(description="内容与查询的相关度打分 (0-1)", ge=0.0, le=1.0)

class ResearchState(TypedDict):
    """
    在 Agent 之间传递的图状态 (Graph State)
    """
    task: str                   # 用户原始任务
    sub_queries: List[str]      # 当前待执行的搜索查询
    notes: List[Note]           # 积累的所有笔记
    report_content: str         # 最终报告
    review_count: int           # 反思循环计数器 (防死循环)
    max_loops: int              # 最大反思循环次数 (默认3)
    feedback: Optional[str]     # Reviewer 的反馈意见
