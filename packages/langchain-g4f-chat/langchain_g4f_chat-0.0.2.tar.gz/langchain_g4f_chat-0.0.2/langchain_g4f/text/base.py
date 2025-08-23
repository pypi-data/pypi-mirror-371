"""GPT4Free chat wrapper."""

from __future__ import annotations

import logging
import sys
import warnings
from collections.abc import AsyncIterator, Iterator, Mapping, Sequence
from operator import itemgetter
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypedDict,
    Union,
    cast,
)

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import (
    BaseChatModel,
    LangSmithParams,
    agenerate_from_stream,
    generate_from_stream,
)
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    ChatMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.runnables import Runnable, RunnableMap, RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_core.utils import (
    get_pydantic_field_names,
    secret_from_env,
    from_env,
)
from langchain_core.utils.function_calling import (
    convert_to_openai_function,
    convert_to_openai_tool,
)
from langchain_core.utils.pydantic import is_basemodel_subclass
from langchain_core.utils.utils import _build_model_kwargs
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator
from typing_extensions import Self

# Import output parsers for structured output
try:
    from langchain_core.output_parsers.openai_tools import PydanticToolsParser
except ImportError:
    # Fallback for older versions
    PydanticToolsParser = None

# Import g4f
try:
    import g4f
    from g4f.Provider import BaseProvider
except ImportError as e:
    raise ImportError(
        "Could not import g4f python package. "
        "Please install it with `pip install g4f`."
    ) from e

logger = logging.getLogger(__name__)


def _convert_message_to_dict(message: BaseMessage) -> dict:
    """Convert a LangChain message to a dictionary for g4f.

    Args:
        message: The LangChain message.

    Returns:
        The dictionary.
    """
    # Handle content - can be string or list for multimodal messages
    content = message.content
    
    # Process content for vision/multimodal support
    if isinstance(content, list):
        # Handle multimodal content (text + images)
        processed_content = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    processed_content.append({
                        "type": "text",
                        "text": item.get("text", "")
                    })
                elif item.get("type") == "image_url":
                    image_url = item.get("image_url", {})
                    if isinstance(image_url, dict):
                        processed_content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": image_url.get("url", ""),
                                "detail": image_url.get("detail", "auto")
                            }
                        })
                    else:
                        # Handle simple image URL string
                        processed_content.append({
                            "type": "image_url",
                            "image_url": {"url": str(image_url)}
                        })
                elif item.get("type") == "image":
                    # Handle Anthropic-style image format
                    if "source" in item:
                        source = item["source"]
                        if source.get("type") == "base64":
                            media_type = source.get("media_type", "image/jpeg")
                            data = source.get("data", "")
                            processed_content.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:{media_type};base64,{data}"}
                            })
            elif isinstance(item, str):
                # Handle simple text in list
                processed_content.append({
                    "type": "text",
                    "text": item
                })
        content = processed_content
    elif isinstance(content, str):
        # Handle simple text content
        content = content
    else:
        # Fallback for other content types
        content = str(content)

    message_dict: dict[str, Any] = {"content": content}

    # Map LangChain message types to OpenAI format
    if isinstance(message, ChatMessage):
        message_dict["role"] = message.role
    elif isinstance(message, HumanMessage):
        message_dict["role"] = "user"
    elif isinstance(message, AIMessage):
        message_dict["role"] = "assistant"
    elif isinstance(message, SystemMessage):
        message_dict["role"] = "system"
    else:
        raise ValueError(f"Got unknown type {type(message)}")

    return message_dict


def _convert_chunk_to_generation_chunk(chunk) -> ChatGenerationChunk:
    """Convert a chunk to a generation chunk."""
    # Handle different types of responses from g4f
    if hasattr(chunk, 'choices') and chunk.choices:
        # Handle OpenAI-style response
        content = chunk.choices[0].delta.content or ""
    elif hasattr(chunk, 'content'):
        # Handle response with content attribute
        content = str(chunk.content)
    elif hasattr(chunk, '__dict__'):
        # Handle Sources or other complex objects
        content = str(chunk)
    elif isinstance(chunk, (str, int, float)):
        # Handle simple string/numeric responses
        content = str(chunk)
    else:
        # Fallback for unknown types
        content = str(chunk) if chunk is not None else ""
    
    return ChatGenerationChunk(
        message=AIMessageChunk(content=content),
        generation_info=None,
    )


