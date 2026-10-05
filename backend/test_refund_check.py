from tools.order_tools import check_refund_eligibility

print("=== Test 1: Recent order (should be eligible) ===")
result1 = check_refund_eligibility(101)
print(result1)

print("\n=== Test 2: Old order (should NOT be eligible) ===")
result2 = check_refund_eligibility(102)
print(result2)

print("\n=== Test 3: Edge case order (6 days, should be eligible) ===")
result3 = check_refund_eligibility(103)
print(result3)

print("\n=== Test 4: Non-existent order ===")
result4 = check_refund_eligibility(999)
print(result4)