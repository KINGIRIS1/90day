import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Badge } from '@/components/ui/badge';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function LlmStatus() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_URL}/api/llm/health`);
      setData(res.data);
      setError(null);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const id = setInterval(fetchStatus, 30000);
    return () => clearInterval(id);
  }, []);

  if (loading) return <div className="text-gray-500">Đang kiểm tra...</div>;
  if (error) return <div className="text-red-600">Lỗi: {String(error)}</div>;
  if (!data) return null;

  const statusColor = data.status === 'healthy' ? 'bg-green-600' : data.status === 'degraded' ? 'bg-yellow-600' : 'bg-red-600';

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className={`inline-block w-3 h-3 rounded-full ${statusColor}`}></span>
        <span className="font-medium">{data.status.toUpperCase()}</span>
      </div>
      <div className="flex items-center gap-2">
        <Badge variant={data.openai_available ? 'default' : 'destructive'}>OpenAI: {data.openai_available ? 'Available' : 'Down'}</Badge>
        <Badge variant={data.emergent_available ? 'default' : 'outline'}>Fallback: {data.emergent_available ? 'Available' : 'Off/Down'}</Badge>
      </div>
      <div className="text-sm text-gray-600">Provider: {data.provider || 'none'} {data.model ? `(model: ${data.model})` : ''}</div>
      {data.details && <div className="text-xs text-gray-500">{data.details}</div>}
      <button onClick={fetchStatus} className="mt-2 px-3 py-1 border rounded hover:bg-gray-50">Làm mới</button>
    </div>
  );
}

export default LlmStatus;
