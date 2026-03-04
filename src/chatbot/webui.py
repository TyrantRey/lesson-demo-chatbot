from pathlib import Path

import gradio as gr

from chatbot.config import settings
from chatbot.multimodal import MultimodalChatbot
from chatbot.prompt_store import (
    delete_prompt,
    get_active_prompt,
    list_prompt_names,
    load_prompts,
    save_prompt,
)


def _classify_file(path: str) -> str:
    """Return 'image', 'pdf', or 'unknown' based on extension."""
    ext = Path(path).suffix.lower()
    if ext in MultimodalChatbot.SUPPORTED_IMAGE_EXTENSIONS:
        return "image"
    if ext in MultimodalChatbot.SUPPORTED_PDF_EXTENSIONS:
        return "pdf"
    return "unknown"


def main() -> None:
    active_name, active_text = get_active_prompt()
    bot = MultimodalChatbot(api_key=settings.google_api_key, system_prompt=active_text)

    # ── Chat handler ──────────────────────────────────────────────────

    def respond(message: dict, history: list[dict]) -> str:
        text: str = message.get("text", "").strip()
        files: list[str] = message.get("files", [])

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

    # ── System prompt callbacks ───────────────────────────────────────

    def on_save(name: str, prompt_text: str) -> tuple[str, gr.update]:
        name = name.strip()
        prompt_text = prompt_text.strip()
        if not name:
            return "⚠️ Please enter a name.", gr.update()
        if not prompt_text:
            return "⚠️ Prompt cannot be empty.", gr.update()
        save_prompt(name, prompt_text)
        bot.set_system_prompt(prompt_text)
        return (
            f'💾 Saved & applied "{name}".',
            gr.update(choices=list_prompt_names(), value=name),
        )

    def on_load(name: str) -> tuple[str, str]:
        if not name:
            return "", "⚠️ Select a prompt first."
        store = load_prompts()
        text = store["prompts"].get(name, "")
        bot.set_system_prompt(text)
        store["active"] = name
        from chatbot.prompt_store import save_prompts

        save_prompts(store)
        return text, f'✅ Loaded "{name}". History cleared.'

    def on_delete(name: str) -> tuple[str, str, gr.update]:
        if not name:
            return "", "⚠️ Select a prompt first.", gr.update()
        names = list_prompt_names()
        if len(names) <= 1:
            return "", "⚠️ Cannot delete the last prompt.", gr.update()
        delete_prompt(name)
        new_names = list_prompt_names()
        _, new_text = get_active_prompt()
        bot.set_system_prompt(new_text)
        return (
            new_text,
            f'🗑️ Deleted "{name}".',
            gr.update(choices=new_names, value=new_names[0] if new_names else ""),
        )

    # ── Build UI ──────────────────────────────────────────────────────

    with gr.Blocks(title="🤖 Multimodal Chatbot") as demo:
        gr.Markdown("# 🤖 Multimodal Chatbot")
        gr.Markdown(
            "Powered by **Gemini 2.5 Flash** via LangChain  •  "
            "Send text, images, or PDFs"
        )

        with gr.Accordion("⚙️ System Prompt", open=False):
            prompt_dropdown = gr.Dropdown(
                choices=list_prompt_names(),
                value=active_name,
                label="Saved Prompts",
            )
            system_prompt_box = gr.Textbox(
                value=active_text,
                label="System Prompt",
                lines=3,
                placeholder="Enter a system prompt…",
            )
            prompt_name_box = gr.Textbox(
                label="Prompt Name",
                placeholder="Enter a name to save this prompt as…",
                value=active_name,
            )
            with gr.Row():
                save_btn = gr.Button("💾 Save", variant="primary")
                load_btn = gr.Button("📂 Load")
                delete_btn = gr.Button("🗑️ Delete", variant="stop")
            status_text = gr.Textbox(
                label="Status", interactive=False, show_label=False
            )

            save_btn.click(
                fn=on_save,
                inputs=[prompt_name_box, system_prompt_box],
                outputs=[status_text, prompt_dropdown],
            )
            load_btn.click(
                fn=on_load,
                inputs=[prompt_dropdown],
                outputs=[system_prompt_box, status_text],
            )
            delete_btn.click(
                fn=on_delete,
                inputs=[prompt_dropdown],
                outputs=[system_prompt_box, status_text, prompt_dropdown],
            )

        chatbot = gr.Chatbot(
            label="Chatbot",
            placeholder="💬 Send text, images, or PDFs — I can understand them all!",
            height=520,
        )

        gr.ChatInterface(
            fn=respond,
            multimodal=True,
            chatbot=chatbot,
            examples=[
                "Hello! What can you do?",
                "Explain quantum computing in simple terms.",
            ],
        )

    demo.launch()


if __name__ == "__main__":
    main()
