from chatbot.config import settings
from chatbot.multimodal import MultimodalChatbot
from chatbot.prompt_store import (
    delete_prompt,
    get_active_prompt,
    list_prompt_names,
    save_prompt,
)

HELP_TEXT = """
Commands:
  /image   <path> [prompt]  — Send an image file (png, jpg, gif, webp, bmp)
  /pdf     <path> [prompt]  — Send a PDF file
  /system  [prompt]         — Show or set the system prompt
  /save    <name>           — Save current system prompt with a name
  /load    <name>           — Load a saved system prompt by name
  /list                     — List all saved system prompts
  /delete  <name>           — Delete a saved system prompt
  /reset                    — Clear conversation history
  /help                     — Show this help message
  quit | exit               — Exit the chatbot
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
    # Load the last-used system prompt from sys_prompt.json
    active_name, active_text = get_active_prompt()
    bot = MultimodalChatbot(api_key=settings.google_api_key, system_prompt=active_text)

    print(f'🤖 Chatbot ready! Active prompt: "{active_name}"')
    print("   Type '/help' for commands or 'quit' to stop.\n")

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

            if user_input.lower() == "/system":
                print(f"📝 Current system prompt:\n{bot.system_prompt}\n")
                continue

            if user_input.lower().startswith("/system "):
                new_prompt = user_input[8:].strip()
                if new_prompt:
                    bot.set_system_prompt(new_prompt)
                    print("✅ System prompt updated. History cleared.\n")
                else:
                    print(f"📝 Current system prompt:\n{bot.system_prompt}\n")
                continue

            if user_input.lower().startswith("/save "):
                name = user_input[6:].strip()
                if name:
                    save_prompt(name, bot.system_prompt)
                    print(f'💾 Saved prompt as "{name}".\n')
                else:
                    print("⚠️  Usage: /save <name>\n")
                continue

            if user_input.lower() == "/list":
                names = list_prompt_names()
                _, current_name = get_active_prompt()
                print("📋 Saved prompts:")
                for n in names:
                    marker = " ← active" if n == active_name else ""
                    print(f"  • {n}{marker}")
                print()
                continue

            if user_input.lower().startswith("/load "):
                name = user_input[6:].strip()
                names = list_prompt_names()
                if name in names:
                    from chatbot.prompt_store import load_prompts

                    store = load_prompts()
                    text = store["prompts"][name]
                    bot.set_system_prompt(text)
                    store["active"] = name
                    from chatbot.prompt_store import save_prompts

                    save_prompts(store)
                    active_name = name
                    print(f'✅ Loaded prompt "{name}". History cleared.\n')
                else:
                    print(
                        f'⚠️  No prompt named "{name}". Use /list to see available prompts.\n'
                    )
                continue

            if user_input.lower().startswith("/delete "):
                name = user_input[8:].strip()
                names = list_prompt_names()
                if name not in names:
                    print(f'⚠️  No prompt named "{name}".\n')
                elif len(names) == 1:
                    print("⚠️  Cannot delete the last prompt.\n")
                else:
                    delete_prompt(name)
                    print(f'🗑️  Deleted prompt "{name}".\n')
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
