import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, XCircle, Clock, User } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

export default function AdminPanel() {
  const [pendingUsers, setPendingUsers] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pending');
  const { token } = useAuth();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const [pendingRes, allRes] = await Promise.all([
        axios.get(`${API_URL}/api/admin/users/pending`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/admin/users/all`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      setPendingUsers(pendingRes.data);
      setAllUsers(allRes.data);
    } catch (error) {
      toast.error('Lỗi tải danh sách users');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (userId) => {
    try {
      await axios.post(
        `${API_URL}/api/admin/users/approve/${userId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success('✅ Đã phê duyệt user');
      fetchUsers();
    } catch (error) {
      toast.error('Lỗi phê duyệt user');
      console.error(error);
    }
  };

  const handleToggleStatus = async (userId, currentStatus) => {
    const endpoint = currentStatus ? 'disable' : 'enable';
    
    try {
      await axios.post(
        `${API_URL}/api/admin/users/${endpoint}/${userId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success(`✅ Đã ${endpoint === 'disable' ? 'vô hiệu hóa' : 'kích hoạt'} user`);
      fetchUsers();
    } catch (error) {
      toast.error('Lỗi cập nhật trạng thái');
      console.error(error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Đang tải...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-2xl font-bold flex items-center gap-2">
              <User className="h-6 w-6" />
              Quản Lý Users
            </CardTitle>
          </CardHeader>
        </Card>

        {/* Tabs */}
        <div className="flex gap-4 mb-6">
          <Button
            variant={activeTab === 'pending' ? 'default' : 'outline'}
            onClick={() => setActiveTab('pending')}
          >
            <Clock className="h-4 w-4 mr-2" />
            Chờ Phê Duyệt ({pendingUsers.length})
          </Button>
          <Button
            variant={activeTab === 'all' ? 'default' : 'outline'}
            onClick={() => setActiveTab('all')}
          >
            <User className="h-4 w-4 mr-2" />
            Tất Cả Users ({allUsers.length})
          </Button>
        </div>

        {/* Pending Users */}
        {activeTab === 'pending' && (
          <div className="space-y-4">
            {pendingUsers.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center text-gray-500">
                  Không có user nào chờ phê duyệt
                </CardContent>
              </Card>
            ) : (
              pendingUsers.map((user) => (
                <Card key={user.id}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">{user.full_name || user.username}</h3>
                        <p className="text-sm text-gray-600">@{user.username}</p>
                        <p className="text-sm text-gray-500">{user.email}</p>
                        <p className="text-xs text-gray-400 mt-1">
                          Đăng ký: {new Date(user.created_at).toLocaleString('vi-VN')}
                        </p>
                      </div>
                      <Button
                        onClick={() => handleApprove(user.id)}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircle2 className="h-4 w-4 mr-2" />
                        Phê Duyệt
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        )}

        {/* All Users */}
        {activeTab === 'all' && (
          <div className="space-y-4">
            {allUsers.map((user) => (
              <Card key={user.id}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-lg">
                          {user.full_name || user.username}
                        </h3>
                        {user.roles.includes('admin') && (
                          <Badge variant="destructive">Admin</Badge>
                        )}
                        <Badge
                          variant={
                            user.status === 'approved'
                              ? 'default'
                              : user.status === 'pending'
                              ? 'secondary'
                              : 'outline'
                          }
                        >
                          {user.status === 'approved'
                            ? 'Approved'
                            : user.status === 'pending'
                            ? 'Pending'
                            : 'Disabled'}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">@{user.username}</p>
                      <p className="text-sm text-gray-500">{user.email}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        Tạo: {new Date(user.created_at).toLocaleString('vi-VN')}
                      </p>
                    </div>
                    {!user.roles.includes('admin') && (
                      <Button
                        variant={user.is_active ? 'destructive' : 'default'}
                        onClick={() => handleToggleStatus(user.id, user.is_active)}
                      >
                        {user.is_active ? (
                          <>
                            <XCircle className="h-4 w-4 mr-2" />
                            Vô Hiệu Hóa
                          </>
                        ) : (
                          <>
                            <CheckCircle2 className="h-4 w-4 mr-2" />
                            Kích Hoạt
                          </>
                        )}
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
