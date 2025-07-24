from .models import Conversation, Message, User
import google.generativeai as genai
import os
import traceback
from .protocol_builder import get_protocol_builder_graph

def run_protocol_agent(user: User, new_prompt: str):
    """Invokes the specialized, template-based protocol builder."""
    print("---SERVICE: RUNNING PROTOCOL BUILDER---")
    conversation, _ = Conversation.objects.get_or_create(user=user)
    Message.objects.create(conversation=conversation, role='user', content=new_prompt)
    
    db_messages = conversation.messages.all().order_by('created_at')
    history_for_agent = [{"role": msg.role, "content": msg.content} for msg in db_messages]

    try:
        agent = get_protocol_builder_graph()
        initial_state = {"conversation_history": history_for_agent}
        final_state = agent.invoke(initial_state)

        if not final_state.get('error'):
            agent_response_content = final_state.get('explanation', 'Protocol generated successfully.')
            Message.objects.create(conversation=conversation, role='model', content=agent_response_content)
        else:
            Message.objects.create(conversation=conversation, role='model', content=final_state['error'])
        
        return final_state
    except Exception as e:
        traceback.print_exc()
        return {"error": f"Error during protocol agent execution: {str(e)}"}

def run_simple_chat(user: User, new_prompt: str):
    """Handles simple, conversational requests with a single, fast API call."""
    print("---SERVICE: RUNNING SIMPLE CONVERSATIONAL CHAT---")
    conversation, _ = Conversation.objects.get_or_create(user=user)
    db_messages = conversation.messages.order_by('created_at').all()[:20] 
    history_for_api = []
    for msg in db_messages:
        history_for_api.append({'role': msg.role, 'parts': [msg.content]})

    Message.objects.create(conversation=conversation, role='user', content=new_prompt)

    system_prompt = """
    You are EasyDAG Assistant, a specialist AI with expertise in BlockDAG technology.

    Your primary purpose is to:
    1.  Answer user questions about BlockDAG concepts (e.g., "What is a DAG?", "How is it different from a blockchain?").
    2.  Explain the features and benefits of the blockdag coin.
    3.  Guide users on how to get started with building on BlockDAG.

    CRITICAL INSTRUCTIONS:
    - You are a conversational guide, NOT a code generator.
    - If a user asks you to create, write, or modify a smart contract, you MUST instruct them to switch to the "Protocol Builder" mode to use the specialized tool for that task but you can verify the robustness of contracts and clear any queries users might have regarding it.
    - Keep your answers concise and easy for beginners to understand.
    """
    
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
        chat_session = model.start_chat(history=history_for_api)
        response = chat_session.send_message(new_prompt)
        
        agent_response_content = response.text
        Message.objects.create(conversation=conversation, role='model', content=agent_response_content)
        return {"success": True, "response": agent_response_content}
    except Exception as e:
        traceback.print_exc()
        return {"error": f"Error during conversational chat: {str(e)}"}

def run_simple_chat_stateless(prompt: str, history: list):
    """
    Runs the conversational chat without a user model or database.
    Accepts history directly from the frontend.
    """
    print("---SERVICE: RUNNING STATELESS GUEST CHAT---")
    
    system_prompt = """
    You are EasyDAG Assistant, a specialist AI with expertise in BlockDAG technology.
    Your primary purpose is to have a conversation and answer user questions.
    CRITICAL INSTRUCTIONS:
    - You are a conversational guide, NOT a code generator.
    - If a user asks to create a smart contract, instruct them to log in with MetaMask to use the "Protocol Builder" mode.
    """
    
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
        
        history_for_api = []
        for msg in history:
            history_for_api.append({'role': msg.get('role'), 'parts': [msg.get('content')]})
        chat_session = model.start_chat(history=history_for_api)
        response = chat_session.send_message(prompt)
        return {"success": True, "response": response.text}
        
    except Exception as e:
        traceback.print_exc()
        return {"error": f"Error during guest chat: {str(e)}"}
    
def run_protocol_agent_stateless(prompt: str, history: list):
    """
    Runs the protocol builder agent without a user model or database.
    Accepts history directly from the frontend.
    """
    print("---SERVICE: RUNNING STATELESS PROTOCOL BUILDER---")
    try:
        agent = get_protocol_builder_graph()
        history_for_agent = history + [{"role": "user", "content": prompt}]
        initial_state = {"conversation_history": history_for_agent}
        final_state = agent.invoke(initial_state)
        return final_state
    except Exception as e:
        traceback.print_exc()
        return {"error": f"Error during stateless protocol agent: {str(e)}"}