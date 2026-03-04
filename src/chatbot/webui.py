from pathlib import Path

import gradio as gr

from chatbot.config import settings
from chatbot.multimodal import MultimodalChatbot


bot = MultimodalChatbot(api_key=settings.google_api_key)


def _classify_file(path: str) -> str:
    """Return 'image', 'pdf', or 'unknown' based on extension."""
    ext = Path(path).suffix.lower()
    if ext in MultimodalChatbot.SUPPORTED_IMAGE_EXTENSIONS:
        return "image"
    if ext in MultimodalChatbot.SUPPORTED_PDF_EXTENSIONS:
        return "pdf"
    return "unknown"


def respond(
    message: dict,
    history: list[dict],
) -> str:
    """Handle a multimodal user message.

    Parameters
    ----------
    message:
        ``{"text": str, "files": list[str]}`` from the multimodal textbox.
    history:
        OpenAI-style list of message dicts (managed by Gradio).
    """
    text: str = message.get("text", "").strip()
    files: list[str] = message.get("files", [])

    # Process attached files first
    replies: list[str] = []
    for file_path in files:
        kind = _classify_file(file_path)
        prompt = text or (
            "Describe this image." if kind == "image" else "Describe this document."
        )
        try:
            if kind == "image":
                replies.append(bot.send_image(file_path, prompt))
            elif kind == "pdf":
                replies.append(bot.send_pdf(file_path, prompt))
            else:
                replies.append(f"⚠️ Unsupported file type: {Path(file_path).suffix}")
        except Exception as exc:
            replies.append(f"❌ Error processing file: {exc}")

    if replies:
        return "\n\n---\n\n".join(replies)

    if text:
        try:
            return bot.send_text(text)
        except Exception as exc:
            return f"❌ Error: {exc}"

    return "Please enter a message or attach a file."


def main() -> None:
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="slate",
        font=gr.themes.GoogleFont("Inter"),
    )

    with gr.Blocks(theme=theme, title="🤖 Multimodal Chatbot") as demo:
        chatbot = gr.Chatbot(
            label="Chatbot",
            placeholder=(
                "💬 Multimodal Chatbot"
                "Send text, images, or PDFs — I can understand them all"
            ),
            height=520,
            elem_id="chatbot-container",
        )

        gr.ChatInterface(
            fn=respond,
            multimodal=True,
            chatbot=chatbot,
            title="🤖 Multimodal Chatbot",
            description="Powered by **Gemini 2.5 Flash** via LangChain  •  Send text, images, or PDFs",
            examples=[
                "Hello! What can you do?",
                "Explain quantum computing in simple terms.",
            ],
        )

    demo.launch()


if __name__ == "__main__":
    main()
