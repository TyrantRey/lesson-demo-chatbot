from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from chatbot.config import settings


def main() -> None:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
    )

    system_message = SystemMessage(
        content="You are a friendly and helpful AI assistant. Keep your answers concise."
    )
    history: list[SystemMessage | HumanMessage | AIMessage] = [system_message]

    print("🤖 Chatbot ready! Type 'quit' or 'exit' to stop.\n")

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

        history.append(HumanMessage(content=user_input))

        response = llm.invoke(history)
        assistant_text = response.content
        history.append(AIMessage(content=assistant_text))

        print(f"Bot: {assistant_text}\n")


if __name__ == "__main__":
    main()
