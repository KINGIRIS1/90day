# Timer Feature Summary

## ✅ Đã Thêm Bộ Đếm Thời Gian Chi Tiết

### 🎯 Tính năng

Đã implement timer tracking đầy đủ cho **Batch Scanner** để theo dõi và so sánh hiệu năng giữa các OCR engines.

---

## 📊 Thông Tin Được Tracking

### 1. **Batch Timer** (Tổng thời gian batch)
- Start time: Khi bắt đầu scan
- End time: Khi kết thúc scan
- Elapsed time: Tổng thời gian (hiển thị live)
- Format: `MM:SS` (phút:giây)

### 2. **File Timers** (Thời gian mỗi file)
Mỗi file được track:
- `fileName`: Tên file
- `folderName`: Thư mục chứa file
- `startTime`: Timestamp bắt đầu (ms)
- `endTime`: Timestamp kết thúc (ms)
- `durationMs`: Thời gian xử lý (milliseconds)
- `engineType`: OCR engine được dùng (gemini-flash, gemini-flash-hybrid, gemini-flash-lite)
- `method`: Method classification (gemini_flash_ai, gemini_hybrid_two_tier, etc.)

### 3. **Folder Timers** (Thời gian mỗi folder)
Mỗi folder được track:
- `folderName`: Tên folder
- `folderPath`: Đường dẫn folder
- `startTime`: Timestamp bắt đầu (ms)
- `endTime`: Timestamp kết thúc (ms)
- `durationMs`: Thời gian xử lý (milliseconds)
- `fileCount`: Số file đã quét
- `avgTimePerFile`: Thời gian trung bình mỗi file (ms)

---

## 🎨 UI Components

### 1. **Live Timer Display** (Trong quá trình scan)
**Vị trí**: Progress section (top right)

**Hiển thị**:
```
⏱️ Thời gian đã quét
    M:SS
```

**Features**:
- Update mỗi giây
- Format: phút:giây (e.g., 2:45)
- Màu nền: Blue gradient
- Visible khi `isScanning = true`

---

### 2. **Summary Stats Box** (Sau khi scan xong)
**Vị trí**: Statistics overview section

**Grid layout (5 columns)**:
```
┌─────────────┬─────────────┬─────────────┬─────────────┬──────────────┐
│ Tổng folder │ Folder hợp  │ Files xử lý │    Lỗi      │ Tổng thời gian│
│     (blue)  │  lệ (green) │  (purple)   │    (red)    │   (orange)   │
└─────────────┴─────────────┴─────────────┴─────────────┴──────────────┘
```

**Orange box chi tiết**:
- Tổng thời gian: `M:SS`
- Avg time per file: `~X.Xs/file`

---

### 3. **Performance Stats Box** (Chi tiết hiệu năng)
**Vị trí**: Sau statistics grid

**Title**: Hiển thị engine type đang dùng
- 🔄 Gemini Hybrid
- 🤖 Gemini Flash
- ⚡ Gemini Flash Lite

**Grid layout (4 columns)**:
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Tổng thời gian│  TB mỗi file │  Nhanh nhất  │  Chậm nhất   │
│   (orange)   │    (blue)    │   (green)    │    (red)     │
│    M:SS      │    X.XXs     │    X.XXs     │    X.XXs     │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

**Speed Rating**:
- 🚀 Rất nhanh: < 2s/file
- ⚡ Nhanh: 2-5s/file
- ✅ Trung bình: 5-10s/file
- 🐢 Chậm: > 10s/file

---

### 4. **Per-File Timing** (Grid view)
**Vị trí**: Trong mỗi file card

**Display**:
```
⏱️ X.XXs
```

**Styling**: Orange text, small font
**Position**: Below doc_type info

---

## 💾 State Structure

### `timers` State
```javascript
{
  batchStartTime: 1234567890123,  // Date.now()
  batchEndTime: 1234567899999,
  batchElapsedSeconds: 180,       // Total seconds
  
  fileTimings: [
    {
      fileName: "image001.jpg",
      folderName: "Folder1",
      startTime: 1234567890123,
      endTime: 1234567891234,
      durationMs: 1111,
      engineType: "gemini-flash-hybrid",
      method: "gemini_hybrid_two_tier"
    },
    // ... more files
  ],
  
  folderTimings: [
    {
      folderName: "Folder1",
      folderPath: "C:\\Documents\\Folder1",
      startTime: 1234567890123,
      endTime: 1234567895000,
      durationMs: 4877,
      fileCount: 5,
      avgTimePerFile: 975
    },
    // ... more folders
  ]
}
```

