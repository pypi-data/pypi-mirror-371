import os
from typing import Dict, TypedDict, Any, List
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import tiktoken
from langchain_chroma import Chroma
from antishlopcli.config import get_validated_api_key

from antishlopcli.prompts import (
    planner_prompt,
    static_vulnerability_scanner_prompt,
    secrets_detector_prompt,
    dependency_vulnerability_checker_prompt,
    auth_analyzer_prompt,
    input_validation_analyzer_prompt,
    crypto_analyzer_prompt,
    data_security_analyzer_prompt,
    config_security_checker_prompt,
    business_logic_analyzer_prompt,
    error_handling_analyzer_prompt,
    code_quality_security_prompt,
    infrastructure_security_prompt,
    api_security_analyzer_prompt,
    filesystem_security_prompt,
    concurrency_analyzer_prompt,
    speculative_execution_prompt,
    quantum_safe_crypto_prompt,
    ai_ml_security_prompt,
    supply_chain_security_prompt,
    cloud_misconfiguration_prompt,
    tocttou_concurrency_prompt,
    iot_firmware_security_prompt,
    business_logic_abuse_prompt,
    reflection_prompt,
    summation_prompt
)

load_dotenv()

# Initialize LLM with validated API key
api_key = get_validated_api_key()
llm = ChatOpenAI(api_key=api_key, model='gpt-4.1', temperature=0, top_p=0)

# Token counter
try:
    encoding = tiktoken.encoding_for_model("gpt-4")
except:
    encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    if not text:
        return 0
    return len(encoding.encode(str(text)))

class State(TypedDict):

    context: list[str]
    file_content: str
    plan: str
    selected_tools: list[str]
    reflection: bool
    final_report: str
    tool_trace: list[str]
    reflection_reason: str
    vulnerabilities: list[dict]
    complete: str
    tokens_used: int

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

import json
import re

def parse_reflection_response(response: str) -> dict:
    """
    Parse reflection agent response and extract decision
    
    Args:
        response: Raw text response from reflection agent
        
    Returns:
        Dict with 'continue_analysis' (bool) and 'reason' (str)
    """
    # Try to extract JSON block first
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL | re.IGNORECASE)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Fallback: extract fields individually
    continue_match = re.search(r'"continue_analysis":\s*(true|false)', response, re.IGNORECASE)
    reason_match = re.search(r'"reason":\s*"([^"]*)"', response, re.DOTALL)
    
    if continue_match:
        return {
            "continue_analysis": continue_match.group(1).lower() == "true",
            "reason": reason_match.group(1) if reason_match else ""
        }
    
    # Default if parsing fails
    return {"continue_analysis": False, "reason": "Failed to parse response"}


def parse_planner_response(response_content: str) -> Dict[str, Any]:
    """Parser for planner agent response"""
    try:
        # Try to extract JSON from the response
        content = response_content.strip()
        
        # If response contains ```json blocks, extract them
        if '```json' in content:
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
        
        planner_result = json.loads(content)
        
        # Validate required fields
        if not isinstance(planner_result, dict):
            print(f"Warning: Expected dict, got {type(planner_result)}")
            return {"selected_tools": [], "plan": ""}
        
        # Check for required fields
        if "selected_tools" not in planner_result:
            print("Warning: Missing 'selected_tools' field in planner response")
            planner_result["selected_tools"] = []
            
        if "plan" not in planner_result:
            print("Warning: Missing 'plan' field in planner response")
            planner_result["plan"] = ""
        
        # Validate selected_tools is a list
        if not isinstance(planner_result["selected_tools"], list):
            print(f"Warning: selected_tools should be list, got {type(planner_result['selected_tools'])}")
            planner_result["selected_tools"] = []
        
        # Validate plan is a string
        if not isinstance(planner_result["plan"], str):
            print(f"Warning: plan should be string, got {type(planner_result['plan'])}")
            planner_result["plan"] = str(planner_result["plan"])
        
        return planner_result
        
    except json.JSONDecodeError as e:
        print(f"Error parsing planner JSON response: {e}")
        print(f"Response content: {response_content[:200]}")
        # Return default tools to at least scan something
        return {
            "selected_tools": ["static_vulnerability_scanner", "secrets_detector"], 
            "plan": "Basic security scan"
        }


