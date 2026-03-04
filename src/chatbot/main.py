from chatbot.config import settings
from chatbot.multimodal import MultimodalChatbot

HELP_TEXT = """
Commands:
  /image <path> [prompt]  — Send an image file (png, jpg, gif, webp, bmp)
  /pdf   <path> [prompt]  — Send a PDF file
  /reset                  — Clear conversation history
  /help                   — Show this help message
  quit | exit             — Exit the chatbot
""".strip()


def _parse_file_command(text: str) -> tuple[str, str]:
    """Split a file command into (path, prompt).

    Handles both quoted and unquoted paths.
    """
    text = text.strip()

    if text.startswith('"'):
        end = text.index('"', 1)
        path = text[1:end]
        prompt = text[end + 1 :].strip()
    elif text.startswith("'"):
        end = text.index("'", 1)
        path = text[1:end]
        prompt = text[end + 1 :].strip()
    else:
        parts = text.split(maxsplit=1)
        path = parts[0]
        prompt = parts[1] if len(parts) > 1 else ""

    return path, prompt


def main() -> None:
    bot = MultimodalChatbot(api_key=settings.google_api_key)

    print("🤖 Chatbot ready! Type '/help' for commands or 'quit' to stop.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        try:
            if user_input.lower() == "/help":
                print(HELP_TEXT + "\n")
                continue

            if user_input.lower() == "/reset":
                bot.reset()
                print("🔄 Conversation history cleared.\n")
                continue

            if user_input.lower().startswith("/image "):
                path, prompt = _parse_file_command(user_input[7:])
                prompt = prompt or "Describe this image."
                reply = bot.send_image(path, prompt)

            elif user_input.lower().startswith("/pdf "):
                path, prompt = _parse_file_command(user_input[5:])
                prompt = prompt or "Describe this document."
                reply = bot.send_pdf(path, prompt)

            else:
                reply = bot.send_text(user_input)

            print(f"Bot: {reply}\n")

        except (FileNotFoundError, ValueError) as exc:
            print(f"⚠️  Error: {exc}\n")
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Unexpected error: {exc}\n")


if __name__ == "__main__":
    main()
