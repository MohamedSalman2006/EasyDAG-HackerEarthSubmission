import os
from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

load_dotenv()

SYSTEM_PROMPT = """
You are BlockDAGBot, an expert assistant in writing smart contracts based on blockDAG architecture focusing on it security.

You have access to the following tools. Use them wisely based on the user's intent:

generate_contract(details: str)
→ Use this when the user wants to create a new smart contract.
→ Supports multiple target environments:
    - BEVM (BlockDAG EVM, based on Go-Ethereum v1.14.11)
    - Kaspa DAG logic (Crescendo metadata logic)
    - Fantom/Avalanche C-Chain (EVM-compatible DAG chains)
→ Always ask for key functional requirements (e.g., token, staking, voting).

modify_contract(update_instruction: str)
→ Use this when the user wants to update, extend, or tweak the current contract.
→ Accepts natural-language instructions like “Add voting logic” or “Make mintable”.

Instructions:
- Be concise and clear in your messages.
- If the user doesn't specify a target chain, ask if they prefer BEVM, Fantom, or Kaspa.
- Always show the latest version of the contract (if one exists).
- If a contract was saved, end the conversation.
- Only respond to queries that are related to blockDAG or smart contract. Ignore other queries unrelated to crypto, blockchain, blockDAG or smart contracts. If query is unrelated, Respond ONLY with the following sentence: "I can only assist with Blockchain (specifically BDAG) related queries and tasks. How can I help you with that?"
- When the user asks to generate a new contract, call the `generate_contract` tool with the user's detailed requirements.
- When the user asks to modify an existing contract, you MUST look at the last message in the history to find the most recent contract code. You must then pass this *entire existing contract code* along with the user's new instructions to the `modify_contract` tool.
- If the user asks ANY question that is NOT about generating or modifying or general queries related to blockchain, blockdag and smart contracts, you MUST refuse to answer. Respond ONLY with the following sentence: "I can only assist with generating and modifying smart contracts. How can I help you with that?"

Current contract content:
{contract_content}
"""
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
def generate_contract(details: str) -> str:
    """Generates a smart contract using BEVM (BlockDAG EVM) or other target VMs."""
    global contract_content
    summary = details.lower()

    if "bevm" in summary:
        # BEVM (Go-Ethereum v1.14.11) EVM-compatible contract
        contract_content = f"""// BEVM Smart Contract (Go-Ethereum v1.14.11)
// Details: {details}

pragma solidity ^0.8.0;

// BEVM-specific optimizations or pragmas could go here
// e.g., chain-specific metadata or gas tweaks

contract BEVMDApp {{
    uint256 public counter;

    event Incremented(address indexed user, uint256 newValue);

    function increment() external {{
        counter++;
        emit Incremented(msg.sender, counter);
    }}

    function getCounter() external view returns (uint256) {{
        return counter;
    }}
}}
"""
        return f"BEVM contract generated:\n{contract_content}"
    else:
        contract_content = f"// Default Solidity contract\n// Details: {details}\npragma solidity ^0.8.0;\ncontract DefaultContract {{}}"
        return f"Default contract generated:\n{contract_content}"

@tool
def modify_contract(existing_content: str, update_instruction: str) -> str:
    """Modifies an existing smart contract with new instructions."""
    print(f"--- TOOL: Modifying contract with instruction: {update_instruction} ---")
    modified_content = f"{existing_content}\n\n// Change based on: {update_instruction}"
    return f"I have modified the contract as you requested. Here is the updated code:\n\n```solidity\n{modified_content}\n```"


tools = [generate_contract, modify_contract]

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY")
)
model_with_tools = model.bind_tools(tools)

def gemini_agent(state: AgentState) -> dict:
    """Invokes the model to decide on the next step."""
    print("---AGENT: Invoking model---")
    messages_with_system_prompt = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = model_with_tools.invoke(messages_with_system_prompt)
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """Determines whether to continue to a tool or end the conversation."""
    last_message = state['messages'][-1]
    if not last_message.tool_calls:
        return "end"
    return "continue"

graph = StateGraph(AgentState)
graph.add_node("agent", gemini_agent)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
graph.add_edge("tools", "agent")

app = graph.compile()