with open("company_policies.txt", "r", encoding="utf-8") as file:
    policies = file.read()
chunks = policies.split("\n\n")  # Split policies into chunks based on double newlines
print(len(chunks))  # Print the number of policy chunks

for i, chunk in enumerate(chunks):
    print(f"----Policy Chunk {i+1}-----")
    print(chunk)
    print()