### `elapsedTime` State
```javascript
elapsedTime: 180  // Current elapsed seconds (live updates)
```

---

## 🔧 Implementation Details

### 1. **Timer Initialization** (handleStartScan)
```javascript
const batchStartTime = Date.now();
setTimers({
  batchStartTime: batchStartTime,
  batchEndTime: null,
  batchElapsedSeconds: 0,
  fileTimings: [],
  folderTimings: []
});
setElapsedTime(0);
```

### 2. **Live Timer Update** (useEffect)
```javascript
useEffect(() => {
  if (isScanning && timers.batchStartTime) {
    timerIntervalRef.current = setInterval(() => {
      const now = Date.now();
      const elapsedMs = now - timers.batchStartTime;
      setElapsedTime(Math.floor(elapsedMs / 1000));
    }, 1000);
  }
  
  return () => {
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
    }
  };
}, [isScanning, timers.batchStartTime]);
```

### 3. **Folder Timer** (Loop start/end)
```javascript
// Start
const folderStartTime = Date.now();

// End (success)
const folderEndTime = Date.now();
const folderDurationMs = folderEndTime - folderStartTime;
setTimers(prev => ({
  ...prev,
  folderTimings: [...prev.folderTimings, {
    folderName: folder.name,
    startTime: folderStartTime,
    endTime: folderEndTime,
    durationMs: folderDurationMs,
    fileCount: folderResults.length,
    avgTimePerFile: folderDurationMs / folderResults.length
  }]
}));
```

### 4. **File Timer** (Loop start/end)
```javascript
// Start
const fileStartTime = Date.now();

// End
const fileEndTime = Date.now();
const fileDurationMs = fileEndTime - fileStartTime;

// Save to fileWithPreview
const fileWithPreview = {
  ...otherFields,
  startTime: fileStartTime,
  endTime: fileEndTime,
  durationMs: fileDurationMs,
  durationSeconds: (fileDurationMs / 1000).toFixed(2)
};

// Save to timers state
setTimers(prev => ({
  ...prev,
  fileTimings: [...prev.fileTimings, {
    fileName: fileName,
    folderName: folder.name,
    startTime: fileStartTime,
    endTime: fileEndTime,
    durationMs: fileDurationMs,
    engineType: ocrEngine,
    method: fileResult.method
  }]
}));
```

### 5. **Batch End Timer**
```javascript
const batchEndTime = Date.now();
const batchElapsedMs = batchEndTime - batchStartTime;
const batchElapsedSeconds = Math.floor(batchElapsedMs / 1000);

setTimers(prev => ({
  ...prev,
  batchEndTime: batchEndTime,
  batchElapsedSeconds: batchElapsedSeconds
}));
```

---

## 📈 Performance Metrics

### Calculations

**Average time per file**:
```javascript
const avgTime = fileTimings.reduce((sum, f) => sum + f.durationMs, 0) 
                / fileTimings.length / 1000;
```

**Fastest file**:
```javascript
const fastest = Math.min(...fileTimings.map(f => f.durationMs)) / 1000;
```

**Slowest file**:
```javascript
const slowest = Math.max(...fileTimings.map(f => f.durationMs)) / 1000;
```

**Speed rating**:
```javascript
if (avgTime < 2) return '🚀 Rất nhanh';
if (avgTime < 5) return '⚡ Nhanh';
if (avgTime < 10) return '✅ Trung bình';
return '🐢 Chậm';
```

---

## 🧪 Testing Scenarios

### Scenario 1: Single Folder (10 files)
**Expected**:
- Batch timer: ~20-50s (depending on engine)
- Folder timer: Same as batch
- File timers: 2-5s each (Hybrid), 1-2s (Flash Lite), 4-8s (GCN with date extraction)

### Scenario 2: Multiple Folders (3 folders, 30 files total)
**Expected**:
- Batch timer: ~60-150s
- Folder timers: 20-50s each
- File timers: Variable based on complexity

