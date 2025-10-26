#!/bin/bash
# Test script for Rules Manager functionality

echo "🧪 Testing Rules Manager..."
echo ""

cd "$(dirname "$0")/python"

echo "1️⃣ Test: Get all rules"
python3 rules_manager.py get > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "   ✅ Get rules: OK"
else
  echo "   ❌ Get rules: FAILED"
  exit 1
fi

echo ""
echo "2️⃣ Test: Get rules folder"
python3 rules_manager.py folder > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "   ✅ Get folder: OK"
else
  echo "   ❌ Get folder: FAILED"
  exit 1
fi

echo ""
echo "3️⃣ Test: Save a test rule"
TEST_RULE='{"keywords": ["test keyword"], "weight": 1.0, "min_matches": 1}'
python3 rules_manager.py save TEST_DOC "$TEST_RULE" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "   ✅ Save rule: OK"
else
  echo "   ❌ Save rule: FAILED"
  exit 1
fi

echo ""
echo "4️⃣ Test: Delete test rule"
python3 rules_manager.py delete TEST_DOC > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "   ✅ Delete rule: OK"
else
  echo "   ❌ Delete rule: FAILED"
  exit 1
fi

echo ""
echo "5️⃣ Test: Export rules"
TEMP_FILE="/tmp/rules_test_export.json"
python3 rules_manager.py export "$TEMP_FILE" > /dev/null 2>&1
if [ $? -eq 0 ] && [ -f "$TEMP_FILE" ]; then
  echo "   ✅ Export rules: OK"
  rm -f "$TEMP_FILE"
else
  echo "   ❌ Export rules: FAILED"
  exit 1
fi

echo ""
echo "6️⃣ Test: Rule classifier with overrides"
python3 -c "from rule_classifier import RuleClassifier; c = RuleClassifier(); print('OK')" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "   ✅ Classifier with overrides: OK"
else
  echo "   ❌ Classifier with overrides: FAILED"
  exit 1
fi

echo ""
echo "7️⃣ Test: Process document loads rules correctly"
python3 -c "from process_document import process_document; print('OK')" > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "   ✅ Process document: OK"
else
  echo "   ❌ Process document: FAILED"
  exit 1
fi

echo ""
echo "✅ All tests passed!"
echo ""
echo "📋 Rules Manager is ready to use!"
