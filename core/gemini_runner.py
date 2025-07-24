from .smart_contract_generator import model, SYSTEM_PROMPT

chat_session = model.start_chat(history=[
    { "role": "user", "parts": [SYSTEM_PROMPT] }
])

def generate_contract_response(history: list) -> str:
    for message in history:
        if message["role"] == "user":
            chat_session.history.append({ "role": "user", "parts": [message["content"]] })
        elif message["role"] == "model":
            chat_session.history.append({ "role": "model", "parts": [message["content"]] })

    last_user_message = next((m["content"] for m in reversed(history) if m["role"] == "user"), None)
    if not last_user_message:
        return "No user message found."

    response = chat_session.send_message(last_user_message)

    return response.text
