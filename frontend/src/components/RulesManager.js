import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import { Plus, Edit2, Trash2, Save, X, Loader2, Settings } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const RulesManager = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({ full_name: '', short_code: '' });
  const [newRule, setNewRule] = useState({ full_name: '', short_code: '' });
  const [showAddForm, setShowAddForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Get auth token from localStorage
  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/rules`, {
        headers: getAuthHeaders()
      });
      setRules(response.data);
    } catch (error) {
      console.error('Error fetching rules:', error);
      toast.error('Lỗi khi tải danh sách quy tắc');
    } finally {
      setLoading(false);
    }
  };

  const handleAddRule = async () => {
    if (!newRule.full_name.trim() || !newRule.short_code.trim()) {
      toast.error('Vui lòng điền đầy đủ thông tin');
      return;
    }

    try {
      const response = await axios.post(`${API}/rules`, newRule, {
        headers: getAuthHeaders()
      });
      setRules([...rules, response.data]);
      setNewRule({ full_name: '', short_code: '' });
      setShowAddForm(false);
      toast.success('✅ Đã thêm quy tắc mới');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      toast.error(`❌ ${errorMsg}`);
    }
  };

  const handleStartEdit = (rule) => {
    setEditingId(rule.id);
    setEditData({ full_name: rule.full_name, short_code: rule.short_code });
  };

  const handleSaveEdit = async (ruleId) => {
    if (!editData.full_name.trim() || !editData.short_code.trim()) {
      toast.error('Vui lòng điền đầy đủ thông tin');
      return;
    }

    try {
      const response = await axios.put(`${API}/rules/${ruleId}`, editData, {
        headers: getAuthHeaders()
      });
      setRules(rules.map(r => r.id === ruleId ? response.data : r));
      setEditingId(null);
      toast.success('✅ Đã cập nhật quy tắc');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      toast.error(`❌ ${errorMsg}`);
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditData({ full_name: '', short_code: '' });
  };

  const handleDeleteRule = async (ruleId, fullName) => {
    if (!window.confirm(`Bạn có chắc muốn xóa quy tắc "${fullName}"?`)) {
      return;
    }

    try {
      await axios.delete(`${API}/rules/${ruleId}`, {
        headers: getAuthHeaders()
      });
      setRules(rules.filter(r => r.id !== ruleId));
      toast.success('✅ Đã xóa quy tắc');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      toast.error(`❌ ${errorMsg}`);
    }
  };

  const handleCleanupDuplicates = async () => {
    if (!window.confirm(`Phát hiện ${rules.length} quy tắc. Có thể có trùng lặp.\n\nBạn có muốn xóa các quy tắc trùng lặp không?\n\n(Sẽ giữ lại 1 quy tắc duy nhất cho mỗi mã ngắn)`)) {
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(`${API}/rules/cleanup-duplicates`);
      toast.success(`✅ ${response.data.message}`);
      // Refresh rules list
      await fetchRules();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message;
      toast.error(`❌ ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const filteredRules = rules.filter(r => 
    !searchTerm || 
    r.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    r.short_code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Quản Lý Quy Tắc Nhận Diện
              </CardTitle>
              <CardDescription>
                Thêm, sửa, xóa các loại tài liệu và mã ngắn
              </CardDescription>
            </div>
            <div className="flex gap-2">
              {rules.length > 200 && (
                <Button 
                  onClick={handleCleanupDuplicates} 
                  variant="outline"
                  className="gap-2"
                >
                  🧹 Xóa Trùng Lặp
                </Button>
              )}
              <Button onClick={() => setShowAddForm(!showAddForm)} className="gap-2">
                <Plus className="h-4 w-4" />
                Thêm Mới
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Search */}
          <div className="mb-4">
            <Input
              placeholder="Tìm kiếm theo tên hoặc mã..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="max-w-md"
            />
          </div>

          {/* Add New Form */}
          {showAddForm && (
            <div className="mb-6 p-4 border rounded-lg bg-blue-50 space-y-3">
              <h3 className="font-semibold">Thêm Quy Tắc Mới</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <Input
                  placeholder="Tên đầy đủ (VD: Giấy chứng nhận quyền sử dụng đất)"
                  value={newRule.full_name}
                  onChange={(e) => setNewRule({ ...newRule, full_name: e.target.value })}
                />
                <Input
                  placeholder="Mã ngắn (VD: GCNM)"
                  value={newRule.short_code}
                  onChange={(e) => setNewRule({ ...newRule, short_code: e.target.value.toUpperCase() })}
                  maxLength={10}
                />
              </div>
              <div className="flex gap-2">
                <Button onClick={handleAddRule} size="sm" className="gap-2">
                  <Save className="h-4 w-4" />
                  Lưu
                </Button>
                <Button 
                  onClick={() => {
                    setShowAddForm(false);
                    setNewRule({ full_name: '', short_code: '' });
                  }} 
                  size="sm" 
                  variant="outline"
                  className="gap-2"
                >
                  <X className="h-4 w-4" />
                  Hủy
                </Button>
              </div>
            </div>
          )}

          {/* Rules Table */}
          <div className="space-y-2">
            <div className="grid grid-cols-12 gap-2 font-semibold text-sm text-gray-600 border-b pb-2">
              <div className="col-span-1">#</div>
              <div className="col-span-6">Tên Đầy Đủ</div>
              <div className="col-span-2">Mã Ngắn</div>
              <div className="col-span-3 text-right">Thao Tác</div>
            </div>

            {filteredRules.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                {searchTerm ? 'Không tìm thấy quy tắc phù hợp' : 'Chưa có quy tắc nào'}
              </div>
            ) : (
              filteredRules.map((rule, index) => (
                <div key={rule.id} className="grid grid-cols-12 gap-2 items-center py-3 border-b hover:bg-gray-50">
                  <div className="col-span-1 text-gray-500 text-sm">{index + 1}</div>
                  
                  {editingId === rule.id ? (
                    <>
                      <div className="col-span-6">
                        <Input
                          value={editData.full_name}
                          onChange={(e) => setEditData({ ...editData, full_name: e.target.value })}
                          size="sm"
                        />
                      </div>
                      <div className="col-span-2">
                        <Input
                          value={editData.short_code}
                          onChange={(e) => setEditData({ ...editData, short_code: e.target.value.toUpperCase() })}
                          size="sm"
                          maxLength={10}
                        />
                      </div>
                      <div className="col-span-3 flex gap-2 justify-end">
                        <Button onClick={() => handleSaveEdit(rule.id)} size="sm" variant="default" className="gap-1">
                          <Save className="h-3 w-3" />
                          Lưu
                        </Button>
                        <Button onClick={handleCancelEdit} size="sm" variant="outline" className="gap-1">
                          <X className="h-3 w-3" />
                          Hủy
                        </Button>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="col-span-6 text-sm">{rule.full_name}</div>
                      <div className="col-span-2">
                        <Badge variant="secondary">{rule.short_code}</Badge>
                      </div>
                      <div className="col-span-3 flex gap-2 justify-end">
                        <Button 
                          onClick={() => handleStartEdit(rule)} 
                          size="sm" 
                          variant="outline"
                          className="gap-1"
                        >
                          <Edit2 className="h-3 w-3" />
                          Sửa
                        </Button>
                        <Button 
                          onClick={() => handleDeleteRule(rule.id, rule.full_name)} 
                          size="sm" 
                          variant="destructive"
                          className="gap-1"
                        >
                          <Trash2 className="h-3 w-3" />
                          Xóa
                        </Button>
                      </div>
                    </>
                  )}
                </div>
              ))
            )}
          </div>

          <div className="mt-4 text-sm text-gray-500">
            Tổng số: {filteredRules.length} quy tắc
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RulesManager;
