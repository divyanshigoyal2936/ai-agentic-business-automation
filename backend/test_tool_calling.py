from tools.customer_tools import find_customer_by_email, get_all_customers, find_customer_by_id
import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
response = client.chat.completions.create(
    
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "user", "content": "Find customer with ID 18735"}
    ],

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
            "name": "get_all_customers",
            "description": "Retrieve a list of all customers",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
])
print(response.choices[0].message)
tool_call = response.choices[0].message.tool_calls[0]
function_name = tool_call.function.name
function_args = json.loads(tool_call.function.arguments)
print(function_name)
print(function_args)
available_tools = {
    "find_customer_by_email": find_customer_by_email,
    "find_customer_by_id": find_customer_by_id,
    "get_all_customers": get_all_customers,
    "search_policies": search_policies
}

function_to_call = available_tools[function_name]
if function_name == "get_all_customers":
    result = function_to_call()
else:
    result = function_to_call(**function_args)

print(result)