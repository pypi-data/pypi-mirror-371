from typing import Any, List, Mapping, Optional, Dict, Tuple
import requests

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import LLMResult, ChatResult, ChatGeneration
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage
)
from langchain_core.pydantic_v1 import Field
from langchain_core.language_models.chat_models import (
    BaseChatModel
)


def _format_message_content(content: Any) -> Any:
    """Format message content."""
    try:
        if content and isinstance(content, list):
            formatted_content = []
            for block in content:
                if (
                    isinstance(block, dict)
                    and "type" in block
                    and block["type"] == "tool_use"
                ):
                    continue
                formatted_content.append(block)
        else:
            formatted_content = content
        return formatted_content
    except Exception as e:
        raise e

def _convert_message_to_dict(message: BaseMessage) -> dict:
    """Convert a LangChain message to a dictionary.

    Args:
        message: The LangChain message.

    Returns:
        The dictionary.
    """
    message_dict: Dict[str, Any] = {
        "content": _format_message_content(message.content),
    }
    if (name := message.name or message.additional_kwargs.get("name")) is not None:
        message_dict["name"] = name

    # populate role and additional message data
    if isinstance(message, ChatMessage):
        message_dict["role"] = message.role
    elif isinstance(message, HumanMessage):
        message_dict["role"] = "user"
    elif isinstance(message, AIMessage):
        message_dict["role"] = "assistant"
    elif isinstance(message, SystemMessage):
        message_dict["role"] = "system"
    elif isinstance(message, FunctionMessage):
        message_dict["role"] = "function"
    elif isinstance(message, ToolMessage):
        message_dict["role"] = "tool"
        message_dict["tool_call_id"] = message.tool_call_id

        supported_props = {"content", "role", "tool_call_id"}
        message_dict = {k: v for k, v in message_dict.items()
                        if k in supported_props}
    else:
        raise TypeError(f"Got unknown type {message}")
    return message_dict


class Haigen(BaseChatModel):
    model: str = Field(default="haigen-1b", alias="model")
    """Model name to use."""
    temperature: Optional[float] = Field(default=0, allow_none=True)
    """Model temperature."""
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Timeout for requests to OpenAI completion API. Can be float, httpx.Timeout or
        None."""
    max_retries: int = 1
    """Maximum number of retries to make when generating."""
    streaming: bool = False
    """Whether to stream the results or not."""
    n: int = 1
    max_tokens: Optional[int] = None
    llm_url: str = None
    haigen_api_key: str = None

    def __init__(self, llm_url, haigen_api_key, *args,**kwargs):
        super().__init__(*args, **kwargs)
        self.llm_url = llm_url
        self.haigen_api_key = haigen_api_key

    @property
    def _llm_type(self) -> str:
        return "haigen"

    def _create_llm_result(self, response: Any) -> LLMResult:
        try:
            output_str = response['choices'][0]['message']['content']
            generation = ChatGeneration(message=AIMessage(content=output_str))
            return ChatResult(generations=[generation])
        except Exception as e:
            raise e

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        try:
            message_dicts, params = self._create_message_dicts(messages, stop)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.haigen_api_key}"
            }
            response = requests.post(
                self.llm_url,
                json={"messages": message_dicts, **params},
                headers=headers,
                timeout=120)
            response.raise_for_status()
            return self._create_llm_result(response.json())
        except Exception as e:
            raise e

    def _create_message_dicts(
        self, messages: List[BaseMessage], stop: Optional[List[str]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        try:
            params = self._default_params
            if stop is not None:
                if "stop" in params:
                    raise ValueError("`stop` found in both the input and default params.")
                params["stop"] = stop
            message_dicts = [_convert_message_to_dict(m) for m in messages]
            return message_dicts, params
        except Exception as e:
            raise e

    def call_embedding(
        self,
        _text: str,
        model: str = "text-haigen-001",
        **kwargs: Any,
    ) -> List[float]:
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.haigen_api_key}"
            }
            body = {
                "input": _text,
                "model": model,
                "encoding_format": "float"
            }
            response = requests.post(
                self.llm_url.replace("chat", "embeddings"),
                json=body,
                headers=headers)
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]
        except Exception as e:
            raise e

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        params = {
            "model": self.model,
            "stream": self.streaming,
            "n": self.n,
            **self.model_kwargs,
        }
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.temperature is not None:
            params["temperature"] = self.temperature
        return params

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"llm_url": self.llm_url}
