from toolbox import CatchException, update_ui, report_exception
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.plugin_template.plugin_class_template import (
    GptAcademicPluginTemplate,
)
from crazy_functions.plugin_template.plugin_class_template import ArgProperty
from .Tools.Chat import RAG_QA
from .Tools.Config import read_config


@CatchException
def 知识库回答(
    txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, web_port
):
    """
    txt             输入栏用户输入的文本，例如需要翻译的一段话，再例如一个包含了待处理文件的路径
    llm_kwargs      gpt模型参数，如温度和top_p等，一般原样传递下去就行
    plugin_kwargs   插件模型的参数，用于灵活调整复杂功能的各种参数
    chatbot         聊天显示框的句柄，用于显示给用户
    history         聊天历史，前情提要
    system_prompt   给gpt的静默提醒
    web_port        当前软件运行的端口号
    """
    Config = read_config()
    chatbot.append(
        [
            "What this can do?\n函数插件功能？",
            "It will answer you questions base the established knowledge base, which leads to precise and correct answers. Function Plugin Contributors : Menghuan1918. \
            \n插件将会根据知识库中的文件进行精准正确的回答。函数插件贡献者: Menghuan1918",
        ]
    )
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面
    # 根据问题生成引用
    i_say_show_user = (
        f"Get the question: {txt} \n Start to search the answer in the knowledge base."
    )
    gpt_say = "[Local Message] Get it, searching now. Please wait a moment."
    chatbot.append([i_say_show_user, gpt_say])
    yield from update_ui(chatbot=chatbot, history=history)
    history_6 = history[-6:]
    knowledge = RAG_QA(query=txt, history=history_6, Config=Config)
    i_say_show_user = txt
    # 不准用户乱动温度！
    llm_kwargs["temperature"] = 0.8
    gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
        inputs=txt,
        inputs_show_user=i_say_show_user,
        llm_kwargs=llm_kwargs,
        chatbot=chatbot,
        history=history,
        sys_prompt=knowledge
    )
    history.append(gpt_say)
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面 # 界面更新