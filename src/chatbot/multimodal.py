import base64
import mimetypes
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI


class MultimodalChatbot:
    """A chatbot that can handle text, image, and PDF inputs."""

    SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
    SUPPORTED_PDF_EXTENSIONS = {".pdf"}

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        *,
        api_key: str = "",
        system_prompt: str = "You are a friendly and helpful AI assistant. Keep your answers concise.",
    ) -> None:
        self.llm = ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
        self._system_message = SystemMessage(content=system_prompt)
        self.history: list[SystemMessage | HumanMessage | AIMessage] = [
            self._system_message
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send_text(self, text: str) -> str:
        """Send a plain text message and return the assistant's reply."""
        message = HumanMessage(content=text)
        return self._invoke(message)

    def send_image(self, image_path: str, prompt: str = "Describe this image.") -> str:
        """Send a local image file with an optional text prompt."""
        path = self._resolve_path(image_path)
        self._validate_extension(path, self.SUPPORTED_IMAGE_EXTENSIONS, "image")
        data_uri = self._file_to_data_uri(path)

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ]
        )
        return self._invoke(message)

    def send_pdf(self, pdf_path: str, prompt: str = "Describe this document.") -> str:
        """Send a local PDF file with an optional text prompt."""
        path = self._resolve_path(pdf_path)
        self._validate_extension(path, self.SUPPORTED_PDF_EXTENSIONS, "PDF")
        data_uri = self._file_to_data_uri(path)

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ]
        )
        return self._invoke(message)

    def reset(self) -> None:
        """Clear conversation history, keeping only the system message."""
        self.history = [self._system_message]

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _invoke(self, message: HumanMessage) -> str:
        self.history.append(message)
        response = self.llm.invoke(self.history)
        assistant_text: str = response.content  # type: ignore[assignment]
        self.history.append(AIMessage(content=assistant_text))
        return assistant_text

    @staticmethod
    def _resolve_path(raw: str) -> Path:
        path = Path(raw).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return path

    @staticmethod
    def _validate_extension(path: Path, allowed: set[str], label: str) -> None:
        if path.suffix.lower() not in allowed:
            exts = ", ".join(sorted(allowed))
            raise ValueError(
                f"Unsupported {label} format '{path.suffix}'. Supported: {exts}"
            )

    @staticmethod
    def _file_to_data_uri(path: Path) -> str:
        mime, _ = mimetypes.guess_type(str(path))
        if mime is None:
            mime = "application/octet-stream"
        data = path.read_bytes()
        b64 = base64.b64encode(data).decode()
        return f"data:{mime};base64,{b64}"
