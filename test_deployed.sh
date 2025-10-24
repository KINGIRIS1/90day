#!/bin/bash

# Test script for deployed app
DEPLOYED_URL="https://imagescan-3.emergent.host"

echo "=== Testing Deployed App: $DEPLOYED_URL ==="
echo ""

# Test 1: Health check
echo "1. Testing health check..."
curl -s -w "\nHTTP Status: %{http_code}\n" "$DEPLOYED_URL/api/rules" | head -5
echo ""

# Test 2: Login (you'll need to run this manually with real credentials)
echo "2. To test scanning, first login:"
echo "   curl -X POST $DEPLOYED_URL/api/auth/login \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"username\":\"admin\",\"password\":\"Thommit@19\"}'"
echo ""

echo "3. Then scan with token:"
echo "   TOKEN=<your_token_here>"
echo "   curl -X POST $DEPLOYED_URL/api/batch-scan \\"
echo "     -H 'Authorization: Bearer \$TOKEN' \\"
echo "     -F 'files=@test_image.jpg'"
echo ""

echo "=== Configuration Applied ==="
echo "- MAX_CONCURRENT_SCANS reduced to 2 (from 5)"
echo "- Both batch-scan and folder-scan use this setting"
echo "- This will reduce memory usage and avoid timeouts"
echo ""
echo "=== Next Steps ==="
echo "1. Deploy this code to production"
echo "2. Set MAX_CONCURRENT_SCANS=2 in deployed environment"
echo "3. Test with SMALL file first (1-2 images)"
echo "4. Then test with larger batches"