class ChatG4F(BaseChatModel):
    """GPT4Free chat model integration.

    This class provides a LangChain interface for the GPT4Free library,
    allowing you to use any g4f provider with LangChain.

    Setup:
        Install ``g4f`` and optionally set environment variables.

        .. code-block:: bash

            pip install -U g4f

    Key init args — completion params:
        model: str
            Name of the model to use (e.g., "gpt-3.5-turbo", "gpt-4", "gpt-4o").
        provider: Any
            G4F provider to use (e.g., g4f.Provider.OpenAI, g4f.Provider.Bing).
        temperature: float
            Sampling temperature. Ranges from 0.0 to 2.0.
        max_tokens: Optional[int]
            Maximum number of tokens to generate.
        top_p: Optional[float]
            Total probability mass of tokens to consider at each step.
        frequency_penalty: Optional[float]
            Penalize new tokens based on their existing frequency.
        presence_penalty: Optional[float]
            Penalize new tokens based on whether they appear in the text so far.
        reasoning_effort: Optional[str]
            Constrains effort on reasoning for reasoning models (o1 models).
        stream: bool
            Whether to stream responses.
        model_kwargs: Dict[str, Any]
            Holds any model parameters valid for create call not explicitly specified.

    Key init args — client params:
        api_key: Optional[str]
            API key for providers that require authentication.
        timeout: Union[float, Tuple[float, float], Any, None]
            Timeout for requests.
        max_retries: int
            Maximum number of retries to make when generating.

    Example:
        .. code-block:: python

            from langchain_g4f import ChatG4F
            import g4f

            llm = ChatG4F(
                model="gpt-4o",
                provider=g4f.Provider.OpenAI,
                api_key="your-api-key",
                temperature=0.7,
                max_tokens=1000,
            )

            messages = [("human", "Hello, how are you?")]
            response = llm.invoke(messages)
    """

    model_name: str = Field(default="gpt-3.5-turbo", alias="model")
    """Model name to use."""

    provider: Any = Field(default=None)
    """G4F provider to use. If None, g4f will auto-select."""

    api_key: Optional[SecretStr] = Field(default=None)
    """API key for providers that require authentication."""

    temperature: float = 0.7
    """What sampling temperature to use."""

    max_tokens: Optional[int] = None
    """The maximum number of tokens to generate."""

    top_p: Optional[float] = None
    """Total probability mass of tokens to consider at each step."""

    frequency_penalty: Optional[float] = None
    """Penalize new tokens based on their existing frequency in the text so far."""

    presence_penalty: Optional[float] = None
    """Penalize new tokens based on whether they appear in the text so far."""

    reasoning_effort: Optional[str] = None
    """Constrains effort on reasoning for reasoning models (o1 models only).

    Currently supported values are low, medium, and high."""

    stream: bool = False
    """Whether to stream the results."""

    streaming: bool = False
    """Whether to stream the results (alias for stream)."""

    n: int = 1
    """Number of chat completions to generate for each prompt."""

    stop: Optional[Union[List[str], str]] = Field(default=None, alias="stop_sequences")
    """Default stop sequences."""

    timeout: Union[float, Tuple[float, float], Any, None] = Field(default=None)
    """Timeout for requests."""

    max_retries: int = 2
    """Maximum number of retries to make when generating."""

    model_kwargs: Dict[str, Any] = Field(default_factory=dict)
    """Holds any additional parameters for the g4f create call."""

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        exclude={"provider"},
    )

    @model_validator(mode="before")
    @classmethod
    def build_extra(cls, values: Dict[str, Any]) -> Any:
        """Build extra kwargs from additional params that were passed in."""
        all_required_field_names = get_pydantic_field_names(cls)
        values = _build_model_kwargs(values, all_required_field_names)
        return values

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        """Validate that the g4f library is available and parameters are valid."""
        # Validate n parameter
        if self.n < 1:
            raise ValueError("n must be at least 1.")
        if self.n > 1 and (self.stream or self.streaming):
            raise ValueError("n must be 1 when streaming.")

        # Sync streaming parameters
        if self.stream != self.streaming:
            self.streaming = self.stream

        # Validate temperature
        if self.temperature == 0:
            self.temperature = 1e-8

        # Validate provider if specified
        if self.provider is not None:
            if not hasattr(self.provider, 'create_completion') and not hasattr(self.provider, 'create_async_generator'):
                logger.warning(f"Provider {self.provider} may not be a valid g4f provider")

        return self

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "g4f"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        provider_name = getattr(self.provider, '__name__', str(self.provider)) if self.provider else None
        return {
            "model_name": self.model_name,
            "provider": provider_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "reasoning_effort": self.reasoning_effort,
            "stream": self.stream,
            "n": self.n,
            "stop": self.stop,
            **self.model_kwargs,
        }

    def _prepare_params(self, stream: Optional[bool] = None, **kwargs: Any) -> Dict[str, Any]:
        """Prepare parameters for g4f call."""
        params = {
            "model": self.model_name,
            "temperature": self.temperature,
            "stream": stream if stream is not None else self.stream,
            **self.model_kwargs,
            **kwargs,
        }

        # Add optional parameters
        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens
        if self.top_p is not None:
            params["top_p"] = self.top_p
        if self.frequency_penalty is not None:
            params["frequency_penalty"] = self.frequency_penalty
        if self.presence_penalty is not None:
            params["presence_penalty"] = self.presence_penalty
        if self.reasoning_effort is not None:
            params["reasoning_effort"] = self.reasoning_effort
        if self.n is not None and self.n != 1:
            params["n"] = self.n
        if self.stop is not None:
            params["stop"] = self.stop
        if self.timeout is not None:
            params["timeout"] = self.timeout

        if self.provider is not None:
            params["provider"] = self.provider

        if self.api_key is not None:
            params["api_key"] = self.api_key.get_secret_value()

        return params

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Stream the LLM on the given messages."""
        params = self._prepare_params(stream=True, **kwargs)
        messages_dict = [_convert_message_to_dict(m) for m in messages]
        
        try:
            response = g4f.ChatCompletion.create(
                messages=messages_dict,
                **params
            )
            
            # Handle streaming response
            if hasattr(response, '__iter__'):
                for chunk in response:
                    if chunk:
                        generation_chunk = _convert_chunk_to_generation_chunk(chunk)
                        # Extract the actual text content for the token callback
                        token_text = generation_chunk.message.content
                        if run_manager and token_text:
                            run_manager.on_llm_new_token(token_text, chunk=generation_chunk)
                        yield generation_chunk
            else:
                # Non-streaming response
                generation_chunk = _convert_chunk_to_generation_chunk(str(response))
                token_text = generation_chunk.message.content
                if run_manager and token_text:
                    run_manager.on_llm_new_token(token_text, chunk=generation_chunk)
                yield generation_chunk
                
        except Exception as e:
            logger.error(f"Error in g4f streaming: {e}")
            raise

    async def _astream(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Async stream the LLM on the given messages."""
        params = self._prepare_params(stream=True, **kwargs)
        messages_dict = [_convert_message_to_dict(m) for m in messages]
        
        try:
            response = await g4f.ChatCompletion.create_async(
                messages=messages_dict,
                **params
            )
            
            # Handle async streaming response
            if hasattr(response, '__aiter__'):
                async for chunk in response:
                    if chunk:
                        generation_chunk = _convert_chunk_to_generation_chunk(chunk)
                        # Extract the actual text content for the token callback
                        token_text = generation_chunk.message.content
                        if run_manager and token_text:
                            await run_manager.on_llm_new_token(token_text, chunk=generation_chunk)
                        yield generation_chunk
            else:
                # Non-streaming response
                generation_chunk = _convert_chunk_to_generation_chunk(str(response))
                token_text = generation_chunk.message.content
                if run_manager and token_text:
                    await run_manager.on_llm_new_token(token_text, chunk=generation_chunk)
                yield generation_chunk
                
        except Exception as e:
            logger.error(f"Error in g4f async streaming: {e}")
            raise

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Call g4f and return the response."""
        if self.stream:
            stream_iter = self._stream(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return generate_from_stream(stream_iter)

        params = self._prepare_params(stream=False, **kwargs)
        messages_dict = [_convert_message_to_dict(m) for m in messages]
        
        try:
            response = g4f.ChatCompletion.create(
                messages=messages_dict,
                **params
            )

            # Convert response to ChatResult
            message = AIMessage(content=str(response))
            generation = ChatGeneration(
                message=message,
                generation_info={
                    "model_name": self.model_name,
                    "provider": str(self.provider) if self.provider else None,
                }
            )

            return ChatResult(
                generations=[generation],
                llm_output={
                    "model_name": self.model_name,
                    "provider": str(self.provider) if self.provider else None,
                },
            )

        except Exception as e:
            logger.error(f"Error in g4f generation: {e}")
            # Re-raise with more context
            raise RuntimeError(f"G4F generation failed: {e}") from e

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async call g4f and return the response."""
        if self.stream:
            stream_iter = self._astream(
                messages, stop=stop, run_manager=run_manager, **kwargs
            )
            return await agenerate_from_stream(stream_iter)

        params = self._prepare_params(stream=False, **kwargs)
        messages_dict = [_convert_message_to_dict(m) for m in messages]
        
        try:
            response = await g4f.ChatCompletion.create_async(
                messages=messages_dict,
                **params
            )

            # Convert response to ChatResult
            message = AIMessage(content=str(response))
            generation = ChatGeneration(
                message=message,
                generation_info={
                    "model_name": self.model_name,
                    "provider": str(self.provider) if self.provider else None,
                }
            )

            return ChatResult(
                generations=[generation],
                llm_output={
                    "model_name": self.model_name,
                    "provider": str(self.provider) if self.provider else None,
                },
            )

        except Exception as e:
            logger.error(f"Error in g4f async generation: {e}")
            # Re-raise with more context
            raise RuntimeError(f"G4F async generation failed: {e}") from e

    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], Type, Callable, BaseTool]],
        *,
        tool_choice: Optional[
            Union[Dict, str, Literal["auto", "none", "required", "any"], bool]
        ] = None,
        strict: Optional[bool] = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, BaseMessage]:
        """Bind tool-like objects to this chat model.

        Assumes model is compatible with OpenAI tool-calling API.

        Args:
            tools: A list of tool definitions to bind to this chat model.
                Supports any tool definition handled by
                :meth:`langchain_core.utils.function_calling.convert_to_openai_tool`.
            tool_choice: Which tool to require the model to call. Options are:

                - ``str`` of the form ``"tool_name"``: calls the tool with that name;
                - ``"auto"``: automatically selects a tool (including no tool);
                - ``"none"``: does not call a tool;
                - ``"required"``: forces at least one tool to be called;
                - ``"any"``: forces at least one tool to be called (same as "required");
                - ``True``: equivalent to "required";
                - ``False``: equivalent to "none".

                .. versionchanged:: 0.2.26
                    ``"required"`` and ``"any"`` are equivalent.

            strict: Whether to enforce strict schema adherence when generating
                the tool call. Only relevant when using ``"function_calling"`` tool choice.
                If ``True``, the model will follow the exact schema defined in the tool.
                If ``False``, the model may deviate from the schema. If ``None``, the
                model will use its default behavior.

        Returns:
            A Runnable that takes the same input as this chat model and returns a
            message with tool calls.
        """
        formatted_tools = [convert_to_openai_tool(tool) for tool in tools]
        if tool_choice is not None and tool_choice:
            if isinstance(tool_choice, str):
                if tool_choice not in ("auto", "none", "required", "any"):
                    tool_choice = {"type": "function", "function": {"name": tool_choice}}
            elif isinstance(tool_choice, bool):
                tool_choice = "required" if tool_choice else "none"
            elif tool_choice in ("required", "any"):
                tool_choice = "required"
            kwargs["tool_choice"] = tool_choice
        return self.bind(tools=formatted_tools, **kwargs)

    def with_structured_output(
        self,
        schema: Optional[Union[Dict, Type[BaseModel]]] = None,
        *,
        method: Literal["function_calling", "json_mode"] = "function_calling",
        include_raw: bool = False,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, Union[Dict, BaseModel]]:
        """Model wrapper that returns outputs formatted to match the given schema.

        Args:
            schema: The output schema. Can be passed in as:

                - an OpenAI function/tool schema,
                - a JSON Schema,
                - a TypedDict class,
                - or a Pydantic class.

                If ``schema`` is a Pydantic class then the model output will be a
                Pydantic instance of that class, and the model-generated fields will be
                validated by the Pydantic class.

            method: The method to use for getting structured output. One of
                "function_calling" or "json_mode". Defaults to "function_calling".

            include_raw: Whether to return the raw message alongside the parsed output.
                If True, will return a dict with keys "raw" and "parsed".

        Returns:
            A Runnable that takes the same input as this chat model and returns
            structured output.

        .. versionadded:: 0.1.7

        Example: schema=Pydantic class, method="function_calling", include_raw=False:
            .. code-block:: python

                from langchain_g4f import ChatG4F
                from pydantic import BaseModel

                class AnswerWithJustification(BaseModel):
                    '''An answer to the user question along with justification for the answer.'''

                    answer: str
                    justification: str

                llm = ChatG4F(model="gpt-4", temperature=0)
                structured_llm = llm.with_structured_output(AnswerWithJustification)

                structured_llm.invoke("What weighs more a pound of bricks or a pound of feathers")
                # -> AnswerWithJustification(
                #     answer='They weigh the same',
                #     justification='Both a pound of bricks and a pound of feathers weigh one pound. The weight is the same, but the volume or density of the materials may differ.'
                # )
        """
        if kwargs:
            raise ValueError(f"Received unsupported arguments {kwargs}")
        is_pydantic_schema = is_basemodel_subclass(schema)
        if method == "function_calling":
            if schema is None:
                raise ValueError(
                    "schema must be specified when method is 'function_calling'. "
                    "Received None."
                )
            tool = convert_to_openai_tool(schema)
            tool_name = tool["function"]["name"]
            llm = self.bind_tools([schema], tool_choice=tool_name)
            if is_pydantic_schema:
                output_parser = PydanticToolsParser(
                    tools=[schema], first_tool_only=True  # type: ignore[list-item]
                )
            else:
                from langchain_core.output_parsers.openai_tools import (
                    JsonOutputKeyToolsParser,
                )
                output_parser = JsonOutputKeyToolsParser(
                    key_name=tool_name, first_tool_only=True
                )
        elif method == "json_mode":
            llm = self.bind(response_format={"type": "json_object"})
            if is_pydantic_schema:
                from langchain_core.output_parsers import PydanticOutputParser
                output_parser = PydanticOutputParser(pydantic_object=schema)  # type: ignore[type-var, arg-type]
            else:
                from langchain_core.output_parsers import JsonOutputParser
                output_parser = JsonOutputParser()
        else:
            raise ValueError(
                f"Unrecognized method argument. Expected one of 'function_calling' or "
                f"'json_mode'. Received: '{method}'"
            )

        if include_raw:
            parser_assign = RunnablePassthrough.assign(
                parsed=itemgetter("raw") | output_parser, parsing_error=lambda _: None
            )
            parser_none = RunnablePassthrough.assign(parsed=lambda _: None)
            parser_with_fallback = parser_assign.with_fallbacks(
                [parser_none], exception_key="parsing_error"
            )
            return RunnableMap(raw=llm) | parser_with_fallback
        else:
            return llm | output_parser

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "chat_models", "g4f"]

    @property
    def lc_secrets(self) -> dict[str, str]:
        """Return secrets dict."""
        return {"api_key": "G4F_API_KEY"} if self.api_key else {}

    @property
    def lc_attributes(self) -> dict[str, Any]:
        """Return attributes dict."""
        attributes: dict[str, Any] = {}
        if self.provider:
            attributes["provider"] = str(self.provider)
        return attributes
