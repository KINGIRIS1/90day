const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn, spawnSync } = require('child_process');
const Store = require('electron-store');
const fs = require('fs');

// Separate stores for better performance
const store = new Store({ name: 'config' }); // Settings only (~100 KB)
const scanStore = new Store({ name: 'scan-history' }); // Scan data (can be large)
let mainWindow;

const isDev = !app.isPackaged;

function createWindow() {
  const splash = new BrowserWindow({
    width: 420,
    height: 420,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    icon: path.join(__dirname, '../assets/icon.png')
  });
  splash.loadURL(`file://${path.join(__dirname, '../public/splash.html')}`);

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
    icon: path.join(__dirname, '../assets/icon.png')
  });

  // Smart URL detection: Check environment variable first, then build folder
  let startUrl;
  
  // Check if ELECTRON_START_URL is set (for dev mode)
  if (process.env.ELECTRON_START_URL) {
    startUrl = process.env.ELECTRON_START_URL;
    console.log('🔧 Dev mode (from env): Loading from', startUrl);
  } else {
    const buildIndexPath = path.join(__dirname, '../build/index.html');
    const hasBuild = fs.existsSync(buildIndexPath);
    
    if (isDev && !hasBuild) {
      // Development mode: No build folder → Use localhost
      startUrl = 'http://localhost:3001';
      console.log('🔧 Development mode: Loading from localhost:3001');
    } else {
      // Production mode OR build exists → Use build folder
      startUrl = `file://${buildIndexPath}`;
      console.log('🚀 Production mode: Loading from build folder');
    }
  }
  
  mainWindow.loadURL(startUrl);

  mainWindow.once('ready-to-show', () => {
    try { splash.destroy(); } catch {}
    mainWindow.show();
  });

  if (isDev) mainWindow.webContents.openDevTools();

  // Renderer crash recovery
  mainWindow.webContents.on('render-process-gone', (event, details) => {
    console.error('❌ Renderer process crashed:', details);
    dialog.showMessageBoxSync({
      type: 'error',
      title: 'Ứng dụng gặp sự cố',
      message: 'Ứng dụng đã gặp sự cố và sẽ được khởi động lại.\n\nDữ liệu scan đã được tự động lưu.',
      buttons: ['OK']
    });
    mainWindow.reload();
  });

  mainWindow.webContents.on('unresponsive', () => {
    console.warn('⚠️ Renderer became unresponsive');
    const choice = dialog.showMessageBoxSync({
      type: 'warning',
      title: 'Ứng dụng không phản hồi',
      message: 'Ứng dụng đang không phản hồi (có thể do scan quá nhiều files).\n\nBạn muốn:',
      buttons: ['Đợi thêm', 'Khởi động lại'],
      defaultId: 0,
      cancelId: 0
    });
    if (choice === 1) {
      mainWindow.reload();
    }
  });

  // Handle close event with confirmation dialog
  mainWindow.on('close', (e) => {
    const choice = dialog.showMessageBoxSync(mainWindow, {
      type: 'question',
      buttons: ['Có', 'Không'],
      title: 'Xác nhận thoát',
      message: 'Bạn có chắc chắn muốn thoát ứng dụng?',
      defaultId: 1,
      cancelId: 1
    });
    
    // If user clicks "Không" (No), prevent window from closing
    if (choice === 1) {
      e.preventDefault();
    }
  });

  mainWindow.on('closed', () => { mainWindow = null; });
}

// Discover system Python and site-packages (Windows prefers py launcher)
function discoverPython() {
  const versionPrefs = ['3.12', '3.11', '3.10'];
  const makeProbeCmd = (launcher, ver) => {
    if (launcher === 'py' && ver) return { cmd: 'py', args: [`-${ver}`, '-c', PY_PROBE] };
    if (launcher === 'py') return { cmd: 'py', args: ['-c', PY_PROBE] };
    if (launcher === 'python') return { cmd: 'python', args: ['-c', PY_PROBE] };
    if (launcher === 'python3') return { cmd: 'python3', args: ['-c', PY_PROBE] };
    return null;
  };

  const attempts = [];
  if (process.platform === 'win32') {
    versionPrefs.forEach(v => attempts.push(makeProbeCmd('py', v)));
    attempts.push(makeProbeCmd('py'));
    attempts.push(makeProbeCmd('python'));
  } else {
    attempts.push(makeProbeCmd('python3'));
    attempts.push(makeProbeCmd('python'));
  }

  for (const a of attempts) {
    if (!a) continue;
    try {
      const r = spawnSync(a.cmd, a.args, { encoding: 'utf8' });
      if (r.status === 0 && r.stdout) {
        const info = JSON.parse(r.stdout.trim());
        const sites = Array.isArray(info.sites) ? info.sites : [];
        const userSite = info.user || '';
        const ver = info.version || '';
        return {
          ok: true,
          launcher: a.cmd,
          args: a.args,
          executable: info.exe,
          version: ver,
          sites,
          userSite
        };
      }
    } catch (e) {
      // continue
    }
  }
  return { ok: false };
}

const PY_PROBE = "import site,sys,sysconfig,json; print(json.dumps({'exe':sys.executable,'version':sys.version.split()[0],'sites':site.getsitepackages() if hasattr(site,'getsitepackages') else [],'user':site.getusersitepackages() if hasattr(site,'getusersitepackages') else ''}))";

function getPythonScriptPath(scriptName) {
  if (isDev) return path.join(__dirname, '../python', scriptName);
  const candidates = [
    path.join(process.resourcesPath, 'python', scriptName),                // extraResources
    path.join(process.resourcesPath, 'app', 'python', scriptName),        // some layouts
    path.join(app.getAppPath(), 'python', scriptName),
    path.join(path.dirname(process.execPath), 'resources', 'python', scriptName),
    path.join(path.dirname(process.execPath), 'resources', 'app', 'python', scriptName)
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) {
      console.log(`Found Python script at: ${p}`);
      return p;
    }
  }
  console.warn('Python script not found. Tried:', candidates);
  return candidates[0];
}

