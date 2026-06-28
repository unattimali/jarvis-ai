from ollama import chat

while True:
    try:
        user = input("You: ").strip()

        if not user:
            print("Please type a question.")
            continue

        if user.lower() == "exit":
            break

        response = chat(
            model="llama3.2",
            messages=[
                {"role": "user", "content": user}
            ]
        )

        print("\nJarvis:", response["message"]["content"])

    except KeyboardInterrupt:
        print("\nProgram stopped.")
        break