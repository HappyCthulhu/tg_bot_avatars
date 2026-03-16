from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain import Message


# TODO: это, случаем, не стоит объединить с LLMService?
class PromptBuilder:
    def build_dialog_prompt(
        self,
        system_prompt: str,
        short_memory: list[Message],
        user_message: str,
    ) -> list[dict[str, str]]:
        formatted_short_memory = "\n".join(
            f"{'User' if message.sender == 'user' else 'Assistant'}: {message.text}" for message in short_memory
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": formatted_short_memory},
            {"role": "user", "content": user_message},
        ]
