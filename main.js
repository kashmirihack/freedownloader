document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const urlForm = document.getElementById('urlForm');
    const videoUrlInput = document.getElementById('videoUrl');
    const fetchBtn = document.getElementById('fetchBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const videoPreview = document.getElementById('videoPreview');
    const videoThumbnail = document.getElementById('videoThumbnail');
    const videoTitle = document.getElementById('videoTitle');
    const videoUploader = document.getElementById('videoUploader').querySelector('span');
    const videoDuration = document.getElementById('videoDuration').querySelector('span');
    const formatSelect = document.getElementById('formatSelect');
    const downloadForm = document.getElementById('downloadForm');
    const downloadUrl = document.getElementById('downloadUrl');
    const formatId = document.getElementById('formatId');

    // Helper functions
    function formatDuration(seconds) {
        if (!seconds) return 'Unknown duration';
        
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        let result = '';
        if (hrs > 0) {
            result += `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            result += `${mins}:${secs.toString().padStart(2, '0')}`;
        }
        
        return result;
    }

    function formatFileSize(bytes) {
        if (!bytes) return 'Unknown size';
        
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }

    function showError(message) {
        errorText.textContent = message;
        errorMessage.classList.remove('d-none');
        loadingIndicator.classList.add('d-none');
        videoPreview.classList.add('d-none');
    }

    function clearError() {
        errorMessage.classList.add('d-none');
    }

    // Event listeners
    urlForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const url = videoUrlInput.value.trim();
        if (!url) {
            showError('Please enter a video URL');
            return;
        }
        
        // Clear previous data and show loading indicator
        clearError();
        videoPreview.classList.add('d-none');
        loadingIndicator.classList.remove('d-none');
        fetchBtn.disabled = true;
        
        // Make a request to get video info
        const formData = new FormData();
        formData.append('url', url);
        
        fetch('/get_video_info', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            // Check if response is actually JSON
            const contentType = response.headers.get('Content-Type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Server returned an invalid response. Please try again.');
            }
            
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to fetch video information');
                }).catch(() => {
                    throw new Error('Server error occurred. Please try again.');
                });
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            loadingIndicator.classList.add('d-none');
            fetchBtn.disabled = false;
            
            // Fill in video information
            videoThumbnail.src = data.thumbnail || 'https://via.placeholder.com/480x360?text=No+Thumbnail';
            videoTitle.textContent = data.title || 'Unknown Title';
            videoUploader.textContent = data.uploader || 'Unknown Uploader';
            videoDuration.textContent = formatDuration(data.duration);
            
            // Populate format select
            formatSelect.innerHTML = '';
            
            if (data.formats && data.formats.length > 0) {
                data.formats.forEach(format => {
                    const option = document.createElement('option');
                    option.value = format.format_id;
                    
                    const filesize = format.filesize || format.filesize_approx || 0;
                    const filesizeText = filesize > 0 ? formatFileSize(filesize) : '';
                    
                    // Format display text based on available information
                    let formatText = format.resolution || 'Best Quality';
                    
                    // Add extension if available and not 'auto'
                    if (format.ext && format.ext !== 'auto') {
                        formatText += ` (${format.ext})`;
                    }
                    
                    // Add format note if available
                    if (format.format_note) {
                        formatText += ` - ${format.format_note}`;
                    }
                    
                    // Add filesize if available
                    if (filesizeText) {
                        formatText += ` - ${filesizeText}`;
                    }
                    
                    option.textContent = formatText;
                    formatSelect.appendChild(option);
                    
                    // Set the default selected option to the first one (best quality)
                    if (format.format_id === 'best') {
                        option.selected = true;
                    }
                });
            } else {
                // Add a default option if no formats are available
                const option = document.createElement('option');
                option.value = 'best';
                option.textContent = 'Best quality';
                formatSelect.appendChild(option);
            }
            
            // Set download form values
            downloadUrl.value = url;
            formatId.value = formatSelect.value;
            
            // Show video preview
            videoPreview.classList.remove('d-none');
        })
        .catch(error => {
            fetchBtn.disabled = false;
            showError(error.message || 'An unexpected error occurred');
        });
    });
    
    // Update format ID when format selection changes
    formatSelect.addEventListener('change', function() {
        formatId.value = formatSelect.value;
    });
    
    // Download progress elements
    const downloadProgress = document.getElementById('downloadProgress');
    const downloadStatus = document.getElementById('downloadStatus');
    
    // Improved download handling with error feedback and progress indication
    downloadForm.addEventListener('submit', function(e) {
        e.preventDefault(); // Prevent the default form submission
        
        const downloadButton = this.querySelector('button[type="submit"]');
        downloadButton.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Downloading...';
        downloadButton.disabled = true;
        
        // Show download progress bar
        downloadProgress.classList.remove('d-none');
        downloadStatus.textContent = 'Starting download...';
        
        // Get form data
        const formData = new FormData(this);
        
        // Create a timeout for slow connections
        const timeoutId = setTimeout(() => {
            downloadStatus.textContent = 'Download is taking longer than expected. Please wait...';
        }, 10000); // 10 seconds
        
        // Make AJAX request to download endpoint
        fetch('/download', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                // Clear timeout
                clearTimeout(timeoutId);
                
                // Parse error message from JSON response
                return response.json().then(data => {
                    throw new Error(data.error || 'Download failed');
                });
            }
            
            // Update status
            downloadStatus.textContent = 'Downloading video...';
            
            // For successful response, create a blob and download it
            return response.blob().then(blob => {
                // Clear timeout
                clearTimeout(timeoutId);
                
                // Update status
                downloadStatus.textContent = 'Preparing file for download...';
                
                // Create a blob URL and trigger download
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                
                // Get filename from Content-Disposition header if available
                let filename = 'video';
                const contentDisposition = response.headers.get('Content-Disposition');
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                    if (filenameMatch) {
                        filename = filenameMatch[1];
                    }
                }
                
                // Add file extension based on content type
                const contentType = response.headers.get('Content-Type');
                if (contentType && contentType.includes('video/')) {
                    const ext = contentType.split('/')[1];
                    if (!filename.endsWith(`.${ext}`)) {
                        filename += `.${ext === 'quicktime' ? 'mov' : ext}`;
                    }
                }
                
                // Update status with filename
                downloadStatus.textContent = `Downloading: ${filename}`;
                
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                // Update status
                downloadStatus.textContent = 'Download complete! File saved to your device.';
                
                // Reset button state after a short delay
                setTimeout(() => {
                    downloadButton.innerHTML = '<i class="fas fa-download me-1"></i> Download';
                    downloadButton.disabled = false;
                    downloadProgress.classList.add('d-none');
                }, 3000);
            });
        })
        .catch(error => {
            // Clear timeout
            clearTimeout(timeoutId);
            
            // Show error and reset button
            downloadButton.innerHTML = '<i class="fas fa-download me-1"></i> Download';
            downloadButton.disabled = false;
            downloadProgress.classList.add('d-none');
            showError(error.message || 'An error occurred during download');
        });
    });
    
    // Input validation with visual feedback
    videoUrlInput.addEventListener('input', function() {
        if (this.value.trim()) {
            clearError();
        }
    });
});
