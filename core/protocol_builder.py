import os
import json
from typing import TypedDict, List
import google.generativeai as genai
from langgraph.graph import StateGraph, END

class ProtocolState(TypedDict):
    conversation_history: List
    protocol_params: dict
    template_code: str
    modified_code: str
    explanation: str
    error: str

def get_protocol_template(protocol_type: str) -> str:
    """Fetches the smart contract template from the file system."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, '..', 'protocol_templates', f'{protocol_type.capitalize()}.sol')
    try:
        with open(template_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "ERROR: Template not found."

class ProtocolBuilderAgent:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_parameters(self, state: ProtocolState):
        print("---AGENT: EXTRACTING PARAMETERS---")
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state['conversation_history']])

        prompt = f"""
        Analyze the user's request and extract the parameters for a smart contract.
        First, determine the 'protocol_type'. It must be one of: 'staking', 'token', 'vesting'.
        Then, extract the relevant parameters for that type:
        - For 'staking': 'staking_token_address', 'reward_token_address', 'apy_percent'.
        - For 'token': 'token_name', 'token_symbol', 'initial_supply'.
        - For 'vesting': 'token_address', 'beneficiary_address', 'vesting_duration_seconds', 'vesting_total_amount'.

        If any required parameter for a given type is missing, set its value to null.
        Respond ONLY with a single, minified JSON object.

        User Request:
        {history_text}
        """
        response = self.model.generate_content(prompt)
        try:
            cleaned_text = response.text.replace('```json', '').replace('```', '').strip()
            params = json.loads(cleaned_text)
            print(f"--- AI EXTRACTED PARAMS: {params} ---")
            state['protocol_params'] = params
        except (json.JSONDecodeError, AttributeError) as e:
            print(f"JSON Decode Error: {e}")
            state['error'] = "Failed to parse parameters."

        return state

    def select_template(self, state: ProtocolState):
        print("---AGENT: SELECTING TEMPLATE---")
        if state.get('error'): return state

        protocol_type = state['protocol_params'].get('protocol_type')

        print(f"--- AGENT IS LOOKING FOR TEMPLATE TYPE: '{protocol_type}' ---")
        # --- END ---

        if not protocol_type:
            state['error'] = "Protocol type could not be determined."
            return state
        
        template_code = get_protocol_template(str(protocol_type).lower())
        
        if "ERROR:" in template_code:
            state['error'] = template_code
        else:
            state['template_code'] = template_code
        
        return state

    def modify_code(self, state: ProtocolState):
        print("---AGENT: MODIFYING CODE---")
        if state.get('error'): return state
        
        params = state.get('protocol_params', {})
        protocol_type = params.get('protocol_type')
        final_prompt = ""

        if protocol_type == 'staking':
            required = ['staking_token_address', 'reward_token_address', 'apy_percent']
            if any(p not in params or not params.get(p) for p in required):
                state['error'] = "For a staking contract, I need two token addresses and an APY."
                return state
            
            apy = params.get('apy_percent', 0)
            reward_rate_per_second = int(((apy / 100) / 31536000) * 10**18)
            
            final_prompt = f"""
            You are a Solidity expert. Modify the provided Staking template.
            1. Replace the placeholder 'REWARD_RATE_PER_SECOND' with the value: {reward_rate_per_second}.
            2. In the constructor, replace the arguments with the actual addresses: `constructor() Ownable(msg.sender) {{ stakingToken = IERC20({params['staking_token_address']}); rewardToken = IERC20({params['reward_token_address']}); }}`.
            Respond ONLY with the full, final Solidity code.
            Template: ```solidity {state['template_code']} ```
            """

        elif protocol_type == 'token':
            required = ['token_name', 'token_symbol', 'initial_supply']
            if any(p not in params or not params.get(p) for p in required):
                state['error'] = "For a token, I need a name, symbol, and initial supply."
                return state
            
            final_prompt = f"""
            You are a Solidity expert. Modify the provided ERC20 Token template.
            In the constructor, replace the arguments `name`, `symbol`, and `initialSupply` with these concrete values:
            - name: "{params['token_name']}"
            - symbol: "{params['token_symbol']}"
            - initialSupply: {params['initial_supply']}
            Respond ONLY with the full, final Solidity code.
            Template: ```solidity {state['template_code']} ```
            """

        elif protocol_type == 'vesting':
            required = ['token_address', 'beneficiary_address', 'vesting_duration_seconds', 'vesting_total_amount']
            if any(p not in params or not params.get(p) for p in required):
                state['error'] = "For a vesting contract, I need a token address, beneficiary, duration, and total amount."
                return state

            final_prompt = f"""
            You are a Solidity expert. Modify the provided Vesting template.
            In the constructor, replace the arguments `tokenAddress`, `beneficiaryAddress`, `vestingDurationSeconds`, and `totalAmount` with these concrete values:
            - tokenAddress: {params['token_address']}
            - beneficiaryAddress: {params['beneficiary_address']}
            - vestingDurationSeconds: {params['vesting_duration_seconds']}
            - totalAmount: {params['vesting_total_amount']}
            Respond ONLY with the full, final Solidity code.
            Template: ```solidity {state['template_code']} ```
            """
        else:
            state['error'] = "Unknown protocol type for code modification."
            return state

        response = self.model.generate_content(final_prompt)
        cleaned_code = response.text.strip().replace('```solidity', '').replace('```', '').strip()
        state['modified_code'] = cleaned_code
        return state

        
    def generate_explanation(self, state: ProtocolState):
        print("---AGENT: GENERATING EXPLANATION---")
        if state.get('error'): return state

        prompt = f"Based on the following parameters, write a simple, one-paragraph explanation of what the generated staking protocol does for a beginner: {json.dumps(state['protocol_params'])}"
        response = self.model.generate_content(prompt)
        state['explanation'] = response.text
        return state

def get_protocol_builder_graph():
    """Compiles and returns the LangGraph agent."""
    agent = ProtocolBuilderAgent()
    
    graph = StateGraph(ProtocolState)
    graph.add_node("extract_parameters", agent.extract_parameters)
    graph.add_node("select_template", agent.select_template)
    graph.add_node("modify_code", agent.modify_code)
    graph.add_node("generate_explanation", agent.generate_explanation)

    graph.set_entry_point("extract_parameters")
    graph.add_edge("extract_parameters", "select_template")
    graph.add_edge("select_template", "modify_code")
    graph.add_edge("modify_code", "generate_explanation")
    graph.add_edge("generate_explanation", END)

    return graph.compile()