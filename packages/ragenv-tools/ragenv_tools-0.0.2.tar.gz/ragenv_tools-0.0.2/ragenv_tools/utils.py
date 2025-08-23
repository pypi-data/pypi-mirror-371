import json
import sys
import os
from pathlib import Path
from openai import OpenAI
import ast 

class SuppressPrint:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def load_config(config: str | dict = "config.json"):
    """加载配置文件"""
    try:
        if isinstance(config, str) and str(config).endswith('.json'):
            with open(config, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
        elif isinstance(config, dict):
            config_dict = config
        else:
            raise Exception('No Valid config. Please Reset.')
        return config_dict
    
    except Exception as e:
        raise Exception(f"加载配置文件失败: {str(e)}")


def kimi_ocr(file_path, config="../config.json"):
    config = load_config(config=config)
    # 输入文件地址
    client = OpenAI(
        api_key = config["llm_config"]["moonshot"]["api_key"],
        base_url= config["llm_config"]["moonshot"]["base_url"],
    )
    #删掉之前已上传的文件
    file_list = client.files.list()
    for file in file_list.data:
        client.files.delete(file_id=file.id)

    #提取文件
    file_object = client.files.create(file=Path(file_path), purpose="file-extract")
    file_content = ast.literal_eval(client.files.content(file_id=file_object.id).text)['content']
    return file_content