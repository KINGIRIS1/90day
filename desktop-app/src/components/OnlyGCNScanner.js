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
  const usePreFilter = true; // ALWAYS ON - Only GCN mode always uses pre-filter
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
  const [batchMode, setBatchMode] = useState('sequential'); // 'sequential', 'fixed', 'smart'

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

  // Modal states
  const [zoomModal, setZoomModal] = useState({ show: false, image: null, fileName: '' });
  const [editModal, setEditModal] = useState({ show: false, file: null, newName: '' });

  React.useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const engine = await window.electronAPI.getConfig('ocrEngine');
      setOcrEngine(engine || 'gemini-flash-lite');
      
      // Load batch mode (giống BatchScanner)
      const savedBatchMode = await window.electronAPI.getConfig('batchMode');
      if (savedBatchMode) {
        setBatchMode(savedBatchMode);
        console.log(`📦 OnlyGCN - Loaded batch mode: ${savedBatchMode}`);
      }
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
      setFolderTabs([]);
      setActiveFolder(null);
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
      setFolderTabs([]);
      setActiveFolder(null);
      
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

  // Process folder batch (COPY Y NGUYÊN từ BatchScanner)
  const processFolderBatch = async (imagePaths, mode, engineType, folderName) => {
    console.log(`\n${'='.repeat(80)}`);
    console.log(`🚀 FOLDER BATCH PROCESSING: ${imagePaths.length} files`);
    console.log(`   Folder: ${folderName}`);
    console.log(`   Mode: ${mode}`);
    console.log(`   Engine: ${engineType}`);
    console.log(`${'='.repeat(80)}\n`);
    
    if (!window.electronAPI) {
      console.error('❌ Electron API not available');
      return null;
    }
    
    // Separate image and PDF files
    const imageFiles = imagePaths.filter(path => 
      /\.(jpg|jpeg|png|gif|bmp)$/i.test(path)
    );
    const pdfFiles = imagePaths.filter(path => 
      /\.pdf$/i.test(path)
    );
    
    console.log(`📊 Files breakdown: ${imageFiles.length} images, ${pdfFiles.length} PDFs`);
    
    // Process images first (batch mode supports images only)
    if (imageFiles.length === 0 && pdfFiles.length === 0) {
      console.error('❌ No valid files found');
      return null;
    }
    
    try {
      // Call batch processor via IPC (images only)
      const batchResult = await window.electronAPI.batchProcessDocuments({
        mode: mode,
        imagePaths: imageFiles,
        ocrEngine: engineType
      });
      
      if (!batchResult.success) {
        console.error('❌ Folder batch failed:', batchResult.error);
        return null;
      }
      
      console.log(`✅ Folder batch complete: ${batchResult.results.length} results`);
      
      // DEBUG: Log first result structure
      if (batchResult.results.length > 0) {
        console.log(`🔍 DEBUG - First batch result:`, batchResult.results[0]);
      }
      
      // Map batch results to OnlyGCNScanner format (GIỐNG BatchScanner)
      const mappedResults = [];
      for (const batchItem of batchResult.results) {
        const fileName = batchItem.file_name;
        const filePath = batchItem.file_path;
        
        // DEBUG: Log item structure
        console.log(`🔍 Mapping item: fileName=${fileName}, filePath=${filePath ? 'OK' : 'UNDEFINED'}`);
        
        // Validate filePath
        if (!filePath) {
          console.error(`⚠️ Missing file_path for item:`, batchItem);
          continue;
        }
        
        // Generate preview (with validation)
        let previewUrl = null;
        try {
          if (filePath && typeof filePath === 'string') {
            previewUrl = await window.electronAPI.readImageDataUrl(filePath);
          }
        } catch (e) {
          console.error(`Preview error for ${fileName}:`, e);
        }
        
        // Check if this is a PDF page (from batch processor)
        const isPdfPage = batchItem.is_pdf_page === true;
        const pdfPage = batchItem.pdf_page || null;
        const originalPdf = batchItem.original_pdf || null;
        
        // Update fileName for PDF pages
        let displayFileName = fileName;
        if (isPdfPage && pdfPage && originalPdf) {
          const pdfName = originalPdf.split(/[/\\]/).pop();
          displayFileName = `${pdfName} (Page ${pdfPage})`;
        }
        
        mappedResults.push({
          filePath: originalPdf || filePath,
          fileName: displayFileName,
          folderName: folderName,
          short_code: batchItem.short_code || 'UNKNOWN',
          doc_type: batchItem.short_code || 'UNKNOWN',
          confidence: batchItem.confidence || 0.5,
          previewUrl: previewUrl,
          success: true,
          method: `batch_${mode}`,
          metadata: batchItem.metadata || {},
          // GCN fields
          color: batchItem.metadata?.color || null,
          issue_date: batchItem.metadata?.issue_date || null,
          issue_date_confidence: batchItem.metadata?.issue_date_confidence || null,
          // For compatibility
          newShortCode: batchItem.short_code || 'UNKNOWN',
          newDocType: batchItem.short_code || 'UNKNOWN',
          originalShortCode: batchItem.short_code || 'UNKNOWN',
          originalDocType: batchItem.short_code || 'UNKNOWN',
          reasoning: batchItem.reasoning || '',
          preFiltered: false,
          // PDF info
          isPdfPage: isPdfPage,
          pdfPage: pdfPage,
          originalPdf: originalPdf
        });
      }
      
      // Process PDF files separately (single-file mode)
      if (pdfFiles.length > 0) {
        console.log(`\n📄 Processing ${pdfFiles.length} PDF files...`);
        
        for (const pdfPath of pdfFiles) {
          try {
            const fileName = pdfPath.split(/[/\\]/).pop();
            console.log(`   Processing PDF: ${fileName}`);
            
            // Call single-file OCR for PDF
            const result = await window.electronAPI.scanDocument({
              filePath: pdfPath,
              ocrEngine: engineType
            });
            
            if (result.success) {
              // Check if this is a multi-page PDF
              if (result.is_multi_page_pdf && result.all_pages) {
                console.log(`      📄 Multi-page PDF: ${result.all_pages.length} pages`);
                
                // Process each page separately
                for (const pageResult of result.all_pages) {
                  const pageFileName = `${fileName} (Page ${pageResult.pdf_page})`;
                  
                  // Generate preview for PDF
                  let previewUrl = null;
                  try {
                    previewUrl = await window.electronAPI.readImageDataUrl(pdfPath);
                  } catch (e) {
                    console.warn(`Preview error for PDF ${pageFileName}`);
                  }
                  
                  mappedResults.push({
                    filePath: pdfPath,
                    fileName: pageFileName,
                    folderName: folderName,
                    short_code: pageResult.short_code || 'UNKNOWN',
                    doc_type: pageResult.doc_type || pageResult.short_code || 'UNKNOWN',
                    confidence: pageResult.confidence || 0.5,
                    previewUrl: previewUrl,
                    success: true,
                    method: 'single_pdf_page',
                    metadata: pageResult.metadata || {},
                    color: pageResult.metadata?.color || pageResult.color || null,
                    issue_date: pageResult.metadata?.issue_date || pageResult.issue_date || null,
                    issue_date_confidence: pageResult.metadata?.issue_date_confidence || null,
                    newShortCode: pageResult.short_code || 'UNKNOWN',
                    newDocType: pageResult.doc_type || pageResult.short_code || 'UNKNOWN',
                    originalShortCode: pageResult.short_code || 'UNKNOWN',
                    originalDocType: pageResult.doc_type || pageResult.short_code || 'UNKNOWN',
                    reasoning: pageResult.reasoning || '',
                    preFiltered: false,
                    isPdf: true,
                    pdfPage: pageResult.pdf_page,
                    totalPages: pageResult.total_pages,
                    originalPdf: pdfPath
                  });
                  
                  console.log(`      ✅ Page ${pageResult.pdf_page}/${pageResult.total_pages}: ${pageResult.short_code}`);
                }
              } else {
                // Single page or non-PDF result
                // Generate preview for PDF
                let previewUrl = null;
                try {
                  previewUrl = await window.electronAPI.readImageDataUrl(pdfPath);
                } catch (e) {
                  console.warn(`Preview error for PDF ${fileName}`);
                }
                
                mappedResults.push({
                  filePath: pdfPath,
                  fileName: fileName,
                  folderName: folderName,
                  short_code: result.short_code || 'UNKNOWN',
                  doc_type: result.doc_type || result.short_code || 'UNKNOWN',
                  confidence: result.confidence || 0.5,
                  previewUrl: previewUrl,
                  success: true,
                  method: 'single_pdf',
                  metadata: result.metadata || {},
                  color: result.metadata?.color || result.color || null,
                  issue_date: result.metadata?.issue_date || result.issue_date || null,
                  issue_date_confidence: result.metadata?.issue_date_confidence || null,
                  newShortCode: result.short_code || 'UNKNOWN',
                  newDocType: result.doc_type || result.short_code || 'UNKNOWN',
                  originalShortCode: result.short_code || 'UNKNOWN',
                  originalDocType: result.doc_type || result.short_code || 'UNKNOWN',
                  reasoning: result.reasoning || '',
                  preFiltered: false,
                  isPdf: true
                });
                
                console.log(`      ✅ ${fileName}: ${result.short_code}`);
              }
            } else {
              console.error(`      ❌ ${fileName}: ${result.error}`);
            }
          } catch (pdfError) {
            console.error(`   ❌ Error processing PDF:`, pdfError);
          }
        }
      }
      
      return mappedResults;
      
    } catch (error) {
      console.error('❌ Folder batch error:', error);
      return null;
    }
  };

  // Post-process GCN: Classify into GCNC/GCNM (COPY Y NGUYÊN từ BatchScanner)
  const postProcessGCN = (results) => {
    try {
      console.log('🔄 Post-processing GCN (DATE-BASED classification)...');
      
      // Step 1: Normalize GCNM/GCNC → GCN (GIỐNG BatchScanner)
      const normalizedResults = results.map(r => {
        if (r.short_code === 'GCNM' || r.short_code === 'GCNC' || r.newShortCode === 'GCNM' || r.newShortCode === 'GCNC') {
          console.log(`🔄 Converting ${r.short_code || r.newShortCode} → GCN for file: ${r.fileName}`);
          return { ...r, short_code: 'GCN', newShortCode: 'GCN', original_short_code: r.short_code || r.newShortCode };
        }
        // Sync short_code and newShortCode
        if (!r.short_code) r.short_code = r.newShortCode;
        if (!r.newShortCode) r.newShortCode = r.short_code;
        return r;
      });
      
      // Step 2: Find all GCN documents
      const allGcnDocs = normalizedResults.filter(r => r.short_code === 'GCN');
      
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
      
      if (hasRedAndPink) {
        console.log(`  🎨 Mixed colors → Classify by color`);
        groupsArray.forEach(group => {
          const classification = (group.color === 'red' || group.color === 'orange') ? 'GCNC' : 'GCNM';
          group.files.forEach(file => {
            const idx = normalizedResults.findIndex(r => r.fileName === file.fileName);
            if (idx >= 0) {
              normalizedResults[idx].short_code = classification;
              normalizedResults[idx].newShortCode = classification;
              normalizedResults[idx].doc_type = classification;
              normalizedResults[idx].newDocType = classification === 'GCNC' ? 'Giấy chứng nhận (Chung)' : 'Giấy chứng nhận (Mẫu)';
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
              const resIdx = normalizedResults.findIndex(r => r.fileName === file.fileName);
              if (resIdx >= 0) {
                normalizedResults[resIdx].short_code = classification;
                normalizedResults[resIdx].newShortCode = classification;
                normalizedResults[resIdx].doc_type = classification;
                normalizedResults[resIdx].newDocType = classification;
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
              const idx = normalizedResults.findIndex(r => r.fileName === file.fileName);
              if (idx >= 0) {
                normalizedResults[idx].short_code = 'GCNC';
                normalizedResults[idx].newShortCode = 'GCNC';
                normalizedResults[idx].doc_type = 'GCNC';
                normalizedResults[idx].newDocType = 'Giấy chứng nhận (Chung)';
                console.log(`      ✅ ${file.fileName} → GCNC (fallback)`);
              }
            });
          } else if (groupsArray.length > 1) {
            console.log(`  ⚠️ Multiple groups but no dates → Cannot classify, keeping as GCN`);
          }
        }
      }
      
      console.log('✅ Post-processing complete');
      return normalizedResults;
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
    setFolderTabs([]);
    setActiveFolder(null);
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
        let gcnCandidates = [];
        let skipped = [];
        if (usePreFilter && hasPreFilter) {
          setCurrentPhase('prefilter');
          setCurrentFile(`Đang phân tích màu sắc thư mục ${folderName}...`);
          
          const preFilterStart = Date.now();
          
          // Separate PDF and image files
          const pdfFiles = folderFiles.filter(f => /\.pdf$/i.test(f));
          const imageFiles = folderFiles.filter(f => /\.(jpg|jpeg|png|gif|bmp)$/i.test(f));
          
          console.log(`   📊 Files: ${imageFiles.length} images, ${pdfFiles.length} PDFs`);
          
          // Pre-filter image files only
          let preFilteredImages = [];
          let skippedImages = [];
          
          if (imageFiles.length > 0) {
            const preFilterResults = await window.electronAPI.preFilterGCNFiles(imageFiles);
            preFilteredImages = preFilterResults.passed || [];
            skippedImages = preFilterResults.skipped || [];
          }
          
          // PDF files always pass pre-filter (will be scanned)
          gcnCandidates = [...preFilteredImages, ...pdfFiles];
          skipped = skippedImages;
          
          const preFilterTime = ((Date.now() - preFilterStart) / 1000).toFixed(1);
          console.log(`   🎨 Pre-filter: ${gcnCandidates.length} files (${preFilteredImages.length} images + ${pdfFiles.length} PDFs), ${skipped.length} skipped (${preFilterTime}s)`);
        } else {
          console.log(`   ⚡ Pre-filter OFF: Scanning all ${folderFiles.length} files`);
          gcnCandidates = folderFiles;
          skipped = [];
        }
        
        // Add skipped files as GTLQ - VẪN HIỂN THỊ để user có thể sửa lại
        console.log(`   💡 Adding ${skipped.length} pre-filtered files as GTLQ (vẫn hiển thị để có thể sửa)`);
        for (const filePath of skipped) {
          const fileName = filePath.split(/[/\\]/).pop();
          
          // Load preview for GTLQ files
          let previewUrl = null;
          try {
            previewUrl = await window.electronAPI.readImageDataUrl(filePath);
          } catch (e) {
            console.warn(`Failed to load preview for GTLQ file: ${fileName}`);
          }
          
          folderResults.push({
            fileName,
            filePath,
            folderName,
            previewUrl,  // Now has preview!
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

          // 🚀 CHECK IF BATCH PROCESSING SHOULD BE USED (COPY từ BatchScanner)
          const isGeminiEngine = ['gemini-flash', 'gemini-flash-lite', 'gemini-flash-hybrid', 'gemini-flash-text'].includes(ocrEngine);
          const shouldUseBatch = (
            isGeminiEngine &&
            (batchMode === 'fixed' || batchMode === 'smart') &&
            gcnCandidates.length >= 2
          );

          if (shouldUseBatch) {
            console.log(`\n🚀 BATCH MODE for folder: ${folderName}`);
            console.log(`   Files: ${gcnCandidates.length}, Mode: ${batchMode}`);
            
            // Use batch processing (COPY Y NGUYÊN từ BatchScanner)
            const batchResults = await processFolderBatch(gcnCandidates, batchMode, ocrEngine, folderName);
            
            if (batchResults && batchResults.length > 0) {
              console.log(`✅ Folder batch success: ${batchResults.length} files`);
              
              // Add all batch results
              folderResults.push(...batchResults);
              
              // Update progress
              setProgress({ current: gcnCandidates.length, total: gcnCandidates.length });
            } else {
              const errorMsg = batchResults?.error || 'Batch returned no results';
              console.error(`⚠️ BATCH FAILED for folder ${folderName}:`, errorMsg);
              console.warn('🔄 FALLBACK: Switching to sequential processing for this folder...');
              console.log(`📋 Files in this folder will be scanned one by one (slower but reliable)`);
              // Fall through to sequential
            }
          }

          // FALLBACK: Single-file processing (if not batch or batch failed)
          if (!shouldUseBatch || folderResults.length === 0) {
            console.log(`   📄 Single-file mode (${gcnCandidates.length} files)`);
            
            for (let i = 0; i < gcnCandidates.length; i++) {
              if (stopRef.current) break;

              const filePath = gcnCandidates[i];
              const fileName = filePath.split(/[/\\]/).pop();

              setProgress({ current: i + 1, total: gcnCandidates.length });
              setCurrentFile(fileName);
              console.log(`      [${i + 1}/${gcnCandidates.length}] ${fileName}`);

              try {
                const result = await window.electronAPI.processDocumentOffline(filePath);
                
                let previewUrl = null;
                try {
                  if (/\.(png|jpg|jpeg|gif|bmp)$/i.test(fileName)) {
                    previewUrl = await window.electronAPI.readImageDataUrl(filePath);
                  }
                } catch (e) {
                  console.warn('Preview error:', fileName);
                }

                // Use AI classification directly (same as BatchScanner)
                const shortCode = result.short_code || result.classification || 'UNKNOWN';
                let newShortCode = shortCode;
                let newDocType = result.doc_type || shortCode;

                const meta = result.metadata || {};
                const color = meta.color || result.color || null;
                const issueDate = meta.issue_date || result.issue_date || null;
                const issueDateConf = meta.issue_date_confidence || result.issue_date_confidence || null;

                if (shortCode === 'GCNC' || shortCode === 'GCNM' || shortCode === 'GCN') {
                  console.log(`      📊 color=${color || 'null'}, date=${issueDate || 'null'}`);
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
                  color: color,
                  issue_date: issueDate,
                  issue_date_confidence: issueDateConf,
                  success: true,
                  preFiltered: false,
                  method: 'single'
                });

              } catch (err) {
                console.error(`Error: ${fileName}:`, err);
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
                  preFiltered: false,
                  method: 'single_error'
                });
              }
            }
          }
        }

        // No pairing logic needed - accept AI classification as-is (same as BatchScanner)

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
        const otherCount = processedFolderResults.filter(r => r.newShortCode !== 'GCNC' && r.newShortCode !== 'GCNM').length;
        console.log(`   ✅ Folder ${folderName} complete: ${gcncCount} GCNC, ${gcnmCount} GCNM, ${otherCount} other docs`);
      }

      setCurrentPhase('complete');
      setCurrentFile('');
      setCurrentFolder('');
      console.log('\n✅ All folders complete!');
      
      const finalGcncCount = allResults.filter(r => r.newShortCode === 'GCNC').length;
      const finalGcnmCount = allResults.filter(r => r.newShortCode === 'GCNM').length;
      const finalOtherCount = allResults.filter(r => r.newShortCode !== 'GCNC' && r.newShortCode !== 'GCNM').length;
      console.log(`📊 Total stats: ${finalGcncCount} GCNC, ${finalGcnmCount} GCNM, ${finalOtherCount} other docs`);
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
          Pre-filter file A3 trước khi quét → Phân loại tự động (giống Batch Mode)
        </p>
      </div>

      {/* Mode Selection - Compact */}
      <div className="mb-2 bg-gray-50 rounded-lg p-2 border border-gray-200 flex gap-2 items-center">
        <button
          onClick={() => {
            setScanMode('folder');
            setFiles([]);
            setFolderTabs([]);
            setActiveFolder(null);
            setTxtFilePath('');
          }}
          className={`px-3 py-1.5 rounded text-sm transition-colors ${
            scanMode === 'folder'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
          }`}
        >
          Thư mục
        </button>
        <button
          onClick={() => {
            setScanMode('batch');
            setFiles([]);
            setFolderTabs([]);
            setActiveFolder(null);
          }}
          className={`px-3 py-1.5 rounded text-sm transition-colors ${
            scanMode === 'batch'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
          }`}
        >
          Danh sách
        </button>
        
        <div className="ml-auto text-xs text-green-600 font-medium">
          🎨 Pre-filter: LUÔN BẬT
        </div>
      </div>

      {/* Controls - Compact */}
      <div className="mb-2 bg-white rounded-lg p-2 border border-gray-200 flex flex-wrap gap-2 items-center">
        {scanMode === 'folder' ? (
          <button
            onClick={handleSelectFolder}
            disabled={isScanning}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors disabled:opacity-50"
          >
            📁 Chọn
          </button>
        ) : (
          <>
            <button
              onClick={handleSelectTxtFile}
              disabled={isScanning || isLoadingFolders}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors disabled:opacity-50"
            >
              📄 File
            </button>
            {txtFilePath && (
              <>
                <span className="text-xs text-gray-600 truncate max-w-xs">
                  {txtFilePath.split(/[/\\]/).pop()}
                </span>
                <button
                  onClick={handleLoadFolders}
                  disabled={isScanning || isLoadingFolders || !txtFilePath}
                  className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded text-sm transition-colors disabled:opacity-50"
                >
                  {isLoadingFolders ? '⏳' : '🔍'}
                </button>
              </>
            )}
          </>
        )}

        <button
          onClick={handleStartScan}
          disabled={files.length === 0 || isScanning}
          className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded text-sm transition-colors disabled:opacity-50"
        >
          {isScanning ? '⏳' : '▶️ Quét'}
        </button>

        {isScanning && (
          <button
            onClick={handleStop}
            className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
          >
            ⏹
          </button>
        )}

        {folderTabs.length > 0 && folderTabs.some(t => t.complete) && !isScanning && (
          <button
            onClick={handleMerge}
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-sm transition-colors"
          >
            📚 Gộp
          </button>
        )}

        <div className="ml-auto text-sm text-gray-600">
          <span className="font-medium">Engine:</span> {ocrEngine}
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

          {/* Compact Progress */}
          {currentPhase === 'scanning' && (
            <div className="mb-2 p-2 bg-white rounded-lg border border-gray-200">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="font-medium text-gray-700 truncate">
                  {currentFile || 'Processing...'}
                </span>
                <span className="text-gray-600 ml-2">{progress.current}/{progress.total}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div
                  className="bg-green-500 h-1.5 rounded-full transition-all"
                  style={{ width: `${progress.total > 0 ? (progress.current / progress.total) * 100 : 0}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Folder List - Compact */}
      {folderList.length > 0 && files.length > 0 && !isScanning && (
        <div className="mb-3 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
          <div className="text-sm font-medium text-blue-900">
            📁 {folderList.length} thư mục, {files.length} files
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

      {/* Results Grid View - Hiển thị TẤT CẢ (bao gồm GTLQ) */}
      {fileResults.length > 0 && (() => {
        // KHÔNG filter, hiển thị tất cả để user có thể sửa lại
        const allResults = fileResults;
        return allResults.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
            {allResults.map((result, idx) => (
              <div key={idx} className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
                {/* Preview Image */}
                <div className="relative aspect-[3/4] bg-gray-100">
                  {result.previewUrl ? (
                    <img
                      src={result.previewUrl}
                      alt={result.fileName}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      <span className="text-4xl">📄</span>
                    </div>
                  )}
                  
                  {/* Badge */}
                  <div className="absolute top-1 right-1">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      result.newShortCode === 'GCNC'
                        ? 'bg-red-500 text-white'
                        : result.newShortCode === 'GCNM'
                        ? 'bg-pink-500 text-white'
                        : result.newShortCode === 'GTLQ'
                        ? 'bg-gray-500 text-white'
                        : 'bg-blue-500 text-white'
                    }`}>
                      {result.newShortCode}
                    </span>
                  </div>
                  
                  {/* Page number indicator */}
                  <div className="absolute top-1 left-1">
                    <span className="bg-black bg-opacity-60 text-white px-1.5 py-0.5 rounded text-xs">
                      #{idx + 1}
                    </span>
                  </div>
                </div>
                
                {/* Info */}
                <div className="p-2">
                  <div className="text-xs text-gray-900 truncate font-medium" title={result.fileName}>
                    {result.fileName}
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-500">
                      {result.issue_date || 'No date'}
                    </span>
                    <span className="text-xs text-gray-400">
                      {Math.round(result.confidence * 100)}%
                    </span>
                  </div>
                  
                  {/* Action buttons */}
                  <div className="flex gap-1 mt-2">
                    <button 
                      onClick={() => setZoomModal({ show: true, image: result.previewUrl, fileName: result.fileName })}
                      className="flex-1 px-2 py-1 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded text-xs"
                      title="Zoom"
                    >
                      🔍
                    </button>
                    <button 
                      onClick={() => setEditModal({ show: true, file: result, newName: result.newShortCode })}
                      className="flex-1 px-2 py-1 bg-gray-50 hover:bg-gray-100 text-gray-600 rounded text-xs"
                      title="Sửa tên"
                    >
                      ✏️
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            Không có GCN nào được tìm thấy
          </div>
        );
      })()}

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

      {/* Zoom Modal */}
      {zoomModal.show && (
        <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50" onClick={() => setZoomModal({ show: false, image: null, fileName: '' })}>
          <div className="relative max-w-6xl max-h-[90vh] p-4">
            <button
              onClick={() => setZoomModal({ show: false, image: null, fileName: '' })}
              className="absolute top-2 right-2 bg-white rounded-full p-2 hover:bg-gray-100 shadow-lg z-10"
            >
              ✕
            </button>
            <div className="bg-white rounded-lg p-2">
              <div className="text-sm font-medium text-gray-700 mb-2 px-2">{zoomModal.fileName}</div>
              <img
                src={zoomModal.image}
                alt={zoomModal.fileName}
                className="max-w-full max-h-[80vh] object-contain"
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          </div>
        </div>
      )}

      {/* Edit Name Modal */}
      {editModal.show && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Sửa phân loại</h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">File:</label>
              <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                {editModal.file?.fileName}
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Phân loại mới:</label>
              <select
                value={editModal.newName}
                onChange={(e) => setEditModal({ ...editModal, newName: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="GCNC">GCNC - Giấy chứng nhận (Chung)</option>
                <option value="GCNM">GCNM - Giấy chứng nhận (Mẫu)</option>
                <option value="GTLQ">GTLQ - Giấy tờ liên quan</option>
              </select>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setEditModal({ show: false, file: null, newName: '' })}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Hủy
              </button>
              <button
                onClick={() => {
                  // Update the file classification in folderTabs
                  setFolderTabs(prev => prev.map(tab => {
                    if (tab.path === activeFolder) {
                      return {
                        ...tab,
                        files: tab.files.map(f => 
                          f.fileName === editModal.file.fileName
                            ? { 
                                ...f, 
                                newShortCode: editModal.newName,
                                newDocType: editModal.newName === 'GCNC' ? 'Giấy chứng nhận (Chung)' :
                                           editModal.newName === 'GCNM' ? 'Giấy chứng nhận (Mẫu)' :
                                           'Giấy tờ liên quan'
                              }
                            : f
                        )
                      };
                    }
                    return tab;
                  }));
                  setEditModal({ show: false, file: null, newName: '' });
                }}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Lưu
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default OnlyGCNScanner;
