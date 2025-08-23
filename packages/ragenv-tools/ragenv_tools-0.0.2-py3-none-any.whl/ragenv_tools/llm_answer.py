import warnings
warnings.filterwarnings("ignore")

import re
import json
import tiktoken
import pandas as pd
from openai import OpenAI
from .utils import load_config

class LLMAnswer:
    def __init__(self, platform, model_name, init_params, config):
        self.platform = platform
        self.model_name = model_name
        self.init_params = init_params
        self.config = load_config(config)
        self.messages = []
        
    def init_messages(self, system_prompt):
        self.messages = [{"role": "system", "content": system_prompt}]

    def add_messages(self, role, prompt):
        self.messages.append({"role": role, "content": prompt})

    def check_params_validity(self, params):
        valid_params_list = ['temperature', 'max_tokens', 'stream', 'frequency_penalty']
        for key in params.keys():
            if key not in valid_params_list:
                print(f"参数{key}不属于合法参数，请修改。")
                return False
        return True

    def get_model_response(self, user_prompt, params):
        if not self.check_params_validity(params):
            raise Exception(f"当前参数不合法：{params}")

        self.add_messages('user', user_prompt)
        # 仿OpenAI接口，统一方法
        if self.platform in ['siliconflow', 'volce', 'deepseek', 'openai', 'moonshot']:
            platform_info = self.config['llm_config'][self.platform]
            client = OpenAI(
                api_key=platform_info['api_key'],
                base_url=platform_info['base_url']
            )
            if self.model_name not in platform_info['model_list']:
                raise Exception(f"无效的模型名称{self.model_name},请重新输入")

            # messages = cast(list[ChatCompletionMessageParam], [
            #     {"role": msg["role"], "content": msg["content"]}
            #     for msg in self.messages
            # ])
            response = client.chat.completions.create(
                model=self.model_name,
                messages=self.messages,
                **params
            )
        else:
            raise Exception(f'未定义的模型平台{self.platform}，请检查platform')
        return response

    def result_process(self, response, stream):
        completion = {'role': 'assistant', 'content': ''}
        try:
            if stream:
                while True:
                    event = next(response).to_dict()
                    if event['choices'][0]['finish_reason'] == 'stop':
                        break
                    res_delta = event['choices'][0]['delta']
                    completion['content'] += res_delta['content'] if res_delta['content'] is not None else ""
            else:
                response_dict = response.to_dict()
                res = response_dict['choices'][0]['message']
                completion['content'] += res['content']
            return completion
        except Exception as e:
            raise Exception(f"获取大模型回答错误！Model: {self.model_name}, {str(e)}") 

    def get_llm_answer(self, system_prompt, user_prompt, params={}):
        self.init_messages(system_prompt)
        if params == {}:
            params = self.init_params
        if 'stream' not in params:
            params['stream'] = False
        response = self.get_model_response(user_prompt, params)
        answer = self.result_process(response, params['stream'])
        self.add_messages(answer['role'], answer['content'])
        return answer['content']

    ### 以下是原本TextHandler部分，实现格式标准化功能。
    @staticmethod
    def format_json_output(input_str):
        # string格式输出为dataframe
        try:
            match_result = re.findall(r'\[(.*?)\]', re.sub("\n| ", '', input_str))[0]
            concat = "[" + match_result + "]"
            df = pd.DataFrame(json.loads(concat))
        except Exception:
            try:
                match_result = re.findall(r'\{(.*?)\}', re.sub('\n| ', '', input_str))
                concat = "[" + ','.join(["{" + i + "}" for i in match_result]) + "]"
                df = pd.DataFrame(json.loads(concat))
            except Exception:
                raise Exception(rf'TextHandler Error 0: Format JSON Fail. Raw String: {input_str}')
        return df

    @staticmethod
    def truncate_content_to_token(content_string, token_limit, model):
        # 若文本集总token长度超过指定长度，剔除每个子文本中靠后的文本.
        if len(content_string) > token_limit * 1.5:  # 先粗略匹配，防止输入过长导致tiktoken无法返回。
            content_string = content_string[: int(token_limit * 1.5)]
        encoding = tiktoken.encoding_for_model(model)
        total_token_usage = len(encoding.encode(content_string))
        if total_token_usage is None:
            print('Truncate Fail in Loading encoding for models.')
        if total_token_usage > token_limit:
            content_string = content_string[: int(len(content_string) * token_limit / total_token_usage * 0.95)]
        return content_string

    def get_format_response(
        self,
        system_prompt: str,
        prompt: str,
        output_cols: list,
        check_col_dict: dict,
        params: dict = {},
        max_retry: int = 1
    ) -> pd.DataFrame:
        """
        确保生成标准化的df回答。自动判断llm回答是否正确，并重复尝试直到获取正确回答。

        Args:
            model: 生成回答的模型
            system_prompt: 初始Prompt, 以system身份输入大模型
            prompt: 后续Prompt，以user身份输入大模型
            output_cols: 输出标准dataframe中需要包含的columns
            check_col_dict: 需要检验的columns以及对应的取值范围
                形如：{'is_duplicated': (['是', '否'], '否')}，表示 {columns名称: ([取值范围], 默认取值)}
            params: 模型基础参数设置
            max_retry: 若出错，最大重试次数
        Returns:
            output:
        """
        count = 0
        output = pd.DataFrame(columns=output_cols)
        while count <= max_retry:
            answer = ''
            try:
                self.init_messages(system_prompt)
                answer = self.get_llm_answer(prompt, params=params)
                output = self.format_json_output(answer)
                output = self.valid_check(output, output_cols, check_col_dict)
                break
            except Exception as e:  # 若解析失败，进行重试.
                print(f'{e} \nCurrent Input: {prompt[:50]}\nCurrent Answer: {answer}')
                count += 1
                params = self.init_params.copy()
                params['temperature'] += 0.1
        return output