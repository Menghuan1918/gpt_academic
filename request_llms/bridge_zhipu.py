import time
import os
from toolbox import update_ui, get_conf, update_ui_lastest_msg
from toolbox import check_packages, report_exception, have_any_recent_upload_image_files

model_name = '智谱AI大模型'
zhipuai_default_model = 'glm-4'

def validate_key():
    ZHIPUAI_API_KEY = get_conf("ZHIPUAI_API_KEY")
    if ZHIPUAI_API_KEY == '': return False
    return True

def make_media_input(inputs, image_paths):
    for image_path in image_paths:
        inputs = inputs + f'<br/><br/><div align="center"><img src="file={os.path.abspath(image_path)}"></div>'
    return inputs

def predict_no_ui_long_connection(inputs, llm_kwargs, history=[], sys_prompt="", observe_window=[], console_slience=False):
    """
        ⭐多线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    watch_dog_patience = 5
    response = ""

    if llm_kwargs["llm_model"] == "zhipuai":
        llm_kwargs["llm_model"] = zhipuai_default_model

    if validate_key() is False:
        raise RuntimeError('请配置ZHIPUAI_API_KEY')

    # 开始接收回复
    from .com_zhipuglm import ZhipuChatInit
    zhipu_bro_init = ZhipuChatInit()
    for chunk, response in zhipu_bro_init.generate_chat(inputs, llm_kwargs, history, sys_prompt):
        if len(observe_window) >= 1:
            observe_window[0] = response
        if len(observe_window) >= 2:
            if (time.time() - observe_window[1]) > watch_dog_patience:
                raise RuntimeError("程序终止。")
    return response


def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream=True, additional_fn=None):
    """
        ⭐单线程方法
        函数的说明请见 request_llms/bridge_all.py
    """
    chatbot.append([inputs, ""])
    yield from update_ui(chatbot=chatbot, history=history)

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        check_packages(["zhipuai"])
    except:
        yield from update_ui_lastest_msg(f"导入软件依赖失败。使用该模型需要额外依赖，安装方法```pip install --upgrade zhipuai```。",
            chatbot=chatbot, history=history, delay=0)
        return

    if validate_key() is False:
        yield from update_ui_lastest_msg(lastmsg="[Local Message] 请配置ZHIPUAI_API_KEY", chatbot=chatbot, history=history, delay=0)
        return

    if additional_fn is not None:
        from core_functional import handle_core_functionality
        inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)

    if llm_kwargs["llm_model"] == "zhipuai":
        llm_kwargs["llm_model"] = zhipuai_default_model

    if llm_kwargs["llm_model"] in ["glm-4v"]:
        have_recent_file, image_paths = have_any_recent_upload_image_files(chatbot)
        if not have_recent_file:
            chatbot.append((inputs, "没有检测到任何近期上传的图像文件，请上传jpg格式的图片，此外，请注意拓展名需要小写"))
            yield from update_ui(chatbot=chatbot, history=history, msg="等待图片") # 刷新界面
            return
        if have_recent_file:
            inputs = make_media_input(inputs, image_paths)
    yield from update_ui_lastest_msg(inputs, chatbot, history)

    # 开始接收回复    
    from .com_zhipuglm import ZhipuChatInit
    zhipu_bro_init = ZhipuChatInit()
    for chunk, response in zhipu_bro_init.generate_chat(inputs, llm_kwargs, history, system_prompt):
        chatbot[-1] = [inputs, response]
        yield from update_ui(chatbot=chatbot, history=history)
    history.extend([inputs, response])
    yield from update_ui(chatbot=chatbot, history=history)