import React, { useState } from 'react';

const InlineShortCodeEditor = ({ value, onChange }) => {
  const [editing, setEditing] = useState(false);
  const [tempValue, setTempValue] = useState(value || '');

  const handleSave = () => {
    const cleaned = (tempValue || '').trim().toUpperCase().slice(0, 32);
    onChange(cleaned);
    setEditing(false);
  };

  const handleCancel = () => {
    setTempValue(value);
    setEditing(false);
  };

  if (!editing) {
    return (
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-600">Short code:</span>
        <button
          onClick={() => setEditing(true)}
          className="text-xs text-blue-600 hover:underline"
        >
          {value} ✏️
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-600">Short code:</span>
      </div>
      <div className="flex items-center space-x-2">
        <input
          type="text"
          value={tempValue}
          onChange={(e) => setTempValue(e.target.value)}
          className="flex-1 px-2 py-1 text-xs border rounded"
          autoFocus
        />
        <button
          onClick={handleSave}
          className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
        >
          ✓
        </button>
        <button
          onClick={handleCancel}
          className="px-2 py-1 text-xs bg-gray-400 text-white rounded hover:bg-gray-500"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default InlineShortCodeEditor;