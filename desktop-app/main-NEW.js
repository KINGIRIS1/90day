const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn, spawnSync } = require('child_process');
const Store = require('electron-store');
const fs = require('fs');

const store = new Store();
let mainWindow;

const isDev = !app.isPackaged;

// CRITICAL FIX: Ensure preload path is correct
const PRELOAD_PATH = path.join(__dirname, 'preload.js');
console.log('🔍 PRELOAD PATH:', PRELOAD_PATH);
console.log('🔍 PRELOAD EXISTS:', fs.existsSync(PRELOAD_PATH));

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
      preload: PRELOAD_PATH  // FIXED: Use constant
    },
    icon: path.join(__dirname, '../assets/icon.png')
  });

  const startUrl = isDev ? 'http://localhost:3001' : `file://${path.join(__dirname, '../build/index.html')}`;
  mainWindow.loadURL(startUrl);

  mainWindow.once('ready-to-show', () => {
    try { splash.destroy(); } catch {}
    mainWindow.show();
  });

  if (isDev) mainWindow.webContents.openDevTools();

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
    
    if (choice === 1) {
      e.preventDefault();
    }
  });

  mainWindow.on('closed', () => { mainWindow = null; });
}

const PY_PROBE = `
import sys, json, site
print(json.dumps({
  'version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
  'executable': sys.executable,
  'sites': site.getsitepackages(),
  'user': site.getusersitepackages()
}))
`;

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
          executable: info.executable || a.cmd,
          version: ver,
          sitePaths: sites,
          userSitePath: userSite
        };
      }
    } catch {}
  }
  return { ok: false };
}

function buildPythonEnv(baseEnv, pyInfo, scriptDir) {
  const env = { ...process.env, ...baseEnv };
  if (pyInfo.sitePaths && pyInfo.sitePaths.length) {
    const combined = [...pyInfo.sitePaths];
    if (pyInfo.userSitePath) combined.push(pyInfo.userSitePath);
    env.PYTHONPATH = combined.join(path.delimiter);
  }
  if (scriptDir) env.PYTHONPATH = `${scriptDir}${path.delimiter}${env.PYTHONPATH || ''}`;
  return env;
}

function getPythonScriptPath(scriptName) {
  return isDev
    ? path.join(__dirname, '../python', scriptName)
    : path.join(process.resourcesPath, 'app.asar.unpacked', 'python', scriptName);
}

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// IPC Handlers
ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  return result.filePaths[0];
});

ipcMain.handle('select-folders', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory', 'multiSelections']
  });
  return result.filePaths;
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

// Batch scanning - select CSV/Excel file
ipcMain.handle('select-file', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    title: options?.title || 'Select File',
    filters: options?.filters || []
  });
  return {
    success: !result.canceled,
    canceled: result.canceled,
    filePath: result.canceled ? null : result.filePaths[0]
  };
});

// Batch scanning - analyze CSV/Excel file
ipcMain.handle('analyze-batch-file', async (event, csvFilePath) => {
  const pyInfo = discoverPython();
  if (!pyInfo.ok) {
    return { success: false, error: 'Python not found' };
  }
  
  const batchScriptPath = isDev 
    ? path.join(__dirname, '../python/batch_scanner.py')
    : getPythonScriptPath('batch_scanner.py');
  
  return new Promise((resolve) => {
    const child = spawn(pyInfo.executable, [batchScriptPath, csvFilePath], {
      env: buildPythonEnv({}, pyInfo, path.dirname(batchScriptPath))
    });
    
    let stdout = '';
    let stderr = '';
    
    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          resolve({ success: false, error: `Failed to parse JSON: ${e.message}` });
        }
      } else {
        resolve({ success: false, error: stderr || `Process exited with code ${code}` });
      }
    });
    
    setTimeout(() => {
      try {
        child.kill();
      } catch {}
      resolve({ success: false, error: 'Analysis timeout' });
    }, 30000);
  });
});

ipcMain.handle('list-subfolders-in-folder', async (event, folderPath) => {
  try {
    const entries = fs.readdirSync(folderPath, { withFileTypes: true });
    const subfolders = entries
      .filter(e => e.isDirectory())
      .map(e => path.join(folderPath, e.name));
    return { success: true, subfolders };
  } catch (err) {
    return { success: false, error: err.message, subfolders: [] };
  }
});

ipcMain.handle('list-folder-tree', async (event, folderPath) => {
  try {
    const results = [];
    function recurse(currentPath) {
      const entries = fs.readdirSync(currentPath, { withFileTypes: true });
      for (const e of entries) {
        if (e.isDirectory()) {
          const fullPath = path.join(currentPath, e.name);
          results.push(fullPath);
          recurse(fullPath);
        }
      }
    }
    recurse(folderPath);
    return { success: true, subfolders: results };
  } catch (err) {
    return { success: false, error: err.message, subfolders: [] };
  }
});

