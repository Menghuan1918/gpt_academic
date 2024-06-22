from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import os
import logging
import shutil
from langchain_community.document_loaders import PyPDFLoader
import glob
import chromadb
from chromadb.config import Settings

def docker_read_vector(Config):
    """
    读取docker中的Chroma对象
    """
    embeddings = OpenAIEmbeddings(
        base_url=Config["openai_base_url"],
        api_key=Config["openai_api_key"],
        model=Config["embeddings_name"],
    )
    import chromadb.utils.embedding_functions as embedding_functions
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=Config["openai_api_key"],
                api_base=Config["openai_base_url"],
                model_name=Config["embeddings_name"],
            )

    client = chromadb.HttpClient(settings=Settings())
    client.get_collection("my_collection",embedding_function=openai_ef)
    return Chroma(client=client, collection_name="my_collection", embedding_function=embeddings)

def document_key(doc):
    return (doc.page_content, frozenset(doc.metadata.items()))


def Search_in_PDF(query_list, Config):
    """
    query_list: list，包含多个查询字符串
    Config: dict，是配置信息

    返回值：list，包含多个查询结果, 格式为[Document(page_content=,metadata={'page': , 'source'})]
    """
    db = docker_read_vector(Config)
    # 依次对每个查询字符串进行混合查询
    return_list = []
    top_k = int(Config["search_top_k"])
    for query in query_list:
        try:
            Similarity_Result = db.similarity_search(query=query, k=top_k)
            MMR_Result = db.as_retriever(
                search_type="mmr", search_kwargs={"k": top_k}
            ).invoke(query)
            combined_dict = {
                document_key(doc): doc for doc in Similarity_Result + MMR_Result
            }
            return_list.extend(list(combined_dict.values()))
        except Exception as e:
            logging.error(f"Error in Search_in_PDF: {e}")
            pass
    return return_list

def docker_create(file_list, Config):
    import chromadb.utils.embedding_functions as embedding_functions
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=Config["openai_api_key"],
                api_base=Config["openai_base_url"],
                model_name=Config["embeddings_name"],
            )

    embeddings = OpenAIEmbeddings(
        base_url=Config["openai_base_url"],
        api_key=Config["openai_api_key"],
        model=Config["embeddings_name"],
    )
    # 每次都会清空原有的数据
    import uuid
    import chromadb
    from chromadb.config import Settings
    client = chromadb.HttpClient(settings=Settings(allow_reset=True))
    client.reset()
    collection = client.create_collection("my_collection",embedding_function = openai_ef)
    docss = []
    for file in file_list:
        loader = PyPDFLoader(file)
        pages = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=128)
        docs = text_splitter.split_documents(pages)
        docss.append(docs)
    for docs in docss:
        for doc in docs:
            collection.add(
                ids=[str(uuid.uuid1())], metadatas=doc.metadata, documents=doc.page_content[:2000]
            )
    
    return Chroma(client=client, collection_name="my_collection", embedding_function=embeddings)

if __name__ == "__main__":
    from .Config import read_config
    Config = read_config()
    # 构建一个Chroma对象
    directory = '/home/menghuan/Code/pdf/All'
    file_list = [os.path.join(directory, file) for file in os.listdir(directory)]
    Config = read_config()
    db4 = docker_create(file_list, Config)
    query = "What should I do if I lost my student ID card?"
    docs = db4.similarity_search(query)
    print(docs[0].page_content)