### Scenario 3: Engine Comparison
**Flash Lite (60% crop)**:
- Avg: 1-2s/file
- Rating: 🚀 Rất nhanh

**Flash Hybrid (60% → 100% if needed)**:
- Avg: 2-5s/file (depends on escalation rate)
- Rating: ⚡ Nhanh

**Flash Full (100% crop)**:
- Avg: 3-6s/file
- Rating: ⚡ Nhanh hoặc ✅ Trung bình

---

## 🎯 Use Cases

### 1. **Engine Performance Comparison**
User có thể chạy cùng batch với 3 engines khác nhau và so sánh:
- Flash Lite: Nhanh nhất, rẻ nhất
- Hybrid: Cân bằng tốc độ/accuracy
- Flash Full: Chậm hơn, accuracy cao nhất

### 2. **Batch Size Optimization**
Track timing để tìm batch size tối ưu:
- Small batch (10 files): Fast feedback
- Large batch (100 files): Efficient but slower

### 3. **Network/API Performance Monitoring**
Nếu timing tăng đột ngột:
- Check network speed
- Check API quota/limits
- Check concurrent requests

### 4. **Cost Estimation**
Dựa vào timing + engine type để estimate cost:
- Flash Lite: ~1s/file × $0.08/1K = $0.00008/file
- Hybrid: ~3s/file × $0.15/1K = $0.00015/file
- Flash Full: ~5s/file × $0.16/1K = $0.00016/file

---

## 📝 Console Logs

### Start Batch
```
⏱️ Batch timer started: 10:30:45 AM
```

### Start Folder
```
📂 [1/3] Scanning: C:\Documents\Folder1
⏱️ Folder timer started: 10:30:46 AM
```

### Start File
```
[1/10] Processing: image001.jpg
⏱️ File timer started: 10:30:47 AM
```

### End File
```
✅ File completed in 2.34s
```

### End Folder
```
✅ Folder "Folder1" completed in 23.45s (10 files)
```

### End Batch
```
✅ Batch scan complete: {...}
⏱️ Total batch time: 180s (3.00 minutes)
```

---

## 🎨 Styling

### Colors
- **Blue**: General progress, folders
- **Green**: Success, fastest time
- **Purple**: Files processed
- **Red**: Errors, slowest time
- **Orange**: Timer stats, performance
- **Yellow**: Warnings

### Icons
- ⏱️ Timer
- 🚀 Very fast
- ⚡ Fast
- ✅ Medium
- 🐢 Slow
- 📊 Stats

---

## 🚀 Future Enhancements

### 1. **Export Timer Stats**
Export timing data to CSV/JSON for analysis:
```javascript
const exportTimings = () => {
  const csv = convertToCSV(timers.fileTimings);
  downloadFile(csv, 'timing-stats.csv');
};
```

### 2. **Historical Comparison**
Save timing history in localStorage:
```javascript
const history = JSON.parse(localStorage.getItem('timerHistory') || '[]');
history.push({
  date: new Date(),
  engine: ocrEngine,
  avgTime: ...,
  totalFiles: ...
});
localStorage.setItem('timerHistory', JSON.stringify(history));
```

### 3. **Real-time Chart**
Show live chart of file processing speed:
- X-axis: File index
- Y-axis: Processing time (seconds)
- Compare multiple runs

### 4. **Cost Calculator**
Real-time cost estimation based on timing + engine:
```javascript
const estimatedCost = (fileCount, avgTime, engineCostPer1K) => {
  return (fileCount * engineCostPer1K / 1000).toFixed(4);
};
```

---

## ✅ Summary

**Files Modified**:
- `/app/desktop-app/src/components/BatchScanner.js` (main implementation)

**Features Added**:
- ✅ Live batch timer (updates every 1s)
- ✅ Per-file timing tracking
- ✅ Per-folder timing tracking
- ✅ Performance stats box (avg, min, max, speed rating)
- ✅ Summary stats with timer
- ✅ Per-file timing display in grid
- ✅ Console logs for all timers
- ✅ Engine-specific stats display

**Benefits**:
- 📊 Compare engine performance
- 💰 Estimate costs based on timing
- 🎯 Optimize batch size
- 🔍 Monitor API/network performance
- 📈 Track processing efficiency

---

**Version**: 1.0  
**Date**: 2025-01-XX  
**Status**: ✅ Complete & Ready for Testing
