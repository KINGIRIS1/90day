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

ipcMain.handle('list-files-in-folder', async (event, folderPath) => {
  const fs = require('fs');
  const path = require('path');
  try {
    const entries = fs.readdirSync(folderPath, { withFileTypes: true });
    const files = entries
      .filter((e) => e.isFile())
      .filter((e) => /\.(jpg|jpeg|png|gif|bmp|tiff|pdf)$/i.test(e.name))
      .map((e) => path.join(folderPath, e.name));
    return { success: true, files };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

ipcMain.handle('rename-file', async (event, oldPath, newBaseName) => {
  const fs = require('fs');
  const path = require('path');
  try {
    const dir = path.dirname(oldPath);
    const ext = path.extname(oldPath);
    const newPath = path.join(dir, `${newBaseName}${ext}`);
    if (fs.existsSync(newPath)) {
      return { success: false, error: 'Tên file đã tồn tại trong thư mục' };
    }
    fs.renameSync(oldPath, newPath);
    return { success: true, newPath };
  } catch (err) {
    return { success: false, error: err.message };
  }
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

ipcMain.handle('choose-save-path', async (event, defaultName) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultName,
    filters: [{ name: 'PDF', extensions: ['pdf'] }]
  });
  if (result.canceled) return null;
  return result.filePath;
});

ipcMain.handle('merge-by-short-code', async (event, items) => {
  // items: [{filePath, short_code}]  -> group by short_code and output one pdf per short_code
  const fs = require('fs');
  const path = require('path');
  const { PDFDocument, StandardFonts } = require('pdf-lib');

  const groups = items.reduce((acc, it) => {
    const key = it.short_code || 'UNKNOWN';
    if (!acc[key]) acc[key] = [];
    acc[key].push(it.filePath);
    return acc;
  }, {});

  const results = [];

  for (const [shortCode, filePaths] of Object.entries(groups)) {
    try {
      // Create a new PDF
      const outPdf = await PDFDocument.create();

      for (const fp of filePaths) {
        const ext = path.extname(fp).toLowerCase();
        const bytes = fs.readFileSync(fp);
        if (ext === '.pdf') {
          // Copy pages from existing PDF
          const srcPdf = await PDFDocument.load(bytes);
          const copiedPages = await outPdf.copyPages(srcPdf, srcPdf.getPageIndices());
          copiedPages.forEach((p) => outPdf.addPage(p));
        } else if (ext === '.jpg' || ext === '.jpeg' || ext === '.png' || ext === '.bmp' || ext === '.gif') {
          // Embed image, keep original size
          let img;
          if (ext === '.png') img = await outPdf.embedPng(bytes);
          else img = await outPdf.embedJpg(bytes); // pdf-lib supports jpg; gif/bmp may need conversion, try jpg embed
          const { width, height } = img.size();
          const page = outPdf.addPage([width, height]);
          page.drawImage(img, { x: 0, y: 0, width, height });
        } else {
          // Skip unsupported
          console.warn('Unsupported for merge:', fp);
        }
      }

      const pdfBytes = await outPdf.save();
      // Ask save path per short_code per your naming rule: short_code.pdf
      const savePath = await dialog.showSaveDialog(mainWindow, {
        defaultPath: `${shortCode}.pdf`,
        filters: [{ name: 'PDF', extensions: ['pdf'] }]
      });
      if (!savePath.canceled && savePath.filePath) {
        fs.writeFileSync(savePath.filePath, pdfBytes);
        results.push({ short_code: shortCode, path: savePath.filePath, count: filePaths.length, success: true });
      } else {
        results.push({ short_code: shortCode, canceled: true, success: false });
      }
    } catch (err) {
      console.error('Merge error for', shortCode, err);
      results.push({ short_code: shortCode, error: err.message, success: false });
    }
  }

  return results;
});

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
