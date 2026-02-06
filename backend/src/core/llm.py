from langchain_openai import ChatOpenAI
from src.core.config import settings

def get_llm(json_mode: bool = False):
    """
    获取配置好的 LLM 实例
    """
    kwargs = {
        "model": settings.OPENAI_MODEL_NAME,
        "api_key": settings.OPENAI_API_KEY,
        "temperature": 0,  # 保持确定性
    }
    
    if settings.OPENAI_API_BASE:
        kwargs["base_url"] = settings.OPENAI_API_BASE
        
    if json_mode:
        kwargs["model_kwargs"] = {"response_format": {"type": "json_object"}}
        
    return ChatOpenAI(**kwargs)
