const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn, spawnSync } = require('child_process');
const Store = require('electron-store');
const fs = require('fs');

const store = new Store();
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

  const startUrl = isDev ? 'http://localhost:3001' : `file://${path.join(__dirname, '../build/index.html')}`;
  mainWindow.loadURL(startUrl);

  mainWindow.once('ready-to-show', () => {
    try { splash.destroy(); } catch {}
    mainWindow.show();
  });

  if (isDev) mainWindow.webContents.openDevTools();

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

app.whenReady().then(() => {
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
    } else if (ocrEngineType === 'gemini-flash') {
      cloudApiKey = store.get('cloudOCR.gemini.apiKey', '') || process.env.GOOGLE_API_KEY || '';
      if (!cloudApiKey) {
        resolve({ success: false, error: 'Google API key not configured for Gemini Flash. Please add it in Cloud OCR settings.', method: 'config_error' });
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
    const child = spawn(pyInfo.executable, args, {
      cwd: pythonScriptDir,
      env: buildPythonEnv({ GOOGLE_API_KEY: cloudApiKey || process.env.GOOGLE_API_KEY || '' }, pyInfo, pythonScriptDir)
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
  const { PDFDocument } = require('pdf-lib');
  const groups = items.reduce((acc, it) => { const key = it.short_code || 'UNKNOWN'; if (!acc[key]) acc[key] = []; acc[key].push(it.filePath); return acc; }, {});
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
        const childFolder = path.dirname(filePaths[0]);
        let targetDir;
        if (options.mergeMode === 'new') {
          const parentOfChild = path.dirname(childFolder);
          const childBaseName = path.basename(childFolder);
          const newFolderName = childBaseName + (options.mergeSuffix || '_merged');
          targetDir = path.join(parentOfChild, newFolderName);
          if (!fs.existsSync(targetDir)) fs.mkdirSync(targetDir, { recursive: true });
        } else {
          targetDir = childFolder;
        }
        outputPath = path.join(targetDir, `${shortCode}.pdf`);
        let count = 1;
        while (fs.existsSync(outputPath)) { outputPath = path.join(targetDir, `${shortCode}(${count}).pdf`); count += 1; }
        fs.writeFileSync(outputPath, Buffer.from(pdfBytes));
        results.push({ short_code: shortCode, path: outputPath, count: filePaths.length, success: true, autoSaved: true });
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
      console.error('Merge error for', shortCode, err);
      results.push({ short_code: shortCode, error: err.message, success: false });
    }
  }
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
  try { return await spawnJsonPython([path.join(__dirname, '../python/rules_manager.py'), 'delete', docType]); }
  catch (e) { return { success: false, error: e.message }; }
});

ipcMain.handle('reset-rules', async () => {
  try { return await spawnJsonPython([path.join(__dirname, '../python/rules_manager.py'), 'reset']); }
  catch (e) { return { success: false, error: e.message }; }
});

ipcMain.handle('export-rules', async () => {
  try {
    const result = await dialog.showSaveDialog(mainWindow, { title: 'Export Rules', defaultPath: 'rules-export.json', filters: [{ name: 'JSON Files', extensions: ['json'] }] });
    if (result.canceled) return { success: false, message: 'Export cancelled' };
    return await spawnJsonPython([path.join(__dirname, '../python/rules_manager.py'), 'export', result.filePath]);
  } catch (e) { return { success: false, error: e.message }; }
});

ipcMain.handle('import-rules', async (event, mergeBool = true) => {
  try {
    const result = await dialog.showOpenDialog(mainWindow, { title: 'Import Rules', filters: [{ name: 'JSON Files', extensions: ['json'] }], properties: ['openFile'] });
    if (result.canceled) return { success: false, message: 'Import cancelled' };
    return await spawnJsonPython([path.join(__dirname, '../python/rules_manager.py'), 'import', result.filePaths[0], mergeBool ? 'true' : 'false']);
  } catch (e) { return { success: false, error: e.message }; }
});

ipcMain.handle('open-rules-folder', async () => {
  try {
    const res = await spawnJsonPython([path.join(__dirname, '../python/rules_manager.py'), 'folder']);
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