def parse_security_tool_response(response_content: str, tool_name: str = "") -> List[Dict[str, Any]]:
    """Generic parser for all security tool responses"""
    try:
        if not response_content or response_content.strip() == "":
            return []
        
        content = response_content.strip()
        
        # Extract JSON from markdown code blocks if present
        if '```json' in content:
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
        elif '```' in content:
            import re
            json_match = re.search(r'```\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
        vulnerabilities = json.loads(content)
        
        if not isinstance(vulnerabilities, list):
            return []
        
        if len(vulnerabilities) > 0:
            print(f"{tool_name}: Found {len(vulnerabilities)} potential vulnerabilities")
        
        return vulnerabilities
        
    except json.JSONDecodeError:
        return []

def static_vulnerability_scanner(state, token_callback=None):
    
    formatted_prompt = static_vulnerability_scanner_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"static_vulnerability_scanner")

    state['vulnerabilities'].extend(vulns)

    return state


def secrets_detector(state, token_callback=None):
    
    formatted_prompt = secrets_detector_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"secrets_detector")

    state['vulnerabilities'].extend(vulns)
    
    return state

def dependency_vulnerability_checker(state, token_callback=None):
    
    formatted_prompt = dependency_vulnerability_checker_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"dependency_vulnerability_checker")

    state['vulnerabilities'].extend(vulns)
    
    return state

def auth_analyzer(state, token_callback=None):
    
    formatted_prompt = auth_analyzer_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"auth_analyzer")

    state['vulnerabilities'].extend(vulns)
    
    return state

def input_validation_analyzer(state, token_callback=None):
    
    formatted_prompt = input_validation_analyzer_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"input_validation_analyzer")

    state['vulnerabilities'].extend(vulns)
    
    return state

def crypto_analyzer(state, token_callback=None):
    
    formatted_prompt = crypto_analyzer_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"crypto_analyzer")

    state['vulnerabilities'].extend(vulns)
    
    return state

def data_security_analyzer(state, token_callback=None):
    
    formatted_prompt = data_security_analyzer_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"data_security_analyzer")

    state['vulnerabilities'].extend(vulns)
    
    return state

def config_security_checker(state, token_callback=None):
    
    formatted_prompt = config_security_checker_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"config_security_checker")

    state['vulnerabilities'].extend(vulns)
    
    return state

def business_logic_analyzer(state, token_callback=None):
    
    formatted_prompt = business_logic_analyzer_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"business_logic_analyzer")

    state['vulnerabilities'].extend(vulns)
    
    return state

def error_handling_analyzer(state, token_callback=None):
    
    formatted_prompt = error_handling_analyzer_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"error_handling_analyzer")

    state['vulnerabilities'].extend(vulns)
    
    return state

def code_quality_security(state, token_callback=None):
    
    formatted_prompt = code_quality_security_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"code_quality_security")

    state['vulnerabilities'].extend(vulns)
    
    return state

def infrastructure_security(state, token_callback=None):
    
    formatted_prompt = infrastructure_security_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"infrastructure_security")

    state['vulnerabilities'].extend(vulns)
    
    return state

def api_security_analyzer(state, token_callback=None):
    
    formatted_prompt = api_security_analyzer_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"api_security_analyzer")

    state['vulnerabilities'].extend(vulns)
    
    return state

def filesystem_security(state, token_callback=None):
    
    formatted_prompt = filesystem_security_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"filesystem_security")

    state['vulnerabilities'].extend(vulns)
    
    return state

