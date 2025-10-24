import React from 'react';
import { Outlet } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import { Loader2 } from 'lucide-react';

function App() {
  const { loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 text-lg">Đang tải...</p>
        </div>
      </div>
    );
  }

  return <Outlet />;
}

export default App;
