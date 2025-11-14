/**
 * Utility functions for highlighting special document types
 */

/**
 * Get CSS classes for highlighting document type
 * @param {string} shortCode - Document short code (e.g., "GCN", "UNKNOWN")
 * @param {string} folderName - Folder name (to detect unnamed folders)
 * @returns {object} - { bgClass, borderClass, textClass, badgeClass }
 */
export const getDocumentHighlight = (shortCode, folderName = '') => {
  const code = shortCode?.toUpperCase() || '';
  const isUnnamed = !folderName || folderName === 'unnamed' || folderName.includes('unnamed_');
  
  // GCN - Highlight with green
  if (code === 'GCN' || code === 'GCNC' || code === 'GCNM') {
    return {
      bgClass: 'bg-green-50 hover:bg-green-100',
      borderClass: 'border-2 border-green-400',
      textClass: 'text-green-900',
      badgeClass: 'bg-green-600 text-white',
      iconBefore: '📜',
      label: 'GCN'
    };
  }
  
  // UNKNOWN - Highlight with red/orange
  if (code === 'UNKNOWN') {
    return {
      bgClass: 'bg-red-50 hover:bg-red-100',
      borderClass: 'border-2 border-red-400',
      textClass: 'text-red-900',
      badgeClass: 'bg-red-600 text-white',
      iconBefore: '⚠️',
      label: 'CHƯA PHÂN LOẠI'
    };
  }
  
  // Unnamed folder - Highlight with yellow
  if (isUnnamed) {
    return {
      bgClass: 'bg-yellow-50 hover:bg-yellow-100',
      borderClass: 'border-2 border-yellow-400',
      textClass: 'text-yellow-900',
      badgeClass: 'bg-yellow-600 text-white',
      iconBefore: '📝',
      label: 'CHƯA ĐẶT TÊN'
    };
  }
  
  // Normal document
  return {
    bgClass: 'bg-white hover:bg-gray-50',
    borderClass: 'border border-gray-300',
    textClass: 'text-gray-900',
    badgeClass: 'bg-blue-600 text-white',
    iconBefore: '',
    label: ''
  };
};

/**
 * Get row highlight class for table/list items
 */
export const getRowHighlight = (shortCode, folderName = '') => {
  const code = shortCode?.toUpperCase() || '';
  const isUnnamed = !folderName || folderName === 'unnamed' || folderName.includes('unnamed_');
  
  if (code === 'GCN' || code === 'GCNC' || code === 'GCNM') {
    return 'bg-green-50 border-l-4 border-green-500';
  }
  
  if (code === 'UNKNOWN') {
    return 'bg-red-50 border-l-4 border-red-500';
  }
  
  if (isUnnamed) {
    return 'bg-yellow-50 border-l-4 border-yellow-500';
  }
  
  return '';
};

/**
 * Get badge for special document types
 */
export const getDocumentBadge = (shortCode, folderName = '') => {
  const highlight = getDocumentHighlight(shortCode, folderName);
  
  if (highlight.label) {
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-semibold rounded-full ${highlight.badgeClass}`}>
        {highlight.iconBefore} {highlight.label}
      </span>
    );
  }
  
  return null;
};

/**
 * Count special documents in results
 */
export const countSpecialDocuments = (results = []) => {
  let gcnCount = 0;
  let unknownCount = 0;
  let unnamedCount = 0;
  
  results.forEach(result => {
    const code = result.short_code?.toUpperCase() || '';
    const folderName = result.folderName || result.folder_name || '';
    
    if (code === 'GCN' || code === 'GCNC' || code === 'GCNM') {
      gcnCount++;
    }
    
    if (code === 'UNKNOWN') {
      unknownCount++;
    }
    
    const isUnnamed = !folderName || folderName === 'unnamed' || folderName.includes('unnamed_');
    if (isUnnamed) {
      unnamedCount++;
    }
  });
  
  return { gcnCount, unknownCount, unnamedCount };
};
