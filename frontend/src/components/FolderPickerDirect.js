import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function FolderPickerDirect({ token }) {
  const [files, setFiles] = useState([]);
  const [job, setJob] = useState(null);
  const [status, setStatus] = useState(null);
  const [packZip, setPackZip] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onPick = (e) => {
    const list = Array.from(e.target.files || []);
    setFiles(list);
  };

  const startScan = async () => {
    if (!files.length) {
      setError('Vui lòng chọn thư mục trước khi quét');
      return;
    }
    try {
      setLoading(true);
      setError(null);
      setStatus(null);
      setJob(null);
      const form = new FormData();
      for (const f of files) form.append('files', f);
      const rels = files.map(f => f.webkitRelativePath || f.name);
      form.append('relative_paths', JSON.stringify(rels));
      form.append('pack_as_zip', String(packZip));
      const res = await axios.post(`${API_URL}/api/scan-folder-direct`, form, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setJob(res.data);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || 'Lỗi không xác định');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!job?.status_url) return;
    const id = setInterval(async () => {
      try {
        const r = await axios.get(`${API_URL}${job.status_url}`);
        setStatus(r.data);
      } catch (e) {
        setError(e?.response?.data?.detail || e.message);
      }
    }, 2000);
    return () => clearInterval(id);
  }, [job]);

  return (
    <div className="space-y-3">
      <div>
        <input type="file" webkitdirectory="" directory="" multiple onChange={onPick} />
      </div>
      <div className="flex items-center gap-2">
        <label className="flex items-center gap-1">
          <input type="checkbox" checked={packZip} onChange={(e)=>setPackZip(e.target.checked)} />
          <span>Tải tất cả (ZIP)</span>
        </label>
        <button onClick={startScan} className="px-3 py-1 border rounded">Bắt đầu quét</button>
        {job && !status && (
          <span className="text-xs text-gray-500 ml-2">Đang khởi tạo tác vụ...</span>
        )}
      </div>
      {status && (
        <div className="text-sm">
          {status.status !== 'completed' && (
            <div className="flex items-center gap-2 text-gray-600">
              <span className="inline-block w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              <span>Đang xử lý... {status.completed_folders}/{status.total_folders} thư mục</span>
            </div>
          )}
          <div>Trạng thái: {status.status}</div>
          <div>Thư mục hoàn tất: {status.completed_folders}/{status.total_folders}</div>
          {status.all_zip_url && status.status === 'completed' && (
            <div className="mt-2">
              <a className="px-3 py-1 border rounded bg-gray-50 hover:bg-gray-100" href={`${API_URL}${status.all_zip_url}`} target="_blank" rel="noreferrer">Tải tất cả (ZIP)</a>
            </div>
          )}
          {status.folder_results?.map(fr => (
            <div key={fr.folder_name} className="mt-2 p-2 border rounded">
              <div className="font-medium">{fr.folder_name}</div>
              <div>Thành công: {fr.success_count}, Lỗi: {fr.error_count}</div>
              {fr.errors?.length > 0 && (
                <details className="text-red-600 text-xs mt-1">
                  <summary>Lỗi chi tiết</summary>
                  <ul className="list-disc ml-6">
                    {fr.errors.map((e,idx)=>(<li key={idx}>{e}</li>))}
                  </ul>
                </details>
              )}
              <div className="space-x-2 mt-1">
                {fr.pdf_urls?.map((u,i)=>(
                  <a key={i} className="text-blue-600 underline" href={`${API_URL}${u}`} target="_blank" rel="noreferrer">PDF {i+1}</a>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
