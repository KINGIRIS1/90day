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
    let errorLogs = '';

    childProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    childProcess.stderr.on('data', (data) => {
      const message = data.toString();
      // Log stderr for debugging but don't fail on warnings
      console.log('[Python stderr]:', message);
      errorLogs += message;
    });

    childProcess.on('close', (code) => {
      if (code === 0) {
        try {
          // Parse only the JSON output from stdout
          const jsonResult = JSON.parse(result);
          resolve(jsonResult);
        } catch (e) {
          console.error('JSON parse error:', e);
          console.error('Raw output:', result);
          console.error('Stderr logs:', errorLogs);
          reject(new Error(`Failed to parse OCR result: ${e.message}`));
        }
      } else {
        console.error('Process exited with code:', code);
        console.error('Stderr:', errorLogs);
        reject(new Error(errorLogs || `OCR processing failed with code ${code}`));
      }
    });

    // Add timeout (30 seconds for PaddleOCR)
    setTimeout(() => {
      childProcess.kill();
      reject(new Error('OCR processing timeout (30s)'));
    }, 30000);
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
  
  return new Promise(async (resolve) => {
    try {
      const backendUrl = store.get('backendUrl', '');
      
      if (!backendUrl) {
        resolve({
          success: false,
          method: 'cloud_boost_failed',
          error: 'Backend URL not configured',
          status: null,
          errorType: 'CONFIG'
        });
        return;
      }
      
      console.log(`Cloud Boost: Uploading ${filePath} to ${backendUrl}`);
      
      // Create form data
      const form = new FormData();
      form.append('file', fs.createReadStream(filePath));
      
      // Call backend API (public endpoint - no auth required)
      const response = await axios.post(`${backendUrl}/api/scan-document-public`, form, {
        headers: {
          ...form.getHeaders(),
        },
        timeout: 30000 // 30 seconds
      });
      
      console.log('Cloud Boost response:', response.data);
      
      // Map backend response to frontend format
      const backendData = response.data;
      
      resolve({
        success: true,
        method: 'cloud_boost',
        doc_type: backendData.detected_full_name || 'Không rõ',
        short_code: backendData.short_code || 'UNKNOWN',
        confidence: backendData.confidence_score || 0,  // Important: confidence_score not confidence
        accuracy_estimate: '93%+',
        original_text: backendData.detected_full_name || '',
        recommend_cloud_boost: false  // Already using cloud boost
      });
      
    } catch (error) {
      console.error('Cloud Boost error:', error);
      const status = error.response?.status || null;
      let errorType = 'OTHER';
      if (error.code === 'ECONNABORTED') errorType = 'TIMEOUT';
      else if (error.code === 'ECONNREFUSED' || !error.response) errorType = 'NETWORK';
      else if (status === 401 || status === 403) errorType = 'UNAUTHORIZED';
      else if (status === 402 || status === 429) errorType = 'QUOTA';
      else if (status && status >= 500) errorType = 'SERVER';

      resolve({
        success: false,
        method: 'cloud_boost_failed',
        error: error.response?.data?.detail || error.message || 'Cloud Boost failed',
        status,
        errorType
      });
    }
  });
});