ipcMain.handle('analyze-parent-folder', async (event, folderPath) => {
  try {
    const entries = fs.readdirSync(folderPath, { withFileTypes: true });
    const imageCount = entries.filter(e => e.isFile() && /\.(jpg|jpeg|png|gif|bmp|tiff|pdf)$/i.test(e.name)).length;
    const subfolderCount = entries.filter(e => e.isDirectory()).length;
    return { success: true, imageCount, subfolderCount };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

ipcMain.handle('list-files-in-folder', async (event, folderPath) => {
  try {
    const entries = fs.readdirSync(folderPath, { withFileTypes: true });
    const files = entries
      .filter(e => e.isFile() && /\.(jpg|jpeg|png|gif|bmp|tiff|pdf)$/i.test(e.name))
      .map(e => ({ name: e.name, path: path.join(folderPath, e.name) }));
    return { success: true, files };
  } catch (err) {
    return { success: false, error: err.message, files: [] };
  }
});

ipcMain.handle('rename-file', async (event, oldPath, newBaseName) => {
  try {
    const dir = path.dirname(oldPath);
    const ext = path.extname(oldPath);
    const newPath = path.join(dir, `${newBaseName}${ext}`);
    fs.renameSync(oldPath, newPath);
    return { success: true, newPath };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

ipcMain.handle('process-document-offline', async (event, filePath) => {
  const pyInfo = discoverPython();
  if (!pyInfo.ok) {
    return { success: false, error: 'Python not available' };
  }

  const processScript = getPythonScriptPath('process_document.py');

  return new Promise((resolve) => {
    const child = spawn(
      pyInfo.executable,
      [processScript, filePath, 'gemini-flash-lite', 'FAKE_KEY'],
      { env: buildPythonEnv({}, pyInfo, path.dirname(processScript)) }
    );

    let stdout = '', stderr = '';
    child.stdout.on('data', d => { stdout += d.toString(); });
    child.stderr.on('data', d => { stderr += d.toString(); });

    child.on('close', (code) => {
      if (code === 0 && stdout.trim()) {
        try {
          const data = JSON.parse(stdout.trim());
          resolve({ success: true, ...data });
        } catch {
          resolve({ success: false, error: 'Invalid JSON from Python' });
        }
      } else {
        resolve({ success: false, error: stderr || 'Process error' });
      }
    });

    setTimeout(() => {
      try { child.kill(); } catch {}
      resolve({ success: false, error: 'Timeout' });
    }, 60000);
  });
});

ipcMain.handle('process-document-cloud', async (event, filePath) => {
  return { success: false, error: 'Cloud OCR not implemented yet' };
});

ipcMain.handle('get-config', (event, key) => {
  return store.get(key);
});

ipcMain.handle('set-config', (event, key, value) => {
  store.set(key, value);
  return true;
});

ipcMain.handle('get-backend-url', () => {
  return store.get('backendUrl', 'http://localhost:8001');
});

ipcMain.handle('set-backend-url', (event, url) => {
  store.set('backendUrl', url);
  return true;
});

ipcMain.handle('merge-by-short-code', async (event, items, options) => {
  return { success: false, error: 'Not implemented' };
});

ipcMain.handle('choose-save-path', async (event, defaultName) => {
  const result = await dialog.showSaveDialog(mainWindow, {
    defaultPath: defaultName,
    filters: [{ name: 'PDF', extensions: ['pdf'] }]
  });
  return result.filePath || null;
});

ipcMain.handle('read-image-data-url', async (event, filePath) => {
  try {
    const data = fs.readFileSync(filePath);
    const base64 = data.toString('base64');
    const ext = path.extname(filePath).toLowerCase();
    const mimeMap = {
      '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
      '.png': 'image/png', '.gif': 'image/gif'
    };
    const mime = mimeMap[ext] || 'application/octet-stream';
    return `data:${mime};base64,${base64}`;
  } catch (err) {
    return null;
  }
});

ipcMain.handle('get-rules', () => {
  return store.get('rules', {});
});

ipcMain.handle('save-rule', (event, docType, ruleData) => {
  const rules = store.get('rules', {});
  rules[docType] = ruleData;
  store.set('rules', rules);
  return true;
});

ipcMain.handle('delete-rule', (event, docType) => {
  const rules = store.get('rules', {});
  delete rules[docType];
  store.set('rules', rules);
  return true;
});

ipcMain.handle('reset-rules', () => {
  store.set('rules', {});
  return true;
});

ipcMain.handle('export-rules', async () => {
  const result = await dialog.showSaveDialog(mainWindow, {
    filters: [{ name: 'JSON', extensions: ['json'] }]
  });
  if (result.filePath) {
    const rules = store.get('rules', {});
    fs.writeFileSync(result.filePath, JSON.stringify(rules, null, 2));
    return { success: true };
  }
  return { success: false };
});

ipcMain.handle('import-rules', async (event, merge) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [{ name: 'JSON', extensions: ['json'] }]
  });
  if (result.filePaths[0]) {
    const data = fs.readFileSync(result.filePaths[0], 'utf8');
    const imported = JSON.parse(data);
    if (merge) {
      const existing = store.get('rules', {});
      store.set('rules', { ...existing, ...imported });
    } else {
      store.set('rules', imported);
    }
    return { success: true };
  }
  return { success: false };
});

ipcMain.handle('open-rules-folder', () => {
  const rulesPath = store.path;
  const dir = path.dirname(rulesPath);
  require('electron').shell.openPath(dir);
  return true;
});

ipcMain.handle('generate-keyword-variants', (event, keyword, includeTypos) => {
  return [keyword];
});

ipcMain.handle('save-api-key', (event, data) => {
  store.set(`apiKey.${data.provider}`, data.key);
  return true;
});

ipcMain.handle('get-api-key', (event, provider) => {
  return store.get(`apiKey.${provider}`);
});

ipcMain.handle('delete-api-key', (event, provider) => {
  store.delete(`apiKey.${provider}`);
  return true;
});

ipcMain.handle('test-api-key', async (event, data) => {
  return { success: false, error: 'Not implemented' };
});
