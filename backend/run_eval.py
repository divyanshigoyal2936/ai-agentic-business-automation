from agents import classify_category
from eval_tests import TEST_CASES

passed = 0
failed = 0

for test in TEST_CASES:
    actual_category = classify_category(test["question"])
    expected_category = test["expected_category"]

    if actual_category == expected_category:
        passed += 1
        print(f"✅ PASS: '{test['question']}' -> {actual_category}")
    else:
        failed += 1
        print(f"❌ FAIL: '{test['question']}' -> got '{actual_category}', expected '{expected_category}'")

total = passed + failed
accuracy = (passed / total) * 100

print(f"\n--- Results ---")
print(f"Passed: {passed}/{total}")
print(f"Accuracy: {accuracy:.1f}%")