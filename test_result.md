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
  - Default: OCR+Rules (85-88%, FREE, offline) using Tesseract OCR (ONLY)
  - Optional: Cloud boost button (93%, có phí, online) using GPT-4
  - User tự chọn trade-off between privacy/cost vs accuracy
  - Electron + React + Python integration
  - Web app continues running in parallel
  - NOTE: Changed from PaddleOCR/VietOCR/RapidOCR to Tesseract-only due to reliability issues

backend:
  - task: "Python OCR Engine for Desktop"
    implemented: true
    working: "NA"
    file: "/app/desktop-app/python/process_document.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "true"
        agent: "main"
        comment: "Updated to use Tesseract OCR exclusively. Removed PaddleOCR, VietOCR, RapidOCR, EasyOCR fallbacks. Script confirmed loading successfully with message 'Using Tesseract OCR (only engine enabled)'."

frontend:
  - task: "Desktop App - Electron + React"
    implemented: true
    working: "NA"
    file: "/app/desktop-app/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Created Electron desktop app with React UI. Features: file/folder picker, offline OCR processing, cloud boost option, settings page. IPC communication via preload.js. Needs testing in electron-dev mode."
  
  - task: "Desktop Scanner Component"
    implemented: true
    working: "NA"
    file: "/app/desktop-app/src/components/DesktopScanner.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Main scanning UI with two processing modes: Offline OCR (free, 85-88%) and Cloud Boost (paid, 93%+). Shows confidence bars, method badges, and recommendations. Needs electron testing."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 7
  run_ui: false

test_plan:
  current_focus:
    - "Test Python OCR engine standalone with sample images"
    - "Test Electron app startup and UI"
    - "Test offline OCR flow end-to-end"
    - "Test cloud boost configuration and flow"
  stuck_tasks: []
  test_all: false
  test_priority: "desktop_app_first"

agent_communication:
  - agent: "main"
    message: |
      Phase 1 Complete: Desktop App Structure Created
      ✅ Electron main process with IPC handlers
      ✅ React UI with Scanner and Settings components
      ✅ Python processing script (OCR + Rules)
      ✅ Package.json with electron-builder config
      ✅ Documentation (README + QUICK_START_VI)
      
      Next Steps:
      1. Install Python dependencies: cd /app/desktop-app/python && pip3 install -r requirements.txt
      2. Test Python script standalone
      3. Run electron-dev mode to test full app
      4. Verify offline OCR works with sample images
      
      Note: Web app (/app/frontend & /app/backend) remains untouched and runs in parallel.
