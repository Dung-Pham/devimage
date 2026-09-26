"""Small OpenAI Responses API client used by the desktop pet."""

from __future__ import annotations

import json
import os
from urllib import error, request


class PetAIError(RuntimeError):
    """Raised when the pet cannot reach or parse the AI service."""


class PetAIService:
    """Call the OpenAI Responses API without adding an SDK dependency."""

    endpoint = "https://api.openai.com/v1/responses"

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna").strip()
        self.system_prompt = os.getenv(
            "DEVIMAGE_PET_PROMPT",
            "You are a cute desktop companion named Mimi. "
            "Reply in Vietnamese unless the user uses another language. "
            "Be concise, warm, playful, and useful. Keep most replies under 3 sentences.",
        )

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def reply(self, history: list[dict[str, str]]) -> str:
        if not self.api_key:
            raise PetAIError(
                "Chưa có OPENAI_API_KEY. Hãy đặt API key trong biến môi trường rồi mở lại pet."
            )

        payload = {
            "model": self.model,
            "input": [
                {"role": "developer", "content": self.system_prompt},
                *history,
            ],
            "max_output_tokens": 180,
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with request.urlopen(req, timeout=45) as response:
                data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise PetAIError(f"OpenAI API trả lỗi HTTP {exc.code}: {detail}") from exc
        except (error.URLError, TimeoutError) as exc:
            raise PetAIError(f"Không kết nối được OpenAI API: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise PetAIError("OpenAI API trả về dữ liệu không hợp lệ.") from exc

        text = data.get("output_text")
        if isinstance(text, str) and text.strip():
            return text.strip()

        for item in data.get("output", []):
            for content in item.get("content", []):
                value = content.get("text")
                if isinstance(value, str) and value.strip():
                    return value.strip()

        raise PetAIError("Không tìm thấy nội dung trả lời từ OpenAI API.")

