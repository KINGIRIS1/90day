import React, { useState } from 'react';

const SetupAdmin = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSetupAdmin = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/setup-admin`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
      } else {
        setError(data.detail || 'Đã xảy ra lỗi');
      }
    } catch (err) {
      setError(`Lỗi kết nối: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      maxWidth: '600px', 
      margin: '50px auto', 
      padding: '30px',
      background: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
    }}>
      <h1 style={{ color: '#333', marginBottom: '20px' }}>🔧 Thiết Lập Admin</h1>
      <p style={{ marginBottom: '20px', color: '#666' }}>
        Công cụ này sẽ tạo tài khoản admin cho ứng dụng Document Scanner.
      </p>
      <div style={{
        padding: '12px',
        background: '#fff3cd',
        border: '1px solid #ffeeba',
        borderRadius: '4px',
        marginBottom: '20px',
        fontSize: '14px',
        color: '#856404'
      }}>
        <strong>⚠️ Lưu ý:</strong> Nếu đã có tài khoản "admin" (kể cả tài khoản pending), 
        tất cả sẽ bị xóa và tạo lại tài khoản admin mới với quyền đầy đủ.
      </div>

      <button 
        onClick={handleSetupAdmin}
        disabled={loading}
        style={{
          width: '100%',
          padding: '12px',
          background: loading ? '#ccc' : '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          fontSize: '16px',
          cursor: loading ? 'not-allowed' : 'pointer',
          fontWeight: 'bold'
        }}
      >
        {loading ? 'Đang xử lý...' : 'Tạo Tài Khoản Admin'}
      </button>

      {result && (
        <div style={{
          marginTop: '20px',
          padding: '15px',
          background: '#d4edda',
          color: '#155724',
          border: '1px solid #c3e6cb',
          borderRadius: '4px'
        }}>
          <strong>✅ {result.message}</strong>
          {result.username && (
            <div style={{ marginTop: '10px' }}>
              <p>Username: <strong>{result.username}</strong></p>
              {result.deleted_old_accounts > 0 && (
                <p style={{ color: '#856404', marginTop: '5px' }}>
                  ⚠️ Đã xóa {result.deleted_old_accounts} tài khoản admin cũ (bao gồm tài khoản pending)
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {error && (
        <div style={{
          marginTop: '20px',
          padding: '15px',
          background: '#f8d7da',
          color: '#721c24',
          border: '1px solid #f5c6cb',
          borderRadius: '4px'
        }}>
          <strong>❌ Lỗi:</strong> {error}
        </div>
      )}

      <div style={{
        marginTop: '20px',
        padding: '15px',
        background: '#fff3cd',
        border: '1px solid #ffeeba',
        borderRadius: '4px'
      }}>
        <h3 style={{ margin: '0 0 10px 0', color: '#856404' }}>📋 Thông Tin Đăng Nhập Admin:</h3>
        <p style={{ margin: '5px 0', color: '#856404' }}><strong>Username:</strong> admin</p>
        <p style={{ margin: '5px 0', color: '#856404' }}><strong>Password:</strong> Thommit@19</p>
      </div>
    </div>
  );
};

export default SetupAdmin;
