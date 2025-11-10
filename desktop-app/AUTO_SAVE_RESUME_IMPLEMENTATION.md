# 🔄 Auto-Save & Resume Feature - Implementation Guide

## ✅ Đã Hoàn Thành:

### 1. Backend (Electron IPC) ✅

**Files:** `main.js` + `preload.js`

**IPC Handlers đã thêm:**
```javascript
- save-scan-state: Lưu scan state vào electron-store
- get-incomplete-scans: Load incomplete scans (< 7 days)
- load-scan-state: Load specific scan by ID
- delete-scan-state: Xóa scan history
- mark-scan-complete: Đánh dấu scan hoàn thành
```

**Auto-cleanup:** Scans > 7 days tự động xóa khi call `get-incomplete-scans`

---

### 2. UI Component ✅

**File:** `ResumeDialog.js` (NEW)

**Features:**
- Hiển thị danh sách incomplete scans
- Show: Type, timestamp, progress, files scanned
- Buttons: "Tiếp tục" / "Xóa" / "Bỏ qua tất cả"
- Auto-calculate time ago (10 phút trước, 2 giờ trước, 3 ngày trước)

---

### 3. Integration (TODO)

**Cần thêm vào DesktopScanner.js:**

#### A. Import ResumeDialog:
```javascript
import ResumeDialog from './ResumeDialog';
```

#### B. Add States:
```javascript
const [showResumeDialog, setShowResumeDialog] = useState(false);
const [incompleteScans, setIncompleteScans] = useState([]);
const [currentScanId, setCurrentScanId] = useState(null);
```

#### C. Check Incomplete Scans on Mount:
```javascript
useEffect(() => {
  const checkIncompleteScans = async () => {
    if (!window.electronAPI) return;
    
    const result = await window.electronAPI.getIncompleteScans();
    if (result.success && result.scans.length > 0) {
      setIncompleteScans(result.scans);
      setShowResumeDialog(true);
    }
  };
  
  checkIncompleteScans();
}, []);
```

#### D. Handle Resume:
```javascript
const handleResumeScan = async (scan) => {
  // Load scan data
  const loadResult = await window.electronAPI.loadScanState(scan.scanId);
  if (!loadResult.success) {
    alert('Không thể load scan data');
    return;
  }
  
  const scanData = loadResult.data;
  
  // Restore state
  setResults(scanData.results || []);
  setSelectedFiles(scanData.selectedFiles || []);
  setLastKnownType(scanData.lastKnownType);
  setCurrentScanId(scan.scanId);
  setProgress(scanData.progress || {current: 0, total: 0});
  
  // Close dialog
  setShowResumeDialog(false);
  
  // Show notification
  alert(`✅ Đã load ${scanData.results?.length || 0} kết quả. Bấm "Tiếp tục scan" để quét tiếp.`);
};
```

#### E. Auto-Save After Each Folder:
```javascript
// In scanChildFolder() or after folder complete:

// Save scan state
await window.electronAPI.saveScanState({
  type: 'folder_scan',
  status: 'incomplete',
  results: childResults,
  progress: {current: i+1, total: childTabs.length},
  currentFolder: childPath,
  lastKnownType: currentLastKnown,
  selectedFiles: files
});
```

#### F. Mark Complete When Scan Done:
```javascript
// At end of handleProcessFiles() or scanAllChildFolders():

if (currentScanId) {
  await window.electronAPI.markScanComplete(currentScanId);
  setCurrentScanId(null);
}
```

#### G. Render Resume Dialog:
```javascript
return (
  <div>
    {/* Resume Dialog */}
    {showResumeDialog && (
      <ResumeDialog
        scans={incompleteScans}
        onResume={handleResumeScan}
        onDismiss={(scanId) => {
          if (scanId === 'all') {
            incompleteScans.forEach(s => 
              window.electronAPI.deleteScanState(s.scanId)
            );
          } else {
            window.electronAPI.deleteScanState(scanId);
          }
          setShowResumeDialog(false);
        }}
      />
    )}
    
    {/* Rest of component */}
  </div>
);
```

---

## 📊 Data Structure:

**Scan State được lưu:**
```javascript
{
  scanId: "scan_1703075422000",
  type: "folder_scan",
  timestamp: 1703075422000,
  status: "incomplete",
  
  // Scan data
  results: [...],  // All scanned files
  selectedFiles: [...],  // Files to process
  progress: {current: 50, total: 100},
  currentFolder: "D:\\test\\folder1",
  lastKnownType: {short_code: "HDCQ", confidence: 0.95},
  
  // Metadata
  engine: "gemini-flash",
  batchMode: "smart",
  
  // Timestamps
  startedAt: 1703075422000,
  lastSavedAt: 1703075500000,
  completedAt: null
}
```

---

## 🎯 User Flow:

**Scenario: App crash giữa scan**

```
1. User đang scan folder với 100 files
2. Scan đến file 50 → App crash/tắt 💥
3. User mở lại app
4. Dialog hiển thị:
   
   ┌─────────────────────────────────────┐
   │ 🔄 Tiếp Tục Scan?                    │
   │                                     │
   │ 📁 Folder Scan                      │
   │ [Chưa xong] 2 giờ trước             │
   │                                     │
   │ Tiến độ: 50 / 100                   │
   │ Files đã scan: 50 files             │
   │                                     │
   │ [▶️ Tiếp Tục] [🗑️ Xóa]              │
   └─────────────────────────────────────┘
   
5. User click "Tiếp Tục"
6. App load 50 results đã scan
7. Resume từ file 51 → 100 ✅
8. Không mất data! ✅
```

---

## 🔄 Implementation Status:

**Completed:**
- ✅ IPC handlers (main.js)
- ✅ Preload bridge (preload.js)
- ✅ ResumeDialog component
- ✅ Auto-cleanup (7 days)
- ✅ Data structure designed

**TODO (Cần integrate vào components):**
- ⏳ DesktopScanner.js integration
- ⏳ BatchScanner.js integration
- ⏳ Auto-save after folder complete
- ⏳ Load incomplete scans on mount
- ⏳ Resume button functionality

**Estimate:** ~30-40 phút để integrate vào components

---

## 💾 Storage Details:

**electron-store location:**
```
Windows: C:\Users\[username]\AppData\Roaming\90dayChonThanh\config.json
```

**Scan history structure:**
```json
{
  "scanHistory": {
    "scan_1703075422000": {...},
    "scan_1703075500000": {...}
  }
}
```

**Max size:** Unlimited (JSON file, grows with scans)

**Cleanup:** Auto-delete scans > 7 days

---

## 🎯 Next Steps:

Bạn muốn tôi:

**Option A:** Tiếp tục integrate vào DesktopScanner + BatchScanner (~30 phút)

**Option B:** Test batch processing trước, implement auto-save sau

**Option C:** Tạo detailed integration guide để bạn tự làm

Bạn chọn option nào? 🤔
