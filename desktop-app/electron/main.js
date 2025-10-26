const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const Store = require('electron-store');

const store = new Store();
let mainWindow;
let pythonProcess;

// Determine if running in development or production
const isDev = !app.isPackaged;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../assets/icon.png')
  });

  // Load React app
  const startUrl = isDev 
    ? 'http://localhost:3000' 
    : `file://${path.join(__dirname, '../build/index.html')}`;
  
  mainWindow.loadURL(startUrl);

  // Open DevTools in development
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Initialize Python OCR engine
function initPythonEngine() {
  const pythonPath = isDev
    ? 'python3'
    : path.join(process.resourcesPath, 'python', 'python3');
  
  const scriptPath = isDev
    ? path.join(__dirname, '../python/ocr_engine.py')
    : path.join(process.resourcesPath, 'python', 'ocr_engine.py');

  pythonProcess = spawn(pythonPath, [scriptPath]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python OCR: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python OCR Error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
  });
}

app.whenReady().then(() => {
  createWindow();
  // initPythonEngine(); // Will enable after creating Python scripts

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC Handlers
ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  return result.filePaths[0];
});

ipcMain.handle('select-files', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: [
      { name: 'Images', extensions: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'] },
      { name: 'PDFs', extensions: ['pdf'] }
    ]
  });
  return result.filePaths;
});

ipcMain.handle('process-document-offline', async (event, filePath) => {
  return new Promise((resolve, reject) => {
    // Auto-detect Python command based on platform
    let pythonPath;
    if (isDev) {
      // Development mode - try different Python commands
      if (process.platform === 'win32') {
        pythonPath = 'py'; // Windows py launcher
      } else {
        pythonPath = 'python3'; // Linux/Mac
      }
    } else {
      // Production mode
      pythonPath = path.join(process.resourcesPath, 'python', 'python3');
    }
    
    const scriptPath = isDev
      ? path.join(__dirname, '../python/process_document.py')
      : path.join(process.resourcesPath, 'python', 'process_document.py');

    console.log(`Spawning: ${pythonPath} ${scriptPath} ${filePath}`);
    const childProcess = spawn(pythonPath, [scriptPath, filePath]);
    let result = '';
    let error = '';

    childProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    childProcess.stderr.on('data', (data) => {
      error += data.toString();
    });

    childProcess.on('close', (code) => {
      if (code === 0) {
        try {
          resolve(JSON.parse(result));
        } catch (e) {
          reject(new Error('Failed to parse OCR result'));
        }
      } else {
        reject(new Error(error || 'OCR processing failed'));
      }
    });
  });
});

ipcMain.handle('get-config', (event, key) => {
  return store.get(key);
});

ipcMain.handle('set-config', (event, key, value) => {
  store.set(key, value);
  return true;
});

ipcMain.handle('get-backend-url', () => {
  return store.get('backendUrl', '');
});

ipcMain.handle('set-backend-url', (event, url) => {
  store.set('backendUrl', url);
  return true;
});

ipcMain.handle('process-document-cloud', async (event, filePath) => {
  const FormData = require('form-data');
  const axios = require('axios');
  const fs = require('fs');
  
  return new Promise(async (resolve, reject) => {
    try {
      const backendUrl = store.get('backendUrl', '');
      
      if (!backendUrl) {
        reject(new Error('Backend URL not configured'));
        return;
      }
      
      // Create form data
      const form = new FormData();
      form.append('file', fs.createReadStream(filePath));
      
      // Call backend API
      const response = await axios.post(`${backendUrl}/scan-document`, form, {
        headers: {
          ...form.getHeaders(),
        },
        timeout: 30000 // 30 seconds
      });
      
      resolve({
        success: true,
        method: 'cloud_boost',
        doc_type: response.data.detected_full_name,
        short_code: response.data.short_code,
        confidence: response.data.confidence_score,
        accuracy_estimate: '93%+',
        original_text: response.data.detected_full_name
      });
      
    } catch (error) {
      reject(new Error(error.message || 'Cloud Boost failed'));
    }
  });
});
