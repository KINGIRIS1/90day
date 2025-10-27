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
  // Splash screen window
  const splash = new BrowserWindow({
    width: 420,
    height: 420,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    icon: path.join(__dirname, isDev ? '../assets/icon.png' : '../assets/icon.png')
  });
  
  const splashPath = isDev 
    ? `file://${path.join(__dirname, 'splash.html')}`
    : `file://${path.join(__dirname, '../build/splash.html')}`;
  splash.loadURL(splashPath);

  // Main window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    show: false,
    title: '90dayChonThanh',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, isDev ? '../assets/icon.png' : '../assets/icon.png')
  });

  // Load React app
  const startUrl = isDev 
    ? 'http://localhost:3001' 
    : `file://${path.join(__dirname, '../build/index.html')}`;
  
  mainWindow.loadURL(startUrl);

  mainWindow.once('ready-to-show', () => {
    splash.destroy();
    mainWindow.show();
  });

  // Open DevTools in development
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Helper function to get Python path
function getPythonPath() {
  if (isDev) {
    // Development mode - use system Python
    if (process.platform === 'win32') {
      return 'py'; // Windows py launcher
    } else {
      return 'python3'; // Linux/Mac
    }
  } else {
    // Production mode - use system Python
    // Try multiple commands to find working Python
    if (process.platform === 'win32') {
      // Windows: try py, python, python3
      return 'py'; // Windows py launcher is most reliable
    } else if (process.platform === 'darwin') {
      return 'python3'; // macOS
    } else {
      return 'python3'; // Linux
    }
  }
}

// Helper function to get Python script path
function getPythonScriptPath(scriptName) {
  if (isDev) {
    // Development mode - scripts in ../python/
    return path.join(__dirname, '../python', scriptName);
  } else {
    // Production mode - scripts in resources/python/
    return path.join(process.resourcesPath, 'python', scriptName);
  }
}

// Initialize Python OCR engine
function initPythonEngine() {
  const pythonPath = getPythonPath();
  
  const scriptPath = isDev
    ? path.join(__dirname, '../python/ocr_engine.py')
    : getPythonScriptPath('ocr_engine.py');

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
  return result.canceled ? null : (result.filePaths[0] || null);
});

ipcMain.handle('select-folders', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory', 'multiSelections']
  });
  return result.canceled ? [] : (result.filePaths || []);
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

