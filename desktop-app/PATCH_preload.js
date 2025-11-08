// ========================================
// PATCH for electron/preload.js
// Add these lines to fix API error
// ========================================

// 1. Find this line (around line 48):
//    testApiKey: (data) => ipcRenderer.invoke('test-api-key', data),

// 2. ADD these 2 lines AFTER it:
  
  // Batch scanning from CSV/Excel
  analyzeBatchFile: (csvFilePath) => ipcRenderer.invoke('analyze-batch-file', csvFilePath),

// 3. Also find this line (around line 8):
//    selectFiles: () => ipcRenderer.invoke('select-files'),

// 4. ADD this line AFTER it:

  selectFile: (options) => ipcRenderer.invoke('select-file', options),

// ========================================
// COMPLETE SECTION - Copy this entire block
// ========================================

// Paste this BEFORE the closing });

  // File/Folder selection
  selectFolder: () => ipcRenderer.invoke('select-folder'),
  selectFolders: () => ipcRenderer.invoke('select-folders'),
  selectFiles: () => ipcRenderer.invoke('select-files'),
  selectFile: (options) => ipcRenderer.invoke('select-file', options),
  listSubfoldersInFolder: (folderPath) => ipcRenderer.invoke('list-subfolders-in-folder', folderPath),
  listFolderTree: (folderPath) => ipcRenderer.invoke('list-folder-tree', folderPath),
  analyzeParentFolder: (folderPath) => ipcRenderer.invoke('analyze-parent-folder', folderPath),
  listFilesInFolder: (folderPath) => ipcRenderer.invoke('list-files-in-folder', folderPath),
  renameFile: (oldPath, newBaseName) => ipcRenderer.invoke('rename-file', oldPath, newBaseName),
  
  // Offline OCR processing
  processDocumentOffline: (filePath) => ipcRenderer.invoke('process-document-offline', filePath),
  
  // Cloud Boost processing
  processDocumentCloud: (filePath) => ipcRenderer.invoke('process-document-cloud', filePath),
  
  // Config management
  getConfig: (key) => ipcRenderer.invoke('get-config', key),
  setConfig: (key, value) => ipcRenderer.invoke('set-config', key, value),
  
  // Backend URL for cloud boost
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
  // PDF merge
  mergeByShortCode: (items, options) => ipcRenderer.invoke('merge-by-short-code', items, options),
  chooseSavePath: (defaultName) => ipcRenderer.invoke('choose-save-path', defaultName),
  readImageDataUrl: (filePath) => ipcRenderer.invoke('read-image-data-url', filePath),

  setBackendUrl: (url) => ipcRenderer.invoke('set-backend-url', url),
  
  // Rules Manager
  getRules: () => ipcRenderer.invoke('get-rules'),
  saveRule: (docType, ruleData) => ipcRenderer.invoke('save-rule', docType, ruleData),
  deleteRule: (docType) => ipcRenderer.invoke('delete-rule', docType),
  resetRules: () => ipcRenderer.invoke('reset-rules'),
  exportRules: () => ipcRenderer.invoke('export-rules'),
  importRules: (merge) => ipcRenderer.invoke('import-rules', merge),
  openRulesFolder: () => ipcRenderer.invoke('open-rules-folder'),
  generateKeywordVariants: (keyword, includeTypos) => ipcRenderer.invoke('generate-keyword-variants', keyword, includeTypos),
  
  // Cloud OCR API Key Management
  saveApiKey: (data) => ipcRenderer.invoke('save-api-key', data),
  getApiKey: (provider) => ipcRenderer.invoke('get-api-key', provider),
  deleteApiKey: (provider) => ipcRenderer.invoke('delete-api-key', provider),
  testApiKey: (data) => ipcRenderer.invoke('test-api-key', data),
  
  // Batch scanning from CSV/Excel
  analyzeBatchFile: (csvFilePath) => ipcRenderer.invoke('analyze-batch-file', csvFilePath),
  
  // Platform info
  platform: process.platform,
  isElectron: true