function buildPythonEnv(extra = {}, pythonInfo = null, scriptDir = '') {
  const env = { ...process.env, ...extra };
  const paths = [];
  if (scriptDir) paths.push(scriptDir);
  if (pythonInfo && pythonInfo.sites) paths.push(...pythonInfo.sites);
  if (pythonInfo && pythonInfo.userSite) paths.push(pythonInfo.userSite);
  const delim = path.delimiter; // ';' on win, ':' on posix
  env.PYTHONPATH = paths.filter(Boolean).join(delim);
  env.PYTHONIOENCODING = 'utf-8';
  env.PYTHONUTF8 = '1';
  return env;
}

// ========== SCAN HISTORY CLEANUP ==========
function cleanupOldScans() {
  try {
    const scans = scanStore.get('scans', {});
    const now = Date.now();
    const sevenDaysAgo = now - (7 * 24 * 60 * 60 * 1000);
    
    let cleaned = 0;
    const remaining = {};
    
    // Keep only recent scans (< 7 days) and limit to 20 most recent
    const entries = Object.entries(scans)
      .filter(([_, scanData]) => {
        if (scanData.timestamp < sevenDaysAgo) {
          cleaned++;
          return false;
        }
        return true;
      })
      .sort((a, b) => b[1].timestamp - a[1].timestamp)
      .slice(0, 20); // Keep only 20 most recent
    
    entries.forEach(([scanId, scanData]) => {
      remaining[scanId] = scanData;
    });
    
    const totalRemoved = Object.keys(scans).length - entries.length;
    
    if (totalRemoved > 0) {
      scanStore.set('scans', remaining);
      console.log(`🗑️ Startup cleanup: Removed ${totalRemoved} scans (${cleaned} old, ${totalRemoved - cleaned} excess)`);
      console.log(`📊 Remaining scans: ${entries.length}`);
    } else {
      console.log(`✅ Scan history clean: ${entries.length} scans`);
    }
  } catch (e) {
    console.error('❌ Cleanup error:', e);
  }
}

// ========== CRASH HANDLERS ==========
// Handle uncaught exceptions in main process
process.on('uncaughtException', (error) => {
  console.error('❌ UNCAUGHT EXCEPTION in main process:', error);
  console.error('Stack:', error.stack);
  
  // Show error dialog
  if (mainWindow && !mainWindow.isDestroyed()) {
    dialog.showErrorBox(
      'Lỗi hệ thống',
      `Ứng dụng gặp lỗi không mong muốn:\n\n${error.message}\n\nDữ liệu scan đã được tự động lưu.\nỨng dụng sẽ tiếp tục hoạt động.`
    );
  }
  
  // Don't exit - try to keep app running
  // app.exit(1); // Only exit if absolutely necessary
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ UNHANDLED PROMISE REJECTION:', reason);
  console.error('Promise:', promise);
  
  // Log but don't crash - these are often non-fatal
  if (mainWindow && !mainWindow.isDestroyed()) {
    console.warn('⚠️ Logging unhandled rejection but continuing...');
  }
});

// Handle process warnings
process.on('warning', (warning) => {
  console.warn('⚠️ PROCESS WARNING:', warning.name);
  console.warn('Message:', warning.message);
  console.warn('Stack:', warning.stack);
});

app.whenReady().then(() => {
  // Cleanup old scans on startup (keep scan-history.json small)
  console.log('🧹 Running startup cleanup...');
  cleanupOldScans();
  
  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });

// ========== IPC HANDLERS ==========

ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, { properties: ['openDirectory'] });
  return result.canceled ? null : (result.filePaths[0] || null);
});

