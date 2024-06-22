def Rerank_list(reranker, query, result_list, Config):
    """
    reranker: model，reranker模型
    query: str，查询字符串
    result_list: list，包含多个查询结果, 格式为[Document(page_content=,metadata={'page': , 'source'})]
    Config: dict，是配置信息

    返回值：list，包含多个查询结果, 格式为[page_content=,metadata={'page': , 'source', 'rerank_score':}]
    """
    if Config["rerank_model_type"] == "local":
        return Rerank_local(reranker, query, result_list, Config)
    else:
        return Rerank_HF(reranker, query, result_list, Config)


def Rerank_local_model(Config):
    if Config["rerank_model_type"] == "local":
        from FlagEmbedding import FlagReranker

        return FlagReranker(Config["rerank_name"], use_fp16=True)
    else:
        return None


def Rerank_local(reranker, query, result_list, Config):
    import json

    QA_list = []
    for list in result_list:
        QA_list.append([query, list.page_content])

    rerank_scores = reranker.compute_score(QA_list, normalize=True)

    try:
        for i, score in enumerate(rerank_scores):
            result_list[i].metadata["rerank_score"] = score
    except:
        result_list[0].metadata["rerank_score"] = rerank_scores

    # 按照rerank_score排序
    result_list = sorted(
        result_list, key=lambda x: x.metadata["rerank_score"], reverse=True
    )
    top_k = int(Config["search_top_k"])
    temp = result_list[:top_k]
    json_result = []
    for list in temp:
        json_result.append(
            {
                "page_content": list.page_content,
                "metadata": list.metadata,
            }
        )
    return json.dumps(json_result, ensure_ascii=False, indent=2)


def Rerank_HF(reranker, query, result_list, Config):
    from gradio_client import Client
    import os
    import json

    os.environ["HUGGING_FACE_HUB_TOKEN"] = Config["huggingface_token"]
    client = Client("Menghuan1918/Rerank_test")
    temp = [
        {"page_content": list.page_content, "metadata": list.metadata}
        for list in result_list
    ]
    result = client.predict(
        query=query,
        result_list_json=json.dumps(temp),
        top_k=Config["search_top_k"],
        api_name="/predict",
    )
    return result
