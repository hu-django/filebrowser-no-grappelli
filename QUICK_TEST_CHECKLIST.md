# Quick Test Checklist: FileBrowser Upload UI

## Setup
- [ ] Server running: `python manage.py runserver`
- [ ] Admin user logged in
- [ ] Navigate to: `http://localhost:8000/admin/filebrowser/upload/`

## Core Functionality Tests

### Basic Upload
- [ ] Upload new file → Success, redirects to browse
- [ ] File appears in queue correctly
- [ ] Progress bar shows during upload

### File Exists - Without Override
- [ ] Upload existing file (override unchecked)
- [ ] Modal appears: "File 'X' already exists. Do you want to override it?"
- [ ] Click "Cancel" → File removed from queue, original file unchanged
- [ ] Click "Override" → Checkbox auto-checks, upload retries, file replaced


### Override Checkbox
- [ ] Checkbox visible and functional
- [ ] State persists when adding files
- [ ] Each file uses checkbox state at upload time

### Multiple Files
- [ ] Add multiple files to queue
- [ ] Mix of existing/new files
- [ ] Each processes independently
- [ ] Correct status for each file

### Error Handling
- [ ] Server errors handled gracefully
- [ ] No unhandled exceptions shown
- [ ] Error modal appears for FILE_EXISTS errors
- [ ] Retry option works

### UI/UX
- [ ] Modal styling matches Django admin
- [ ] Modal centered with overlay
- [ ] Buttons clearly labeled
- [ ] Clear Queue button works
- [ ] No JavaScript console errors

## Edge Cases
- [ ] Large files (near size limit)
- [ ] Different file types (.jpg, .png, .gif, etc.)
- [ ] Concurrent uploads of same filename

## Browser Compatibility
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (if available)
- [ ] Edge

## Quick Test Script

1. **Setup**: Create test file `test1.jpg`
2. **Test 1**: Upload `test1.jpg` → Should succeed
3. **Test 2**: Upload `test1.jpg` again (override unchecked) → Modal appears
4. **Test 3**: Click "Override" in modal → File replaces, checkbox checks
5. **Test 4**: Clear queue, add multiple files, upload → All process correctly

## Issues Found
1. 
2. 
3. 

