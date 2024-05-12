import json
import time
import gradio as gr
import logging
import traceback
import requests
import importlib
import random

# config_private.py放自己的秘密如API和代理网址
# 读取时首先看是否存在私密的config_private配置文件（不受git管控），如果有，则覆盖原config文件
from toolbox import (
    get_conf,
    update_ui,
    trimmed_format_exc,
    is_the_upload_folder,
    read_one_api_model_name,
)

proxies, TIMEOUT_SECONDS, MAX_RETRY = get_conf(
    "proxies", "TIMEOUT_SECONDS", "MAX_RETRY"
)

timeout_bot_msg = (
    "[Local Message] Request timeout. Network error. Please check proxy settings in config.py."
    + "网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。"
)


def get_full_error(chunk, stream_response):
    """
    尝试获取完整的错误信息
    """
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk


def decode_chunk(chunk):
    """
    用于解读"content"和"finish_reason"的内容
    """
    chunk = chunk.decode()
    respose = ""
    finish_reason = "False"
    try:
        chunk = json.loads(chunk)
    except:
        pass
    try:
        respose = chunk["choices"][0]["delta"]["content"]
    except:
        pass
    try:
        finish_reason = chunk["choices"][0]["finish_reason"]
    except:
        pass
    return respose, finish_reason


def generate_message(input, model, key, history, token, system_prompt, temperature):
    """
    整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
    """
    api_key = f"Bearer {key}"

    headers = {"Content-Type": "application/json", "Authorization": api_key}

    conversation_cnt = len(history) // 2

    messages = [{"role": "system", "content": system_prompt}]
    if conversation_cnt:
        for index in range(0, 2 * conversation_cnt, 2):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["content"] = history[index]
            what_gpt_answer = {}
            what_gpt_answer["role"] = "assistant"
            what_gpt_answer["content"] = history[index + 1]
            if what_i_have_asked["content"] != "":
                if what_gpt_answer["content"] == "":
                    continue
                if what_gpt_answer["content"] == timeout_bot_msg:
                    continue
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]["content"] = what_gpt_answer["content"]
    what_i_ask_now = {}
    what_i_ask_now["role"] = "user"
    what_i_ask_now["content"] = input
    messages.append(what_i_ask_now)
    playload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
        "max_tokens": token,
    }
    try:
        print(f" {model} : {conversation_cnt} : {input[:100]} ..........")
    except:
        print("输入中可能存在乱码。")
    return headers, playload


def predict_no_ui_long_connection(
    inputs,
    llm_kwargs,
    history=[],
    sys_prompt="",
    observe_window=None,
    console_slience=False,
):
    """
    发送至chatGPT，等待回复，一次性完成，不显示中间过程。但内部用stream的方法避免中途网线被掐。
    inputs：
        是本次问询的输入
    sys_prompt:
        系统静默prompt
    llm_kwargs：
        chatGPT的内部调优参数
    history：
        是之前的对话列表
    observe_window = None：
        用于负责跨越线程传递已经输出的部分，大部分时候仅仅为了fancy的视觉效果，留空即可。observe_window[0]：观测窗。observe_window[1]：看门狗
    """
    watch_dog_patience = 5  # 看门狗的耐心，设置5秒不准咬人(咬的也不是人
    if len(get_conf(llm_kwargs["APIKEY"])) == 0:
        raise RuntimeError(f"APIKEY为空,请检查配置文件的{llm_kwargs["APIKEY"]}")
    if inputs == "":
        inputs = "你好👋"
    headers, playload = generate_message(
        input=inputs,
        model=llm_kwargs["model"],
        key=get_conf(llm_kwargs["APIKEY"]),
        history=history,
        token=llm_kwargs["token"],
        system_prompt=sys_prompt,
        temperature=llm_kwargs["temperature"],
    )
    retry = 0
    while True:
        try:
            from .bridge_all import model_info

            endpoint = model_info[llm_kwargs["llm_model"]]["endpoint"]
            if not llm_kwargs["not_use_proxy"]:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    proxies=proxies,
                    json=playload,
                    stream=True,
                    timeout=TIMEOUT_SECONDS,
                )
            else:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=playload,
                    stream=True,
                    timeout=TIMEOUT_SECONDS,
                )
            break
        except:
            retry += 1
            traceback.print_exc()
            if retry > MAX_RETRY:
                raise TimeoutError
            if MAX_RETRY != 0:
                print(f"请求超时，正在重试 ({retry}/{MAX_RETRY}) ……")

    stream_response = response.iter_lines()
    result = ""
    while True:
        try:
            chunk = next(stream_response)
        except StopIteration:
            break
        except requests.exceptions.ConnectionError:
            chunk = next(stream_response)  # 失败了，重试一次？再失败就没办法了。
        response_text, finish_reason = decode_chunk(chunk)
        # 返回的数据流第一次为空，继续等待
        if response_text == "" and finish_reason != "False":
            continue
        if chunk:
            try:
                if finish_reason == "stop":
                    logging.info(f"[response] {result}")
                    break
                result += response_text
                if not console_slience:
                    print(response_text, end="")
                if observe_window is not None:
                    # 观测窗，把已经获取的数据显示出去
                    if len(observe_window) >= 1:
                        observe_window[0] += response_text
                    # 看门狗，如果超过期限没有喂狗，则终止
                    if len(observe_window) >= 2:
                        if (time.time()-observe_window[1]) > watch_dog_patience:
                            raise RuntimeError("用户取消了程序。")
            except Exception as e:
                chunk = get_full_error(chunk, stream_response)
                chunk_decoded = chunk.decode()
                error_msg = chunk_decoded
                print(error_msg)
                raise RuntimeError("Json解析不合常规")
    return result

