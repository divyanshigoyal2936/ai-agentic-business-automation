import os,json,datetime
from groq import Groq
from dotenv import load_dotenv
from tools.customer_tools import find_customer_by_email,find_customer_by_id,get_all_customers
from tools.policy_tools import search_policies
from tools.order_tools import check_refund_eligibility,process_refund
from core.database import audit_logs_collection

load_dotenv()
MODEL="openai/gpt-oss-120b"
RISKY=["process_refund"]
TOOLS={"find_customer_by_email":find_customer_by_email,"find_customer_by_id":find_customer_by_id,"get_all_customers":get_all_customers,"search_policies":search_policies,"check_refund_eligibility":check_refund_eligibility,"process_refund":process_refund}

def log_action(email,role,action,args,result,approved=None):
    audit_logs_collection.insert_one({"timestamp":datetime.datetime.now(),"user_email":email,"user_role":role,"action":action,"arguments":args,"result":result,"approved":approved})

def run_agent(client,tools_schema,message,role,email):
    messages=[{"role":"user","content":message}]
    while True:
        r=client.chat.completions.create(model=MODEL,messages=messages,tools=tools_schema)
        ai=r.choices[0].message
        messages.append(ai)
        if not ai.tool_calls:return ai.content
        call=ai.tool_calls[0]
        name=call.function.name
        args=json.loads(call.function.arguments)
        approved=None
        if name in RISKY:
            if role!="manager":
                result={"error":"Permission denied: only managers can perform this action"};approved=False
            else:
                print(f"\nAI wants to call: {name}({args})")
                if input("Approve this action? (yes/no): ").lower()!="yes":
                    result={"error":"Action was not approved by human reviewer"};approved=False
                else:
                    result=TOOLS[name](**args);approved=True
        elif name=="get_all_customers":result=TOOLS[name]()
        else:result=TOOLS[name](**args)
        log_action(email,role,name,args,result,approved)
        messages.append({"role":"tool","tool_call_id":call.id,"content":json.dumps(result,default=str)})

def customer_agent(message,role,email):
    client=Groq(api_key=os.getenv("GROQ_API_KEY"))
    schema=[
        {"type":"function","function":{"name":"find_customer_by_email","description":"Find customer details using email","parameters":{"type":"object","properties":{"email":{"type":"string"}},"required":["email"]}}},
        {"type":"function","function":{"name":"find_customer_by_id","description":"Find customer details using ID","parameters":{"type":"object","properties":{"customer_id":{"type":"integer"}},"required":["customer_id"]}}},
        {"type":"function","function":{"name":"get_all_customers","description":"Retrieve all customers","parameters":{"type":"object","properties":{}}}}
    ]
    return run_agent(client,schema,message,role,email)

def policy_agent(message,role,email):
    client=Groq(api_key=os.getenv("GROQ_API_KEY"))
    schema=[{"type":"function","function":{"name":"search_policies","description":"Search company policies such as delivery, refund and warranty","parameters":{"type":"object","properties":{"question":{"type":"string"}},"required":["question"]}}}]
    return run_agent(client,schema,message,role,email)

def refund_agent(message,role,email):
    client=Groq(api_key=os.getenv("GROQ_API_KEY"))
    schema=[
        {"type":"function","function":{"name":"check_refund_eligibility","description":"Check refund eligibility for an order","parameters":{"type":"object","properties":{"order_id":{"type":"integer"}},"required":["order_id"]}}},
        {"type":"function","function":{"name":"process_refund","description":"Process refund for an order after eligibility is confirmed","parameters":{"type":"object","properties":{"order_id":{"type":"integer"}},"required":["order_id"]}}}
    ]
    return run_agent(client,schema,message,role,email)

def classify_category(user_message):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    system_prompt = """You are a router. Based on the user's message, decide which category it belongs to.
Reply with ONLY one word: "customer", "policy", or "refund".

- "customer" if the question is about finding or listing customer details.
- "policy" if the question is about company policies (delivery, refund rules, warranty).
- "refund" if the question is about checking eligibility or processing an actual refund for an order.
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content.strip().lower()


def orchestrator(user_message, role, email):
    category = classify_category(user_message)

    if category == "customer":
        return customer_agent(user_message, role, email)
    elif category == "policy":
        return policy_agent(user_message, role, email)
    elif category == "refund":
        return refund_agent(user_message, role, email)
    else:
        return "Sorry, I couldn't understand which department this belongs to."
