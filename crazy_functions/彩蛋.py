from toolbox import CatchException, update_ui, report_exception
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
from crazy_functions.plugin_template.plugin_class_template import (
    GptAcademicPluginTemplate,
)
from crazy_functions.plugin_template.plugin_class_template import ArgProperty
from .Tools.Chat import RAG_QA
from .Tools.Config import read_config

bochi = """
"""

@CatchException
def eggs(
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
            "恭喜你发现了彩蛋🎉!",
            "实在想不到放什么啦，放只小波奇吧：\
            ![bocchi](https://private-user-images.githubusercontent.com/122662527/337961797-f7cc8fef-8035-456e-a067-3081f30c872e.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MTkxMjM1MjQsIm5iZiI6MTcxOTEyMzIyNCwicGF0aCI6Ii8xMjI2NjI1MjcvMzM3OTYxNzk3LWY3Y2M4ZmVmLTgwMzUtNDU2ZS1hMDY3LTMwODFmMzBjODcyZS5naWY_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjQwNjIzJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI0MDYyM1QwNjEzNDRaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT05NzUwZWY0NzhlZGE1MTIzMzgyMmFmMWEzMzkwNjRlZDAxYmNmZTI1ZTIzMGEzN2I1YTE4OWYwZTQ2N2Y4YTc3JlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZhY3Rvcl9pZD0wJmtleV9pZD0wJnJlcG9faWQ9MCJ9.LhFV98LTMZ9jAh3pqFewN1ka5vMQWX6aHG6hgT3VrR8)",
        ]
    )
    yield from update_ui(chatbot=chatbot, history=history)  # 刷新界面