from toolbox import CatchException, update_ui, report_exception
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.plugin_template.plugin_class_template import (
    GptAcademicPluginTemplate,
)
from crazy_functions.plugin_template.plugin_class_template import ArgProperty
from .Tools.Chat import RAG_QA
from .Tools.Config import read_config

@CatchException
def doc2x(
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
    chatbot.append(
        [
            "抱歉！我们还在完善这个功能！\nSorry! We are still working on this function!",
            "不过你可以尝试使用[https://doc2x.com](https://doc2x.com/login?invite_code=4AREZ6)进行文档翻译。未来我们会使用其文档解析服务将做到与之类似(甚至更好)的效果。\
            \nBut you can try to use [https://doc2x.com](https://doc2x.com/login?invite_code=4AREZ6) for document translation. We will achieve similar effects in the future.",
        ]
    )
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面