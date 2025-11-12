import React, { useState, useRef, useEffect } from 'react';
import { VALID_DOCUMENT_CODES, getCodeDescription } from '../constants/documentCodes';

const InlineShortCodeEditor = ({ value, onChange }) => {
  const [editing, setEditing] = useState(false);
  const [inputValue, setInputValue] = useState(value || '');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);
  const inputRef = useRef(null);

  // Filter codes based on input
  const filteredCodes = VALID_DOCUMENT_CODES.filter(code => 
    code.includes(inputValue.toUpperCase()) ||
    getCodeDescription(code).toLowerCase().includes(inputValue.toLowerCase())
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
    setInputValue(code);
    setShowDropdown(false);
    setSelectedIndex(0);
    inputRef.current?.focus();
  };

  const handleSave = () => {
    const cleaned = inputValue.trim().toUpperCase();
    if (cleaned) {
      onChange(cleaned);
      setEditing(false);
      setShowDropdown(false);
    }
  };

  const handleCancel = () => {
    setInputValue(value || '');
    setEditing(false);
    setShowDropdown(false);
    setSelectedIndex(0);
  };

  const handleKeyDown = (e) => {
    // Ctrl+Enter always saves
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      handleSave();
      return;
    }

    if (showDropdown && filteredCodes.length > 0) {
      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex(prev => Math.min(prev + 1, Math.min(filteredCodes.length - 1, 9))); // Limit to 10 items
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex(prev => Math.max(prev - 1, 0));
          break;
        case 'Tab':
        case 'Enter':
          if (filteredCodes[selectedIndex]) {
            e.preventDefault();
            handleSelect(filteredCodes[selectedIndex]);
          }
          break;
        case 'Escape':
          e.preventDefault();
          setShowDropdown(false);
          break;
        default:
          break;
      }
    } else if (e.key === 'Enter') {
      e.preventDefault();
      handleSave();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      handleCancel();
    }
  };

  // Get color based on code validity
  const getCodeColor = (code) => {
    if (code === 'UNKNOWN') return 'text-red-600 bg-red-50';
    if (code === 'GCN') return 'text-yellow-600 bg-yellow-50 font-bold'; // Temporary - needs post-processing
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
            setInputValue(value || '');
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
        <span className="text-xs text-gray-600 font-medium">Sửa mã tài liệu:</span>
        <span className="text-xs text-gray-500">({VALID_DOCUMENT_CODES.length} gợi ý)</span>
      </div>
      
      {/* Input with autocomplete */}
      <div className="flex items-center space-x-2">
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => {
              const val = e.target.value;
              setInputValue(val);
              setSelectedIndex(0);
              setShowDropdown(val.length > 0); // Show suggestions when typing
            }}
            onFocus={() => {
              if (inputValue.length > 0) {
                setShowDropdown(true);
              }
            }}
            onKeyDown={handleKeyDown}
            placeholder="Nhập hoặc chọn mã (vd: GCN, PCT, CCCD...)"
            className="w-full px-2 py-1 text-xs border border-blue-300 rounded focus:outline-none focus:border-blue-500 font-mono uppercase"
            autoFocus
          />
          <span className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-400">
            {showDropdown && filteredCodes.length > 0 ? '↓' : '✎'}
          </span>
        </div>
        <button
          onClick={handleSave}
          className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 font-medium"
          title="Lưu"
        >
          ✓
        </button>
        <button
          onClick={handleCancel}
          className="px-2 py-1 text-xs bg-gray-400 text-white rounded hover:bg-gray-500"
          title="Hủy"
        >
          ✕
        </button>
      </div>

      {/* Dropdown Suggestions */}
      {showDropdown && filteredCodes.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border-2 border-blue-300 rounded-lg shadow-xl max-h-64 overflow-y-auto">
          <div className="py-1">
            {filteredCodes.slice(0, 10).map((code, index) => (
              <button
                key={code}
                onClick={() => handleSelect(code)}
                onMouseEnter={() => setSelectedIndex(index)}
                className={`w-full text-left px-3 py-2 text-xs hover:bg-blue-50 transition-colors ${
                  index === selectedIndex ? 'bg-blue-100 border-l-4 border-blue-600' : ''
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className={`font-mono font-bold ${
                    code === 'GCNC' || code === 'GCNM' ? 'text-green-600' :
                    code === 'GCN' ? 'text-yellow-600' : 
                    code === 'UNKNOWN' ? 'text-red-600' : 
                    'text-blue-600'
                  }`}>
                    {code}
                  </span>
                </div>
                <div className="text-gray-600 mt-0.5 truncate text-[10px]">
                  {getCodeDescription(code)}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Info hint */}
      <div className="text-xs text-gray-500 flex items-center gap-1">
        <span>💡</span>
        <span>Gõ để tìm hoặc nhập mã bất kỳ • Tab/Enter để chọn gợi ý • Ctrl+Enter để lưu</span>
      </div>
    </div>
  );
};

export default InlineShortCodeEditor;