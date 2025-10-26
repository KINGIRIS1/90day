const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // File/Folder selection
  selectFolder: () => ipcRenderer.invoke('select-folder'),
  selectFiles: () => ipcRenderer.invoke('select-files'),
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
  mergeByShortCode: (items) => ipcRenderer.invoke('merge-by-short-code', items),
  chooseSavePath: (defaultName) => ipcRenderer.invoke('choose-save-path', defaultName),

  setBackendUrl: (url) => ipcRenderer.invoke('set-backend-url', url),
  
  // Platform info
  platform: process.platform,
  isElectron: true
});
