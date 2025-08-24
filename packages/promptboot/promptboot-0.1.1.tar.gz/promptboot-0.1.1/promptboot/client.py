import json
from typing import List, Dict, Optional, Type

from openai import OpenAI
from pydantic import BaseModel, ValidationError
from tenacity import retry, wait_fixed, stop_after_attempt
from .config import *
from promptboot.logs.logger import log_manager

LOG_DIR = Path(config["logging"]["dir"])
client = OpenAI(api_key=config[MODEL_CONFIG_KEY]["api_key"], base_url=config[MODEL_CONFIG_KEY]["base_url"])


class PromptClient:
    def __init__(self,
                 model: str = None,
                 temperature: float = None,
                 max_retries: int = None,
                 retry_wait: int = None):
        self.model = model or config[MODEL_CONFIG_KEY]["model"]
        self.temperature = temperature or config[MODEL_CONFIG_KEY]["temperature"]
        self.max_retries = max_retries or config[MODEL_CONFIG_KEY]["max_retries"]
        self.retry_wait = retry_wait or config[MODEL_CONFIG_KEY]["retry_wait"]

    @retry(wait=wait_fixed(config[MODEL_CONFIG_KEY]["retry_wait"]),
           stop=stop_after_attempt(config[MODEL_CONFIG_KEY]["max_retries"]))
    def call(self,
             system_prompt: Optional[str] = None,
             user_prompt: Optional[str] = None,
             messages: Optional[List[Dict]] = None,
             schema: Optional[Type[BaseModel]] = None):

        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if user_prompt:
                messages.append({"role": "user", "content": user_prompt})

        request_payload = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": messages,
            "response_format": {"type": "json_object"} if schema else None,
        }

        # 记录请求
        log_manager.run_before_request(request_payload)
        # logger.info(f"Request: {json.dumps(request_payload, ensure_ascii=False)}")
        with open(LOG_DIR / "requests.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(request_payload, ensure_ascii=False) + "\n")

        response = client.chat.completions.create(
            **{k: v for k, v in request_payload.items() if v is not None}
        )
        content = response.choices[0].message.content

        # 检查content是否为空
        if content is None:
            error_msg = "API returned empty content"
            log_manager.error(error_msg)
            raise ValueError(error_msg)

        # 记录响应
        log_manager.run_after_response(request=request_payload, response=response)
        with open(LOG_DIR / "responses.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"response": content}, ensure_ascii=False) + "\n")

        if schema:
            try:
                # 尝试解析JSON之前去除可能的空白字符
                cleaned_content = content.strip()
                if not cleaned_content:
                    raise ValueError("Content is empty after stripping whitespace")
                data = json.loads(cleaned_content)
                return schema.model_validate(data)
            except (json.JSONDecodeError, ValidationError, ValueError) as e:
                log_manager.error(f"Validation error: {str(e)}")
                log_manager.error(f"Content causing error: {content}")
                raise e  # 自动触发重试
        return content