ipcMain.handle('list-subfolders-in-folder', async (event, folderPath) => {
  const fs = require('fs');
  const path = require('path');
  try {
    const entries = fs.readdirSync(folderPath, { withFileTypes: true });
    const dirs = entries
      .filter((e) => e.isDirectory())
      .map((e) => path.join(folderPath, e.name));
    return { success: true, folders: dirs };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

ipcMain.handle('list-folder-tree', async (event, basePath) => {
  const fs = require('fs');
  const path = require('path');

  function buildTree(dirPath) {
    let children = [];
    try {
      const entries = fs.readdirSync(dirPath, { withFileTypes: true });
      for (const e of entries) {
        if (e.isDirectory()) {
          const childPath = path.join(dirPath, e.name);
          const node = buildTree(childPath); // no depth limit per user request
          children.push({ path: childPath, name: e.name, children: node ? node.children : [] });
        }
      }
    } catch (err) {
      // Ignore permission errors
    }
    return { path: dirPath, name: path.basename(dirPath), children };
  }

  try {
    const tree = buildTree(basePath);
    return { success: true, tree };
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

ipcMain.handle('analyze-parent-folder', async (event, folderPath) => {
  const fs = require('fs');
  const path = require('path');
  try {
    const entries = fs.readdirSync(folderPath, { withFileTypes: true });
    const files = entries.filter(e => e.isFile()).filter(e => /\.(jpg|jpeg|png|gif|bmp|tiff|pdf)$/i.test(e.name));
    const dirs = entries.filter(e => e.isDirectory());
    const subfolders = dirs.map(d => {
      const subPath = path.join(folderPath, d.name);
      let count = 0;
      try {
        const subEntries = fs.readdirSync(subPath, { withFileTypes: true });
        count = subEntries.filter(e => e.isFile()).filter(e => /\.(jpg|jpeg|png|gif|bmp|tiff|pdf)$/i.test(e.name)).length;
      } catch {}
      return { path: subPath, name: d.name, fileCount: count };
    });
    return { success: true, summary: { subfolderCount: subfolders.length, rootFileCount: files.length }, subfolders };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

    return { success: false, error: err.message };
  }
});


ipcMain.handle('process-document-offline', async (event, filePath) => {
  return new Promise((resolve, reject) => {
    // Get OCR engine preference from store (default: tesseract)
    const ocrEngineType = store.get('ocrEngineType', 'tesseract');
    
    // Auto-detect Python command based on platform
    let pythonPath;
    if (isDev) {
      // Development mode - use python command directly
      if (process.platform === 'win32') {
        pythonPath = 'python'; // Windows - use 'python' command
      } else {
        pythonPath = 'python3'; // Linux/Mac
      }
    } else {
      // Production mode - use system Python
      pythonPath = getPythonPath();
    }
    
    const scriptPath = isDev
      ? getPythonScriptPath('process_document.py')
      : getPythonScriptPath('process_document.py');

    console.log(`Spawning: ${pythonPath} ${scriptPath} ${filePath} ${ocrEngineType}`);
    const childProcess = spawn(pythonPath, [scriptPath, filePath, ocrEngineType]);
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

    // Add timeout (30 seconds for OCR processing)
    setTimeout(() => {
      childProcess.kill();
      reject(new Error('OCR processing timeout (30s)'));
    }, 30000);
  });
});

// Choose save path (not used in autoSave flow but kept for future)
ipcMain.handle('choose-save-path', async (event, defaultName) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultName,
    filters: [{ name: 'PDF', extensions: ['pdf'] }]
  });
  if (result.canceled) return null;
  return result.filePath;
});

ipcMain.handle('merge-by-short-code', async (event, items, options = {}) => {
  // items: [{filePath, short_code}]  -> group by short_code and output one pdf per short_code
  // options: { autoSave: true }
  const fs = require('fs');
  const path = require('path');
  const { PDFDocument } = require('pdf-lib');

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
          else img = await outPdf.embedJpg(bytes);
          const { width, height } = img.size();
          const page = outPdf.addPage([width, height]);
          page.drawImage(img, { x: 0, y: 0, width, height });
        } else {
          // Skip unsupported
          console.warn('Unsupported for merge:', fp);
        }
      }

      const pdfBytes = await outPdf.save();

      let outputPath;
      if (options.autoSave) {
        // Save directly to the folder of the first file in the group
        const firstDir = path.dirname(filePaths[0]);
        outputPath = path.join(firstDir, `${shortCode}.pdf`);
        // If exists, add numeric suffix
        let count = 1;
        while (fs.existsSync(outputPath)) {
          outputPath = path.join(firstDir, `${shortCode}(${count}).pdf`);
          count += 1;
        }
        fs.writeFileSync(outputPath, Buffer.from(pdfBytes));
        results.push({ short_code: shortCode, path: outputPath, count: filePaths.length, success: true, autoSaved: true });
      } else {
        const savePath = await dialog.showSaveDialog(mainWindow, {
          defaultPath: `${shortCode}.pdf`,
          filters: [{ name: 'PDF', extensions: ['pdf'] }]
        });
        if (!savePath.canceled && savePath.filePath) {
          fs.writeFileSync(savePath.filePath, pdfBytes);
          outputPath = savePath.filePath;
          results.push({ short_code: shortCode, path: outputPath, count: filePaths.length, success: true });
        } else {
          results.push({ short_code: shortCode, canceled: true, success: false });
        }
      }
    } catch (err) {
      console.error('Merge error for', shortCode, err);
      results.push({ short_code: shortCode, error: err.message, success: false });
    }
  }

  return results;
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
      
      // Normalize backend URL (remove trailing slash if exists)
      const normalizedUrl = backendUrl.replace(/\/$/, '');
      
      // Create form data
      const form = new FormData();
      form.append('file', fs.createReadStream(filePath));
      
      // Call backend API (public endpoint - no auth required)
      const response = await axios.post(`${normalizedUrl}/api/scan-document-public`, form, {
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

// Read local image as data URL for safe rendering in renderer
ipcMain.handle('read-image-data-url', async (event, filePath) => {
  const fs = require('fs');
  const path = require('path');
  try {
    const ext = path.extname(filePath).toLowerCase();
    const mimeMap = {
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.gif': 'image/gif',
      '.bmp': 'image/bmp'
    };
    const mime = mimeMap[ext];
    if (!mime) return null; // not supported
    const data = fs.readFileSync(filePath);
    const base64 = data.toString('base64');
    return `data:${mime};base64,${base64}`;
  } catch (err) {
    console.error('read-image-data-url error:', err);
    return null;
  }
});


// ===== Rules Manager IPC Handlers =====

// Get all rules (merged default + overrides)
ipcMain.handle('get-rules', async () => {
  try {
    const pythonPath = getPythonPath();
    const scriptPath = getPythonScriptPath('rules_manager.py');
    
    return new Promise((resolve, reject) => {
      const childProcess = spawn(pythonPath, [scriptPath, 'get']);
      let output = '';
      let errorOutput = '';
      
      childProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      childProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      childProcess.on('close', (code) => {
        if (code === 0) {
          try {
            const rules = JSON.parse(output);
            resolve({ success: true, rules });
          } catch (e) {
            reject(new Error(`Failed to parse rules: ${e.message}`));
          }
        } else {
          reject(new Error(`Rules manager failed: ${errorOutput}`));
        }
      });
      
      setTimeout(() => {
        childProcess.kill();
        reject(new Error('Rules fetch timeout'));
      }, 10000);
    });
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Save a single rule
ipcMain.handle('save-rule', async (event, docType, ruleData) => {
  try {
    const pythonPath = getPythonPath();
    const scriptPath = getPythonScriptPath('rules_manager.py');
    const ruleJson = JSON.stringify(ruleData);
    
    return new Promise((resolve, reject) => {
      const childProcess = spawn(pythonPath, [scriptPath, 'save', docType, ruleJson]);
      let output = '';
      let errorOutput = '';
      
      childProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      childProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      childProcess.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output);
            resolve(result);
          } catch (e) {
            reject(new Error(`Failed to parse result: ${e.message}`));
          }
        } else {
          reject(new Error(`Save rule failed: ${errorOutput}`));
        }
      });
      
      setTimeout(() => {
        childProcess.kill();
        reject(new Error('Save rule timeout'));
      }, 10000);
    });
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Delete a rule (revert to default)
ipcMain.handle('delete-rule', async (event, docType) => {
  try {
    const pythonPath = getPythonPath();
    const scriptPath = getPythonScriptPath('rules_manager.py');
    
    return new Promise((resolve, reject) => {
      const childProcess = spawn(pythonPath, [scriptPath, 'delete', docType]);
      let output = '';
      let errorOutput = '';
      
      childProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      childProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      childProcess.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output);
            resolve(result);
          } catch (e) {
            reject(new Error(`Failed to parse result: ${e.message}`));
          }
        } else {
          reject(new Error(`Delete rule failed: ${errorOutput}`));
        }
      });
      
      setTimeout(() => {
        childProcess.kill();
        reject(new Error('Delete rule timeout'));
      }, 10000);
    });
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Reset all rules to defaults
ipcMain.handle('reset-rules', async () => {
  try {
    const pythonPath = getPythonPath();
    const scriptPath = getPythonScriptPath('rules_manager.py');
    
    return new Promise((resolve, reject) => {
      const childProcess = spawn(pythonPath, [scriptPath, 'reset']);
      let output = '';
      let errorOutput = '';
      
      childProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      childProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      childProcess.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output);
            resolve(result);
          } catch (e) {
            reject(new Error(`Failed to parse result: ${e.message}`));
          }
        } else {
          reject(new Error(`Reset rules failed: ${errorOutput}`));
        }
      });
      
      setTimeout(() => {
        childProcess.kill();
        reject(new Error('Reset rules timeout'));
      }, 10000);
    });
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Export rules to file
ipcMain.handle('export-rules', async () => {
  try {
    const result = await dialog.showSaveDialog(mainWindow, {
      title: 'Export Rules',
      defaultPath: 'rules-export.json',
      filters: [{ name: 'JSON Files', extensions: ['json'] }]
    });
    
    if (result.canceled) {
      return { success: false, message: 'Export cancelled' };
    }
    
    const exportPath = result.filePath;
    const pythonPath = getPythonPath();
    const scriptPath = getPythonScriptPath('rules_manager.py');
    
    return new Promise((resolve, reject) => {
      const childProcess = spawn(pythonPath, [scriptPath, 'export', exportPath]);
      let output = '';
      let errorOutput = '';
      
      childProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      childProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      childProcess.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output);
            resolve(result);
          } catch (e) {
            reject(new Error(`Failed to parse result: ${e.message}`));
          }
        } else {
          reject(new Error(`Export failed: ${errorOutput}`));
        }
      });
      
      setTimeout(() => {
        childProcess.kill();
        reject(new Error('Export timeout'));
      }, 10000);
    });
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Import rules from file
ipcMain.handle('import-rules', async (event, mergeBool = true) => {
  try {
    const result = await dialog.showOpenDialog(mainWindow, {
      title: 'Import Rules',
      filters: [{ name: 'JSON Files', extensions: ['json'] }],
      properties: ['openFile']
    });
    
    if (result.canceled) {
      return { success: false, message: 'Import cancelled' };
    }
    
    const importPath = result.filePaths[0];
    const pythonPath = getPythonPath();
    const scriptPath = getPythonScriptPath('rules_manager.py');
    const mergeFlag = mergeBool ? 'true' : 'false';
    
    return new Promise((resolve, reject) => {
      const childProcess = spawn(pythonPath, [scriptPath, 'import', importPath, mergeFlag]);
      let output = '';
      let errorOutput = '';
      
      childProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      childProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      childProcess.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output);
            resolve(result);
          } catch (e) {
            reject(new Error(`Failed to parse result: ${e.message}`));
          }
        } else {
          reject(new Error(`Import failed: ${errorOutput}`));
        }
      });
      
      setTimeout(() => {
        childProcess.kill();
        reject(new Error('Import timeout'));
      }, 10000);
    });
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Open rules folder in file explorer
ipcMain.handle('open-rules-folder', async () => {
  try {
    const pythonPath = getPythonPath();
    const scriptPath = getPythonScriptPath('rules_manager.py');
    
    return new Promise((resolve, reject) => {
      const childProcess = spawn(pythonPath, [scriptPath, 'folder']);
      let output = '';
      let errorOutput = '';
      
      childProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      childProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      childProcess.on('close', async (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output);
            if (result.success && result.path) {
              // Open folder in file explorer
              const { shell } = require('electron');
              await shell.openPath(result.path);
              resolve({ success: true, message: `Opened ${result.path}` });
            } else {
              reject(new Error('Failed to get folder path'));
            }
          } catch (e) {
            reject(new Error(`Failed to parse result: ${e.message}`));
          }
        } else {
          reject(new Error(`Get folder failed: ${errorOutput}`));
        }
      });
      
      setTimeout(() => {
        childProcess.kill();
        reject(new Error('Get folder timeout'));
      }, 10000);
    });
  } catch (error) {
    return { success: false, error: error.message };
  }
});


// Generate keyword variants
ipcMain.handle('generate-keyword-variants', async (event, keyword, includeTypos = true) => {
  try {
    const pythonPath = getPythonPath();
    const scriptPath = getPythonScriptPath('keyword_variants.py');
    const typosFlag = includeTypos ? 'true' : 'false';
    
    return new Promise((resolve, reject) => {
      const childProcess = spawn(pythonPath, [scriptPath, keyword, typosFlag]);
      let output = '';
      let errorOutput = '';
      
      childProcess.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      childProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      childProcess.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(output);
            resolve(result);
          } catch (e) {
            reject(new Error(`Failed to parse result: ${e.message}`));
          }
        } else {
          reject(new Error(`Generate variants failed: ${errorOutput}`));
        }
      });
      
      setTimeout(() => {
        childProcess.kill();
        reject(new Error('Generate variants timeout'));
      }, 5000);
    });
  } catch (error) {
    return { success: false, error: error.message };
  }
});

