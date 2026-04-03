from abc import ABC, abstractmethod

from app.core.config import Settings


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, question: str, context: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def simplify(self, text: str) -> str:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    def generate(self, question: str, context: str) -> str:
        if not context.strip():
            return "[AUSENCIA DE EVIDENCIA] No encontré evidencia suficiente en las fuentes disponibles."
        return (
            "[EVIDENCIA DOCUMENTAL] Respuesta basada en fuentes documentadas:\n"
            f"{context[:900]}\n\n"
            "Fuentes: revisar referencias adjuntas."
        )

    def simplify(self, text: str) -> str:
        return (
            f"{text[:600]}...\n\n"
            "Este es un resumen simplificado. Consulta el documento original para el texto completo."
        )


class GroqLLMProvider(LLMProvider):
    def __init__(self, settings: Settings):
        from groq import Groq

        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model

    def generate(self, question: str, context: str) -> str:
        from app.ai.prompts import SYSTEM_PROMPT

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Pregunta: {question}\n\nContexto:\n{context}",
                },
            ],
        )
        return response.choices[0].message.content or ""

    def simplify(self, text: str) -> str:
        from app.ai.prompts import SIMPLIFY_PROMPT

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SIMPLIFY_PROMPT},
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message.content or text


class OpenAILLMProvider(LLMProvider):
    def __init__(self, settings: Settings):
        from openai import OpenAI

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def generate(self, question: str, context: str) -> str:
        from app.ai.prompts import SYSTEM_PROMPT

        response = self.client.responses.create(
            model=self.model,
            temperature=0,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Pregunta: {question}\n\nContexto:\n{context}"},
            ],
        )
        return response.output_text

    def simplify(self, text: str) -> str:
        from app.ai.prompts import SIMPLIFY_PROMPT

        response = self.client.responses.create(
            model=self.model,
            temperature=0.3,
            input=[
                {"role": "system", "content": SIMPLIFY_PROMPT},
                {"role": "user", "content": text},
            ],
        )
        return response.output_text


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "groq":
        return GroqLLMProvider(settings)
    if settings.llm_provider == "openai":
        return OpenAILLMProvider(settings)
    return MockLLMProvider()

