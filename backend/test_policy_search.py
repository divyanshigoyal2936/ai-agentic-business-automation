from tools.policy_tools import search_policies

print("=== ENGLISH TEST ===")
result1 = search_policies("How do I get my money back if I don't like the product?")
print(result1)

print("\n=== HINGLISH TEST ===")
result2 = search_policies("Agar mujhe product pasand nahi aaya toh paisa wapas kaise milega?")
print(result2)