def concurrency_analyzer(state, token_callback=None):
    
    formatted_prompt = concurrency_analyzer_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"concurrency_analyzer")

    state['vulnerabilities'].extend(vulns)
    
    return state

def speculative_execution(state, token_callback=None):
    
    formatted_prompt = speculative_execution_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"speculative_execution")

    state['vulnerabilities'].extend(vulns)
    
    return state

def quantum_safe_crypto(state, token_callback=None):
    
    formatted_prompt = quantum_safe_crypto_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"quantum_safe_crypto")

    state['vulnerabilities'].extend(vulns)
    
    return state

def ai_ml_security(state, token_callback=None):
    
    formatted_prompt = ai_ml_security_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"ai_ml_security")

    state['vulnerabilities'].extend(vulns)
    
    return state

def supply_chain_security(state, token_callback=None):
    
    formatted_prompt = supply_chain_security_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"supply_chain_security")

    state['vulnerabilities'].extend(vulns)
    
    return state

def cloud_misconfiguration(state, token_callback=None):
    
    formatted_prompt = cloud_misconfiguration_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"cloud_misconfiguration")

    state['vulnerabilities'].extend(vulns)
    
    return state

def tocttou_concurrency(state, token_callback=None):
    
    formatted_prompt = tocttou_concurrency_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"tocttou_concurrency")

    state['vulnerabilities'].extend(vulns)
    
    return state

def iot_firmware_security(state, token_callback=None):
    
    formatted_prompt = iot_firmware_security_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"iot_firmware_security")

    state['vulnerabilities'].extend(vulns)
    
    return state

def business_logic_abuse(state, token_callback=None):
    
    formatted_prompt = business_logic_abuse_prompt.format(context=state['context'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])
    
    vulns = parse_security_tool_response(response.content.strip(),"business_logic_abuse")

    state['vulnerabilities'].extend(vulns)
    
    return state

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



def context_node(codebase_path):
    """Vectorize the entire codebase once"""
    import shutil
    from antishlopcli.vector_db import store_codebase
    
    # Clean up old vector database first
    if os.path.exists("chroma_db"):
        shutil.rmtree("chroma_db")
    
    if codebase_path and os.path.exists(codebase_path):
        store_codebase(codebase_path, "chroma_db")
        return True
    return False

def get_context(state):
    """Retrieve relevant context for current file"""
    if os.path.exists("chroma_db"):
        vector_store = Chroma(persist_directory="chroma_db", embedding_function=OpenAIEmbeddings())
        
        # Query for where this file's content is used elsewhere
        query = f"usage of functions classes variables from:\n{state['file_content'][:500]}"
        similar_docs = vector_store.similarity_search(query, k=5)
        
        # Add context from similar files
        context_info = []
        for doc in similar_docs:
            file_path = doc.metadata.get('file_path', 'unknown')
            context_info.append(f"File: {file_path}\nContent: {doc.page_content[:300]}...")
        
        state['context'] = context_info
    else:
        state['context'] = []
    
    return state

def planner_node(state, token_callback=None):
    
    # Format the prompt template
    formatted_prompt = planner_prompt.format(
        context=state['context'], 
        reason=state['reflection_reason'], 
        tool_trace=state['tool_trace'], 
        reflection=state['reflection'], 
        file_content=state['file_content']
    )
    
    # Count input tokens
    input_tokens = count_tokens(formatted_prompt)
    state['tokens_used'] += input_tokens
    
    response = llm.invoke(formatted_prompt)
    
    # Count output tokens
    output_tokens = count_tokens(response.content)
    state['tokens_used'] += output_tokens
    
    if token_callback:
        token_callback(state['tokens_used'])

    output = parse_planner_response(response.content.strip())
    state['selected_tools'] = output['selected_tools']
    state['plan'] = output['plan']

    state['reflection'] = False

    return state


