import React, { useState, useEffect } from 'react';

const RulesManager = () => {
  const [rules, setRules] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedRule, setSelectedRule] = useState(null);
  const [editingRule, setEditingRule] = useState(null);
  const [notification, setNotification] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Load rules on mount
  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    try {
      setLoading(true);
      const result = await window.electronAPI.getRules();
      if (result.success) {
        setRules(result.rules);
      } else {
        showNotification('Lỗi tải rules: ' + result.error, 'error');
      }
    } catch (error) {
      showNotification('Lỗi: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const handleSaveRule = async () => {
    if (!editingRule) return;

    try {
      setLoading(true);
      const result = await window.electronAPI.saveRule(editingRule.docType, {
        keywords: editingRule.keywords,
        weight: parseFloat(editingRule.weight) || 1.0,
        min_matches: parseInt(editingRule.min_matches) || 1
      });

      if (result.success) {
        showNotification(result.message, 'success');
        await loadRules();
        setEditingRule(null);
      } else {
        showNotification('Lỗi lưu rule: ' + result.error, 'error');
      }
    } catch (error) {
      showNotification('Lỗi: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRule = async (docType) => {
    if (!window.confirm(`Xóa rule "${docType}"?\nSẽ quay về rule mặc định.`)) {
      return;
    }

    try {
      setLoading(true);
      const result = await window.electronAPI.deleteRule(docType);

      if (result.success) {
        showNotification(result.message, 'success');
        await loadRules();
        if (selectedRule === docType) {
          setSelectedRule(null);
        }
      } else {
        showNotification('Lỗi xóa rule: ' + result.error, 'error');
      }
    } catch (error) {
      showNotification('Lỗi: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleResetAll = async () => {
    if (!window.confirm('Reset TẤT CẢ rules về mặc định?\nThao tác này không thể hoàn tác!')) {
      return;
    }

    try {
      setLoading(true);
      const result = await window.electronAPI.resetRules();

      if (result.success) {
        showNotification(result.message, 'success');
        await loadRules();
        setSelectedRule(null);
        setEditingRule(null);
      } else {
        showNotification('Lỗi reset: ' + result.error, 'error');
      }
    } catch (error) {
      showNotification('Lỗi: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      setLoading(true);
      const result = await window.electronAPI.exportRules();

      if (result.success) {
        showNotification(result.message, 'success');
      } else {
        showNotification('Lỗi export: ' + (result.error || result.message), 'info');
      }
    } catch (error) {
      showNotification('Lỗi: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (merge = true) => {
    try {
      setLoading(true);
      const result = await window.electronAPI.importRules(merge);

      if (result.success) {
        showNotification(`${result.message} (${result.count} rules)`, 'success');
        await loadRules();
      } else {
        showNotification('Lỗi import: ' + (result.error || result.message), 'info');
      }
    } catch (error) {
      showNotification('Lỗi: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenFolder = async () => {
    try {
      const result = await window.electronAPI.openRulesFolder();
      if (result.success) {
        showNotification(result.message, 'success');
      }
    } catch (error) {
      showNotification('Lỗi: ' + error.message, 'error');
    }
  };

  const startEdit = (docType) => {
    const rule = rules[docType];
    setEditingRule({
      docType,
      keywords: rule.keywords || [],
      weight: rule.weight || 1.0,
      min_matches: rule.min_matches || 1,
      newKeyword: ''
    });
  };

  const addKeyword = () => {
    if (!editingRule.newKeyword.trim()) return;
    setEditingRule({
      ...editingRule,
      keywords: [...editingRule.keywords, editingRule.newKeyword.trim()],
      newKeyword: ''
    });
  };

  const removeKeyword = (index) => {
    setEditingRule({
      ...editingRule,
      keywords: editingRule.keywords.filter((_, i) => i !== index)
    });
  };

  // Filter rules by search term
  const filteredRules = Object.keys(rules).filter(docType =>
    docType.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (rules[docType].keywords && rules[docType].keywords.some(k => 
      k.toLowerCase().includes(searchTerm.toLowerCase())
    ))
  );

  return (
    <div className="space-y-4">
      {/* Notification */}
      {notification && (
        <div className={`p-3 rounded-lg ${
          notification.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' :
          notification.type === 'error' ? 'bg-red-50 text-red-800 border border-red-200' :
          'bg-blue-50 text-blue-800 border border-blue-200'
        }`}>
          {notification.message}
        </div>
      )}

      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          📋 Quản Lý Rules Phân Loại
        </h2>
        <p className="text-sm text-gray-600 mb-4">
          Quản lý các quy tắc phân loại tài liệu. Bạn có thể thêm/sửa keywords, điều chỉnh trọng số, và quản lý các quy tắc tùy chỉnh.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={loadRules}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🔄 Tải lại
          </button>
          <button
            onClick={handleExport}
            disabled={loading}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            📤 Export JSON
          </button>
          <button
            onClick={() => handleImport(true)}
            disabled={loading}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            📥 Import (Merge)
          </button>
          <button
            onClick={() => handleImport(false)}
            disabled={loading}
            className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50"
          >
            📥 Import (Replace)
          </button>
          <button
            onClick={handleResetAll}
            disabled={loading}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            🔄 Reset Tất Cả
          </button>
          <button
            onClick={handleOpenFolder}
            disabled={loading}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
          >
            📁 Mở Folder
          </button>
        </div>

        {/* Search */}
        <div className="mt-4">
          <input
            type="text"
            placeholder="🔍 Tìm kiếm rule hoặc keyword..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Rules List */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Danh sách Rules ({filteredRules.length}/{Object.keys(rules).length})
        </h3>

        {loading ? (
          <div className="text-center py-8 text-gray-500">
            Đang tải...
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {filteredRules.map(docType => (
              <div
                key={docType}
                className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                  selectedRule === docType 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedRule(docType)}
              >
                <div className="flex justify-between items-start">
                  <div className="font-mono font-bold text-gray-900">{docType}</div>
                  <div className="text-xs text-gray-500">
                    weight: {rules[docType].weight || 1.0}
                  </div>
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  {rules[docType].keywords?.length || 0} keywords
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Rule Detail / Editor */}
      {selectedRule && !editingRule && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Chi tiết: {selectedRule}
            </h3>
            <div className="flex gap-2">
              <button
                onClick={() => startEdit(selectedRule)}
                className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
              >
                ✏️ Sửa
              </button>
              <button
                onClick={() => handleDeleteRule(selectedRule)}
                className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
              >
                🗑️ Xóa
              </button>
              <button
                onClick={() => setSelectedRule(null)}
                className="px-3 py-1 bg-gray-500 text-white text-sm rounded hover:bg-gray-600"
              >
                ✖️ Đóng
              </button>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-700">Weight:</label>
              <div className="text-gray-900">{rules[selectedRule].weight || 1.0}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Min Matches:</label>
              <div className="text-gray-900">{rules[selectedRule].min_matches || 1}</div>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">
                Keywords ({rules[selectedRule].keywords?.length || 0}):
              </label>
              <div className="mt-2 flex flex-wrap gap-2">
                {rules[selectedRule].keywords?.map((keyword, idx) => (
                  <span
                    key={idx}
                    className="inline-block px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Rule */}
      {editingRule && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Chỉnh sửa: {editingRule.docType}
            </h3>
            <div className="flex gap-2">
              <button
                onClick={handleSaveRule}
                disabled={loading}
                className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
              >
                💾 Lưu
              </button>
              <button
                onClick={() => setEditingRule(null)}
                className="px-3 py-1 bg-gray-500 text-white text-sm rounded hover:bg-gray-600"
              >
                ❌ Hủy
              </button>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Weight (trọng số):
              </label>
              <input
                type="number"
                step="0.1"
                value={editingRule.weight}
                onChange={(e) => setEditingRule({ ...editingRule, weight: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Matches (số keyword tối thiểu):
              </label>
              <input
                type="number"
                value={editingRule.min_matches}
                onChange={(e) => setEditingRule({ ...editingRule, min_matches: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Keywords ({editingRule.keywords.length}):
              </label>
              
              {/* Add keyword */}
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  placeholder="Thêm keyword mới..."
                  value={editingRule.newKeyword}
                  onChange={(e) => setEditingRule({ ...editingRule, newKeyword: e.target.value })}
                  onKeyPress={(e) => e.key === 'Enter' && addKeyword()}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={addKeyword}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  ➕ Thêm
                </button>
              </div>

              {/* Keywords list */}
              <div className="border border-gray-300 rounded-lg p-3 max-h-64 overflow-y-auto">
                <div className="flex flex-wrap gap-2">
                  {editingRule.keywords.map((keyword, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-800 text-sm rounded"
                    >
                      {keyword}
                      <button
                        onClick={() => removeKeyword(idx)}
                        className="text-red-600 hover:text-red-800 ml-1"
                      >
                        ✖
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RulesManager;
