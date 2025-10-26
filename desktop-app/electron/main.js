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
    const pythonPath = isDev ? 'python3' : path.join(process.resourcesPath, 'python', 'python3');
    const scriptPath = isDev
      ? path.join(__dirname, '../python/process_document.py')
      : path.join(process.resourcesPath, 'python', 'process_document.py');

    const process = spawn(pythonPath, [scriptPath, filePath]);
    let result = '';
    let error = '';

    process.stdout.on('data', (data) => {
      result += data.toString();
    });

    process.stderr.on('data', (data) => {
      error += data.toString();
    });

    process.on('close', (code) => {
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
