import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '@/App.css';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Upload, FileText, Download, History, Trash2, Edit2, Check, X, Loader2, CheckCircle2, Settings, LogOut, Shield, User } from 'lucide-react';
import axios from 'axios';
import RulesManager from '@/components/RulesManager';
import { compressImages } from '@/utils/imageCompression';
import { useAuth } from '@/contexts/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DocumentScanner = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [scanResults, setScanResults] = useState([]);
  const [scanHistory, setScanHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [exporting, setExporting] = useState(false);
  const [scanProgress, setScanProgress] = useState({ current: 0, total: 0 });
  const [processedFiles, setProcessedFiles] = useState(new Set());
  
  // NEW: States for new features
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all'); // all, success, error
  const [filterCode, setFilterCode] = useState('all'); // all, GCNM, HSKT, etc
  const [retryingIds, setRetryingIds] = useState(new Set());
  const [scanDuration, setScanDuration] = useState(null); // Track scan time
  const [scanStartTime, setScanStartTime] = useState(null);
  
  // Folder scanning states
  const [zipFile, setZipFile] = useState(null);
  const [folderScanLoading, setFolderScanLoading] = useState(false);
  const [folderScanResult, setFolderScanResult] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [scanJobId, setScanJobId] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);
  
  // History lazy loading
  const [historyLoaded, setHistoryLoaded] = useState(false);

  // DON'T auto-load history on mount - only load when user clicks History tab
  // useEffect(() => {
  //   fetchScanHistory();
  // }, []);

  const fetchScanHistory = async () => {
    try {
      const response = await axios.get(`${API}/scan-history`);
      setScanHistory(response.data);
    } catch (error) {
      console.error('Error fetching scan history:', error);
    }
  };

  // NEW FEATURE 1: RETRY FAILED FILES
  const handleRetry = async (scanId) => {
    setRetryingIds(prev => new Set([...prev, scanId]));
    try {
      const response = await axios.post(`${API}/retry-scan?scan_id=${scanId}`);
      
      // Update results in state
      setScanResults(results => 
        results.map(r => r.id === scanId ? {
          ...r,
          detected_type: response.data.detected_type,
          detected_full_name: response.data.detected_type,
          short_code: response.data.short_code,
          confidence_score: response.data.confidence
        } : r)
      );
      
      fetchScanHistory();
      toast.success('✅ Quét lại thành công!');
    } catch (error) {
      console.error('Error retrying scan:', error);
      const errorMsg = error.response?.data?.detail || error.message;
      toast.error(`❌ Lỗi khi quét lại: ${errorMsg}`);
    } finally {
      setRetryingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(scanId);
        return newSet;
      });
    }
  };

  // NEW FEATURE 2: SEARCH & FILTER
  const getFilteredResults = (results) => {
    return results.filter(r => {
      const matchSearch = !searchTerm || 
        r.original_filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        r.detected_full_name.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchType = filterType === 'all' || 
        (filterType === 'error' && r.short_code === 'ERROR') ||
        (filterType === 'success' && r.short_code !== 'ERROR');
      
      const matchCode = filterCode === 'all' || r.short_code === filterCode;
      
      return matchSearch && matchType && matchCode;
    });
  };

  // NEW FEATURE 3: BULK OPERATIONS
  const handleSelectAll = () => {
    const filtered = getFilteredResults(scanResults);
    setSelectedIds(new Set(filtered.map(r => r.id)));
  };

  const handleDeselectAll = () => {
    setSelectedIds(new Set());
  };

  const toggleSelect = (id) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    
    if (!window.confirm(`Xóa ${selectedIds.size} file đã chọn?`)) return;
    
    try {
      // Delete from results
      setScanResults(results => results.filter(r => !selectedIds.has(r.id)));
      
      // Delete from backend (batch)
      await Promise.all(
        Array.from(selectedIds).map(id => 
          axios.delete(`${API}/scan-result/${id}`).catch(() => {})
        )
      );
      
      setSelectedIds(new Set());
      fetchScanHistory();
      toast.success(`Đã xóa ${selectedIds.size} file`);
    } catch (error) {
      console.error('Error bulk deleting:', error);
      toast.error('Lỗi khi xóa file');
    }
  };

  const handleBulkExport = async () => {
    if (selectedIds.size === 0) return;
    
    setExporting(true);
    try {
      const response = await axios.post(`${API}/export-pdf-single`, 
        { scan_ids: Array.from(selectedIds) },
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `selected_${selectedIds.size}_files.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`Đã xuất ${selectedIds.size} file`);
    } catch (error) {
      console.error('Error bulk exporting:', error);
      toast.error('Lỗi khi xuất file');
    } finally {
      setExporting(false);
    }
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    const fileWithPreviews = files.map(file => ({
      file,
      preview: URL.createObjectURL(file),
      id: Math.random().toString(36).substr(2, 9)
    }));
    setUploadedFiles([...uploadedFiles, ...fileWithPreviews]);
  };

  const handleScanDocuments = async () => {
    if (uploadedFiles.length === 0) {
      toast.error('Vui lòng upload ít nhất 1 file');
      return;
    }

    // CHECK DUPLICATES: Warn if files already exist in scan history
    const uploadedFilenames = uploadedFiles.map(f => f.file.name);
    const historyFilenames = new Set(scanHistory.map(h => h.original_filename));
    const duplicates = uploadedFilenames.filter(name => historyFilenames.has(name));
    
    if (duplicates.length > 0) {
      const proceed = window.confirm(
        `⚠️ Phát hiện ${duplicates.length} file đã được quét trước đó:\n\n${duplicates.slice(0, 5).join('\n')}${duplicates.length > 5 ? '\n...' : ''}\n\nBạn có muốn quét lại không?`
      );
      if (!proceed) {
        return;
      }
    }

    setLoading(true);
    setScanProgress({ current: 0, total: uploadedFiles.length });
    setProcessedFiles(new Set());
    setScanDuration(null);
    
    // Start timer
    const startTime = Date.now();
    setScanStartTime(startTime);
    
    // Show compression notification for large batches
    if (uploadedFiles.length > 5) {
      toast.info(`🗜️ Đang nén ${uploadedFiles.length} ảnh để tăng tốc upload...`, {
        duration: 3000
      });
    }
    
    try {
      // CLIENT-SIDE COMPRESSION: Compress all images first
      const filesToCompress = uploadedFiles.map(f => f.file);
      const compressedFiles = await compressImages(filesToCompress, (current, total, fileName) => {
        // Optional: Show compression progress
        console.log(`Compressing ${current}/${total}: ${fileName}`);
      });
      
      // Show compression complete notification
      if (uploadedFiles.length > 5) {
        toast.success(`✅ Đã nén ${uploadedFiles.length} ảnh! Đang upload...`, {
          duration: 2000
        });
      }
      
      // Process files in smaller chunks to avoid timeout (reduced from 10 to 5)
      const CHUNK_SIZE = 5;
      const allResults = [];
      
      for (let i = 0; i < compressedFiles.length; i += CHUNK_SIZE) {
        const chunk = compressedFiles.slice(i, i + CHUNK_SIZE);
        const formData = new FormData();
        chunk.forEach((file) => {
          formData.append('files', file);
        });

        // Retry logic with exponential backoff
        let retries = 0;
        let success = false;
        let response;
        
        while (retries < 3 && !success) {
          try {
            response = await axios.post(`${API}/batch-scan`, formData, {
              headers: { 'Content-Type': 'multipart/form-data' },
              timeout: 300000, // 5 minutes
              onUploadProgress: (progressEvent) => {
                const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                console.log(`Upload progress: ${percentCompleted}%`);
              }
            });
            success = true;
          } catch (error) {
            retries++;
            if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
              console.log(`Timeout on attempt ${retries}, retrying...`);
              if (retries < 3) {
                // Wait before retry (exponential backoff)
                await new Promise(resolve => setTimeout(resolve, retries * 2000));
                toast.info(`⏱️ Timeout - đang thử lại lần ${retries}/3...`);
              } else {
                throw new Error(`Timeout sau 3 lần thử. Vui lòng giảm số lượng file hoặc thử lại sau.`);
              }
            } else {
              throw error;
            }
          }
        }

        // Update progress
        allResults.push(...response.data);
        setScanProgress({ 
          current: Math.min(i + CHUNK_SIZE, uploadedFiles.length), 
          total: uploadedFiles.length 
        });
        
        // Mark these files as processed
        setProcessedFiles(prev => {
          const newSet = new Set(prev);
          chunk.forEach(({id}) => newSet.add(id));
          return newSet;
        });
        
        // Update results incrementally
        setScanResults([...allResults]);
      }

      // Count successful scans and collect error details
      const successCount = allResults.filter(r => r.short_code !== 'ERROR').length;
      const errorCount = allResults.length - successCount;
      const errors = allResults.filter(r => r.short_code === 'ERROR');
      
      // Calculate duration
      const duration = ((Date.now() - startTime) / 1000).toFixed(1);
      setScanDuration(duration);
      
      if (errorCount > 0) {
        toast.warning(`Quét thành công ${successCount}/${allResults.length} tài liệu (${duration}s)`, {
          duration: 4000
        });
        
        // Show detailed error messages
        errors.slice(0, 3).forEach((err, idx) => {
          setTimeout(() => {
            toast.error(`❌ ${err.original_filename}: ${err.detected_full_name}`, {
              duration: 6000
            });
          }, (idx + 1) * 500);
        });
        
        if (errors.length > 3) {
          setTimeout(() => {
            toast.info(`Và ${errors.length - 3} lỗi khác. Xem chi tiết trong danh sách.`, {
              duration: 5000
            });
          }, 2000);
        }
      } else {
        toast.success(`✅ Quét thành công ${allResults.length} tài liệu! (${duration}s - ${(allResults.length / parseFloat(duration)).toFixed(1)} file/s)`);
      }
      
      // SMART CLEAR: Only keep failed files for retry
      if (errorCount > 0) {
        // Keep only files that resulted in errors (for retry)
        const errorFilenames = new Set(errors.map(e => e.original_filename));
        setUploadedFiles(uploadedFiles.filter(f => errorFilenames.has(f.file.name)));
        toast.info(`Giữ lại ${errorCount} file lỗi để retry. Xóa ${successCount} file đã quét thành công.`, {
          duration: 4000
        });
      } else {
        // Clear all files if all successful
        setUploadedFiles([]);
      }
      
      fetchScanHistory();
    } catch (error) {
      console.error('Error scanning documents:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Lỗi không xác định';
      toast.error(`Lỗi khi quét tài liệu: ${errorMsg}`, {
        duration: 6000
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateFilename = async (id, newCode) => {
    if (!newCode || newCode.trim() === '') {
      toast.error('Tên file không được để trống');
      return;
    }
    
    try {
      await axios.put(`${API}/update-filename`, {
        id,
        new_short_code: newCode.trim()
      });
      
      // Update local state - allow duplicates
      setScanResults(results => 
        results.map(r => r.id === id ? { ...r, short_code: newCode.trim() } : r)
      );
      
      // Refresh scan history to reflect changes
      fetchScanHistory();
      
      toast.success('Đã cập nhật tên file');
      setEditingId(null);
      setEditValue('');
    } catch (error) {
      console.error('Error updating filename:', error);
      toast.error('Lỗi khi cập nhật tên file: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleExportSingle = async () => {
    if (scanResults.length === 0) {
      toast.error('Không có tài liệu để xuất');
      return;
    }

    setExporting(true);
    try {
      const scanIds = scanResults.map(r => r.id);
      
      // Check for duplicate short codes
      const shortCodes = scanResults.map(r => r.short_code);
      const duplicates = shortCodes.filter((code, idx) => shortCodes.indexOf(code) !== idx);
      const uniqueDuplicates = [...new Set(duplicates)];
      
      if (uniqueDuplicates.length > 0) {
        toast.info(`Các file cùng loại (${uniqueDuplicates.join(', ')}) sẽ được gộp tự động vào 1 PDF`, {
          duration: 3000
        });
      }
      
      const response = await axios.post(`${API}/export-pdf-single`, 
        { scan_ids: scanIds },
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'documents_single.zip');
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('Đã xuất các file PDF (tự động gộp các file cùng loại)');
    } catch (error) {
      console.error('Error exporting single PDFs:', error);
      toast.error('Lỗi khi xuất PDF');
    } finally {
      setExporting(false);
    }
  };

  const handleExportMerged = async () => {
    if (scanResults.length === 0) {
      toast.error('Không có tài liệu để xuất');
      return;
    }

    setExporting(true);
    try {
      const scanIds = scanResults.map(r => r.id);
      const response = await axios.post(`${API}/export-pdf-merged`, 
        { scan_ids: scanIds },
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'documents_merged.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success('Đã xuất file PDF gộp');
    } catch (error) {
      console.error('Error exporting merged PDF:', error);
      toast.error('Lỗi khi xuất PDF');
    } finally {
      setExporting(false);
    }
  };

  const handleClearHistory = async () => {
    if (window.confirm('Bạn có chắc muốn xóa toàn bộ lịch sử?')) {
      try {
        await axios.delete(`${API}/clear-history`);
        setScanHistory([]);
        toast.success('Đã xóa lịch sử');
      } catch (error) {
        console.error('Error clearing history:', error);
        toast.error('Lỗi khi xóa lịch sử');
      }
    }
  };

  const handleRemoveFile = (id) => {
    setUploadedFiles(files => files.filter(f => f.id !== id));
  };

  const handleClearResults = () => {
    setScanResults([]);
    setUploadedFiles([]);
  };

  const startEdit = (id, currentCode, event) => {
    // Prevent default action and stop propagation
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    
    setEditingId(id);
    setEditValue(currentCode);
    
    // Scroll to the element being edited after a short delay
    setTimeout(() => {
      const element = document.querySelector(`[data-result-id="${id}"]`);
      if (element) {
        element.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        });
      }
    }, 100);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditValue('');
  };

  const handleExportSingleFile = async (scanId, shortCode) => {
    try {
      const response = await axios.post(`${API}/export-single-document`, 
        { scan_ids: [scanId] },
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${shortCode}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      toast.success(`Đã xuất file ${shortCode}.pdf`);
    } catch (error) {
      console.error('Error exporting single file:', error);
      toast.error('Lỗi khi xuất file');
    }
  };

  // ============= FOLDER SCANNING HANDLERS =============
  
  const handleZipUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validate file type
    if (!file.name.endsWith('.zip')) {
      toast.error('Chỉ chấp nhận file ZIP');
      return;
    }
    
    // Validate file size (500MB)
    const maxSize = 500 * 1024 * 1024; // 500MB
    if (file.size > maxSize) {
      toast.error(`File quá lớn (${(file.size / 1024 / 1024).toFixed(1)}MB). Giới hạn: 500MB`);
      return;
    }
    
    setZipFile(file);
    setFolderScanResult(null);
    toast.success(`Đã chọn file: ${file.name} (${(file.size / 1024 / 1024).toFixed(1)}MB)`);
  };

  const handleScanFolder = async () => {
    if (!zipFile) {
      toast.error('Vui lòng chọn file ZIP');
      return;
    }

    setFolderScanLoading(true);
    setUploadProgress(0);
    setFolderScanResult(null);
    
    try {
      const formData = new FormData();
      formData.append('file', zipFile);

      toast.info('Đang upload ZIP...', { duration: 3000 });

      // Start scan job
      const response = await axios.post(`${API}/scan-folder`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // 2 minutes for upload only
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        },
      });

      const jobId = response.data.job_id;
      setScanJobId(jobId);
      
      toast.success(`✅ Đã bắt đầu quét ${response.data.total_folders} thư mục!`, { duration: 4000 });
      
      // Start polling for results
      pollFolderScanStatus(jobId);

    } catch (error) {
      console.error('Error scanning folder:', error);
      
      let errorMsg = error.response?.data?.detail || error.message || 'Lỗi không xác định';
      
      if (error.code === 'ECONNABORTED' || errorMsg.includes('timeout')) {
        errorMsg = 'Timeout khi upload. File quá lớn. Vui lòng thử lại.';
      }
      
      toast.error(`Lỗi: ${errorMsg}`, { duration: 8000 });
      setFolderScanLoading(false);
    }
  };

  const pollFolderScanStatus = (jobId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${API}/folder-scan-status/${jobId}`);
        const status = response.data;
        
        // Update result state (progressive)
        setFolderScanResult(status);
        
        // Show toast for each completed folder
        if (status.folder_results.length > (folderScanResult?.folder_results?.length || 0)) {
          const latestFolder = status.folder_results[status.folder_results.length - 1];
          toast.success(`✅ ${latestFolder.folder_name}: ${latestFolder.success_count}/${latestFolder.total_files} files`, {
            duration: 3000
          });
        }
        
        // Check if completed or error
        if (status.status === 'completed') {
          clearInterval(interval);
          setPollingInterval(null);
          setFolderScanLoading(false);
          setScanJobId(null);
          
          const totalSuccess = status.folder_results.reduce((sum, f) => sum + f.success_count, 0);
          const totalFiles = status.folder_results.reduce((sum, f) => sum + f.total_files, 0);
          
          toast.success(`🎉 Hoàn thành! ${totalSuccess}/${totalFiles} files quét thành công!`, {
            duration: 5000
          });
        } else if (status.status === 'error') {
          clearInterval(interval);
          setPollingInterval(null);
          setFolderScanLoading(false);
          setScanJobId(null);
          
          toast.error(`❌ Lỗi: ${status.error_message}`, { duration: 8000 });
        }
        
      } catch (error) {
        console.error('Error polling status:', error);
        clearInterval(interval);
        setPollingInterval(null);
        setFolderScanLoading(false);
      }
    }, 3000); // Poll every 3 seconds
    
    setPollingInterval(interval);
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  const handleDownloadResult = async () => {
    if (!folderScanResult || !folderScanResult.download_url) {
      toast.error('Không có kết quả để tải');
      return;
    }

    try {
      toast.info('Đang chuẩn bị tải xuống...', { duration: 2000 });
      
      // Use direct link approach instead of axios to avoid CORS/blob issues
      const downloadUrl = `${BACKEND_URL}${folderScanResult.download_url}`;
      
      // Create temporary link and trigger download
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.setAttribute('download', 'scanned_documents.zip');
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      setTimeout(() => {
        document.body.removeChild(link);
      }, 100);

      toast.success('✅ Đã bắt đầu tải xuống ZIP kết quả');
    } catch (error) {
      console.error('Error downloading result:', error);
      toast.error('Lỗi khi tải xuống kết quả');
    }
  };

  const handleClearFolder = () => {
    setZipFile(null);
    setFolderScanResult(null);
    setUploadProgress(0);
  };

  const ResultCard = ({ result, showActions = true, showCheckbox = false }) => {
    const isError = result.short_code === 'ERROR';
    const isRetrying = retryingIds.has(result.id);
    const isSelected = selectedIds.has(result.id);
    
    return (
    <Card 
      className={`overflow-hidden hover-card ${isError ? 'border-red-500 border-2' : ''} ${isSelected ? 'ring-2 ring-2 ring-blue-500' : ''}`} 
      data-testid={`result-card-${result.id}`}
      data-result-id={result.id}
    >
      {/* Checkbox for bulk selection */}
      {showCheckbox && (
        <div className="absolute top-2 left-2 z-10">
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => toggleSelect(result.id)}
            className="w-5 h-5 cursor-pointer"
            data-testid={`checkbox-${result.id}`}
          />
        </div>
      )}
      
      <div className="relative aspect-[3/4] bg-muted">
        {result.image_base64 ? (
          <img 
            src={`data:image/jpeg;base64,${result.image_base64}`} 
            alt={result.detected_type}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-red-50">
            <div className="text-center p-4">
              <span className="text-6xl">❌</span>
              <p className="text-sm text-red-600 mt-2 font-semibold">Lỗi quét</p>
            </div>
          </div>
        )}
        <Badge 
          className="absolute top-2 right-2" 
          variant={isError ? 'destructive' : (result.confidence_score > 0.8 ? 'default' : 'secondary')}
        >
          {isError ? '❌' : `${Math.round(result.confidence_score * 100)}%`}
        </Badge>
      </div>
      <CardContent className="p-4 space-y-2">
        {isError ? (
          <div className="space-y-1">
            <p className="text-sm font-semibold text-red-600" title={result.detected_type}>
              {result.detected_type}
            </p>
            <p className="text-xs text-red-500 break-words" title={result.detected_full_name}>
              {result.detected_full_name}
            </p>
          </div>
        ) : (
          <p className="text-xs text-muted-foreground truncate" title={result.detected_full_name}>
            {result.detected_full_name}
          </p>
        )}
        
        {editingId === result.id ? (
          <div className="flex gap-2" data-testid={`edit-mode-${result.id}`}>
            <Input 
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="h-8"
              data-testid={`edit-input-${result.id}`}
            />
            <Button 
              size="sm" 
              onClick={() => handleUpdateFilename(result.id, editValue)}
              data-testid={`save-btn-${result.id}`}
            >
              <Check className="h-4 w-4" />
            </Button>
            <Button 
              size="sm" 
              variant="outline" 
              onClick={cancelEdit}
              data-testid={`cancel-btn-${result.id}`}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="font-semibold text-lg" data-testid={`short-code-${result.id}`}>
                {result.short_code}.pdf
              </p>
              {showActions && (
                <Button 
                  size="sm" 
                  variant="ghost" 
                  onClick={(e) => startEdit(result.id, result.short_code, e)}
                  data-testid={`edit-btn-${result.id}`}
                >
                  <Edit2 className="h-4 w-4" />
                </Button>
              )}
            </div>
            
            {showActions && !isError && (
              <Button 
                size="sm" 
                className="w-full"
                variant="outline"
                onClick={() => handleExportSingleFile(result.id, result.short_code)}
                data-testid={`export-single-btn-${result.id}`}
              >
                <Download className="h-4 w-4 mr-2" />
                Xuất file này
              </Button>
            )}
            
            {isError && showActions && (
              <>
                <Button 
                  size="sm" 
                  className="w-full mb-2"
                  variant="outline"
                  onClick={() => handleRetry(result.id)}
                  disabled={isRetrying}
                  data-testid={`retry-btn-${result.id}`}
                >
                  {isRetrying ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Đang quét lại...
                    </>
                  ) : (
                    <>
                      🔄 Quét lại
                    </>
                  )}
                </Button>
                <Button 
                  size="sm" 
                  className="w-full"
                  variant="destructive"
                  disabled
                >
                  ❌ Không thể xuất
                </Button>
              </>
            )}
          </div>
        )}
        
        <p className="text-xs text-muted-foreground">
          {result.original_filename}
        </p>
      </CardContent>
    </Card>
  );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50" data-testid="document-scanner-app">
      {/* Header with User Info */}
      <div className="bg-white border-b shadow-sm">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-gray-800">Document Scanner</h1>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-700 flex items-center gap-2">
                <User className="h-4 w-4" />
                {user?.full_name || user?.username}
              </p>
              <p className="text-xs text-gray-500">{user?.email}</p>
            </div>
            {isAdmin() && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/admin')}
              >
                <Shield className="h-4 w-4 mr-2" />
                Admin Panel
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                logout();
                toast.success('Đã đăng xuất');
              }}
            >
              <LogOut className="h-4 w-4 mr-2" />
              Đăng Xuất
            </Button>
          </div>
        </div>
      </div>

      <Toaster position="top-right" richColors />
      
      {/* Main Content */}
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-3 bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent" style={{fontFamily: 'Space Grotesk, sans-serif'}}>
            Convert images to PDF and Auto Name
          </h1>
          <p className="text-muted-foreground text-lg">
            Tự động nhận diện và đặt tên tài liệu bằng AI
          </p>
        </div>

        <Tabs defaultValue="scan" className="w-full" data-testid="main-tabs" onValueChange={(value) => {
          // Lazy load history only when user clicks History tab
          if (value === 'history' && !historyLoaded) {
            fetchScanHistory();
            setHistoryLoaded(true);
          }
        }}>
          <TabsList className="grid w-full max-w-2xl mx-auto grid-cols-4 mb-8">
            <TabsTrigger value="scan" data-testid="scan-tab">
              <FileText className="h-4 w-4 mr-2" />
              Quét Tài Liệu
            </TabsTrigger>
            <TabsTrigger value="folder" data-testid="folder-tab">
              <Upload className="h-4 w-4 mr-2" />
              Quét Thư Mục
            </TabsTrigger>
            <TabsTrigger value="history" data-testid="history-tab">
              <History className="h-4 w-4 mr-2" />
              Lịch Sử
            </TabsTrigger>
            <TabsTrigger value="rules" data-testid="rules-tab">
              <Settings className="h-4 w-4 mr-2" />
              Quy Tắc
            </TabsTrigger>
          </TabsList>

          <TabsContent value="scan" className="space-y-6">
            {/* Upload Section */}
            <Card data-testid="upload-section">
              <CardHeader>
                <CardTitle>Upload Tài Liệu</CardTitle>
                <CardDescription>
                  Chọn nhiều ảnh tài liệu để quét và phân loại tự động
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <label 
                  htmlFor="file-upload" 
                  className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-primary/30 rounded-xl cursor-pointer bg-primary/5 hover:bg-primary/10 transition-all"
                  data-testid="upload-zone"
                >
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <Upload className="h-12 w-12 text-primary mb-3" />
                    <p className="mb-2 text-sm font-medium">
                      Click để chọn file hoặc kéo thả vào đây
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Hỗ trợ: PNG, JPG, JPEG
                    </p>
                  </div>
                  <input 
                    id="file-upload" 
                    type="file" 
                    className="hidden" 
                    accept="image/*"
                    multiple
                    onChange={handleFileUpload}
                    data-testid="file-input"
                  />
                </label>

                {uploadedFiles.length > 0 && (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <p className="text-sm font-medium">
                        Đã chọn {uploadedFiles.length} file
                      </p>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={handleClearResults}
                        data-testid="clear-files-btn"
                      >
                        Xóa tất cả
                      </Button>
                    </div>
                    
                    {/* Scan Button - MOVED TO TOP for easy access */}
                    <Button 
                      onClick={handleScanDocuments} 
                      disabled={loading}
                      className="w-full"
                      size="lg"
                      data-testid="scan-btn"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                          Đang quét...
                        </>
                      ) : (
                        <>
                          <FileText className="h-5 w-5 mr-2" />
                          Quét Tài Liệu
                        </>
                      )}
                    </Button>

                    {/* Progress Bar */}
                    {loading && scanProgress.total > 0 && (
                      <div className="space-y-2 p-4 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800" data-testid="progress-section">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
                            Đang quét tài liệu...
                          </span>
                          <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                            {scanProgress.current}/{scanProgress.total}
                          </span>
                        </div>
                        <div className="w-full bg-blue-200 dark:bg-blue-900 rounded-full h-3 overflow-hidden">
                          <div 
                            className="bg-blue-600 dark:bg-blue-400 h-3 rounded-full transition-all duration-300 flex items-center justify-end pr-1"
                            style={{ width: `${(scanProgress.current / scanProgress.total) * 100}%` }}
                          >
                            <span className="text-xs font-bold text-white">
                              {Math.round((scanProgress.current / scanProgress.total) * 100)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {uploadedFiles.map(({ id, preview, file }) => (
                        <div key={id} className="relative group" data-testid={`uploaded-file-${id}`}>
                          <div className="relative">
                            <img 
                              src={preview} 
                              alt={file.name}
                              className={`w-full h-32 object-cover rounded-lg ${processedFiles.has(id) ? 'ring-2 ring-green-500' : ''}`}
                            />
                            {/* Checkmark overlay when processed */}
                            {processedFiles.has(id) && (
                              <div className="absolute inset-0 bg-green-500/20 rounded-lg flex items-center justify-center">
                                <CheckCircle2 className="h-12 w-12 text-green-600 drop-shadow-lg" strokeWidth={3} />
                              </div>
                            )}
                            {/* Loading spinner */}
                            {loading && !processedFiles.has(id) && scanProgress.total > 0 && (
                              <div className="absolute inset-0 bg-black/30 rounded-lg flex items-center justify-center">
                                <Loader2 className="h-8 w-8 text-white animate-spin" />
                              </div>
                            )}
                          </div>
                          <Button
                            size="sm"
                            variant="destructive"
                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0 z-10"
                            onClick={() => handleRemoveFile(id)}
                            data-testid={`remove-file-btn-${id}`}
                            disabled={loading}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                          <p className="text-xs mt-1 truncate" title={file.name}>
                            {file.name}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Results Section */}
            {scanResults.length > 0 && (
              <Card data-testid="results-section">
                <CardHeader>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <CardTitle>Kết Quả Quét</CardTitle>
                        <CardDescription>
                          {getFilteredResults(scanResults).length}/{scanResults.length} tài liệu
                          {selectedIds.size > 0 && ` (${selectedIds.size} đã chọn)`}
                          {scanDuration && ` • ⏱️ ${scanDuration}s (${(scanResults.length / parseFloat(scanDuration)).toFixed(1)} file/s)`}
                        </CardDescription>
                        <p className="text-xs text-muted-foreground mt-1">
                          💡 Mẹo: Bật "Hỏi nơi lưu" trong cài đặt trình duyệt để chọn thư mục
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button 
                          onClick={handleExportSingle}
                          disabled={exporting}
                          variant="outline"
                          data-testid="export-single-btn"
                        >
                          {exporting ? (
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          ) : (
                            <Download className="h-4 w-4 mr-2" />
                          )}
                          Xuất PDF Riêng
                        </Button>
                        <Button 
                          onClick={handleExportMerged}
                          disabled={exporting}
                          data-testid="export-merged-btn"
                        >
                          {exporting ? (
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                          ) : (
                            <Download className="h-4 w-4 mr-2" />
                          )}
                          Xuất PDF Gộp
                        </Button>
                      </div>
                    </div>

                    {/* SEARCH & FILTER UI */}
                    <div className="flex flex-wrap gap-3 p-4 bg-muted/30 rounded-lg">
                      {/* Search */}
                      <div className="flex-1 min-w-[200px]">
                        <Input
                          placeholder="🔍 Tìm kiếm theo tên file..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="w-full"
                          data-testid="search-input"
                        />
                      </div>

                      {/* Filter by Type */}
                      <select
                        value={filterType}
                        onChange={(e) => setFilterType(e.target.value)}
                        className="px-3 py-2 border rounded-md bg-background"
                        data-testid="filter-type"
                      >
                        <option value="all">Tất cả trạng thái</option>
                        <option value="success">✅ Thành công</option>
                        <option value="error">❌ Lỗi</option>
                      </select>

                      {/* Filter by Code */}
                      <select
                        value={filterCode}
                        onChange={(e) => setFilterCode(e.target.value)}
                        className="px-3 py-2 border rounded-md bg-background"
                        data-testid="filter-code"
                      >
                        <option value="all">Tất cả loại</option>
                        <option value="GCNM">GCNM</option>
                        <option value="HSKT">HSKT</option>
                        <option value="DDK">DDK</option>
                        <option value="HDCQ">HDCQ</option>
                        <option value="BN">BN</option>
                        <option value="PCT">PCT</option>
                      </select>

                      {/* Clear Filters */}
                      {(searchTerm || filterType !== 'all' || filterCode !== 'all') && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSearchTerm('');
                            setFilterType('all');
                            setFilterCode('all');
                          }}
                        >
                          ✕ Xóa bộ lọc
                        </Button>
                      )}
                    </div>

                    {/* BULK OPERATIONS BAR */}
                    <div className="flex justify-between items-center p-3 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200">
                      <div className="flex gap-2 items-center">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={selectedIds.size === getFilteredResults(scanResults).length ? handleDeselectAll : handleSelectAll}
                        >
                          {selectedIds.size === getFilteredResults(scanResults).length ? '☐ Bỏ chọn tất cả' : '☑ Chọn tất cả'}
                        </Button>
                        {selectedIds.size > 0 && (
                          <span className="text-sm font-medium">
                            {selectedIds.size} file đã chọn
                          </span>
                        )}
                      </div>
                      {selectedIds.size > 0 && (
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={handleBulkExport}
                            disabled={exporting}
                          >
                            <Download className="h-4 w-4 mr-1" />
                            Xuất đã chọn
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={handleBulkDelete}
                          >
                            <Trash2 className="h-4 w-4 mr-1" />
                            Xóa đã chọn
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {getFilteredResults(scanResults).map(result => (
                      <ResultCard key={result.id} result={result} showCheckbox={true} />
                    ))}
                  </div>
                  {getFilteredResults(scanResults).length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
                      <p>Không tìm thấy tài liệu phù hợp với bộ lọc</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* NEW TAB: FOLDER SCANNING */}
          <TabsContent value="folder" className="space-y-6">
            <Card data-testid="folder-upload-section">
              <CardHeader>
                <CardTitle>Quét Thư Mục ZIP</CardTitle>
                <CardDescription>
                  Upload file ZIP chứa nhiều thư mục và file ảnh. Hệ thống sẽ quét tất cả và giữ nguyên cấu trúc thư mục.
                  <br/>
                  <span className="text-amber-600 font-medium mt-2 block">
                    ⚠️ Khuyến nghị: 50-100 files/ZIP để tránh timeout. Files lớn có thể mất 10-20 phút.
                  </span>
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* ZIP Upload Zone */}
                <label 
                  htmlFor="zip-upload" 
                  className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-primary/30 rounded-xl cursor-pointer bg-primary/5 hover:bg-primary/10 transition-all"
                  data-testid="zip-upload-zone"
                >
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <Upload className="h-12 w-12 text-primary mb-3" />
                    <p className="mb-2 text-sm font-medium">
                      Click để chọn file ZIP
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Giới hạn: 500MB, tối đa 500 files
                    </p>
                  </div>
                  <input 
                    id="zip-upload" 
                    type="file" 
                    className="hidden" 
                    accept=".zip"
                    onChange={handleZipUpload}
                    data-testid="zip-input"
                  />
                </label>

                {/* ZIP File Info */}
                {zipFile && (
                  <Card className="bg-blue-50 border-blue-200">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-sm">📦 {zipFile.name}</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Kích thước: {(zipFile.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={handleClearFolder}
                          disabled={folderScanLoading}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Scan Button */}
                {zipFile && !folderScanResult && (
                  <Button 
                    onClick={handleScanFolder} 
                    disabled={folderScanLoading}
                    className="w-full"
                    size="lg"
                    data-testid="scan-folder-btn"
                  >
                    {folderScanLoading ? (
                      <>
                        <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                        Đang xử lý...
                      </>
                    ) : (
                      <>
                        <FileText className="h-5 w-5 mr-2" />
                        Quét Thư Mục
                      </>
                    )}
                  </Button>
                )}

                {/* Upload Progress */}
                {folderScanLoading && uploadProgress > 0 && uploadProgress < 100 && (
                  <div className="space-y-2 p-4 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
                        Đang upload...
                      </span>
                      <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                        {uploadProgress}%
                      </span>
                    </div>
                    <div className="w-full bg-blue-200 dark:bg-blue-900 rounded-full h-2.5">
                      <div 
                        className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                )}
                
                {/* Scanning Progress */}
                {folderScanLoading && uploadProgress >= 100 && folderScanResult && (
                  <div className="space-y-2 p-4 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-green-900 dark:text-green-100">
                        {folderScanResult.current_folder 
                          ? `Đang quét: ${folderScanResult.current_folder}` 
                          : 'Đang xử lý...'}
                      </span>
                      <span className="text-sm font-bold text-green-600 dark:text-green-400">
                        {folderScanResult.completed_folders}/{folderScanResult.total_folders} thư mục
                      </span>
                    </div>
                    <div className="w-full bg-green-200 dark:bg-green-900 rounded-full h-2.5">
                      <div 
                        className="bg-green-600 h-2.5 rounded-full transition-all duration-300"
                        style={{ width: `${(folderScanResult.completed_folders / folderScanResult.total_folders * 100)}%` }}
                      />
                    </div>
                    <p className="text-xs text-green-700 dark:text-green-300 mt-2">
                      💡 Các thư mục đã quét xong có thể tải xuống ngay bên dưới
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Results Section - Shows progressively as folders complete */}
            {folderScanResult && folderScanResult.folder_results.length > 0 && (
              <Card data-testid="folder-result-section">
                <CardHeader>
                  <CardTitle>
                    Kết Quả Quét {folderScanResult.status === 'completed' ? '✅' : '⏳'}
                  </CardTitle>
                  <CardDescription>
                    {folderScanResult.completed_folders}/{folderScanResult.total_folders} thư mục đã hoàn thành
                    {folderScanResult.status === 'processing' && ' (Đang quét...)'}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Summary Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-blue-50 rounded-lg text-center">
                      <p className="text-2xl font-bold text-blue-600">{folderScanResult.total_folders}</p>
                      <p className="text-xs text-muted-foreground">Tổng thư mục</p>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg text-center">
                      <p className="text-2xl font-bold text-green-600">{folderScanResult.completed_folders}</p>
                      <p className="text-xs text-muted-foreground">Đã hoàn thành</p>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg text-center">
                      <p className="text-2xl font-bold text-purple-600">
                        {folderScanResult.folder_results.reduce((sum, f) => sum + f.success_count, 0)}
                      </p>
                      <p className="text-xs text-muted-foreground">Files thành công</p>
                    </div>
                  </div>

                  {/* Folder Results - Each folder with download button */}
                  <div className="space-y-3">
                    <h3 className="font-semibold text-lg">
                      Tải Xuống Từng Thư Mục: {folderScanLoading && '(Đang cập nhật...)'}
                    </h3>
                    {folderScanResult.folder_results.map((folder, idx) => (
                      <Card key={idx} className="bg-slate-50 border-2 border-green-200">
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex-1">
                              <h4 className="font-bold text-md flex items-center gap-2">
                                <CheckCircle2 className="h-5 w-5 text-green-600" />
                                📁 {folder.folder_name}
                              </h4>
                              <p className="text-sm text-muted-foreground mt-1">
                                {folder.success_count}/{folder.total_files} files • {folder.processing_time_seconds.toFixed(1)}s
                              </p>
                            </div>
                            <Button
                              onClick={() => {
                                const link = document.createElement('a');
                                link.href = `${BACKEND_URL}${folder.download_url}`;
                                link.download = `${folder.folder_name}.zip`;
                                link.style.display = 'none';
                                document.body.appendChild(link);
                                link.click();
                                setTimeout(() => document.body.removeChild(link), 100);
                                toast.success(`✅ Đang tải ${folder.folder_name}.zip`);
                              }}
                              variant="default"
                              size="sm"
                            >
                              <Download className="h-4 w-4 mr-2" />
                              Tải ZIP
                            </Button>
                          </div>
                          
                          {/* Progress bar */}
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-green-600 h-2 rounded-full"
                              style={{ width: `${(folder.success_count / folder.total_files * 100)}%` }}
                            />
                          </div>
                          
                          {folder.error_count > 0 && (
                            <p className="text-xs text-red-600 mt-2">
                              ⚠️ {folder.error_count} files lỗi
                            </p>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>

                  {/* New Scan Button - only show when completed */}
                  {folderScanResult.status === 'completed' && (
                    <Button
                      onClick={handleClearFolder}
                      variant="outline"
                      className="w-full"
                      data-testid="new-scan-btn"
                    >
                      Quét Thư Mục Mới
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="history" className="space-y-4">
            <Card data-testid="history-section">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Lịch Sử Quét</CardTitle>
                    <CardDescription>
                      {scanHistory.length} tài liệu đã quét
                    </CardDescription>
                  </div>
                  {scanHistory.length > 0 && (
                    <Button 
                      variant="destructive" 
                      onClick={handleClearHistory}
                      data-testid="clear-history-btn"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Xóa Lịch Sử
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {scanHistory.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <History className="h-12 w-12 mx-auto mb-3 opacity-50" />
                    <p>Chưa có lịch sử quét</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {scanHistory.map(result => (
                      <ResultCard key={result.id} result={result} showActions={true} />
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="rules" className="space-y-4">
            <RulesManager />
          </TabsContent>
        </Tabs>

        {/* Footer Credit */}
        <footer className="mt-12 pb-8 text-center text-sm text-gray-600 border-t pt-6">
          <p className="font-medium">
            Ứng dụng được lên ý tưởng bởi <span className="text-blue-600 font-semibold">Nguyễn Thìn Trung</span>
          </p>
          <p className="text-xs mt-1">
            Văn phòng Đăng ký Đất đai tỉnh Đồng Nai - Chi nhánh Chơn Thành
          </p>
        </footer>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DocumentScanner />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;