import ollama


# 初始化带历史记忆的对话
def continuous_chat():
    history = [
        {"role": "system", "content": "对话需保持连贯，参考历史记录回答"}
    ]
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break
        history.append({"role": "user", "content": user_input})

        response = ollama.chat(
            model='gemma3:4b',
            messages=history,
            options={'temperature': 0.5}
        )
        print(f"AI: {response['message']['content']}")
        history.append({"role": "assistant", "content": response['message']['content']})
        print(history)


if __name__ == '__main__':
    continuous_chat()