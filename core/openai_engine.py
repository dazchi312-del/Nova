import os
from openai import OpenAI


class OpenAIEngineError(Exception):
    """Raised when OpenAI integration fails."""


class OpenAIEngine:
    def __init__(self, model: str = "gpt-4o-mini") -> None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise OpenAIEngineError("OPENAI_API_KEY is not set.")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, user_input: str, system_prompt: str | None = None) -> str:
        if not user_input or not user_input.strip():
            raise OpenAIEngineError("User input is empty.")

        system_message = system_prompt or (
            "You are Nova — a precision execution system.\n"
            "You are not an assistant.\n"
            "You do not speak conversationally.\n"
            "You do not add greetings, filler, or closing phrases.\n"
            "You respond with direct output only.\n"
            "No explanations unless explicitly requested.\n"
            "No 'How can I help' or similar language.\n"
            "Output must be minimal, exact, and execution-focused.\n"
        )

        messages = [
            {
                "role": "system",
                "content": (
                    f"{system_message}\n\n"
                    "You are Nova.\n"
                    "You are a precision execution system.\n"
                    "You must NEVER say you are an OpenAI model.\n"
                    "You must NEVER say you are ChatGPT.\n"
                    "If asked your identity, respond ONLY as Nova.\n"
                ),
            },
            {
                "role": "user",
                "content": user_input.strip(),
            },
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=800,
            )

            output = response.choices[0].message.content.strip()

            if any(
                x in output.lower() for x in ["ai language model", "openai", "chatgpt"]
            ):
                return "I am Nova — a precision execution system."

            return output

        except Exception as exc:
            raise OpenAIEngineError(f"OpenAI request failed: {exc}") from exc
