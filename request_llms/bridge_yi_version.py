from toolbox import encode_image, every_image_file_in_path ,read_one_api_model_name
from .oai_version_std import multiple_picture_types

timeout_bot_msg = (
    "[Local Message] Request timeout. Network error. Please check proxy settings in config.py."
    + "网络错误，检查代理服务器是否可用，以及代理设置的格式是否正确，格式须是[协议]://[地址]:[端口]，缺一不可。"
)

def yi_version_generate_message_version(
    chatbot, input, model, key, history, max_output_token, system_prompt, temperature
):
    """
    整合所有信息，选择LLM模型，生成http请求，为发送请求做准备
    """
    if chatbot != None:
        have_recent_file, image_paths = every_image_file_in_path(chatbot)
    else:
        have_recent_file = False
        image_paths = []
    conversation_cnt = len(history) // 2
    messages = []
    input = system_prompt + "\n" + input

    # def make_media_input(inputs, image_paths):
    #     for image_path in image_paths:
    #         inputs = (
    #             inputs
    #             + f'<br/><br/><div align="center"><img src="file={os.path.abspath(image_path)}"></div>'
    #         )
    #     return inputs

    # if have_recent_file and chatbot != None:
    #     chatbot.append((make_media_input(input, image_paths), ""))

    if conversation_cnt:
        for index in range(0, 2 * conversation_cnt, 2):
            what_i_have_asked = {}
            what_i_have_asked["role"] = "user"
            what_i_have_asked["content"] = [{"type": "text", "text": history[index]}]
            what_gpt_answer = {}
            what_gpt_answer["role"] = "assistant"
            what_gpt_answer["content"] = [{"type": "text", "text": history[index + 1]}]
            if what_i_have_asked["content"][0]["text"] != "":
                if what_i_have_asked["content"][0]["text"] == "":
                    continue
                if what_i_have_asked["content"][0]["text"] == timeout_bot_msg:
                    continue
                messages.append(what_i_have_asked)
                messages.append(what_gpt_answer)
            else:
                messages[-1]["content"][0]["text"] = what_gpt_answer["content"][0][
                    "text"
                ]

    what_i_ask_now = {}
    what_i_ask_now["role"] = "user"
    what_i_ask_now["content"] = []
    if have_recent_file:
        for image_path in image_paths:
            what_i_ask_now["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{multiple_picture_types(image_path)};base64,{encode_image(image_path)}"
                    },
                }
            )
    what_i_ask_now["content"].append({"type": "text", "text": input})

    messages.append(what_i_ask_now)
    # 开始整理headers与message
    api_key = f"Bearer {key}"
    headers = {"Content-Type": "application/json", "Authorization": api_key}
    if model.startswith("one-api-version-"):
        model,_ = read_one_api_model_name(model)
        model = model.replace("one-api-version-", "")
    playload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
        "max_tokens": max_output_token,
    }
    try:
        print(f" {model} : {conversation_cnt} : {input[:100]} ..........")
    except:
        print("输入中可能存在乱码。")
    return headers, playload
