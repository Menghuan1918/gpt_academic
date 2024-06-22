# 借鉴了 https://github.com/binary-husky/gpt_academic 项目
import json
import logging
import requests

timeout_bot_msg = "Time out! Please try again later."


def get_full_error(chunk, stream_response):
    """
    Get the full error message from the stream response.
    """
    while True:
        try:
            chunk += next(stream_response)
        except:
            break
    return chunk


def decode_chunk(chunk):
    """
    Try to decode the chunk.
    """
    chunk = chunk.decode()
    respose = ""
    finish_reason = "False"
    try:
        chunk = json.loads(chunk[6:])
    except:
        finish_reason = "JSON_ERROR"
    # error message
    if "error" in chunk:
        respose = "API_ERROR"
        try:
            chunk = json.loads(chunk)
            finish_reason = chunk["error"]["code"]
        except:
            finish_reason = "API_ERROR"
        return respose, finish_reason
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
    Get the message for the model.
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
    return headers, playload


def predict(
    inputs,
    Config,
    temperature,
    model_name,
    max_tokens,
    history=[],
    system_prompt="You are a helpful AI assistant",
):
    """
    Get the response from the model.
    inputs: str, the input text.
    Config: dict, the kwargs for the model.
    temperature: float, the temperature for the model.
    model_name: str, the model name.
    max_tokens: int, the max tokens for the model.
    history: list, the history of the conversation.
    system_prompt: str, the system prompt.
    """
    APIKEY = Config["openai_api_key"]
    if inputs == "":
        inputs = "Hi!👋"

    headers, playload = generate_message(
        input=inputs,
        model=model_name,
        key=APIKEY,
        history=history,
        token=int(max_tokens),
        system_prompt=system_prompt,
        temperature=float(temperature),
    )

    history.append(inputs)
    history.append("")
    retry = 0
    while True:
        try:
            endpoint = Config["openai_base_url"] + "/chat/completions"
            response = requests.post(
                endpoint,
                headers=headers,
                json=playload,
                stream=True,
                timeout=int(Config["time_out"]),
            )
            break
        except:
            retry += 1
            logging.error(f"Request failed, retrying {retry}/{Config['max_retry']}")
            if retry > int(Config["max_retry"]):
                raise TimeoutError

    gpt_replying_buffer = ""

    stream_response = response.iter_lines()
    while True:
        try:
            chunk = next(stream_response)
        except StopIteration:
            break
        except requests.exceptions.ConnectionError:
            chunk = next(stream_response)
        response_text, finish_reason = decode_chunk(chunk)
        # 返回的数据流第一次为空，继续等待
        if response_text == "" and finish_reason != "False":
            continue
        if chunk:
            try:
                if response_text == "API_ERROR" and (
                    finish_reason != "False" or finish_reason != "stop"
                ):
                    chunk = get_full_error(chunk, stream_response)
                    chunk_decoded = chunk.decode()
                    logging.error(f"[response] {chunk_decoded}")
                    raise RuntimeError(
                        f"⚠️ API Error: {finish_reason}! Get: \n {chunk_decoded}"
                    )

                # if finish_reason == "stop":
                #     break
                gpt_replying_buffer += response_text
                yield response_text
            except Exception as e:
                chunk = get_full_error(chunk, stream_response)
                chunk_decoded = chunk.decode()
                logging.error(f"[response] {chunk_decoded}")
                raise RuntimeError(f"⚠️ Error: {e}! Get: \n {chunk_decoded}")


def get_text(
    inputs,
    Config,
    temperature,
    model_name,
    max_tokens,
    history=[],
    system_prompt="You are a helpful AI assistant",
):
    """
    Get the response from the model.
    inputs: str, the input text.
    Config: dict, the kwargs for the model.
    temperature: float, the temperature for the model.
    model_name: str, the model name.
    max_tokens: int, the max tokens for the model.
    history: list, the history of the conversation.
    system_prompt: str, the system prompt.
    """
    text = ""
    try:
        for temp in predict(
            inputs,
            Config,
            temperature,
            model_name,
            max_tokens,
            history,
            system_prompt,
        ):
            text += temp
    except Exception as e:
        raise e
    return text
