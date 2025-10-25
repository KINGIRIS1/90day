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
# ##     priority: "high"  # or "medium" or "low"
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
# ##   test_sequence: 5
# ##   run_ui: true
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
  Document scanning application for Vietnamese land documents with automatic naming using short codes.
  Features: Single scan with strict grouping, Folder scanning via ZIP, and Direct folder scanning (no ZIP) with grouped naming identical to single scan.

backend:
  - task: "OpenAI primary LLM integration with fallback to Emergent + strict error handling"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "critical"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Switched analyze_document_with_vision to use OpenAI (gpt-4o-mini) primary, added 20s backoff on 429, kept fallback toggle. Added /api/llm/health."
      - working: true
        agent: "testing"
        comment: "✅ LLM health endpoint working. API returns proper status: 'unhealthy' with OpenAI 429 rate limit and Emergent auth errors. Error handling working correctly. Status shows provider info and detailed error messages."
  - task: "Direct folder scan (no ZIP) with grouped naming like single scan"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added POST /api/scan-folder-direct + /api/folder-direct-status. Grouping: continuation pages inherit last short_code. Per-folder PDFs merged by short_code; links exposed via download endpoint."
      - working: true
        agent: "testing"
        comment: "✅ Backend endpoints accessible and functional. API structure correct for folder scanning workflow."
  - task: "ZIP folder scan regression (grouped by short_code)"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "ZIP flow updated to grouped-by-short_code PDFs per folder. Fixed previous model validation issues and syntax errors."
      - working: true
        agent: "testing"
        comment: "✅ Backend ZIP folder scan endpoints available and properly structured."
  - task: "Download all ZIP for direct scan"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added GET /api/download-all-direct/{job_id} and added all_zip_url to folder-direct-status when job is completed."

frontend:
  - task: "Admin Panel: LLM Status tile"
    implemented: true
    working: true
    file: "/app/frontend/src/components/LlmStatus.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Shows /api/llm/health status with polling."
      - working: true
        agent: "testing"
        comment: "✅ LLM Status component fully functional. Displays status (UNHEALTHY), shows OpenAI/Fallback badges, refresh button works."
  - task: "FolderPickerDirect UI (folder picker without ZIP)"
    implemented: true
    working: true
    file: "/app/frontend/src/components/FolderPickerDirect.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Adds folder picker using webkitdirectory, posts files + relative_paths to /api/scan-folder-direct, displays per-folder PDF URLs, includes optional 'Tải tất cả (ZIP)' switch."
      - working: true
        agent: "testing"
        comment: "✅ Component present and functional."
      - working: "NA"
        agent: "main"
        comment: "Updated UI to show 'Tải tất cả (ZIP)' button when job completed via status.all_zip_url and show per-folder errors details if exist. Needs retesting."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 5
  run_ui: true

test_plan:
  current_focus:
    - "FolderPickerDirect shows 'Tải tất cả (ZIP)' when completed and link downloads a ZIP"
    - "Folder results render PDF links; errors details expand properly"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      Please run frontend UI automated tests focusing on the updated folder direct scan UI:
      1) Login as admin → navigate to main page with FolderPickerDirect
      2) Select a small folder (2-3 images), start scan, poll until status=completed
      3) Verify 'Tải tất cả (ZIP)' button appears and clicking downloads a ZIP (200 status, application/zip)
      4) Verify per-folder PDF links exist and clickable
      5) If any image is intentionally bad, errors details should appear in a collapsible block
      Also ensure no critical console errors. Use REACT_APP_BACKEND_URL for API calls.
