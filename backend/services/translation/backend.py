"""
Translation backends. `NLLBBackend` runs a real pretrained facebook/nllb-200 model through Hugging Face
Transformers (default: facebook/nllb-200-distilled-600M). The interface is tiny so a larger NLLB checkpoint,
a fine-tuned model or a hosted API can be dropped in later by implementing `translate_batch`.
No dictionaries, no string replacement, no fake output: if the model can't load, we raise.
"""
import logging
import threading
from typing import Protocol

from config import settings

log = logging.getLogger("globalguru.translation")


class TranslationUnavailable(RuntimeError):
    pass


class TranslationBackend(Protocol):
    name: str
    def translate_batch(self, texts: list[str], src_nllb: str, tgt_nllb: str) -> list[str]: ...


class NLLBBackend:
    def __init__(self, model_name: str | None = None) -> None:
        self.name = model_name or "GlobalGuru Hugging Face Space"
        self._client = None
        self._lock = threading.Lock()

    def _load(self) -> None:
        if self._client is not None:
            return

        with self._lock:
            if self._client is not None:
                return

            import os

            space_url = os.getenv("HF_SPACE_URL", "").strip()
            token = os.getenv("HF_TOKEN", "").strip()

            if not space_url or not token:
                raise TranslationUnavailable(
                    "Set HF_SPACE_URL and HF_TOKEN in the backend environment."
                )

            try:
                from gradio_client import Client
            except ImportError as e:
                raise TranslationUnavailable(
                    "Install gradio_client in the backend requirements."
                ) from e

            try:
                log.info("Connecting to translation Space: %s", space_url)
                self._client = Client(space_url, token=token, verbose=False)
            except Exception as e:
                raise TranslationUnavailable(
                    f"Could not connect to the Hugging Face translation Space: {e}"
                ) from e

    def translate_batch(
        self, texts: list[str], src_nllb: str, tgt_nllb: str
    ) -> list[str]:
        self._load()
        translations = []

        try:
            for text in texts:
                result = self._client.predict(
                    text,
                    src_nllb,
                    tgt_nllb,
                    api_name="/translate_batch",
                )
                translations.append(result)
        except Exception as e:
            raise TranslationUnavailable(
                f"The Hugging Face translation Space failed: {e}"
            ) from e

        return translations
_backend: TranslationBackend | None = None


def get_backend() -> TranslationBackend:
    global _backend
    if _backend is None:
        _backend = NLLBBackend()
    return _backend


def set_backend(b: TranslationBackend | None) -> None:
    global _backend
    _backend = b
