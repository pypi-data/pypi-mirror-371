import json
import logging
from pathlib import Path
from typing import Any, Dict, Callable, List


class LogManager:
    def __init__(self, log_dir: Path, use_full_logging: bool = False):
        self.log_dir = log_dir
        self._before_request_hooks: List[Callable] = []
        self._after_response_hooks: List[Callable] = []
        
        # 设置日志记录
        logging.basicConfig(
            filename=self.log_dir / "promptboot.log",
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
        )
        
        self.logger = logging.getLogger("promptboot")
        
        if use_full_logging:
            self.register_before_request(self._log_request_full)
            self.register_after_response(self._log_response_full)
        else:
            # 注册默认钩子
            self.register_before_request(self._log_request)
            self.register_after_response(self._log_response)

    def get_logger(self):
        """返回logger实例"""
        return self.logger

    def _log_request(self, request):
        """默认的请求日志钩子"""
        self.logger.info(f"Request: {request}")

    def _log_request_full(self,request):
        # request_record = {
        #     "timestamp": datetime.utcnow().isoformat(),
        #     "request": request,
        # }
        # f.write(json.dumps(request_record, ensure_ascii=False) + "\n")
        self.logger.info(f"Request: {json.dumps(request, ensure_ascii=False)}")

    def _log_response(self, request, response):
        """默认的响应日志钩子"""
        self.logger.info(f"Response: {response}")

    def _log_response_full(self,request, response):
        response_record = {
            "request": request,
            "response": response.model_dump() if hasattr(response, "model_dump") else str(response),
        }
        self.logger.info(f"Response: {response_record}")
        # with open(self.log_dir / "responses.jsonl", "a", encoding="utf-8") as f:
        #     f.write(json.dumps(response_record, ensure_ascii=False) + "\n")

    def register_before_request(self, func: Callable):
        self._before_request_hooks.append(func)

    def register_after_response(self, func: Callable):
        self._after_response_hooks.append(func)

    def run_before_request(self, request: Dict[str, Any]):
        for hook in self._before_request_hooks:
            hook(request)

    def run_after_response(self, request: Dict[str, Any], response: Any):
        for hook in self._after_response_hooks:
            hook(request, response)

    def error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)