# UC17: Download Resume Capability

## Feature: Resumable Downloads
As a user with unstable connection
I want to resume interrupted downloads
So that large files can be downloaded reliably

## Background
Given download resume is supported
And partial files are tracked

## Scenario 1: Network Interruption
```gherkin
Given a 50MB EPUB is downloading
And 20MB has been downloaded
When the network connection drops
Then the system should:
  - Save the partial file
  - Record download position
  - Mark as incomplete
When connection restored
Then resume from byte 20,971,520
```

## Scenario 2: Progress Tracking
```gherkin
Given multiple downloads in progress
When checking status
Then show for each download:
  | File | Size | Downloaded | Progress | Speed | ETA |
  | Book1.epub | 10MB | 7.5MB | 75% | 1.2MB/s | 2s |
  | Book2.pdf | 25MB | 5MB | 20% | 500KB/s | 40s |
  | Book3.mobi | 5MB | 5MB | 100% | Complete | - |
```

## Scenario 3: Checksum Validation
```gherkin
Given a download completes
When validating integrity
Then:
  - Calculate MD5/SHA256 checksum
  - Compare with server checksum
  - If mismatch, mark corrupted
  - Offer re-download option
```

## Scenario 4: Concurrent Downloads
```gherkin
Given bandwidth limit of 5MB/s
When downloading 3 files simultaneously
Then:
  - Distribute bandwidth fairly
  - Each gets ~1.67MB/s
  - Adjust dynamically as downloads complete
  - Prevent bandwidth exhaustion
```

## Implementation Design

### 1. Download State Management
```python
class DownloadState:
    def __init__(self, url, file_path):
        self.url = url
        self.file_path = file_path
        self.total_size = 0
        self.downloaded = 0
        self.status = 'pending'  # pending, downloading, paused, complete, error
        self.chunks = []
        self.checksum = None
        self.start_time = None
        self.resume_count = 0
```

### 2. Resume Headers
```python
headers = {
    'Range': f'bytes={downloaded_bytes}-',
    'If-Range': etag,  # Ensure file hasn't changed
    'Accept-Encoding': 'identity'  # No compression for resume
}
```

### 3. Chunk Management
```python
CHUNK_SIZE = 1024 * 1024  # 1MB chunks

async def download_with_resume(url, file_path):
    state = load_state(file_path)
    
    headers = {}
    if state.downloaded > 0:
        headers['Range'] = f'bytes={state.downloaded}-'
    
    async with session.get(url, headers=headers) as response:
        if response.status == 206:  # Partial content
            print(f"Resuming from byte {state.downloaded}")
        
        with open(file_path, 'ab' if state.downloaded else 'wb') as f:
            async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                f.write(chunk)
                state.downloaded += len(chunk)
                save_state(state)
                update_progress(state)
```

### 4. Progress Tracking
```python
class ProgressTracker:
    def __init__(self):
        self.downloads = {}
        
    def update(self, file_id, downloaded, total):
        now = time.time()
        if file_id in self.downloads:
            elapsed = now - self.downloads[file_id]['last_update']
            bytes_delta = downloaded - self.downloads[file_id]['downloaded']
            speed = bytes_delta / elapsed if elapsed > 0 else 0
            eta = (total - downloaded) / speed if speed > 0 else 0
        else:
            speed = 0
            eta = 0
            
        self.downloads[file_id] = {
            'downloaded': downloaded,
            'total': total,
            'progress': (downloaded / total * 100) if total > 0 else 0,
            'speed': speed,
            'eta': eta,
            'last_update': now
        }
```

### 5. Checksum Validation
```python
import hashlib

async def validate_download(file_path, expected_checksum):
    hash_md5 = hashlib.md5()
    hash_sha256 = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
            hash_sha256.update(chunk)
    
    return {
        'md5': hash_md5.hexdigest(),
        'sha256': hash_sha256.hexdigest(),
        'valid': hash_md5.hexdigest() == expected_checksum
    }
```

## Success Criteria
- ✅ Downloads resume from exact byte position
- ✅ Progress tracked accurately
- ✅ Checksums validate correctly
- ✅ Concurrent downloads managed
- ✅ Bandwidth limits respected

## Performance Metrics
- Resume overhead: <100ms
- Chunk size: 1MB optimal
- Max concurrent: 5 downloads
- Bandwidth efficiency: >95%
- Checksum speed: >50MB/s