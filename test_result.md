#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
# ## user_problem_statement: {problem_statement}
# ## backend:
# ##   - task: "Task name"
# ##     implemented: true
# ##     working: true  # or false or "NA"
# ##     file: "file_path.py"
# ##     stuck_count: 0
# ##     priority: "high"
# ##     needs_retesting: false
# ##     status_history:
# ##         -working: true  # or false or "NA"
# ##         -agent: "main"  # or "testing" or "user"
# ##         -comment: "Detailed comment about status"
# ##
# ## frontend:
# ##   - task: "Task name"
# ##     implemented: true
# ##     working: true  # or false or "NA"
# ##     file: "file_path.js"
# ##     stuck_count: 0
# ##     priority: "high"
# ##     needs_retesting: false
# ##     status_history:
# ##         -working: true  # or false or "NA"
# ##         -agent: "main"  # or "testing" or "user"
# ##         -comment: "Detailed comment about status"
# ##
# ## metadata:
# ##   created_by: "main_agent"
# ##   version: "1.0"
# ##   test_sequence: 6
# ##   run_ui: false
# ##
# ## test_plan:
# ##   current_focus:
# ##     - "Task name 1"
# ##     - "Task name 2"
# ##   stuck_tasks:
# ##     - "Task name with persistent issues"
# ##   test_all: false
# ##   test_priority: "high_first"
# ##
# ## agent_communication:
# ##     -agent: "main"  # or "testing" or "user"
# ##     -message: "Communication message between agents"

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================


#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Hybrid Desktop App with offline-first architecture:
  - Default: OCR+Rules (85-88%, FREE, offline) using PaddleOCR
  - Optional: Cloud boost button (93%, có phí, online) using GPT-4
  - User tự chọn trade-off between privacy/cost vs accuracy
  - Electron + React + Python integration
  - Web app continues running in parallel

backend:
  - task: "Python OCR Engine for Desktop"
    implemented: true
    working: "NA"
    file: "/app/desktop-app/python/process_document.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Created Python processing script that uses PaddleOCR + Rule Classifier for offline document processing. Returns JSON with doc_type, confidence, short_code. Needs testing with real images."

frontend: []

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 7
  run_ui: false

test_plan:
  current_focus:
    - "Capture /api/llm/health current status and details"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      Please call GET {REACT_APP_BACKEND_URL}/api/llm/health and return the JSON including 'details'. We need to know if it's 401 (invalid key), 429 (rate limit), or other. Also confirm openai_available/emergent_available flags.
  - agent: "testing"
    message: |
      DIAGNOSIS COMPLETE: Called GET /api/llm/health successfully. FULL JSON RESPONSE: {"status": "unhealthy", "provider": "none", "model": null, "openai_available": false, "emergent_available": false, "details": "openai: Error code: 429 - Rate limit reached for gpt-4o-mini in organization org-aVxmtoYadWM8J3RXY1VJLj3a; emergent: AuthenticationError"}. ROOT CAUSE: 429 rate limit on OpenAI API + Emergent auth failure. BOTH providers down. Document scanning will fail until rate limit resets or API plan upgraded.
  - agent: "testing"
    message: |
      RE-TEST COMPLETE AFTER EMERGENT_LLM_KEY UPDATE: System status IMPROVED! Called GET /api/llm/health - Status: degraded, OpenAI: false, Emergent: true. FULL JSON: {"status": "degraded", "provider": "emergent", "model": "gpt-4o", "openai_available": false, "emergent_available": true, "details": "openai: Error code: 429 - Rate limit reached for gpt-4o-mini in organization org-aVxmtoYadWM8J3RXY1VJLj3a"}. RESULT: Emergent fallback now working! OpenAI still rate-limited but system functional in degraded mode. Document scanning should work using Emergent provider.
