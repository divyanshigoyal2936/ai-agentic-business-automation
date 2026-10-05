from typing import TypedDict
import os
import json
from dotenv import load_dotenv  
from groq import Groq
from tools.customer_tools import find_customer_by_email
from tools.customer_tools import get_all_customers
from tools.customer_tools import find_customer_by_id
from langgraph.graph import StateGraph , END   
from tools.policy_tools import search_policies 
from tools.order_tools import check_refund_eligibility, process_refund

load_dotenv()
RISKY_TOOLS = ["process_refund"]
class AgentState(TypedDict):
    messages: list

def call_llm(state: AgentState):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    last_message = state["messages"][-1]
    if isinstance(last_message, dict) and last_message.get("role") == "tool":
        tool_choice_setting = "auto"
    else:
        tool_choice_setting = "required"

    response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=state["messages"],
    tool_choice=tool_choice_setting,
    
    tools = [
    {
        "type": "function",
        "function": {
            "name": "find_customer_by_email",
            "description": "Find a customer's details using their email address",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "The customer's email address"
                    }
                },
                "required": ["email"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "check_refund_eligibility",
        "description": "Check if a specific order is eligible for a refund based on the order ID and company refund policy",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "integer",
                    "description": "The order's unique ID"
                }
            },
            "required": ["order_id"]
        }
    }
},
     {
        "type": "function",
        "function": {
            "name": "find_customer_by_id",
            "description": "Find a customer's details using their ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The customer's ID"
                    }
                },
                "required": ["customer_id"]
            }
        }
    },
    {
    "type": "function",
    "function": {
        "name": "search_policies",
        "description": "Search company policies (delivery, refund, warranty) to answer policy-related questions",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The user's question about company policy"
                }
            },
            "required": ["question"]
        }
    }
},
     {
        "type": "function",
        "function": {
            "name": "get_all_customers",
            "description": "Retrieve a list of all customers",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "process_refund",
            "description": "Process an actual refund for a specific order after eligibility has been confirmed",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "The order's unique ID"
                    }
                },
                "required": ["order_id"]
            }
        }
    }
])  
    ai_message = response.choices[0].message
    return {"messages": state["messages"] + [ai_message]}

def call_tool(state: AgentState):
    last_message = state["messages"][-1]    
    tool_call = last_message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    if function_name in RISKY_TOOLS:
        print(f"\n⚠️  AI wants to call: {function_name}({function_args})")
        approval = input("Approve this action? (yes/no): ")

        if approval.lower() != "yes":
            tool_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps({"error": "Action was not approved by human reviewer"})
            }
            return {"messages": state["messages"] + [tool_message]}

    available_tools = {
    "find_customer_by_email": find_customer_by_email,
    "find_customer_by_id": find_customer_by_id,
    "get_all_customers": get_all_customers,
    "search_policies": search_policies,
    "check_refund_eligibility": check_refund_eligibility,
    "process_refund": process_refund
}       
    function_to_call = available_tools[function_name]
    if function_name == "get_all_customers":
        result = function_to_call()   
    else:         
        result = function_to_call(**function_args)

    tool_message = {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result, default=str)
    }       
    return {"messages": state["messages"] + [tool_message]}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return  "continue"
    return "stop"        
   
graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("tool", call_tool)
graph.set_entry_point("llm")
graph.add_conditional_edges("llm", should_continue, {"continue": "tool", "stop": END})

graph.add_edge("tool", "llm")
app = graph.compile()   
result = app.invoke({
    "messages": [
        {
            "role": "system",
            "content": "When a user asks you to perform an action like processing a refund, you must always call the corresponding tool to actually perform it. Never claim an action was completed unless you have called the tool and received its result. Only confirm completion after seeing the tool's actual output."
        },
        {
            "role": "user",
            "content": "Please process a refund for order 103."
        }
    ]
})
print(result["messages"][-1].content)