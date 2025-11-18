import React, { useState, useRef } from 'react';
import { handleError, isCriticalError } from '../utils/errorHandler';

// Helper for path operations (client-side safe)
const path = {
  dirname: (p) => p.substring(0, Math.max(p.lastIndexOf('/'), p.lastIndexOf('\\'))),
  basename: (p) => p.split(/[/\\]/).pop()
};

/**
 * Only GCN Scanner - Chế độ đặc biệt
 * - Quét và phân loại tất cả file
 * - GCN A3 (GCNC/GCNM) → Đặt tên theo GCN
 * - File khác → Đặt tên "GTLQ"
 * - Giữ nguyên thứ tự file
 */
function OnlyGCNScanner() {
  const [scanMode, setScanMode] = useState('folder'); // 'folder' or 'batch'
  const [usePreFilter, setUsePreFilter] = useState(false); // Pre-filter OFF by default
  const [files, setFiles] = useState([]);
  
  // Folder tabs (giống BatchScanner)
  const [folderTabs, setFolderTabs] = useState([]);
  const [activeFolder, setActiveFolder] = useState(null);
  
  const [isScanning, setIsScanning] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [currentPhase, setCurrentPhase] = useState(''); // 'prefilter', 'scanning', 'complete'
  const [currentFile, setCurrentFile] = useState('');
  const [currentFolder, setCurrentFolder] = useState('');
  const [folderProgress, setFolderProgress] = useState({ current: 0, total: 0 });
  const [phaseStats, setPhaseStats] = useState({ passed: 0, skipped: 0, scanned: 0 });
  const [txtFilePath, setTxtFilePath] = useState('');
  const [isLoadingFolders, setIsLoadingFolders] = useState(false);
  const [folderList, setFolderList] = useState([]);
  const stopRef = useRef(false);

  // Load OCR engine config
  const [ocrEngine, setOcrEngine] = useState('gemini-flash-lite');

  // Merge modal states (giống BatchScanner & DesktopScanner)
  const [showMergeModal, setShowMergeModal] = useState(false);
  const [mergeInProgress, setMergeInProgress] = useState(false);
  const [outputOption, setOutputOption] = useState('same_folder');
  const [mergeSuffix, setMergeSuffix] = useState('_merged');
  const [outputFolder, setOutputFolder] = useState('');
  
  // Get results for active folder
  const fileResults = React.useMemo(() => {
    if (!activeFolder || folderTabs.length === 0) return [];
    const tab = folderTabs.find(t => t.path === activeFolder);
    return tab ? tab.files : [];
  }, [folderTabs, activeFolder]);

  React.useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const engine = await window.electronAPI.getConfig('ocrEngine');
      setOcrEngine(engine || 'gemini-flash-lite');
    } catch (err) {
      console.error('Failed to load config:', err);
    }
  };

  // Select folder
  const handleSelectFolder = async () => {
    try {
      // Check if API is available
      if (!window.electronAPI.getImagesInFolder) {
        alert('⚠️ Chức năng này cần cập nhật app.\n\nVui lòng:\n1. Save to GitHub\n2. Pull code mới\n3. Đóng app hoàn toàn\n4. Xóa cache: %APPDATA%\\Electron\n5. Chạy: yarn install\n6. Restart app');
        return;
      }

      const folderPath = await window.electronAPI.selectFolder();
      if (!folderPath) return;

      // Get all image files
      const imageFiles = await window.electronAPI.getImagesInFolder(folderPath);
      
      if (imageFiles.length === 0) {
        alert('Không tìm thấy file ảnh nào trong thư mục!');
        return;
      }

      setFiles(imageFiles);
      setResults([]);
      setTxtFilePath('');
      console.log(`📁 Selected folder: ${imageFiles.length} files`);
    } catch (err) {
      console.error('Error selecting folder:', err);
      alert('Lỗi chọn thư mục: ' + err.message);
    }
  };

  // Select txt file for batch mode
  const handleSelectTxtFile = async () => {
    try {
      // Check if API is available
      if (!window.electronAPI.getImagesInFolder) {
        alert('⚠️ Chức năng này cần cập nhật app.\n\nVui lòng:\n1. Save to GitHub\n2. Pull code mới\n3. Đóng app hoàn toàn\n4. Xóa cache: %APPDATA%\\Electron\n5. Chạy: yarn install\n6. Restart app');
        return;
      }

      const txtPath = await window.electronAPI.selectTxtFile();
      if (!txtPath) return;

      setTxtFilePath(txtPath);
      setFolderList([]);
      setFiles([]);
      setResults([]);
      
      console.log(`📋 Selected txt file: ${txtPath}`);
    } catch (err) {
      console.error('Error selecting txt file:', err);
      alert('Lỗi chọn file txt: ' + err.message);
    }
  };

  // Helper: Parse issue date for GCN classification (giống BatchScanner)
  const parseIssueDate = (issueDate, confidence) => {
    if (!issueDate) return null;
    
    try {
      let comparable = 0;
      let parts;
      
      if (confidence === 'full') {
        parts = issueDate.split('/');
        if (parts.length === 3) {
          const day = parseInt(parts[0], 10);
          const month = parseInt(parts[1], 10);
          const year = parseInt(parts[2], 10);
          comparable = year * 10000 + month * 100 + day;
        }
      } else if (confidence === 'partial') {
        parts = issueDate.split('/');
        if (parts.length === 2) {
          const month = parseInt(parts[0], 10);
          const year = parseInt(parts[1], 10);
          comparable = year * 10000 + month * 100 + 1;
        }
      } else if (confidence === 'year_only') {
        const year = parseInt(issueDate, 10);
        comparable = year * 10000 + 1 * 100 + 1;
      }
      
      return { comparable, original: issueDate };
    } catch (e) {
      console.error(`❌ Error parsing date: ${issueDate}`, e);
      return null;
    }
  };

  // Post-process GCN: Classify into GCNC/GCNM (giống BatchScanner)
  const postProcessGCN = (results) => {
    try {
      console.log('🔄 Post-processing GCN (DATE-BASED classification)...');
      
      // Step 1: Find all GCN documents
      const allGcnDocs = results.filter(r => 
        r.newShortCode === 'GCNC' || r.newShortCode === 'GCNM' || r.newShortCode === 'GCN'
      );
      
      if (allGcnDocs.length === 0) {
        console.log('✅ No GCN documents found');
        return results;
      }
      
      console.log(`📋 Found ${allGcnDocs.length} GCN document(s) to process`);
      
      // Step 2: Group by metadata (color + issue_date)
      const gcnGroups = new Map();
      
      allGcnDocs.forEach(doc => {
        const meta = doc.metadata || {};
        const color = meta.color || doc.color || 'unknown';
        const issueDate = meta.issue_date || doc.issue_date || null;
        const issueDateConf = meta.issue_date_confidence || doc.issue_date_confidence || null;
        
        const groupKey = `${color}_${issueDate || 'null'}`;
        
        if (!gcnGroups.has(groupKey)) {
          gcnGroups.set(groupKey, {
            files: [],
            color: color,
            issueDate: issueDate,
            issueDateConfidence: issueDateConf,
            parsedDate: parseIssueDate(issueDate, issueDateConf)
          });
        }
        
        gcnGroups.get(groupKey).files.push(doc);
      });
      
      console.log(`📋 Found ${gcnGroups.size} unique GCN group(s)`);
      
      const groupsArray = Array.from(gcnGroups.values());
      
      // DEBUG: Log all groups with dates
      console.log('🔍 DEBUG - GCN Groups:');
      groupsArray.forEach((group, idx) => {
        console.log(`  Group ${idx + 1}:`, {
          color: group.color,
          issueDate: group.issueDate || 'null',
          confidence: group.issueDateConfidence || 'null',
          parsedDate: group.parsedDate ? group.parsedDate.comparable : 'null',
          fileCount: group.files.length
        });
      });
      
      // Step 3: Classify by color or date
      const colors = groupsArray.map(g => g.color).filter(c => c && c !== 'unknown');
      const uniqueColors = [...new Set(colors)];
      const hasRedAndPink = uniqueColors.includes('red') && uniqueColors.includes('pink');
      
      console.log(`🎨 Color analysis: ${uniqueColors.join(', ') || 'none'}, hasRedAndPink=${hasRedAndPink}`);
      
      const processedResults = [...results];
      
      if (hasRedAndPink) {
        console.log(`  🎨 Mixed colors → Classify by color`);
        groupsArray.forEach(group => {
          const classification = (group.color === 'red' || group.color === 'orange') ? 'GCNC' : 'GCNM';
          group.files.forEach(file => {
            const idx = processedResults.findIndex(r => r.fileName === file.fileName);
            if (idx >= 0) {
              processedResults[idx].newShortCode = classification;
              processedResults[idx].newDocType = classification === 'GCNC' ? 'Giấy chứng nhận (Chung)' : 'Giấy chứng nhận (Mẫu)';
            }
          });
        });
      } else {
        console.log(`  📅 Same color → Classify by date`);
        const groupsWithDate = groupsArray.filter(g => g.parsedDate && g.parsedDate.comparable > 0);
        
        console.log(`  📊 Groups with valid dates: ${groupsWithDate.length}/${groupsArray.length}`);
        
        if (groupsWithDate.length >= 2) {
          groupsWithDate.sort((a, b) => a.parsedDate.comparable - b.parsedDate.comparable);
          console.log(`  📊 Sorted by date: Oldest = GCNC, others = GCNM`);
          
          groupsWithDate.forEach((group, idx) => {
            const classification = (idx === 0) ? 'GCNC' : 'GCNM';
            console.log(`    Group ${idx + 1}: ${group.issueDate} (${group.parsedDate.comparable}) → ${classification}`);
            
            group.files.forEach(file => {
              const resIdx = processedResults.findIndex(r => r.fileName === file.fileName);
              if (resIdx >= 0) {
                processedResults[resIdx].newShortCode = classification;
                processedResults[resIdx].newDocType = classification === 'GCNC' ? 'Giấy chứng nhận (Chung)' : 'Giấy chứng nhận (Mẫu)';
                console.log(`      ✅ ${file.fileName} → ${classification}`);
              }
            });
          });
        } else {
          // Fallback: Not enough dates → Use first as GCNC
          console.log(`  ⚠️ Not enough dates (${groupsWithDate.length} groups with dates)`);
          console.log(`  ⚠️ Fallback: First GCN = GCNC`);
          
          if (groupsArray.length === 1) {
            groupsArray[0].files.forEach(file => {
              const idx = processedResults.findIndex(r => r.fileName === file.fileName);
              if (idx >= 0) {
                processedResults[idx].newShortCode = 'GCNC';
                processedResults[idx].newDocType = 'Giấy chứng nhận (Chung)';
                console.log(`      ✅ ${file.fileName} → GCNC (fallback)`);
              }
            });
          } else if (groupsArray.length > 1) {
            console.log(`  ⚠️ Multiple groups but no dates → Cannot classify, keeping as GCN`);
          }
        }
      }
      
      console.log('✅ Post-processing complete');
      return processedResults;
    } catch (err) {
      console.error('❌ Post-processing error:', err);
      return results; // Return original on error
    }
  };

  // Load folders from txt file
  const handleLoadFolders = async () => {
    if (!txtFilePath) {
      alert('Vui lòng chọn file txt trước!');
      return;
    }

    setIsLoadingFolders(true);
    
    try {
      // Read and validate folders from txt
      const validation = await window.electronAPI.validateBatchFolders(txtFilePath);
      
      if (!validation.success) {
        alert('Lỗi đọc file txt: ' + validation.error);
        setIsLoadingFolders(false);
        return;
      }

      setFolderList(validation.folders);

      // Collect all image files from all folders
      const allFiles = [];
      for (const folder of validation.folders) {
        const imageFiles = await window.electronAPI.getImagesInFolder(folder.path);
        allFiles.push(...imageFiles);
      }

      if (allFiles.length === 0) {
        alert('Không tìm thấy file ảnh nào trong các thư mục!');
        setIsLoadingFolders(false);
        return;
      }

      setFiles(allFiles);
      console.log(`✅ Loaded ${validation.folders.length} folders: ${allFiles.length} total files`);
    } catch (err) {
      console.error('Error loading folders:', err);
      alert('Lỗi tải thư mục: ' + err.message);
    } finally {
      setIsLoadingFolders(false);
    }
  };

  // Start scanning with pre-filter BY FOLDER
  const handleStartScan = async () => {
    if (files.length === 0) {
      alert('Vui lòng chọn thư mục trước!');
      return;
    }

    setIsScanning(true);
    setResults([]);
    setCurrentPhase('prefilter');
    setPhaseStats({ passed: 0, skipped: 0, scanned: 0 });
    stopRef.current = false;

    const allResults = [];

    try {
      // Check if pre-filter API is available
      const hasPreFilter = !!window.electronAPI.preFilterGCNFiles;

      // Group files by folder
      const folderGroups = {};
      files.forEach(filePath => {
        const folderPath = filePath.substring(0, filePath.lastIndexOf(/[/\\]/.exec(filePath)[0]));
        if (!folderGroups[folderPath]) {
          folderGroups[folderPath] = [];
        }
        folderGroups[folderPath].push(filePath);
      });

      const folderPaths = Object.keys(folderGroups);
      console.log(`📁 Processing ${folderPaths.length} folders...`);
      
      // Initialize folder tabs
      const tabs = folderPaths.map(fp => ({
        path: fp,
        name: fp.split(/[/\\]/).pop(),
        files: [],
        processing: false,
        complete: false
      }));
      setFolderTabs(tabs);
      if (tabs.length > 0) setActiveFolder(tabs[0].path);
      
      setFolderProgress({ current: 0, total: folderPaths.length });

      // Process each folder
      for (let folderIdx = 0; folderIdx < folderPaths.length; folderIdx++) {
        if (stopRef.current) {
          console.log('⏹️ Scan stopped by user');
          break;
        }

        const folderPath = folderPaths[folderIdx];
        const folderFiles = folderGroups[folderPath];
        const folderName = folderPath.split(/[/\\]/).pop() || 'root';

        // Update tab status
        setFolderTabs(prev => prev.map(t => 
          t.path === folderPath ? { ...t, processing: true } : t
        ));
        setActiveFolder(folderPath);

        setFolderProgress({ current: folderIdx + 1, total: folderPaths.length });
        setCurrentFolder(folderName);

        console.log(`\n📂 [${folderIdx + 1}/${folderPaths.length}] Processing folder: ${folderName}`);
        console.log(`   Files: ${folderFiles.length}`);

        // Results for THIS FOLDER only
        const folderResults = [];

        // Phase 1: Pre-filter THIS FOLDER (if enabled)
        let gcnCandidates = folderFiles;
        let skipped = [];

        if (usePreFilter && hasPreFilter) {
          setCurrentPhase('prefilter');
          setCurrentFile(`Đang phân tích màu sắc thư mục ${folderName}...`);
          
          const preFilterStart = Date.now();
          const preFilterResults = await window.electronAPI.preFilterGCNFiles(folderFiles);
          const preFilterTime = ((Date.now() - preFilterStart) / 1000).toFixed(1);
          
          gcnCandidates = preFilterResults.passed || [];
          skipped = preFilterResults.skipped || [];
          
          console.log(`   🎨 Pre-filter: ${gcnCandidates.length} GCN, ${skipped.length} skipped (${preFilterTime}s)`);
        } else {
          console.log(`   ⚡ Pre-filter OFF: Scanning all ${folderFiles.length} files`);
          gcnCandidates = folderFiles;
          skipped = [];
        }
        
        // Add skipped files as GTLQ
        for (const filePath of skipped) {
          const fileName = filePath.split(/[/\\]/).pop();
          folderResults.push({
            fileName,
            filePath,
            folderName,
            previewUrl: null,
            originalShortCode: 'SKIPPED',
            originalDocType: 'Bỏ qua (không phải GCN)',
            newShortCode: 'GTLQ',
            newDocType: 'Giấy tờ liên quan',
            confidence: 0,
            reasoning: 'Pre-filter: Không có màu GCN (red/pink)',
            metadata: {},
            success: true,
            preFiltered: true
          });
        }

        // Phase 2: AI scan GCN candidates OF THIS FOLDER
        if (gcnCandidates.length > 0) {
          setCurrentPhase('scanning');
          console.log(`   🤖 AI scanning ${gcnCandidates.length} GCN candidates...`);
          setProgress({ current: 0, total: gcnCandidates.length });

          for (let i = 0; i < gcnCandidates.length; i++) {
            if (stopRef.current) break;

            const filePath = gcnCandidates[i];
            const fileName = filePath.split(/[/\\]/).pop();

            setProgress({ current: i + 1, total: gcnCandidates.length });
            setCurrentFile(fileName);
            console.log(`      [${i + 1}/${gcnCandidates.length}] Scanning: ${fileName}`);

            try {
              const result = await window.electronAPI.processDocumentOffline(filePath);
              
              let previewUrl = null;
              try {
                if (/\.(png|jpg|jpeg|gif|bmp)$/i.test(fileName)) {
                  previewUrl = await window.electronAPI.readImageDataUrl(filePath);
                }
              } catch (e) {
                console.warn('Failed to load preview:', fileName);
              }

              // Normalize: GCNM/GCNC → GCN temporarily (will be re-classified in post-process)
              let newShortCode = 'GTLQ';
              let newDocType = 'Giấy tờ liên quan';
              
              const shortCode = result.short_code || result.classification || '';
              if (shortCode === 'GCNC' || shortCode === 'GCNM' || shortCode === 'GCN') {
                newShortCode = 'GCN'; // Normalize to GCN (will be post-processed)
                newDocType = 'Giấy chứng nhận';
              }

              // Extract GCN metadata for post-processing
              const meta = result.metadata || {};
              const color = meta.color || result.color || null;
              const issueDate = meta.issue_date || result.issue_date || null;
              const issueDateConf = meta.issue_date_confidence || result.issue_date_confidence || null;

              // DEBUG: Log GCN metadata if found
              if (shortCode === 'GCNC' || shortCode === 'GCNM' || shortCode === 'GCN') {
                console.log(`      📊 GCN metadata: color=${color || 'null'}, date=${issueDate || 'null'}, confidence=${issueDateConf || 'null'}`);
              }

              folderResults.push({
                fileName,
                filePath,
                folderName,
                previewUrl,
                originalShortCode: shortCode,
                originalDocType: result.doc_type || shortCode,
                newShortCode,
                newDocType,
                confidence: result.confidence || 0,
                reasoning: result.reasoning || '',
                metadata: meta,
                // GCN-specific fields for post-processing
                color: color,
                issue_date: issueDate,
                issue_date_confidence: issueDateConf,
                success: true,
                preFiltered: false
              });

            } catch (err) {
              console.error(`Error processing ${fileName}:`, err);
              folderResults.push({
                fileName,
                filePath,
                folderName,
                previewUrl: null,
                originalShortCode: 'ERROR',
                originalDocType: 'Lỗi',
                newShortCode: 'GTLQ',
                newDocType: 'Giấy tờ liên quan',
                confidence: 0,
                reasoning: `Lỗi: ${err.message}`,
                metadata: {},
                success: false,
                preFiltered: false
              });
            }
          }
        }

        // Post-process GCN for THIS FOLDER immediately (giống BatchScanner)
        console.log(`\n   🔄 Post-processing GCN for folder: ${folderName}...`);
        const processedFolderResults = postProcessGCN(folderResults);

        // Update folder tab with results
        setFolderTabs(prev => prev.map(t => 
          t.path === folderPath ? { 
            ...t, 
            files: processedFolderResults, 
            processing: false, 
            complete: true 
          } : t
        ));

        // Add to allResults
        allResults.push(...processedFolderResults);

        const gcncCount = processedFolderResults.filter(r => r.newShortCode === 'GCNC').length;
        const gcnmCount = processedFolderResults.filter(r => r.newShortCode === 'GCNM').length;
        const gtlqCount = processedFolderResults.filter(r => r.newShortCode === 'GTLQ').length;
        console.log(`   ✅ Folder ${folderName} complete: ${gcncCount} GCNC, ${gcnmCount} GCNM, ${gtlqCount} GTLQ`);
      }

      setCurrentPhase('complete');
      setCurrentFile('');
      setCurrentFolder('');
      console.log('\n✅ All folders complete!');
      
      const finalGcncCount = allResults.filter(r => r.newShortCode === 'GCNC').length;
      const finalGcnmCount = allResults.filter(r => r.newShortCode === 'GCNM').length;
      const finalGtlqCount = allResults.filter(r => r.newShortCode === 'GTLQ').length;
      console.log(`📊 Total stats: ${finalGcncCount} GCNC, ${finalGcnmCount} GCNM, ${finalGtlqCount} GTLQ`);
    } catch (err) {
      console.error('Scan error:', err);
      alert('Lỗi quét: ' + err.message);
      setCurrentPhase('');
    } finally {
      setIsScanning(false);
    }
  };

  // Stop scanning
  const handleStop = () => {
    stopRef.current = true;
  };

  // Show merge modal (giống BatchScanner)
  const handleMerge = () => {
    const allResults = folderTabs.flatMap(t => t.files);
    if (allResults.length === 0) {
      alert('Chưa có kết quả nào để gộp!');
      return;
    }
    setShowMergeModal(true);
  };

  // Execute merge with options (giống BatchScanner & DesktopScanner)
  const executeMerge = async () => {
    console.log('🚀 executeMerge called:', { outputOption, mergeSuffix, outputFolder });
    
    setShowMergeModal(false);
    setMergeInProgress(true);

    try {
      // Collect all results from all folder tabs
      const allResults = folderTabs.flatMap(t => t.files);
      
      // Prepare data for mergeByShortCode API (chuẩn như các tab khác)
      const payload = allResults
        .filter(r => r.success && r.newShortCode)
        .map(r => ({ 
          filePath: r.filePath, 
          short_code: r.newShortCode,
          folder: r.folderName || path.dirname(r.filePath)
        }));

      if (payload.length === 0) {
        alert('Không có file hợp lệ để gộp.');
        setMergeInProgress(false);
        return;
      }

      console.log('📦 Merging PDFs with GCN filter...');
      console.log(`   Total files: ${payload.length}`);
      console.log(`   GCN files: ${payload.filter(f => f.short_code !== 'GTLQ').length}`);
      console.log(`   GTLQ files: ${payload.filter(f => f.short_code === 'GTLQ').length}`);

      // Group by folder
      const folderGroups = {};
      payload.forEach(item => {
        const folder = path.dirname(item.filePath);
        if (!folderGroups[folder]) {
          folderGroups[folder] = [];
        }
        folderGroups[folder].push(item);
      });

      let totalMerged = 0;
      let totalSuccess = 0;

      // Merge each folder separately (giống BatchScanner)
      for (const [folder, items] of Object.entries(folderGroups)) {
        const mergeOptions = {
          autoSave: true,
          mergeMode: outputOption === 'same_folder' ? 'root' : (outputOption === 'new_folder' ? 'new' : 'custom'),
          mergeSuffix: mergeSuffix || '_merged',
          parentFolder: folder,
          customOutputFolder: outputOption === 'custom_folder' ? outputFolder : null
        };
        
        console.log('Merge options:', mergeOptions);
        console.log('Items to merge:', items.length, 'files');
        
        try {
          const merged = await window.electronAPI.mergeByShortCode(items, mergeOptions);
          console.log('Merge result:', merged);
          const okCount = (merged || []).filter(m => m.success && !m.canceled).length;
          totalMerged += (merged || []).length;
          totalSuccess += okCount;
        } catch (mergeErr) {
          console.error('❌ Merge failed for folder:', folder, mergeErr);
          alert(`❌ Lỗi merge folder ${folder}:\n${mergeErr.message}`);
        }
      }

      alert(`✅ Gộp PDF hoàn tất!\n\nThành công: ${totalSuccess}/${totalMerged} file PDF`);
    } catch (err) {
      console.error('Merge error:', err);
      alert(`❌ Lỗi khi gộp PDF: ${err.message}`);
    } finally {
      setMergeInProgress(false);
    }
  };

  // Select custom output folder
  const handleSelectOutputFolder = async () => {
    try {
      const folder = await window.electronAPI.selectFolder();
      if (folder) {
        setOutputFolder(folder);
      }
    } catch (err) {
      console.error('Error selecting folder:', err);
    }
  };

  const gcncCount = fileResults.filter(r => r.newShortCode === 'GCNC').length;
  const gcnmCount = fileResults.filter(r => r.newShortCode === 'GCNM').length;
  const gtlqCount = fileResults.filter(r => r.newShortCode === 'GTLQ').length;
  const totalGcnCount = gcncCount + gcnmCount;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          📋 Only GCN - Chế độ đặc biệt
        </h1>
        <p className="text-gray-600">
          Quét và phân loại: GCN A3 → Đặt tên GCN | File khác → Đặt tên GTLQ (giữ nguyên thứ tự)
        </p>
      </div>

      {/* Mode Selection */}
      <div className="mb-4 bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="flex gap-4 items-center flex-wrap">
          <button
            onClick={() => {
              setScanMode('folder');
              setFiles([]);
              setResults([]);
              setTxtFilePath('');
            }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              scanMode === 'folder'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            📁 Quét thư mục
          </button>
          <button
            onClick={() => {
              setScanMode('batch');
              setFiles([]);
              setResults([]);
            }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              scanMode === 'batch'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
            }`}
          >
            📋 Quét theo danh sách
          </button>

          <div className="ml-auto flex items-center space-x-2 bg-white px-3 py-2 rounded-lg border border-gray-300">
            <input
              type="checkbox"
              id="usePreFilter"
              checked={usePreFilter}
              onChange={(e) => setUsePreFilter(e.target.checked)}
              className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            />
            <label htmlFor="usePreFilter" className="text-sm font-medium text-gray-700 cursor-pointer">
              🎨 Pre-filter (lọc màu)
            </label>
          </div>
        </div>
        <p className="text-xs text-gray-600 mt-2">
          {scanMode === 'folder' 
            ? '💡 Quét tất cả file trong 1 thư mục' 
            : '💡 Quét nhiều thư mục từ file .txt (mỗi dòng 1 đường dẫn)'}
          {usePreFilter && (
            <span className="ml-2 text-green-600 font-medium">
              • Pre-filter BẬT: Chỉ quét file có màu đỏ/hồng (tiết kiệm ~85% API)
            </span>
          )}
          {!usePreFilter && (
            <span className="ml-2 text-blue-600 font-medium">
              • Pre-filter TẮT: Quét tất cả file (chính xác 100%, tốn API hơn)
            </span>
          )}
        </p>
      </div>

      {/* Controls */}
      <div className="mb-6 bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <div className="flex flex-wrap gap-3 items-center">
          {scanMode === 'folder' ? (
            <button
              onClick={handleSelectFolder}
              disabled={isScanning}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              📁 Chọn thư mục
            </button>
          ) : (
            <>
              <button
                onClick={handleSelectTxtFile}
                disabled={isScanning || isLoadingFolders}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                📄 Chọn file .txt
              </button>
              {txtFilePath && (
                <>
                  <span className="text-sm text-gray-600">
                    {txtFilePath.split(/[/\\]/).pop()}
                  </span>
                  <button
                    onClick={handleLoadFolders}
                    disabled={isScanning || isLoadingFolders || !txtFilePath}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoadingFolders ? '⏳ Đang tìm...' : '🔍 Tìm kiếm thư mục'}
                  </button>
                </>
              )}
            </>
          )}

          <button
            onClick={handleStartScan}
            disabled={files.length === 0 || isScanning}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isScanning ? '⏳ Đang quét...' : '▶️ Bắt đầu quét'}
          </button>

          {isScanning && (
            <button
              onClick={handleStop}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium shadow-sm transition-colors"
            >
              ⏹️ Dừng
            </button>
          )}

          {folderTabs.length > 0 && folderTabs.some(t => t.complete) && !isScanning && (
            <button
              onClick={handleMerge}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium shadow-sm transition-colors"
            >
              📚 Gộp PDF
            </button>
          )}

          <div className="ml-auto text-sm text-gray-600">
            <span className="font-medium">Engine:</span> {ocrEngine}
          </div>
        </div>
      </div>

      {/* Progress - Detailed */}
      {isScanning && (
        <div className="mb-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-lg p-5 shadow-sm">
          {/* Folder Progress */}
          {folderProgress.total > 0 && (
            <div className="mb-3 p-3 bg-purple-50 border border-purple-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-purple-700 font-semibold">📁 Thư mục:</span>
                  <span className="text-purple-900 font-bold">{folderProgress.current} / {folderProgress.total}</span>
                </div>
                {currentFolder && (
                  <span className="text-sm text-purple-700 font-medium">{currentFolder}</span>
                )}
              </div>
              <div className="mt-2 w-full bg-purple-200 rounded-full h-2">
                <div
                  className="bg-purple-600 h-2 rounded-full transition-all"
                  style={{ width: `${(folderProgress.current / folderProgress.total) * 100}%` }}
                />
              </div>
            </div>
          )}

          {/* Phase indicator */}
          <div className="mb-4">
            <div className="flex items-center space-x-3">
              {currentPhase === 'prefilter' && (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  <span className="text-lg font-bold text-blue-900">🎨 Phase 1: Pre-filter (Lọc màu sắc)</span>
                </>
              )}
              {currentPhase === 'scanning' && (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-green-600"></div>
                  <span className="text-lg font-bold text-green-900">🤖 Phase 2: AI Scanning</span>
                </>
              )}
              {currentPhase === 'complete' && (
                <>
                  <span className="text-2xl">✅</span>
                  <span className="text-lg font-bold text-green-900">Hoàn thành!</span>
                </>
              )}
            </div>
          </div>

          {/* Phase 1 Stats */}
          {(currentPhase === 'prefilter' || currentPhase === 'scanning') && (
            <div className="mb-3 p-3 bg-white rounded-lg border border-blue-200">
              <div className="text-sm font-medium text-gray-700 mb-2">📊 Phase 1 - Kết quả lọc màu:</div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="flex items-center">
                  <span className="text-green-600 font-semibold">🟢 GCN candidates:</span>
                  <span className="ml-2 font-bold text-green-700">{phaseStats.passed} files</span>
                </div>
                <div className="flex items-center">
                  <span className="text-gray-600 font-semibold">⏭️  Skipped:</span>
                  <span className="ml-2 font-bold text-gray-700">{phaseStats.skipped} files</span>
                </div>
              </div>
            </div>
          )}

          {/* Phase 2 Progress */}
          {currentPhase === 'scanning' && (
            <>
              <div className="mb-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold text-gray-700">
                    🔍 Đang quét AI: {progress.current} / {progress.total}
                  </span>
                  <span className="text-sm font-bold text-green-700">
                    {progress.total > 0 ? Math.round((progress.current / progress.total) * 100) : 0}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-green-500 to-emerald-600 h-3 rounded-full transition-all duration-300 shadow-sm"
                    style={{ width: `${progress.total > 0 ? (progress.current / progress.total) * 100 : 0}%` }}
                  />
                </div>
              </div>

              {/* Current file */}
              {currentFile && (
                <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm">
                  <span className="text-yellow-800 font-medium">📄 File hiện tại:</span>
                  <span className="ml-2 text-yellow-900 font-mono text-xs">{currentFile}</span>
                </div>
              )}

              {/* Time estimate */}
              {progress.current > 0 && progress.total > 0 && (
                <div className="mt-2 text-xs text-gray-600">
                  ⏱️ Ước tính: ~{Math.ceil((progress.total - progress.current) * 15)} giây còn lại
                </div>
              )}
            </>
          )}

          {/* Summary */}
          {currentPhase === 'complete' && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="text-sm font-medium text-green-800">
                🎉 Đã quét xong {progress.total} files!
              </div>
            </div>
          )}
        </div>
      )}

      {/* Folder List */}
      {folderList.length > 0 && files.length > 0 && !isScanning && (
        <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="font-semibold text-blue-900 mb-2">
            📁 {folderList.length} thư mục - {files.length} files
          </div>
          <div className="text-sm text-blue-700 max-h-32 overflow-y-auto">
            {folderList.map((folder, idx) => (
              <div key={idx} className="py-1">
                {idx + 1}. {folder.name} ({folder.path})
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Folder Tabs (giống BatchScanner) */}
      {folderTabs.length > 0 && (
        <div className="mb-4 border-b border-gray-200">
          <div className="flex overflow-x-auto">
            {folderTabs.map((tab) => (
              <button
                key={tab.path}
                onClick={() => setActiveFolder(tab.path)}
                className={`
                  px-4 py-2 text-sm font-medium whitespace-nowrap border-b-2 transition-colors
                  ${activeFolder === tab.path
                    ? 'border-blue-500 text-blue-600 bg-blue-50'
                    : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }
                  ${tab.processing ? 'animate-pulse' : ''}
                `}
              >
                {tab.processing && '⏳ '}
                {tab.complete && '✅ '}
                {tab.name}
                {tab.files.length > 0 && (
                  <span className="ml-2 text-xs bg-gray-200 px-2 py-0.5 rounded-full">
                    {tab.files.length}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Stats - Compact */}
      {fileResults.length > 0 && (
        <div className="mb-3 flex gap-2 text-sm">
          <div className="flex-1 bg-white border border-gray-200 rounded-lg px-3 py-2">
            <span className="font-bold text-gray-900">{fileResults.length}</span>
            <span className="text-gray-600 ml-1">files</span>
          </div>
          <div className="flex-1 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
            <span className="font-bold text-red-600">{gcncCount}</span>
            <span className="text-red-700 ml-1">GCNC</span>
          </div>
          <div className="flex-1 bg-pink-50 border border-pink-200 rounded-lg px-3 py-2">
            <span className="font-bold text-pink-600">{gcnmCount}</span>
            <span className="text-pink-700 ml-1">GCNM</span>
          </div>
          <div className="flex-1 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
            <span className="font-bold text-gray-600">{gtlqCount}</span>
            <span className="text-gray-700 ml-1">GTLQ</span>
          </div>
        </div>
      )}

      {/* Results Table */}
      {fileResults.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    #
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Thư mục
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    File
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Phân loại gốc
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    → Tên mới
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                    Preview
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {fileResults.map((result, idx) => (
                  <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-4 py-3 text-sm text-gray-900">{idx + 1}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{result.folderName || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{result.fileName}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        result.originalShortCode === 'GCNC' || result.originalShortCode === 'GCNM' || result.originalShortCode === 'GCN'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {result.originalShortCode}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        result.newShortCode !== 'GTLQ'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {result.newShortCode}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {result.previewUrl && (
                        <img
                          src={result.previewUrl}
                          alt={result.fileName}
                          className="w-16 h-20 object-cover rounded border border-gray-300"
                        />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty state */}
      {files.length === 0 && !isScanning && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <div className="text-6xl mb-4">
            {scanMode === 'folder' ? '📁' : '📋'}
          </div>
          <div className="text-xl font-medium text-gray-900 mb-2">
            {scanMode === 'folder' ? 'Chưa chọn thư mục' : 'Chưa chọn file .txt'}
          </div>
          <div className="text-gray-600">
            {scanMode === 'folder' 
              ? 'Nhấn "Chọn thư mục" để bắt đầu'
              : 'Nhấn "Chọn file .txt" để bắt đầu'}
          </div>
        </div>
      )}

      {/* Merge Options Modal (giống BatchScanner & DesktopScanner) */}
      {showMergeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-lg w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">⚙️ Tùy chọn gộp PDF</h3>
            
            <div className="space-y-4">
              {/* Output location */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  📁 Vị trí lưu file PDF
                </label>
                <div className="space-y-2">
                  <label className="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                    <input
                      type="radio"
                      name="outputOption"
                      value="same_folder"
                      checked={outputOption === 'same_folder'}
                      onChange={(e) => setOutputOption(e.target.value)}
                      className="text-blue-600"
                    />
                    <span className="text-sm">Cùng thư mục với file gốc</span>
                  </label>
                  
                  <label className="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                    <input
                      type="radio"
                      name="outputOption"
                      value="new_folder"
                      checked={outputOption === 'new_folder'}
                      onChange={(e) => setOutputOption(e.target.value)}
                      className="text-blue-600"
                    />
                    <span className="text-sm">Tạo thư mục mới (tên + suffix)</span>
                  </label>
                  
                  <label className="flex items-center space-x-2 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                    <input
                      type="radio"
                      name="outputOption"
                      value="custom_folder"
                      checked={outputOption === 'custom_folder'}
                      onChange={(e) => setOutputOption(e.target.value)}
                      className="text-blue-600"
                    />
                    <span className="text-sm">Chọn thư mục tùy chỉnh</span>
                  </label>
                </div>
              </div>

              {/* Suffix for new folder */}
              {outputOption === 'new_folder' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    🏷️ Hậu tố tên thư mục
                  </label>
                  <input
                    type="text"
                    value={mergeSuffix}
                    onChange={(e) => setMergeSuffix(e.target.value)}
                    placeholder="_merged"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-xs text-gray-600 mt-1">
                    VD: Thư mục "HSDT_001" → "HSDT_001{mergeSuffix}"
                  </p>
                </div>
              )}

              {/* Custom folder selection */}
              {outputOption === 'custom_folder' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    📂 Thư mục tùy chỉnh
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={outputFolder}
                      readOnly
                      placeholder="Chọn thư mục..."
                      className="flex-1 px-3 py-2 border rounded-lg bg-gray-50"
                    />
                    <button
                      onClick={handleSelectOutputFolder}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Chọn
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Buttons */}
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowMergeModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Hủy
              </button>
              <button
                onClick={executeMerge}
                disabled={outputOption === 'custom_folder' && !outputFolder}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ✅ Gộp PDF
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Merge in progress overlay */}
      {mergeInProgress && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
              <span className="text-lg font-medium">Đang gộp PDF...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default OnlyGCNScanner;