def execute_node(state, token_callback=None):
    
    tool_functions = {
        "static_vulnerability_scanner": static_vulnerability_scanner,
        "secrets_detector": secrets_detector,
        "dependency_vulnerability_checker": dependency_vulnerability_checker,
        "auth_analyzer": auth_analyzer,
        "input_validation_analyzer": input_validation_analyzer,
        "crypto_analyzer": crypto_analyzer,
        "data_security_analyzer": data_security_analyzer,
        "config_security_checker": config_security_checker,
        "business_logic_analyzer": business_logic_analyzer,
        "error_handling_analyzer": error_handling_analyzer,
        "code_quality_security": code_quality_security,
        "infrastructure_security": infrastructure_security,
        "api_security_analyzer": api_security_analyzer,
        "filesystem_security": filesystem_security,
        "concurrency_analyzer": concurrency_analyzer,
        "speculative_execution": speculative_execution,
        "quantum_safe_crypto": quantum_safe_crypto,
        "ai_ml_security": ai_ml_security,
        "supply_chain_security": supply_chain_security,
        "cloud_misconfiguration": cloud_misconfiguration,
        "tocttou_concurrency": tocttou_concurrency,
        "iot_firmware_security": iot_firmware_security,
        "business_logic_abuse": business_logic_abuse
    }
    
    
    for tool_name in state['selected_tools']:
        if tool_name in tool_functions:
        
            state = tool_functions[tool_name](state, token_callback)
            state['tool_trace'].append(tool_name)
        else:
            print(f"Warning: Unknown tool '{tool_name}'")
    
    return state
    
def reflection_node(state, token_callback=None):
    
    formatted_prompt = reflection_prompt.format(current_findings=state['vulnerabilities'], context=state['context'], tool_trace=state['tool_trace'], file_content=state['file_content'])
    state['tokens_used'] += count_tokens(formatted_prompt)
    response = llm.invoke(formatted_prompt)
    state['tokens_used'] += count_tokens(response.content)
    
    if token_callback:
        token_callback(state['tokens_used'])

    output = parse_reflection_response(response.content.strip())

    if output['continue_analysis']:
        state['reflection'] = True
        state['reflection_reason'] = output['reason']
        state['selected_tools'] = []
        state['plan'] = ""

        return state
    else:
        return state
    
    


def summation_node(state):
    
    # If no vulnerabilities, return simple message
    if not state['vulnerabilities']:
        state['final_report'] = "No security vulnerabilities detected in this file."
        return state
    
    # Create a simple summary without calling LLM again
    report = f"Found {len(state['vulnerabilities'])} security vulnerabilities:\n\n"
    
    for vuln in state['vulnerabilities']:
        if isinstance(vuln, dict):
            report += f"• {vuln.get('vulnerability_type', 'Unknown')} (Severity: {vuln.get('severity', 'Unknown')})\n"
            report += f"  Line {vuln.get('line_number', 'Unknown')}: {vuln.get('description', 'No description')}\n"
            report += f"  Fix: {vuln.get('remediation', 'No remediation provided')}\n\n"
    
    state['final_report'] = report

    return state

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def Agent(file_content, token_callback=None, status_callback=None):
    
    state = State()
    state['file_content'] = file_content
    state['plan'] = ""
    state['selected_tools'] = []
    state['reflection'] = False
    state['final_report'] = ""
    state['tool_trace'] = []
    state['reflection_reason'] = "Initial analysis required"
    state['vulnerabilities'] = []
    state['complete'] = ""
    state['tokens_used'] = 0

    state = get_context(state)

    max_iterations = 3
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1

        state = planner_node(state, token_callback)

        state = execute_node(state, token_callback)

        state = reflection_node(state, token_callback)

        if not state['reflection']:
            break
        else:
            # Notify user that agent is doing deeper analysis
            if status_callback:
                status_callback(f"iteration_{iteration + 1}")

    state = summation_node(state)
    state['complete'] = "Analysis complete"
    
    return state['final_report'], state['tokens_used']

