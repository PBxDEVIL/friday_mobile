import openai
import json
import config
from tools_mobile import available_functions
from memory_mobile import get_relevant_errors, get_user_profile

openai.api_key = config.OPENAI_API_KEY

SYSTEM_PROMPT = """
You are FRIDAY, a mobile AI assistant based on Iron Man's tech. You are helpful, concise, and learn from your mistakes.
You have tools: web_search, execute_python (safe), send_email, stock_price.
Use them when appropriate. If a tool fails, note it and try an alternative.
User profile: {profile}
Relevant past errors: {errors}
"""

def get_tool_definitions():
    return [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web.",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_python",
                "description": "Run a safe Python snippet.",
                "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "send_email",
                "description": "Send an email.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"}
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "stock_price",
                "description": "Get current stock price.",
                "parameters": {"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}
            }
        }
    ]

def chat(messages):
    profile = get_user_profile()
    errors = get_relevant_errors(messages[-1]["content"] if messages else "")
    error_text = "\n".join([f"- {e['context']}: corrected to {e['correction']}" for e in errors]) if errors else "None"
    system_msg = SYSTEM_PROMPT.format(profile=profile, errors=error_text)
    full_messages = [{"role": "system", "content": system_msg}] + messages[-10:]  # keep short context
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # cheaper, fast
        messages=full_messages,
        tools=get_tool_definitions(),
        tool_choice="auto"
    )
    msg = response.choices[0].message
    if msg.tool_calls:
        messages.append(msg)
        for tool_call in msg.tool_calls:
            fname = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            print(f"Calling {fname} with {args}")
            result = available_functions[fname](**args)
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "name": fname, "content": str(result)})
        # Recursively call to get final answer
        return chat(messages)
    return msg.content
