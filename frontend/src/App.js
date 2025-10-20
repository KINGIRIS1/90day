import React, { useState, useEffect } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast, Toaster } from 'sonner';
import { Upload, FileText, Download, History, Trash2, Edit2, Check, X, Loader2 } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DocumentScanner = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [scanResults, setScanResults] = useState([]);
  const [scanHistory, setScanHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetchScanHistory();
  }, []);

  const fetchScanHistory = async () => {
    try {
      const response = await axios.get(`${API}/scan-history`);
      setScanHistory(response.data);
    } catch (error) {
      console.error('Error fetching scan history:', error);
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

    setLoading(true);
    
    // Show info for large batches
    if (uploadedFiles.length > 20) {
      toast.info(`Đang xử lý ${uploadedFiles.length} file... Vui lòng đợi (có thể mất 1-2 phút)`, {
        duration: 5000
      });
    }
    
    try {
      const formData = new FormData();
      uploadedFiles.forEach(({ file }) => {
        formData.append('files', file);
      });

      const response = await axios.post(`${API}/batch-scan`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 180000  // 3 minutes timeout for large batches
      });

      setScanResults(response.data);
      
      // Count successful scans
      const successCount = response.data.filter(r => r.short_code !== 'ERROR').length;
      const errorCount = response.data.length - successCount;
      
      if (errorCount > 0) {
        toast.warning(`Quét thành công ${successCount}/${response.data.length} tài liệu`);
      } else {
        toast.success(`Quét thành công ${response.data.length} tài liệu!`);
      }
      
      fetchScanHistory();
    } catch (error) {
      console.error('Error scanning documents:', error);
      toast.error('Lỗi khi quét tài liệu');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateFilename = async (id, newCode) => {
    try {
      await axios.put(`${API}/update-filename`, {
        id,
        new_short_code: newCode
      });
      
      // Update local state
      setScanResults(results => 
        results.map(r => r.id === id ? { ...r, short_code: newCode } : r)
      );
      setScanHistory(history => 
        history.map(h => h.id === id ? { ...h, short_code: newCode } : h)
      );
      
      toast.success('Đã cập nhật tên file');
      setEditingId(null);
    } catch (error) {
      console.error('Error updating filename:', error);
      toast.error('Lỗi khi cập nhật tên file');
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

  const startEdit = (id, currentCode) => {
    setEditingId(id);
    setEditValue(currentCode);
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

  const ResultCard = ({ result, showActions = true }) => (
    <Card className="overflow-hidden hover-card" data-testid={`result-card-${result.id}`}>
      <div className="relative aspect-[3/4] bg-muted">
        <img 
          src={`data:image/jpeg;base64,${result.image_base64}`} 
          alt={result.detected_type}
          className="w-full h-full object-cover"
        />
        <Badge 
          className="absolute top-2 right-2" 
          variant={result.confidence_score > 0.8 ? 'default' : 'secondary'}
          data-testid={`confidence-badge-${result.id}`}
        >
          {Math.round(result.confidence_score * 100)}%
        </Badge>
      </div>
      <CardContent className="p-4 space-y-2">
        <p className="text-xs text-muted-foreground truncate" title={result.detected_full_name}>
          {result.detected_full_name}
        </p>
        
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
                  onClick={() => startEdit(result.id, result.short_code)}
                  data-testid={`edit-btn-${result.id}`}
                >
                  <Edit2 className="h-4 w-4" />
                </Button>
              )}
            </div>
            
            {showActions && (
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
          </div>
        )}
        
        <p className="text-xs text-muted-foreground">
          {result.original_filename}
        </p>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50" data-testid="document-scanner-app">
      <Toaster position="top-right" richColors />
      
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold mb-3 bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent" style={{fontFamily: 'Space Grotesk, sans-serif'}}>
            Quét & Phân Loại Tài Liệu Đất Đai
          </h1>
          <p className="text-muted-foreground text-lg">
            Tự động nhận diện và đặt tên tài liệu bằng AI
          </p>
        </div>

        <Tabs defaultValue="scan" className="w-full" data-testid="main-tabs">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8">
            <TabsTrigger value="scan" data-testid="scan-tab">
              <FileText className="h-4 w-4 mr-2" />
              Quét Tài Liệu
            </TabsTrigger>
            <TabsTrigger value="history" data-testid="history-tab">
              <History className="h-4 w-4 mr-2" />
              Lịch Sử
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
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {uploadedFiles.map(({ id, preview, file }) => (
                        <div key={id} className="relative group" data-testid={`uploaded-file-${id}`}>
                          <img 
                            src={preview} 
                            alt={file.name}
                            className="w-full h-32 object-cover rounded-lg"
                          />
                          <Button
                            size="sm"
                            variant="destructive"
                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0"
                            onClick={() => handleRemoveFile(id)}
                            data-testid={`remove-file-btn-${id}`}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                          <p className="text-xs mt-1 truncate" title={file.name}>
                            {file.name}
                          </p>
                        </div>
                      ))}
                    </div>

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
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Results Section */}
            {scanResults.length > 0 && (
              <Card data-testid="results-section">
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle>Kết Quả Quét</CardTitle>
                      <CardDescription>
                        {scanResults.length} tài liệu đã được nhận diện
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
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {scanResults.map(result => (
                      <ResultCard key={result.id} result={result} />
                    ))}
                  </div>
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
                      <ResultCard key={result.id} result={result} showActions={false} />
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
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