ipcMain.handle('select-folders', async () => {
  const result = await dialog.showOpenDialog(mainWindow, { properties: ['openDirectory', 'multiSelections'] });
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

ipcMain.handle('select-txt-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Text Files', extensions: ['txt'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  return result.canceled ? null : (result.filePaths[0] || null);
});

ipcMain.handle('validate-batch-folders', async (event, txtPath) => {
  try {
    console.log('Validating folders from:', txtPath);
    
    // Read TXT file
    const content = fs.readFileSync(txtPath, 'utf-8');
    const lines = content.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#'));
    
    console.log(`Found ${lines.length} folder paths`);
    
    // Validate each folder
    const folders = [];
    for (const folderPath of lines) {
      try {
        const stats = fs.statSync(folderPath);
        if (!stats.isDirectory()) {
          folders.push({
            path: folderPath,
            name: path.basename(folderPath),
            imageCount: 0,
            valid: false,
            selected: false,
            error: 'Không phải thư mục'
          });
          continue;
        }
        
        // Count image files
        const files = fs.readdirSync(folderPath);
        const imageExtensions = ['.jpg', '.jpeg', '.png'];
        const imageFiles = files.filter(f => {
          const ext = path.extname(f).toLowerCase();
          return imageExtensions.includes(ext);
        });
        
        folders.push({
          path: folderPath,
          name: path.basename(folderPath),
          imageCount: imageFiles.length,
          valid: imageFiles.length > 0,
          selected: imageFiles.length > 0, // Auto-select valid folders
          error: imageFiles.length === 0 ? 'Không có ảnh' : null
        });
      } catch (err) {
        folders.push({
          path: folderPath,
          name: path.basename(folderPath),
          imageCount: 0,
          valid: false,
          selected: false,
          error: 'Không tồn tại hoặc không truy cập được'
        });
      }
    }
    
    return {
      success: true,
      folders: folders
    };
  } catch (err) {
    console.error('Validate folders error:', err);
    return {
      success: false,
      error: err.message
    };
  }
});

ipcMain.handle('scan-single-folder', async (event, folderPath, ocrEngineType) => {
  return new Promise(async (resolve, reject) => {
    try {
      console.log(`Scanning single folder: ${folderPath}`);
      
      // Get API key
      let cloudApiKey = null;
      if (ocrEngineType === 'google') {
        cloudApiKey = store.get('cloudOCR.google.apiKey', '');
      } else if (ocrEngineType === 'gemini-flash' || ocrEngineType === 'gemini-flash-hybrid' || ocrEngineType === 'gemini-flash-lite') {
        cloudApiKey = store.get('cloudOCR.gemini.apiKey', '') || process.env.GOOGLE_API_KEY || '';
      }

      // Get image files
      const imageExtensions = ['.jpg', '.jpeg', '.png'];
      const files = fs.readdirSync(folderPath);
      const imageFiles = files
        .filter(f => imageExtensions.includes(path.extname(f).toLowerCase()))
        .map(f => path.join(folderPath, f));

      if (imageFiles.length === 0) {
        resolve({
          success: false,
          error: 'No image files found',
          results: []
        });
        return;
      }

      const pyInfo = discoverPython();
      if (!pyInfo.ok) {
        reject(new Error('Python 3.10–3.12 not found'));
        return;
      }

      const scriptPath = isDev ? path.join(__dirname, '../python/process_document.py') : getPythonScriptPath('process_document.py');
      const pythonScriptDir = path.dirname(scriptPath);
      
      // Process each image
      const results = [];
      for (const imagePath of imageFiles) {
        const args = [scriptPath, imagePath, ocrEngineType];
        if (cloudApiKey) args.push(cloudApiKey);

        const child = spawn(pyInfo.executable, args, {
          cwd: pythonScriptDir,
          env: buildPythonEnv({ 
            GOOGLE_API_KEY: cloudApiKey || process.env.GOOGLE_API_KEY || ''
          }, pyInfo, pythonScriptDir)
        });

        let result = '';
        let errorLogs = '';
        child.stdout.setEncoding('utf8');
        child.stderr.setEncoding('utf8');
        child.stdout.on('data', (d) => { result += d; });
        child.stderr.on('data', (d) => { errorLogs += d; });

        await new Promise((res) => {
          child.on('close', (code) => {
            if (code === 0) {
              try {
                const lines = result.trim().split('\n');
                const jsonLine = lines[lines.length - 1];
                const jsonResult = JSON.parse(jsonLine);
                results.push({
                  original_path: imagePath,
                  short_code: jsonResult.short_code || 'UNKNOWN',
                  doc_type: jsonResult.doc_type || 'Unknown',
                  confidence: jsonResult.confidence || 0,
                  folder: folderPath,
                  success: jsonResult.success || false
                });
              } catch (e) {
                console.error('Parse error:', e);
              }
            }
            res();
          });
        });
      }

      resolve({
        success: true,
        results: results
      });
    } catch (err) {
      console.error('Scan single folder error:', err);
      reject(err);
    }
  });
});

ipcMain.handle('process-batch-scan', async (event, txtPath, outputOption, mergeSuffix, outputFolder) => {
  return new Promise(async (resolve, reject) => {
    const ocrEngineType = store.get('ocrEngine', store.get('ocrEngineType', 'tesseract'));

    let cloudApiKey = null;

    // Get API key if using cloud OCR
    if (ocrEngineType === 'google') {
      cloudApiKey = store.get('cloudOCR.google.apiKey', '');
      if (!cloudApiKey) {
        resolve({ success: false, error: 'Google Cloud Vision API key not configured. Please add it in Cloud OCR settings.' });
        return;
      }
    } else if (ocrEngineType === 'gemini-flash' || ocrEngineType === 'gemini-flash-hybrid' || ocrEngineType === 'gemini-flash-lite') {
      cloudApiKey = store.get('cloudOCR.gemini.apiKey', '') || process.env.GOOGLE_API_KEY || '';
      if (!cloudApiKey) {
        resolve({ success: false, error: 'Google API key not configured for Gemini. Please add it in Cloud OCR settings.' });
        return;
      }
    }

    const pyInfo = discoverPython();
    if (!pyInfo.ok) {
      reject(new Error('Python 3.10–3.12 not found. Please install Python.'));
      return;
    }

    const scriptPath = isDev ? path.join(__dirname, '../python/batch_scanner.py') : getPythonScriptPath('batch_scanner.py');
    const args = [scriptPath, txtPath, ocrEngineType];
    
    // Add API key if available
    if (cloudApiKey) {
      args.push(cloudApiKey);
    } else {
      args.push('none');
    }
    
    // Add output option, merge suffix, and folder
    args.push(outputOption);
    args.push(mergeSuffix || '_merged');
    if (outputFolder) {
      args.push(outputFolder);
    }

    console.log(`Spawning batch scan: ${pyInfo.executable} ${args.map(a => (a === cloudApiKey ? '[API_KEY]' : a)).join(' ')}`);

    const pythonScriptDir = path.dirname(scriptPath);
    
    const child = spawn(pyInfo.executable, args, {
      cwd: pythonScriptDir,
      env: buildPythonEnv({ 
        GOOGLE_API_KEY: cloudApiKey || process.env.GOOGLE_API_KEY || ''
      }, pyInfo, pythonScriptDir)
    });

    let result = '';
    let errorLogs = '';
    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');

    child.stdout.on('data', (d) => { result += d; });
    child.stderr.on('data', (d) => { 
      console.log('[Batch Scanner stderr]:', d); 
      errorLogs += d; 
      // Send progress updates to renderer if needed
      event.sender.send('batch-scan-progress', d);
    });

    child.on('close', (code) => {
      if (code === 0) {
        try {
          const lines = result.trim().split('\n');
          let jsonLine = lines[lines.length - 1];
          if (!jsonLine || !jsonLine.trim().startsWith('{')) jsonLine = lines.find(l => l.trim().startsWith('{'));
          if (!jsonLine) throw new Error('No JSON found in output');
          const jsonResult = JSON.parse(jsonLine);
          resolve(jsonResult);
        } catch (e) {
          console.error('JSON parse error:', e); 
          console.error('Raw output:', result); 
          console.error('Stderr logs:', errorLogs);
          reject(new Error(`Failed to parse batch scan result: ${e.message}`));
        }
      } else {
        console.error('Process exited with code:', code); 
        console.error('Stderr:', errorLogs);
        reject(new Error(errorLogs || `Batch scan failed with code ${code}`));
      }
    });

    // Longer timeout for batch processing: 5 minutes
    setTimeout(() => { 
      try { child.kill(); } catch {} 
      reject(new Error('Batch scan timeout (300s)')); 
    }, 300000);
  });
});

ipcMain.handle('list-files-in-folder', async (event, folderPath) => {
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
  try {
    const entries = fs.readdirSync(folderPath, { withFileTypes: true });
    const dirs = entries.filter((e) => e.isDirectory());
    const subfolders = dirs.map((d) => path.join(folderPath, d.name));
    return { success: true, folders: subfolders };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

ipcMain.handle('list-folder-tree', async (event, basePath) => {
  function buildTree(dirPath) {
    const children = [];
    try {
      const entries = fs.readdirSync(dirPath, { withFileTypes: true });
      for (const e of entries) {
        if (e.isDirectory()) {
          const childPath = path.join(dirPath, e.name);
          const node = buildTree(childPath);
          children.push({ path: childPath, name: e.name, children: node ? node.children : [] });
        }
      }
    } catch {}
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

ipcMain.handle('analyze-parent-folder', async (event, folderPath) => {
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

ipcMain.handle('process-document-offline', async (event, filePath) => {
  return new Promise(async (resolve, reject) => {
    const ocrEngineType = store.get('ocrEngine', store.get('ocrEngineType', 'tesseract'));

    let cloudApiKey = null;
    let cloudEndpoint = null;

    if (ocrEngineType === 'google') {
      cloudApiKey = store.get('cloudOCR.google.apiKey', '');
      if (!cloudApiKey) {
        resolve({ success: false, error: 'Google Cloud Vision API key not configured. Please add it in Cloud OCR settings.', method: 'config_error' });
        return;
      }
    } else if (ocrEngineType === 'azure') {
      cloudApiKey = store.get('cloudOCR.azure.apiKey', '');
      cloudEndpoint = store.get('cloudOCR.azureEndpoint.apiKey', '');
      if (!cloudApiKey || !cloudEndpoint) {
        resolve({ success: false, error: 'Azure Computer Vision API key and endpoint not configured. Please add them in Cloud OCR settings.', method: 'config_error' });
        return;
      }
    } else if (ocrEngineType === 'gemini-flash' || ocrEngineType === 'gemini-flash-hybrid' || ocrEngineType === 'gemini-flash-lite' || ocrEngineType === 'gemini-flash-text') {
      cloudApiKey = store.get('cloudOCR.gemini.apiKey', '') || process.env.GOOGLE_API_KEY || '';
      if (!cloudApiKey) {
        resolve({ success: false, error: 'Google API key not configured for Gemini. Please add it in Cloud OCR settings.', method: 'config_error' });
        return;
      }
    } else if (ocrEngineType === 'openai-gpt4o-mini') {
      cloudApiKey = store.get('cloudOCR.openai.apiKey', '');
      if (!cloudApiKey) {
        resolve({ success: false, error: 'OpenAI API key not configured. Please add it in Cloud OCR settings.', method: 'config_error' });
        return;
      }
    }

    const pyInfo = discoverPython();
    if (!pyInfo.ok) {
      reject(new Error('Python 3.10–3.12 not found. Please install Python.'));
      return;
    }

    const scriptPath = isDev ? path.join(__dirname, '../python/process_document.py') : getPythonScriptPath('process_document.py');
    const args = [scriptPath, filePath, ocrEngineType];
    if (cloudApiKey) {
      args.push(cloudApiKey);
      if (cloudEndpoint) args.push(cloudEndpoint);
    }

    console.log(`Spawning: ${pyInfo.executable} ${args.map(a => (a === cloudApiKey ? '[API_KEY]' : a)).join(' ')}`);

    const pythonScriptDir = path.dirname(scriptPath);
    
    // Get resize settings from store
    const enableResize = store.get('enableResize', true);
    const maxWidth = store.get('maxWidth', 2000);
    const maxHeight = store.get('maxHeight', 2800);
    
    const child = spawn(pyInfo.executable, args, {
      cwd: pythonScriptDir,
      env: buildPythonEnv({ 
        GOOGLE_API_KEY: cloudApiKey || process.env.GOOGLE_API_KEY || '',
        ENABLE_RESIZE: enableResize ? 'true' : 'false',
        MAX_WIDTH: String(maxWidth),
        MAX_HEIGHT: String(maxHeight)
      }, pyInfo, pythonScriptDir)
    });

    let result = '';
    let errorLogs = '';
    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');

    child.stdout.on('data', (d) => { result += d; });
    child.stderr.on('data', (d) => { console.log('[Python stderr]:', d); errorLogs += d; });

    child.on('close', (code) => {
      if (code === 0) {
        try {
          const lines = result.trim().split('\n');
          let jsonLine = lines[lines.length - 1];
          if (!jsonLine || !jsonLine.trim().startsWith('{')) jsonLine = lines.find(l => l.trim().startsWith('{'));
          if (!jsonLine) throw new Error('No JSON found in output');
          const jsonResult = JSON.parse(jsonLine);
          console.log('📝 Original text extracted:', (jsonResult.original_text || '').substring(0, 100));
          resolve(jsonResult);
        } catch (e) {
          console.error('JSON parse error:', e); console.error('Raw output:', result); console.error('Stderr logs:', errorLogs);
          reject(new Error(`Failed to parse OCR result: ${e.message}`));
        }
      } else {
        console.error('Process exited with code:', code); console.error('Stderr:', errorLogs);
        reject(new Error(errorLogs || `OCR processing failed with code ${code}`));
      }
    });

    setTimeout(() => { try { child.kill(); } catch {} reject(new Error('OCR processing timeout (60s)')); }, 60000);
  });
});

ipcMain.handle('choose-save-path', async (event, defaultName) => {
  const result = await dialog.showSaveDialog(mainWindow, { defaultPath: defaultName, filters: [{ name: 'PDF', extensions: ['pdf'] }] });
  if (result.canceled) return null; return result.filePath;
});

ipcMain.handle('merge-by-short-code', async (event, items, options = {}) => {
  console.log('='.repeat(80));
  console.log('🚀 MERGE HANDLER CALLED IN MAIN.JS');
  console.log('📦 Items count:', items.length);
  console.log('⚙️ Options:', JSON.stringify(options, null, 2));
  console.log('='.repeat(80));
  
  const { PDFDocument } = require('pdf-lib');
  const groups = items.reduce((acc, it) => { const key = it.short_code || 'UNKNOWN'; if (!acc[key]) acc[key] = []; acc[key].push(it.filePath); return acc; }, {});
  
  console.log('📊 Groups created:', Object.keys(groups).join(', '));
  console.log('📊 Group details:', Object.entries(groups).map(([k, v]) => `${k}: ${v.length} files`).join(', '));
  
  const results = [];
  for (const [shortCode, filePaths] of Object.entries(groups)) {
    try {
      const outPdf = await PDFDocument.create();
      for (const fp of filePaths) {
        const ext = path.extname(fp).toLowerCase();
        const bytes = fs.readFileSync(fp);
        if (ext === '.pdf') {
          const srcPdf = await PDFDocument.load(bytes);
          const copiedPages = await outPdf.copyPages(srcPdf, srcPdf.getPageIndices());
          copiedPages.forEach((p) => outPdf.addPage(p));
        } else if (['.jpg', '.jpeg', '.png', '.bmp', '.gif'].includes(ext)) {
          const img = ext === '.png' ? await outPdf.embedPng(bytes) : await outPdf.embedJpg(bytes);
          const { width, height } = img.size();
          const page = outPdf.addPage([width, height]);
          page.drawImage(img, { x: 0, y: 0, width, height });
        } else {
          console.warn('Unsupported for merge:', fp);
        }
      }
      const pdfBytes = await outPdf.save();
      let outputPath;
      if (options.autoSave) {
        // Use parentFolder from options if provided, otherwise get from filePath
        const childFolder = options.parentFolder || path.dirname(filePaths[0]);
        let targetDir;
        
        console.log(`📂 Merge processing for ${shortCode}:`);
        console.log(`   childFolder: ${childFolder}`);
        console.log(`   parentFolder (from options): ${options.parentFolder || 'null'}`);
        console.log(`   mergeMode: ${options.mergeMode}`);
        console.log(`   customOutputFolder: ${options.customOutputFolder || 'null'}`);
        console.log(`   Files to merge: ${filePaths.length}`);
        
        if (options.mergeMode === 'new') {
          const parentOfChild = path.dirname(childFolder);
          const childBaseName = path.basename(childFolder);
          const newFolderName = childBaseName + (options.mergeSuffix || '_merged');
          targetDir = path.join(parentOfChild, newFolderName);
          if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });
          console.log(`   ✅ Mode 'new': targetDir = ${targetDir}`);
        } else if (options.mergeMode === 'custom' && options.customOutputFolder) {
          // Custom folder mode: Create subfolder named after source folder
          const childBaseName = path.basename(childFolder);
          targetDir = path.join(options.customOutputFolder, childBaseName);
          console.log(`   📁 Attempting to create custom folder:`);
          console.log(`      customOutputFolder: ${options.customOutputFolder}`);
          console.log(`      childBaseName: ${childBaseName}`);
          console.log(`      targetDir: ${targetDir}`);
          
          try {
            // First check if customOutputFolder exists
            if (!fs.existsSync(options.customOutputFolder)) {
              console.error(`   ❌ Custom output folder does not exist: ${options.customOutputFolder}`);
              throw new Error(`Custom output folder does not exist: ${options.customOutputFolder}`);
            }
            
            // Check if we have write permission
            try {
              fs.accessSync(options.customOutputFolder, fs.constants.W_OK);
              console.log(`   ✅ Write permission OK for: ${options.customOutputFolder}`);
            } catch (permErr) {
              console.error(`   ❌ No write permission for: ${options.customOutputFolder}`);
              throw new Error(`No write permission for custom folder: ${options.customOutputFolder}`);
            }
            
            // Now try to create subfolder
            if (!fs.existsSync(targetDir)) {
              console.log(`   📁 Creating subfolder: ${targetDir}`);
              fs.mkdirSync(targetDir, { recursive: true });
              console.log(`   ✅ Subfolder created successfully: ${targetDir}`);
            } else {
              console.log(`   ✅ Subfolder already exists: ${targetDir}`);
            }
          } catch (mkdirErr) {
            console.error(`   ❌ Failed to create directory:`, mkdirErr);
            console.error(`      Error code: ${mkdirErr.code}`);
            console.error(`      Error message: ${mkdirErr.message}`);
            throw new Error(`Cannot create output directory: ${targetDir} - ${mkdirErr.message}`);
          }
        } else {
          // Default: Same folder (root mode)
          targetDir = childFolder;
          console.log(`   ✅ Mode 'root': targetDir = ${targetDir}`);
        }
        outputPath = path.join(targetDir, `${shortCode}.pdf`);
        console.log(`   🎯 Final output path: ${outputPath}`);
        let count = 1;
        while (fs.existsSync(outputPath)) { outputPath = path.join(targetDir, `${shortCode}(${count}).pdf`); count += 1; }
        
        try {
          fs.writeFileSync(outputPath, Buffer.from(pdfBytes));
          console.log(`   ✅ PDF written successfully: ${outputPath}`);
          results.push({ short_code: shortCode, path: outputPath, count: filePaths.length, success: true, autoSaved: true });
        } catch (writeErr) {
          console.error(`   ❌ Failed to write PDF: ${writeErr.message}`);
          throw new Error(`Cannot write PDF to: ${outputPath} - ${writeErr.message}`);
        }
      } else {
        const savePath = await dialog.showSaveDialog(mainWindow, { defaultPath: `${shortCode}.pdf`, filters: [{ name: 'PDF', extensions: ['pdf'] }] });
        if (!savePath.canceled && savePath.filePath) {
          fs.writeFileSync(savePath.filePath, pdfBytes);
          outputPath = savePath.filePath;
          results.push({ short_code: shortCode, path: outputPath, count: filePaths.length, success: true });
        } else {
          results.push({ short_code: shortCode, canceled: true, success: false });
        }
      }
    } catch (err) {
      console.error('❌ Merge error for', shortCode, ':', err.message);
      console.error('   Stack:', err.stack);
      results.push({ short_code: shortCode, error: err.message, success: false });
    }
  }
  
  console.log('='.repeat(80));
  console.log('✅ MERGE HANDLER COMPLETED');
  console.log('📊 Results:', results.map(r => `${r.short_code}: ${r.success ? '✅' : '❌'}`).join(', '));
  console.log('='.repeat(80));
  
  return results;
});

ipcMain.handle('get-config', (event, key) => { try { return typeof key === 'string' ? store.get(key) : store.store; } catch (e) { return null; } });
ipcMain.handle('set-config', (event, key, value) => { store.set(key, value); return true; });

ipcMain.handle('get-backend-url', () => store.get('backendUrl', 'https://sohoavpdkct.up.railway.app'));
ipcMain.handle('set-backend-url', (event, url) => { store.set('backendUrl', url); return true; });

ipcMain.handle('process-document-cloud', async (event, filePath) => {
  const FormData = require('form-data');
  const axios = require('axios');
  return new Promise(async (resolve) => {
    try {
      const backendUrl = store.get('backendUrl', 'https://sohoavpdkct.up.railway.app');
      if (!backendUrl) { resolve({ success: false, method: 'cloud_boost_failed', error: 'Backend URL not configured', status: null, errorType: 'CONFIG' }); return; }
      console.log(`Cloud Boost: Uploading ${filePath} to ${backendUrl}`);
      const normalizedUrl = backendUrl.replace(/\/$/, '');
      const form = new FormData();
      form.append('file', fs.createReadStream(filePath));
      const response = await axios.post(`${normalizedUrl}/api/scan-document-public`, form, { headers: { ...form.getHeaders() }, timeout: 30000 });
      const backendData = response.data;
      resolve({ success: true, method: 'cloud_boost', doc_type: backendData.detected_full_name || 'Không rõ', short_code: backendData.short_code || 'UNKNOWN', confidence: backendData.confidence_score || 0, accuracy_estimate: '93%+', original_text: backendData.detected_full_name || '', recommend_cloud_boost: false });
    } catch (error) {
      console.error('Cloud Boost error:', error);
      const status = error.response?.status || null;
      let errorType = 'OTHER';
      if (error.code === 'ECONNABORTED') errorType = 'TIMEOUT';
      else if (error.code === 'ECONNREFUSED' || !error.response) errorType = 'NETWORK';
      else if (status === 401 || status === 403) errorType = 'UNAUTHORIZED';
      else if (status === 402 || status === 429) errorType = 'QUOTA';
      else if (status && status >= 500) errorType = 'SERVER';
      resolve({ success: false, method: 'cloud_boost_failed', error: error.response?.data?.detail || error.message || 'Cloud Boost failed', status, errorType });
    }
  });
});

// Batch Process Handler
ipcMain.handle('batch-process-documents', async (event, { mode, imagePaths, ocrEngine }) => {
  return new Promise((resolve) => {
    try {
      console.log(`\n📦 Batch Process: mode=${mode}, images=${imagePaths.length}, engine=${ocrEngine}`);
      
      // Check if engine is gemini-flash-text (Tesseract + Gemini Text)
      let finalMode = mode;
      if (ocrEngine === 'gemini-flash-text') {
        finalMode = 'tesseract_text';
        console.log(`🔬 [ENGINE] Using Tesseract + Gemini Text mode`);
        console.log(`   Overriding: ${mode} → tesseract_text`);
      } else {
        console.log(`   Using standard mode: ${mode}, engine: ${ocrEngine}`);
      }
      
      // Get API key for cloud engines
      let cloudApiKey = null;
      if (ocrEngine === 'gemini-flash' || ocrEngine === 'gemini-flash-hybrid' || ocrEngine === 'gemini-flash-lite' || ocrEngine === 'gemini-flash-text') {
        cloudApiKey = store.get('cloudOCR.gemini.apiKey', '') || process.env.GOOGLE_API_KEY || '';
        if (!cloudApiKey) {
          resolve({ success: false, error: 'Google API key not configured', results: [] });
          return;
        }
      }
      
      // Determine Python script path
      const pythonDir = isDev 
        ? path.join(__dirname, '../python')
        : path.join(process.resourcesPath, 'python');
      const scriptPath = path.join(pythonDir, 'batch_processor.py');
      
      // Build args (use finalMode instead of mode)
      const args = [scriptPath, finalMode, ocrEngine, cloudApiKey, ...imagePaths];
      
      console.log(`🐍 Calling Python batch processor:`);
      console.log(`   Script: ${scriptPath}`);
      console.log(`   Mode: ${finalMode}`);
      console.log(`   Engine: ${ocrEngine}`);
      console.log(`   Images: ${imagePaths.length}`);
      
      // Discover Python executable
      const pyInfo = discoverPython();
      if (!pyInfo.ok) {
        resolve({ success: false, error: 'Python not found', results: [] });
        return;
      }
      
      console.log(`   Python: ${pyInfo.executable}`);
      
      // Get smart batch size setting
      const smartMaxBatchSize = store.get('smartMaxBatchSize') || 10;
      console.log(`🔍 DEBUG: smartMaxBatchSize from store = ${smartMaxBatchSize}`);
      console.log(`🔍 DEBUG: Passing SMART_MAX_BATCH_SIZE = ${smartMaxBatchSize}`);
      
      // Spawn Python process
      const pythonProcess = spawn(pyInfo.executable, args, {
        cwd: pythonDir,
        env: buildPythonEnv({ SMART_MAX_BATCH_SIZE: smartMaxBatchSize.toString() }, pyInfo, pythonDir)
      });
      
      let stdoutData = '';
      let stderrData = '';
      
      pythonProcess.stdout.on('data', (data) => {
        stdoutData += data.toString();
      });
      
      pythonProcess.stderr.on('data', (data) => {
        const text = data.toString();
        stderrData += text;
        console.log(`[Python batch]: ${text.trim()}`);
      });
      
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          try {
            // Parse JSON output from stdout
            const results = JSON.parse(stdoutData);
            console.log(`✅ Batch process complete: ${results.length} results`);
            resolve({ success: true, results: results });
          } catch (e) {
            console.error('Failed to parse batch results:', e);
            console.error('Stdout:', stdoutData);
            console.error('Stderr:', stderrData);
            resolve({ success: false, error: 'Failed to parse results', results: [] });
          }
        } else {
          console.error(`Batch process failed with code ${code}`);
          console.error('Stderr output:', stderrData);
          console.error('Stdout output:', stdoutData);
          resolve({ success: false, error: `Process exited with code ${code}. Error: ${stderrData}`, results: [] });
        }
      });
      
      pythonProcess.on('error', (err) => {
        console.error('Batch process error:', err);
        resolve({ success: false, error: err.message, results: [] });
      });
      
    } catch (err) {
      console.error('Batch process handler error:', err);
      resolve({ success: false, error: err.message, results: [] });
    }
  });
});

ipcMain.handle('read-image-data-url', async (event, filePath) => {
  try {
    const ext = path.extname(filePath).toLowerCase();
    const mimeMap = { '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.bmp': 'image/bmp' };
    const mime = mimeMap[ext];
    if (!mime) return null;
    const data = fs.readFileSync(filePath);
    const base64 = data.toString('base64');
    return `data:${mime};base64,${base64}`;
  } catch (err) { console.error('read-image-data-url error:', err); return null; }
});

// Rules Manager helpers via Python scripts
function spawnJsonPython(args, timeoutMs = 10000) {
  const pyInfo = discoverPython();
  if (!pyInfo.ok) return Promise.reject(new Error('Python not found'));
  return new Promise((resolve, reject) => {
    const child = spawn(pyInfo.executable, args, { env: buildPythonEnv({}, pyInfo, path.dirname(args[0])) });
    let out = '', err = '';
    child.stdout.on('data', d => out += d.toString());
    child.stderr.on('data', d => err += d.toString());
    child.on('close', (code) => {
      if (code === 0) {
        try { resolve(JSON.parse(out)); } catch (e) { reject(new Error(`Failed to parse result: ${e.message}`)); }
      } else { reject(new Error(err || `Failed with code ${code}`)); }
    });
    setTimeout(() => { try { child.kill(); } catch {} reject(new Error('Timeout')); }, timeoutMs);
  });
}

ipcMain.handle('get-rules', async () => {
  try { return { success: true, rules: await spawnJsonPython([(isDev ? path.join(__dirname, '../python/rules_manager.py') : getPythonScriptPath('rules_manager.py')), 'get']) }; }
  catch (e) { return { success: false, error: e.message }; }
});

ipcMain.handle('save-rule', async (event, docType, ruleData) => {
  try { return await spawnJsonPython([(isDev ? path.join(__dirname, '../python/rules_manager.py') : getPythonScriptPath('rules_manager.py')), 'save', docType, JSON.stringify(ruleData)]); }
  catch (e) { return { success: false, error: e.message }; }
});

ipcMain.handle('delete-rule', async (event, docType) => {
  try { return await spawnJsonPython([(isDev ? path.join(__dirname, '../python/rules_manager.py') : getPythonScriptPath('rules_manager.py')), 'delete', docType]); }
  catch (e) { return { success: false, error: e.message }; }
});

ipcMain.handle('reset-rules', async () => {
  try { return await spawnJsonPython([(isDev ? path.join(__dirname, '../python/rules_manager.py') : getPythonScriptPath('rules_manager.py')), 'reset']); }
  catch (e) { return { success: false, error: e.message }; }
});

ipcMain.handle('export-rules', async () => {
  try {
    const result = await dialog.showSaveDialog(mainWindow, { title: 'Export Rules', defaultPath: 'rules-export.json', filters: [{ name: 'JSON Files', extensions: ['json'] }] });
    if (result.canceled) return { success: false, message: 'Export cancelled' };
    return await spawnJsonPython([(isDev ? path.join(__dirname, '../python/rules_manager.py') : getPythonScriptPath('rules_manager.py')), 'export', result.filePath]);
  } catch (e) { return { success: false, error: e.message }; }
});

ipcMain.handle('import-rules', async (event, mergeBool = true) => {
  try {
    const result = await dialog.showOpenDialog(mainWindow, { title: 'Import Rules', filters: [{ name: 'JSON Files', extensions: ['json'] }], properties: ['openFile'] });
    if (result.canceled) return { success: false, message: 'Import cancelled' };
    return await spawnJsonPython([(isDev ? path.join(__dirname, '../python/rules_manager.py') : getPythonScriptPath('rules_manager.py')), 'import', result.filePaths[0], mergeBool ? 'true' : 'false']);
  } catch (e) { return { success: false, error: e.message }; }
});

// Scan History Management
ipcMain.handle('save-scan-state', (event, scanData) => {
  try {
    // Use provided scanId or generate new one
    const scanId = scanData.scanId || `scan_${Date.now()}`;
    const scans = scanStore.get('scans', {});
    
    // Add/update scan (OVERWRITE if same scanId)
    scanData.scanId = scanId;
    scanData.timestamp = Date.now();
    
    // Overwrite existing or create new
    scans[scanId] = scanData;
    scanStore.set('scans', scans);
    
    const action = scans[scanId] ? 'Updated' : 'Created';
    console.log(`💾 ${action} scan state: ${scanId}, ${scanData.results?.length || scanData.folderTabs?.filter(t => t.status === 'done').length || 0} items`);
    return { success: true, scanId: scanId };
  } catch (e) {
    console.error('❌ Save scan state error:', e);
    return { success: false, error: e.message };
  }
});

ipcMain.handle('get-incomplete-scans', () => {
  try {
    const scans = scanStore.get('scans', {});
    
    // Filter: incomplete only (cleanup already done on startup)
    const incompleteScans = [];
    
    for (const [scanId, scanData] of Object.entries(scans)) {
      if (scanData.status === 'incomplete') {
        incompleteScans.push({
          scanId: scanId,
          ...scanData
        });
      }
    }
    
    console.log(`📋 Found ${incompleteScans.length} incomplete scan(s)`);
    return { success: true, scans: incompleteScans };
  } catch (e) {
    console.error('❌ Get incomplete scans error:', e);
    return { success: false, error: e.message, scans: [] };
  }
});

ipcMain.handle('load-scan-state', (event, scanId) => {
  try {
    const scans = scanStore.get('scans', {});
    const scanData = scans[scanId];
    
    if (!scanData) {
      return { success: false, error: 'Scan not found' };
    }
    
    console.log(`📂 Loaded scan state: ${scanId}`);
    return { success: true, data: scanData };
  } catch (e) {
    console.error('Load scan state error:', e);
    return { success: false, error: e.message };
  }
});

ipcMain.handle('delete-scan-state', (event, scanId) => {
  try {
    const scans = scanStore.get('scans', {});
    delete scans[scanId];
    scanStore.set('scans', scans);
    
    console.log(`🗑️ Deleted scan state: ${scanId}`);
    return { success: true };
  } catch (e) {
    console.error('❌ Delete scan state error:', e);
    return { success: false, error: e.message };
  }
});

// Get base64 image for preview
ipcMain.handle('get-base64-image', async (event, filePath) => {
  try {
    if (!fs.existsSync(filePath)) {
      throw new Error('File not found');
    }
    
    const imageBuffer = fs.readFileSync(filePath);
    const base64Image = imageBuffer.toString('base64');
    const ext = path.extname(filePath).toLowerCase();
    
    // Determine MIME type
    let mimeType = 'image/jpeg';
    if (ext === '.png') mimeType = 'image/png';
    else if (ext === '.gif') mimeType = 'image/gif';
    else if (ext === '.bmp') mimeType = 'image/bmp';
    else if (ext === '.webp') mimeType = 'image/webp';
    
    return `data:${mimeType};base64,${base64Image}`;
  } catch (e) {
    console.error('❌ Get base64 image error:', filePath, e.message);
    throw e;
  }
});

ipcMain.handle('mark-scan-complete', (event, scanId) => {
  try {
    const scanHistory = store.get('scanHistory', {});
    if (scanHistory[scanId]) {
      scanHistory[scanId].status = 'complete';
      scanHistory[scanId].completedAt = Date.now();
      store.set('scanHistory', scanHistory);
      console.log(`✅ Marked scan complete: ${scanId}`);
    }
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
});

ipcMain.handle('open-rules-folder', async () => {
  try {
    const res = await spawnJsonPython([(isDev ? path.join(__dirname, '../python/rules_manager.py') : getPythonScriptPath('rules_manager.py')), 'folder']);
    if (res.success && res.path) {
      const { shell } = require('electron');
      await shell.openPath(res.path);
      return { success: true, message: `Opened ${res.path}` };
    }
    return { success: false, error: 'Failed to get folder path' };
  } catch (e) { return { success: false, error: e.message }; }
});

ipcMain.handle('generate-keyword-variants', async (event, keyword, includeTypos = true) => {
  try {
    return await spawnJsonPython([path.join(__dirname, '../python/keyword_variants.py'), keyword, includeTypos ? 'true' : 'false'], 5000);
  } catch (e) { return { success: false, error: e.message }; }
});

// ===== Cloud OCR API Key Management =====
ipcMain.handle('save-api-key', async (event, { provider, apiKey }) => {
  try {
    if (!provider || typeof apiKey !== 'string') {
      return { success: false, error: 'Thiếu provider hoặc apiKey' };
    }
    store.set(`cloudOCR.${provider}.apiKey`, apiKey);
    return { success: true, message: `API key cho ${provider} đã lưu` };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-api-key', async (event, provider) => {
  try {
    return store.get(`cloudOCR.${provider}.apiKey`, '');
  } catch (error) {
    return '';
  }
});

ipcMain.handle('delete-api-key', async (event, provider) => {
  try {
    store.delete(`cloudOCR.${provider}.apiKey`);
    if (provider === 'azure') {
      store.delete('cloudOCR.azureEndpoint.apiKey');
    }
    return { success: true, message: `Đã xóa API key của ${provider}` };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('test-api-key', async (event, { provider, apiKey, endpoint }) => {
  try {
    const axios = require('axios');

    if (provider === 'google') {
      const testUrl = `https://vision.googleapis.com/v1/images:annotate?key=${apiKey}`;
      const response = await axios.post(testUrl, {
        requests: [{
          image: { content: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==' },
          features: [{ type: 'TEXT_DETECTION', maxResults: 1 }]
        }]
      }, { timeout: 10000 });
      if (response.status === 200) {
        return { success: true, message: '✅ Google Cloud Vision API key hợp lệ' };
      }
      return { success: false, error: 'Google Vision test thất bại' };
    }

    if (provider === 'azure') {
      if (!endpoint) return { success: false, error: 'Thiếu Azure endpoint' };
      const normalizedEndpoint = endpoint.replace(/\/$/, '');
      const testUrl = `${normalizedEndpoint}/vision/v3.2/read/analyze`;
      const response = await axios.post(testUrl, { url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Atomist_quote_from_Democritus.png/338px-Atomist_quote_from_Democritus.png' }, {
        headers: { 'Ocp-Apim-Subscription-Key': apiKey, 'Content-Type': 'application/json' },
        timeout: 10000
      });
      if (response.status === 202) {
        return { success: true, message: '✅ Azure Computer Vision API key hợp lệ' };
      }
      return { success: false, error: 'Azure test thất bại' };
    }

    if (provider === 'gemini') {
      const testUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;
      const response = await axios.post(testUrl, { contents: [{ parts: [{ text: 'Hello, this is a test.' }] }] }, { headers: { 'Content-Type': 'application/json' }, timeout: 10000 });
      if (response.status === 200 && response.data && response.data.candidates) {
        return { success: true, message: '✅ Gemini Flash API key hợp lệ' };
      }
      return { success: false, error: 'Gemini test thất bại' };
    }

    if (provider === 'openai') {
      const testUrl = 'https://api.openai.com/v1/chat/completions';
      const response = await axios.post(testUrl, {
        model: 'gpt-4o-mini',
        messages: [{ role: 'user', content: 'Hello, this is a test.' }],
        max_tokens: 10
      }, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        timeout: 15000
      });
      if (response.status === 200 && response.data && response.data.choices) {
        return { success: true, message: '✅ OpenAI GPT-4o mini API key hợp lệ' };
      }
      return { success: false, error: 'OpenAI test thất bại' };
    }

    return { success: false, error: `Provider không hỗ trợ: ${provider}` };
  } catch (error) {
    let msg = error.message;
    const status = error.response?.status;
    if (status === 401 || status === 403) msg = 'API key không hợp lệ hoặc không có quyền';
    else if (status === 429) msg = 'Quá giới hạn request';
    else if (error.code === 'ENOTFOUND' || error.code === 'ETIMEDOUT') msg = 'Không thể kết nối tới Cloud API';
    return { success: false, error: msg };
  }
});

