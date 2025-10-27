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
  - Default: OCR+Rules (85-88%, FREE, offline) using Tesseract OCR
  - Optional: VietOCR engine (90-95%, FREE, offline, Vietnamese specialized) - User can switch in Settings
  - Optional: Cloud boost button (93%, có phí, online) using GPT-4
  - User tự chọn OCR engine (Tesseract vs VietOCR) và trade-off between privacy/cost vs accuracy
  - Electron + React + Python integration
  - Web app continues running in parallel
  - UI toggle in Settings to choose between Tesseract and VietOCR

backend:
  - task: "Python OCR Engine for Desktop"
    implemented: true
    working: "needs_testing"
    file: "/app/desktop-app/python/process_document.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "needs_testing"
        agent: "main"
        comment: "Updated to support BOTH Tesseract and VietOCR engines. User can select engine in Settings UI. Added ocr_engine_type parameter to process_document.py. VietOCR auto-installed and verified on user's Python 3.12 environment."

frontend:
  - task: "Desktop App - Electron + React"
    implemented: true
    working: "needs_testing"
    file: "/app/desktop-app/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "needs_testing"
        agent: "main"
        comment: "Created Electron desktop app with React UI. Features: file/folder picker, offline OCR processing, cloud boost option, settings page with OCR engine selection. IPC communication via preload.js. Needs testing in electron-dev mode."
  
  - task: "Desktop Scanner Component"
    implemented: true
    working: "needs_testing"
    file: "/app/desktop-app/src/components/DesktopScanner.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "needs_testing"
        agent: "main"
        comment: "Main scanning UI with two processing modes: Offline OCR (free, 85-95% depending on engine) and Cloud Boost (paid, 93%+). Shows confidence bars, method badges, and recommendations. Needs electron testing."
  
  - task: "Settings - OCR Engine Selection"
    implemented: true
    working: "needs_testing"
    file: "/app/desktop-app/src/components/Settings.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "needs_testing"
        agent: "main"
        comment: "Added new UI section for OCR engine selection. Users can choose between Tesseract (fast, 85-88%) and VietOCR (Vietnamese specialized, 90-95%). Preference saved via electron-store. Dynamic display of selected engine in App Info section."

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
      ✅ VietOCR INTEGRATION COMPLETE - User Can Choose OCR Engine!
      
      🎯 FEATURE IMPLEMENTED:
      ✅ Both Tesseract and VietOCR engines supported in process_document.py
      ✅ New Settings UI section: "🔍 Chọn OCR Engine (Offline)"
      ✅ Radio buttons to switch between Tesseract and VietOCR
      ✅ User preference saved via electron-store (ocrEngineType)
      ✅ Dynamic display in App Info showing selected engine
      ✅ Auto-fallback if VietOCR selected but not installed
      
      📦 FILES MODIFIED:
      1. /app/desktop-app/python/process_document.py
         - Import both Tesseract and VietOCR engines
         - Added ocr_engine_type parameter (default: 'tesseract')
         - Engine selection logic with fallback
         - Returns engine name in result
      
      2. /app/desktop-app/electron/main.js
         - Read ocrEngineType from electron-store
         - Pass to Python script as argument
      
      3. /app/desktop-app/public/electron.js
         - Same changes as main.js for production build
      
      4. /app/desktop-app/src/components/Settings.js
         - New component: OCREngineTypeSetting
         - Radio buttons: Tesseract vs VietOCR
         - Description of each engine
         - Auto-save preference
         - Dynamic OCR engine display in App Info
         - Updated Usage Guide
      
      5. /app/desktop-app/python/requirements.txt
         - Added VietOCR as optional dependency (commented)
         - Instructions on how to enable
      
      6. /app/desktop-app/VIETOCR_SETUP.md
         - Updated with new UI toggle instructions
      
      🎨 UI FEATURES:
      - Clear engine descriptions in Vietnamese
      - Tesseract: "Nhanh, nhẹ, hỗ trợ đa ngôn ngữ"
      - VietOCR: "Chuyên cho tiếng Việt, độ chính xác cao (90-95%)"
      - Green checkmark on save
      - Dynamic engine name in App Info section
      
      🔧 TECHNICAL DETAILS:
      - VietOCR already verified installed on user's Python 3.12
      - Test command worked: py -3.12 ocr_engine_vietocr.py "test.jpg"
      - Both engines use same interface (extract_text returns dict)
      - Graceful fallback if VietOCR import fails
      - Clear console logs show which engine is being used
      
      ⏭️ NEXT STEPS:
      1. Test in development mode (yarn start + yarn electron-dev)
      2. Test switching between engines in Settings
      3. Test OCR with both engines
      4. Verify persistence of preference
      5. Test packaged app
      
      📝 USER TESTING REQUIRED:
      - Switch between Tesseract and VietOCR in Settings
      - Process document with each engine
      - Verify accuracy difference (VietOCR should be 90-95% vs Tesseract 85-88%)
      - Check if engine name shows correctly in results
