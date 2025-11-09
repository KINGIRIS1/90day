const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // File/Folder selection
  selectFolder: () => ipcRenderer.invoke('select-folder'),
  selectFolders: () => ipcRenderer.invoke('select-folders'),
  selectFiles: () => ipcRenderer.invoke('select-files'),
  selectTxtFile: () => ipcRenderer.invoke('select-txt-file'),
  listSubfoldersInFolder: (folderPath) => ipcRenderer.invoke('list-subfolders-in-folder', folderPath),
  listFolderTree: (folderPath) => ipcRenderer.invoke('list-folder-tree', folderPath),
  analyzeParentFolder: (folderPath) => ipcRenderer.invoke('analyze-parent-folder', folderPath),
  listFilesInFolder: (folderPath) => ipcRenderer.invoke('list-files-in-folder', folderPath),
  renameFile: (oldPath, newBaseName) => ipcRenderer.invoke('rename-file', oldPath, newBaseName),
  
  // Offline OCR processing
  processDocumentOffline: (filePath) => ipcRenderer.invoke('process-document-offline', filePath),
  
  // Batch scan processing
  validateBatchFolders: (txtPath) => ipcRenderer.invoke('validate-batch-folders', txtPath),
  scanSingleFolder: (folderPath, ocrEngine) => ipcRenderer.invoke('scan-single-folder', folderPath, ocrEngine),
  processBatchScan: (txtPath, outputOption, mergeSuffix, outputFolder) => ipcRenderer.invoke('process-batch-scan', txtPath, outputOption, mergeSuffix, outputFolder),
  onBatchScanProgress: (callback) => ipcRenderer.on('batch-scan-progress', (event, data) => callback(data)),
  
  // Batch multi-image processing (NEW)
  batchProcessDocuments: (params) => ipcRenderer.invoke('batch-process-documents', params),
  
  // Cloud Boost processing
  processDocumentCloud: (filePath) => ipcRenderer.invoke('process-document-cloud', filePath),
  
  // Config management
  getConfig: (key) => ipcRenderer.invoke('get-config', key),
  setConfig: (key, value) => ipcRenderer.invoke('set-config', key, value),
  
  // Backend URL for cloud boost
  getBackendUrl: () => ipcRenderer.invoke('get-backend-url'),
  // PDF merge
  mergeByShortCode: (items, options) => {
    console.log('📡 PRELOAD.JS: mergeByShortCode called');
    console.log('   Items:', items.length);
    console.log('   Options:', options);
    return ipcRenderer.invoke('merge-by-short-code', items, options);
  },
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
  
  // Platform info
  platform: process.platform,
  isElectron: true
});
