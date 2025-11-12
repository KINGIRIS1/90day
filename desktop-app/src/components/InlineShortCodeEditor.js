import React, { useState, useRef, useEffect } from 'react';
import { VALID_DOCUMENT_CODES, isValidDocumentCode, getCodeDescription } from '../constants/documentCodes';

const InlineShortCodeEditor = ({ value, onChange }) => {
  const [editing, setEditing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  // Filter codes based on search term
  const filteredCodes = VALID_DOCUMENT_CODES.filter(code => 
    code.includes(searchTerm.toUpperCase()) ||
    getCodeDescription(code).toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };

    if (showDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showDropdown]);

  const handleSelect = (code) => {
    onChange(code);
    setEditing(false);
    setShowDropdown(false);
    setSearchTerm('');
    setSelectedIndex(0);
  };

  const handleCancel = () => {
    setEditing(false);
    setShowDropdown(false);
    setSearchTerm('');
    setSelectedIndex(0);
  };

  const handleKeyDown = (e) => {
    if (!showDropdown) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => Math.min(prev + 1, filteredCodes.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => Math.max(prev - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (filteredCodes[selectedIndex]) {
          handleSelect(filteredCodes[selectedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        handleCancel();
        break;
      default:
        break;
    }
  };

  // Get color based on code validity
  const getCodeColor = (code) => {
    if (code === 'UNKNOWN') return 'text-red-600 bg-red-50';
    if (code === 'GCNC' || code === 'GCNM') return 'text-green-600 bg-green-50 font-bold';
    return 'text-blue-600 bg-blue-50';
  };

  if (!editing) {
    return (
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-600">Short code:</span>
        <button
          onClick={() => {
            setEditing(true);
            setShowDropdown(true);
          }}
          className={`text-xs px-2 py-0.5 rounded hover:opacity-80 ${getCodeColor(value)}`}
        >
          {value} ✏️
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-2 relative" ref={dropdownRef}>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-600 font-medium">Chọn mã tài liệu:</span>
        <span className="text-xs text-gray-500">({VALID_DOCUMENT_CODES.length} mã)</span>
      </div>
      
      {/* Search Input */}
      <div className="flex items-center space-x-2">
        <div className="flex-1 relative">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setSelectedIndex(0);
              setShowDropdown(true);
            }}
            onFocus={() => setShowDropdown(true)}
            onKeyDown={handleKeyDown}
            placeholder="Tìm mã (vd: GCN, PCT, CCCD...)"
            className="w-full px-2 py-1 text-xs border border-blue-300 rounded focus:outline-none focus:border-blue-500"
            autoFocus
          />
          <span className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-400">
            🔍
          </span>
        </div>
        <button
          onClick={handleCancel}
          className="px-2 py-1 text-xs bg-gray-400 text-white rounded hover:bg-gray-500"
          title="Hủy"
        >
          ✕
        </button>
      </div>

      {/* Dropdown List */}
      {showDropdown && (
        <div className="absolute z-50 w-full mt-1 bg-white border-2 border-blue-300 rounded-lg shadow-xl max-h-64 overflow-y-auto">
          {filteredCodes.length > 0 ? (
            <div className="py-1">
              {filteredCodes.map((code, index) => (
                <button
                  key={code}
                  onClick={() => handleSelect(code)}
                  onMouseEnter={() => setSelectedIndex(index)}
                  className={`w-full text-left px-3 py-2 text-xs hover:bg-blue-50 transition-colors ${
                    index === selectedIndex ? 'bg-blue-100 border-l-4 border-blue-600' : ''
                  } ${code === value ? 'bg-green-50' : ''}`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`font-mono font-bold ${
                      code === 'GCNC' || code === 'GCNM' ? 'text-green-600' : 
                      code === 'UNKNOWN' ? 'text-red-600' : 
                      'text-blue-600'
                    }`}>
                      {code}
                    </span>
                    {code === value && <span className="text-green-600 text-lg">✓</span>}
                  </div>
                  <div className="text-gray-600 mt-0.5 truncate">
                    {getCodeDescription(code)}
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="px-3 py-4 text-xs text-center text-gray-500">
              <div className="text-2xl mb-2">🔍</div>
              <div>Không tìm thấy mã "{searchTerm}"</div>
              <div className="mt-1 text-gray-400">Chỉ có {VALID_DOCUMENT_CODES.length} mã hợp lệ</div>
            </div>
          )}
        </div>
      )}

      {/* Info hint */}
      <div className="text-xs text-gray-500 flex items-center gap-1">
        <span>💡</span>
        <span>Chỉ cho phép chọn mã từ danh sách có sẵn</span>
      </div>
    </div>
  );
};

export default InlineShortCodeEditor;