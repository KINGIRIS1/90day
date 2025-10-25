import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { compressImages } from '../utils/imageCompression';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const BATCH_SIZE = 10; // Upload 10 ảnh mỗi lần để tránh quá tải băng thông

export default function FolderPickerDirectBatched({ token }) {
  const [files, setFiles] = useState([]);
  const [jobs, setJobs] = useState([]); // Multiple batch jobs
  const [status, setStatus] = useState(null);
  const [packZip, setPackZip] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState({ current: 0, total: 0 });
  const [batchProgress, setBatchProgress] = useState({ current: 0, total: 0 });

  const onPick = (e) => {
    const list = Array.from(e.target.files || []);
    setFiles(list);
    setJobs([]);
    setError(null);
  };

  const startScan = async () => {
    if (!files.length) {
      setError('Vui lòng chọn thư mục trước khi quét');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setStatus('Đang chuẩn bị...');
      setJobs([]);

      // Filter image files only
      const imageFiles = files.filter(f => {
        const ext = f.name.toLowerCase();
        return ext.endsWith('.jpg') || ext.endsWith('.jpeg') || 
               ext.endsWith('.png') || ext.endsWith('.gif') ||
               ext.endsWith('.bmp') || ext.endsWith('.tiff') ||
               ext.endsWith('.webp') || ext.endsWith('.heic');
      });

      if (!imageFiles.length) {
        setError('Không tìm thấy file ảnh hợp lệ trong thư mục');
        setLoading(false);
        return;
      }

      // Compress all images first
      setStatus('Đang nén ảnh...');
      const compressedFiles = await compressImages(imageFiles, (current, total) => {
        setUploadProgress({ current, total });
        setStatus(`Đang nén ảnh ${current}/${total}...`);
      });

      // Split into batches of BATCH_SIZE
      const batches = [];
      for (let i = 0; i < compressedFiles.length; i += BATCH_SIZE) {
        batches.push(compressedFiles.slice(i, i + BATCH_SIZE));
      }

      setBatchProgress({ current: 0, total: batches.length });
      setStatus(`Chia thành ${batches.length} batch (${BATCH_SIZE} ảnh/batch)`);

      // Upload each batch sequentially
      const allJobs = [];
      for (let i = 0; i < batches.length; i++) {
        const batch = batches[i];
        setBatchProgress({ current: i + 1, total: batches.length });
        setStatus(`Đang tải batch ${i + 1}/${batches.length} (${batch.length} ảnh)...`);

        const form = new FormData();
        for (const f of batch) form.append('files', f);
        const rels = batch.map(f => f.webkitRelativePath || f.name);
        form.append('relative_paths', JSON.stringify(rels));
        form.append('pack_as_zip', String(packZip));

        const res = await axios.post(`${API_URL}/api/scan-folder-direct`, form, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        allJobs.push(res.data);
        setJobs([...allJobs]); // Update UI with current jobs
      }

      setStatus(`✅ Đã tải lên ${batches.length} batch. Đang xử lý...`);
      setLoading(false);

    } catch (e) {
      setError(e?.response?.data?.detail || e.message || 'Lỗi không xác định');
      setLoading(false);
    }
  };

  // Poll all jobs for status
  useEffect(() => {
    if (!jobs.length) return;

    const interval = setInterval(async () => {
      try {
        const updatedJobs = await Promise.all(
          jobs.map(async (job) => {
            const res = await axios.get(`${API_URL}/api/folder-direct-status/${job.job_id}`, {
              headers: { 'Authorization': `Bearer ${token}` }
            });
            return res.data;
          })
        );
        setJobs(updatedJobs);

        // Check if all completed
        const allDone = updatedJobs.every(j => j.status === 'completed' || j.status === 'error');
        if (allDone) {
          setStatus('✅ Hoàn thành tất cả batch!');
        }
      } catch (e) {
        console.error('Poll error:', e);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobs, token]);

  return (
    <div className="border rounded p-4 bg-gray-50">
      <h3 className="font-bold text-lg mb-2">📁 Quét Thư Mục (Batch Mode)</h3>
      <p className="text-sm text-gray-600 mb-3">
        Upload từng batch {BATCH_SIZE} ảnh để tránh quá tải băng thông
      </p>

      <input
        type="file"
        webkitdirectory=""
        directory=""
        multiple
        onChange={onPick}
        className="mb-3 text-sm"
      />

      {files.length > 0 && (
        <div className="text-sm mb-2 text-gray-700">
          📂 Đã chọn: {files.length} file
        </div>
      )}

      <div className="flex items-center gap-3 mb-3">
        <label className="text-sm flex items-center gap-2">
          <input
            type="checkbox"
            checked={packZip}
            onChange={(e) => setPackZip(e.target.checked)}
          />
          Tạo file ZIP cho mỗi thư mục
        </label>
      </div>

      <button
        onClick={startScan}
        disabled={loading || !files.length}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm font-medium"
      >
        {loading ? 'Đang xử lý...' : 'Bắt đầu quét'}
      </button>

      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          ❌ {error}
        </div>
      )}

      {status && (
        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded text-sm">
          ℹ️ {status}
        </div>
      )}

      {uploadProgress.total > 0 && (
        <div className="mt-2">
          <div className="text-xs text-gray-600 mb-1">
            Nén ảnh: {uploadProgress.current}/{uploadProgress.total}
          </div>
          <div className="w-full bg-gray-200 rounded h-2">
            <div
              className="bg-green-500 h-2 rounded transition-all"
              style={{ width: `${(uploadProgress.current / uploadProgress.total) * 100}%` }}
            />
          </div>
        </div>
      )}

      {batchProgress.total > 0 && (
        <div className="mt-2">
          <div className="text-xs text-gray-600 mb-1">
            Upload batch: {batchProgress.current}/{batchProgress.total}
          </div>
          <div className="w-full bg-gray-200 rounded h-2">
            <div
              className="bg-blue-500 h-2 rounded transition-all"
              style={{ width: `${(batchProgress.current / batchProgress.total) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Display all batch results */}
      {jobs.length > 0 && (
        <div className="mt-4 space-y-3">
          <h4 className="font-semibold text-sm">Kết quả theo batch:</h4>
          {jobs.map((job, idx) => (
            <div key={job.job_id} className="border rounded p-3 bg-white text-sm">
              <div className="font-medium mb-1">
                Batch {idx + 1} - {job.status === 'completed' ? '✅' : job.status === 'error' ? '❌' : '⏳'} {job.status}
              </div>

              {job.status === 'processing' && job.folder_results && (
                <div className="text-xs text-gray-600">
                  Đã xử lý: {job.completed_folders}/{job.total_folders} thư mục
                </div>
              )}

              {job.status === 'completed' && job.folder_results && (
                <div className="mt-2">
                  {job.folder_results.map((folder, fidx) => (
                    <div key={fidx} className="mb-2 pb-2 border-b last:border-b-0">
                      <div className="font-medium text-xs">📁 {folder.folder_name}</div>
                      <div className="text-xs text-gray-600 mt-1">
                        ✅ {folder.success_count} thành công | ❌ {folder.error_count} lỗi
                      </div>
                      {folder.pdf_urls && folder.pdf_urls.length > 0 && (
                        <div className="mt-1 flex flex-wrap gap-2">
                          {folder.pdf_urls.map((url, uidx) => (
                            <a
                              key={uidx}
                              href={`${API_URL}${url}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:underline text-xs"
                            >
                              📄 Tải PDF {uidx + 1}
                            </a>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}

                  {job.all_zip_url && (
                    <a
                      href={`${API_URL}${job.all_zip_url}`}
                      className="inline-block mt-2 px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-xs font-medium"
                    >
                      📦 Tải tất cả (ZIP)
                    </a>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
