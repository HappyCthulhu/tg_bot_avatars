from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain import Message


class PromptBuilder:
    def build_dialog_prompt(
        self,
        system_prompt: str,
        short_memory: list[Message],
        user_message: str,
        long_term_facts: list[str] | None = None,
    ) -> list[dict[str, str]]:
        formatted_short_memory = "\n".join(
            f"{'User' if message.sender == 'user' else 'Assistant'}: {message.text}" for message in short_memory
        )
        facts = long_term_facts or []
        formatted_facts = "\n".join(f"- {fact}" for fact in facts)
        long_term_memory_block = (
            "Важно, ты помнишь о пользователе:\n" + formatted_facts
            if formatted_facts
            else "Важно, пока нет сохраненных фактов о пользователе."
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": long_term_memory_block},
            {"role": "system", "content": formatted_short_memory},
            {"role": "user", "content": user_message},
        ]

    def build_fact_extraction_prompt(self, dialog_messages: list[Message]) -> list[dict[str, str]]:
        dialog_block = "\n".join(
            f"{'User' if message.sender == 'user' else 'Assistant'}: {message.text}" for message in dialog_messages
        )
        instruction = (
            "Выдели важные факты о пользователе и теме диалога, которые нужно помнить.\n"
            "Верни JSON список строк без пояснений.\n"
            "Формат:\n"
            "[\n"
            '  "факт",\n'
            '  "факт"\n'
            "]"
        )
        return [
            {"role": "system", "content": instruction},
            {"role": "user", "content": dialog_block},
        ]
