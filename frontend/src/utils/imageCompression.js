import imageCompression from 'browser-image-compression';

/**
 * Client-side image compression and optimization
 * Reduces image size by 40-60% while maintaining OCR quality
 */
export const compressImageForOCR = async (file) => {
  try {
    console.log(`📸 Original file: ${file.name}, Size: ${(file.size / 1024 / 1024).toFixed(2)}MB`);
    
    const options = {
      maxSizeMB: 1,              // Max 1MB per image (giảm upload time)
      maxWidthOrHeight: 2048,    // Max dimension 2048px (đủ cho OCR)
      useWebWorker: true,        // Dùng Web Worker để không block UI
      fileType: 'image/jpeg',    // Convert to JPEG
      initialQuality: 0.8,       // Quality 80% (cân bằng giữa size và OCR accuracy)
    };

    const compressedFile = await imageCompression(file, options);
    
    const compressionRatio = ((1 - compressedFile.size / file.size) * 100).toFixed(1);
    console.log(`✅ Compressed: ${(compressedFile.size / 1024 / 1024).toFixed(2)}MB (giảm ${compressionRatio}%)`);
    
    return compressedFile;
  } catch (error) {
    console.error('❌ Compression error:', error);
    // Fallback: return original file if compression fails
    return file;
  }
};

/**
 * Batch compress multiple images
 */
export const compressImages = async (files, onProgress) => {
  const compressedFiles = [];
  
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    
    // Update progress
    if (onProgress) {
      onProgress(i + 1, files.length, file.name);
    }
    
    const compressed = await compressImageForOCR(file);
    compressedFiles.push(compressed);
  }
  
  return compressedFiles;
};

/**
 * Pre-crop image to top 70% for faster processing
 * (Optional - can be enabled for even faster upload)
 */
export const preCropImage = async (file, cropPercentage = 0.70) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        // Create canvas with cropped dimensions
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = img.width;
        canvas.height = Math.floor(img.height * cropPercentage);
        
        // Draw cropped image
        ctx.drawImage(
          img,
          0, 0, img.width, canvas.height,  // Source rect (top portion)
          0, 0, canvas.width, canvas.height // Dest rect
        );
        
        // Convert to blob
        canvas.toBlob((blob) => {
          const croppedFile = new File([blob], file.name, {
            type: 'image/jpeg',
            lastModified: Date.now(),
          });
          
          console.log(`✂️  Pre-cropped to ${(cropPercentage * 100).toFixed(0)}%: ${img.height}px → ${canvas.height}px`);
          resolve(croppedFile);
        }, 'image/jpeg', 0.85);
      };
      
      img.onerror = reject;
      img.src = e.target.result;
    };
    
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};
