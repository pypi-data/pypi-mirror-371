from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Literal, cast

try:
    import instructor
    import together

    PACKAGES_INSTALLED = True
except ImportError:
    PACKAGES_INSTALLED = False

from any_llm.provider import Provider
from any_llm.providers.together.utils import _create_openai_chunk_from_together_chunk
from any_llm.types.completion import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage,
    Choice,
    CompletionParams,
    CompletionUsage,
)
from any_llm.utils.instructor import _convert_instructor_response

if TYPE_CHECKING:
    from together.types import (
        ChatCompletionResponse,
    )
    from together.types.chat_completions import ChatCompletionChunk as TogetherChatCompletionChunk


class TogetherProvider(Provider):
    PROVIDER_NAME = "together"
    ENV_API_KEY_NAME = "TOGETHER_API_KEY"
    PROVIDER_DOCUMENTATION_URL = "https://together.ai/"

    SUPPORTS_COMPLETION_STREAMING = True
    SUPPORTS_COMPLETION = True
    SUPPORTS_RESPONSES = False
    SUPPORTS_COMPLETION_REASONING = False
    SUPPORTS_EMBEDDING = False
    SUPPORTS_LIST_MODELS = True

    PACKAGES_INSTALLED = PACKAGES_INSTALLED

    def _stream_completion(
        self,
        client: "together.Together",
        model: str,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> Iterator[ChatCompletionChunk]:
        """Handle streaming completion - extracted to avoid generator issues."""
        from typing import cast

        response = cast(
            "Iterator[TogetherChatCompletionChunk]",
            client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs,
            ),
        )
        for chunk in response:
            yield _create_openai_chunk_from_together_chunk(chunk)

    def completion(
        self,
        params: CompletionParams,
        **kwargs: Any,
    ) -> ChatCompletion | Iterator[ChatCompletionChunk]:
        """Make the API call to Together AI with instructor support for structured outputs."""
        if self.config.api_base:
            client = together.Together(api_key=self.config.api_key, base_url=self.config.api_base)
        else:
            client = together.Together(api_key=self.config.api_key)

        if params.reasoning_effort == "auto":
            params.reasoning_effort = None

        if params.response_format:
            instructor_client = instructor.patch(client, mode=instructor.Mode.JSON)  # type: ignore [call-overload]

            instructor_response = instructor_client.chat.completions.create(
                model=params.model_id,
                messages=cast("Any", params.messages),
                response_model=params.response_format,
                **params.model_dump(exclude_none=True, exclude={"model_id", "messages", "response_format"}),
                **kwargs,
            )

            return _convert_instructor_response(instructor_response, params.model_id, self.PROVIDER_NAME)

        if params.stream:
            return self._stream_completion(
                client,
                params.model_id,
                params.messages,
                **params.model_dump(exclude_none=True, exclude={"model_id", "messages", "stream"}),
                **kwargs,
            )

        response = cast(
            "ChatCompletionResponse",
            client.chat.completions.create(
                model=params.model_id,
                messages=cast("Any", params.messages),
                **params.model_dump(exclude_none=True, exclude={"model_id", "messages", "response_format"}),
                **kwargs,
            ),
        )

        data = response.model_dump()
        choices_out: list[Choice] = []
        for i, ch in enumerate(data.get("choices", [])):
            msg = ch.get("message", {})

            message = ChatCompletionMessage(
                role=cast("Literal['assistant']", msg.get("role")),
                content=msg.get("content"),
                tool_calls=msg.get("tool_calls"),
            )
            choices_out.append(
                Choice(
                    index=i,
                    finish_reason=cast(
                        "Literal['stop', 'length', 'tool_calls', 'content_filter', 'function_call']",
                        ch.get("finish_reason"),
                    ),
                    message=message,
                )
            )

        usage = None
        if data.get("usage"):
            u = data["usage"]
            usage = CompletionUsage(
                prompt_tokens=u.get("prompt_tokens", 0),
                completion_tokens=u.get("completion_tokens", 0),
                total_tokens=u.get("total_tokens", 0),
            )

        return ChatCompletion(
            id=data.get("id", ""),
            model=params.model_id,
            created=data.get("created", 0),
            object="chat.completion",
            choices=choices_out,
            usage=usage,
        )
