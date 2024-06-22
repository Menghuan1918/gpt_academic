import os
import logging

# 读取配置文件，返回配置字典，优先读取config_private.py，如果不存在则读取config.py
def read_config():
    config_file_path = (
        os.path.join(os.getcwd(), "config_private.py")
        if os.path.exists(os.path.join(os.getcwd(), "config_private.py"))
        else os.path.join(os.getcwd(), "config.py")
    )
    config = {}
    try:
        with open(config_file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=")
                    config[key.strip()] = value.strip().strip('"')
                    logging.info(f"Read config: {key}={value}")
    except:
        logging.critical(f"Config file not found: {config_file_path}")
    return config
