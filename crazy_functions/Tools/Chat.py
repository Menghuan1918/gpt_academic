from .Chat_Prompt import RAG, QUESTIONS, RAG2
import re
from .Chat_LLM import predict, get_text
import logging
import json
from .Search import Search_in_PDF
from .Rerank import Rerank_local_model, Rerank_list

def Gen_questions(query, history, Config):
    """
    用于向量搜索的问题生成优化
    """
    his = ""
    if len(history) == 0:
        pass
    else:
        for temp in history[:-1]:
            his += f"Q: {temp[0]}\n"
            his += f"A: {temp[1]}\n"

    Q = QUESTIONS.format(his=his, query=query)
    text = get_text(
        inputs=Q,
        Config=Config,
        model_name=Config["llm_model_cheap"],
        max_tokens=Config["llm_model_cheap_max_tokens"],
        temperature=Config["llm_model_cheap_temperature_normal"],
    )
    text = re.sub(r"```json|```", "", text)
    return text

def RAG_QA(query, history, Config, Prompt_mode=0):
    """
    RAG QA部分
    """
    # 第0步，敏感词检测
    # if not Sensitive(query):
    #     raise RuntimeError("⚠️Sensitive content detected⚠️")

    # 第一步，优化问题
    try:
        text = json.loads(Gen_questions(query, history, Config))
        assert text != ""
    except Exception:
        logging.info(f"Failed to generate questions for {query}")
        text = [query]

    # 第二步，搜索相似文本
    try:
        Emb_lists = Search_in_PDF(text, Config)
    except Exception as e:
        logging.error(f"Failed to search in PDF for {text}")
        logging.error(e)
        raise RuntimeError(f"Failed to search in PDF for {query}")

    # 第三步，重排序
    try:
        reranker = Rerank_local_model(Config)
        Reranked_list = Rerank_list(reranker, query, Emb_lists, Config)
        Rerank = json.loads(Reranked_list)
    except Exception as e:
        logging.error(f"Failed to rerank for {query}")
        logging.error(e)
        raise RuntimeError(f"Failed to rerank for {query}")

    # 第四步，重整提示词
    try:
        Related = ""
        for temp in Rerank:
            Related += f'{temp["page_content"]}\n'
    except Exception as e:
        logging.error(f"Failed to reorganize related content for {query}")
        logging.error(e)
        raise RuntimeError(f"Failed to reorganize related content for {query}")

    if Prompt_mode == 0:
        Prompt = RAG.format(lists=Related)
    elif Prompt_mode == 1:
        Prompt = RAG2.format(lists=Related)
    
    return Prompt