def predict(inputs, llm_kwargs, plugin_kwargs, chatbot, history=[], system_prompt='', stream = True, additional_fn=None):
    """
    发送至chatGPT，流式获取输出。
    用于基础的对话功能。
    inputs 是本次问询的输入
    top_p, temperature是chatGPT的内部调优参数
    history 是之前的对话列表（注意无论是inputs还是history，内容太长了都会触发token数量溢出的错误）
    chatbot 为WebUI中显示的对话列表，修改它，然后yeild出去，可以直接修改对话界面内容
    additional_fn代表点击的哪个按钮，按钮见functional.py
    """
    if len(get_conf(llm_kwargs["APIKEY"])) == 0:
        raise RuntimeError(f"APIKEY为空,请检查配置文件的{llm_kwargs["APIKEY"]}")
    if inputs == "":
        inputs = "你好👋"
        if additional_fn is not None:
            from core_functional import handle_core_functionality
            inputs, history = handle_core_functionality(additional_fn, inputs, history, chatbot)
    logging.info(f'[raw_input] {inputs}')
    chatbot.append((inputs, ""))
    yield from update_ui(chatbot=chatbot, history=history, msg="等待响应") # 刷新界面

    # check mis-behavior
    if is_the_upload_folder(inputs):
        chatbot[-1] = (inputs, f"[Local Message] 检测到操作错误！当您上传文档之后，需点击“**函数插件区**”按钮进行处理，请勿点击“提交”按钮或者“基础功能区”按钮。")
        yield from update_ui(chatbot=chatbot, history=history, msg="正常") # 刷新界面
        time.sleep(2)

    headers, playload = generate_message(
        input=inputs,
        model=llm_kwargs["model"],
        key=get_conf(llm_kwargs["APIKEY"]),
        history=history,
        token=llm_kwargs["token"],
        system_prompt=system_prompt,
        temperature=llm_kwargs["temperature"],
    )

    history.append(inputs); history.append("")
    retry = 0
    while True:
        try:
            from .bridge_all import model_info

            endpoint = model_info[llm_kwargs["llm_model"]]["endpoint"]
            if not llm_kwargs["not_use_proxy"]:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    proxies=proxies,
                    json=playload,
                    stream=True,
                    timeout=TIMEOUT_SECONDS,
                )
            else:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=playload,
                    stream=True,
                    timeout=TIMEOUT_SECONDS,
                )
            break
        except:
            retry += 1
            chatbot[-1] = ((chatbot[-1][0], timeout_bot_msg))
            retry_msg = f"，正在重试 ({retry}/{MAX_RETRY}) ……" if MAX_RETRY > 0 else ""
            yield from update_ui(chatbot=chatbot, history=history, msg="请求超时"+retry_msg) # 刷新界面
            if retry > MAX_RETRY: raise TimeoutError

    gpt_replying_buffer = ""

    stream_response = response.iter_lines()
    while True:
        try:
            chunk = next(stream_response)
        except StopIteration:
            break
        except requests.exceptions.ConnectionError:
            chunk = next(stream_response)  # 失败了，重试一次？再失败就没办法了。
        response_text, finish_reason = decode_chunk(chunk)
        # 返回的数据流第一次为空，继续等待
        if response_text == "" and finish_reason != "False":
            continue
        if chunk:
            try:
                if finish_reason == "stop":
                    logging.info(f"[response] {gpt_replying_buffer}")
                    break
                status_text = f"finish_reason: {finish_reason}"
                gpt_replying_buffer += response_text
                # 如果这里抛出异常，一般是文本过长，详情见get_full_error的输出
                history[-1] = gpt_replying_buffer
                chatbot[-1] = (history[-2], history[-1])
                yield from update_ui(chatbot=chatbot, history=history, msg=status_text) # 刷新界面
            except Exception as e:
                    yield from update_ui(chatbot=chatbot, history=history, msg="Json解析不合常规") # 刷新界面
                    chunk = get_full_error(chunk, stream_response)
                    chunk_decoded = chunk.decode()
                    chatbot[-1] = (chatbot[-1][0], "[Local Message] API异常,获得以下报错信息：\n" + chunk_decoded)
                    yield from update_ui(chatbot=chatbot, history=history, msg="Json异常" + chunk_decoded) # 刷新界面
                    print(chunk_decoded)
                    return
                    
def get_predict_function():
    return predict_no_ui_long_connection,predict