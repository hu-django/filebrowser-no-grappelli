# Manual Test Plan: FileBrowser Upload UI

## Test Environment Setup

### Prerequisites
1. Start the Django development server:
   ```bash
   cd /home/andriyg/src/projects/hu_django/filebrowser-no-grappelli/filebrowsertest
   source /home/andriyg/src/projects/hu_django/.pyenv/bin/activate
   python manage.py runserver
   ```

2. Access the admin interface:
   - URL: `http://localhost:8000/admin/`
   - Create a superuser if needed: `python manage.py createsuperuser`
   - Login with admin credentials

3. Navigate to FileBrowser:
   - URL: `http://localhost:8000/admin/filebrowser/browse/`
   - Or click on "FileBrowser" in the admin interface

4. Prepare test files:
   - Create a few test image files (e.g., `test1.jpg`, `test2.png`)
   - Create a test text file (e.g., `test.txt`)
   - Note: FileBrowser may convert filenames (lowercase, spaces to underscores)

---

## Test Cases

### TC-1: Basic File Upload (New File)

**Objective**: Verify that uploading a new file works correctly.

**Steps**:
1. Navigate to FileBrowser upload page: `http://localhost:8000/admin/filebrowser/upload/`
2. Click "BROWSE" button
3. Select a file that doesn't exist in the media directory (e.g., `newfile.jpg`)
4. Verify the file appears in the upload queue
5. Click "Upload" button
6. Wait for upload to complete

**Expected Results**:
- ✅ File appears in the queue with filename displayed
- ✅ Progress bar shows upload progress
- ✅ After completion, shows "Completed" status
- ✅ Page redirects to browse page
- ✅ File appears in the file list
- ✅ File can be opened/viewed correctly

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

### TC-2: Upload File That Already Exists (Without Override)

**Objective**: Verify that uploading an existing file shows error modal when override is not checked.

**Prerequisites**:
- Upload a file first (e.g., `existing.jpg`) using TC-1

**Steps**:
1. Navigate to upload page
2. Ensure "Override existing files" checkbox is **NOT checked**
3. Click "BROWSE" and select the same file (`existing.jpg`)
4. Click "Upload" button

**Expected Results**:
- ✅ File appears in queue
- ✅ During upload, a modal popup appears with message: "File 'existing.jpg' already exists. Do you want to override it?"
- ✅ Modal has two buttons: "Cancel" and "Override"
- ✅ Modal has proper styling (Django admin-style)
- ✅ If "Cancel" is clicked:
  - Modal closes
  - File is removed from queue or marked as error
  - File is NOT replaced
- ✅ If "Override" is clicked:
  - Modal closes
  - Override checkbox becomes checked
  - Upload retries automatically
  - File is replaced successfully

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

### TC-3: Override Checkbox Functionality

**Objective**: Verify the override checkbox works correctly and persists state.

**Steps**:
1. Navigate to upload page
2. Verify "Override existing files" checkbox is visible and unchecked by default
3. Check the checkbox
4. Add a file to queue
5. Uncheck the checkbox
6. Add another file to queue
7. Upload both files (one with override, one without)

**Expected Results**:
- ✅ Checkbox is visible and accessible
- ✅ Checkbox state persists when adding files to queue
- ✅ Each file upload uses the checkbox state at upload time
- ✅ Files upload according to their respective override settings

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

### TC-4: Modal Popup - Cancel Action

**Objective**: Verify cancel action in file exists modal works correctly.

**Prerequisites**:
- Have an existing file (e.g., `cancel_test.jpg`)

**Steps**:
1. Navigate to upload page
2. Ensure override checkbox is **NOT checked**
3. Upload `cancel_test.jpg`
4. When modal appears, click "Cancel" button
5. Verify file state

**Expected Results**:
- ✅ Modal closes immediately
- ✅ File is removed from queue OR marked with error message
- ✅ Original file remains unchanged
- ✅ No file replacement occurs
- ✅ User can continue with other uploads

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

### TC-5: Modal Popup - Override Action

**Objective**: Verify override action in file exists modal works correctly.

**Prerequisites**:
- Have an existing file (e.g., `override_test.jpg`) with known content

**Steps**:
1. Navigate to upload page
2. Ensure override checkbox is **NOT checked**
3. Upload a new version of `override_test.jpg` (with different content)
4. When modal appears, click "Override" button
5. Verify file replacement

**Expected Results**:
- ✅ Modal closes immediately
- ✅ Override checkbox becomes checked automatically
- ✅ Upload retries automatically
- ✅ File is replaced with new content
- ✅ Success message or completion status shown
- ✅ New file content is correct when viewed

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

### TC-6: Multiple Files Upload - Mixed Scenarios

**Objective**: Verify handling of multiple files with different override states.

**Prerequisites**:
- Create two existing files: `file1.jpg` and `file2.jpg`
- Prepare two new files: `file3.jpg` and `file4.jpg`

**Steps**:
1. Navigate to upload page
2. Check "Override existing files" checkbox
3. Add `file1.jpg` (existing) to queue
4. Uncheck "Override existing files" checkbox
5. Add `file2.jpg` (existing) to queue
6. Add `file3.jpg` (new) to queue
7. Check "Override existing files" checkbox
8. Add `file4.jpg` (new) to queue
9. Click "Upload"

**Expected Results**:
- ✅ All files appear in queue
- ✅ `file1.jpg`: Uploads and replaces (override checked)
- ✅ `file2.jpg`: Shows modal, user can choose
- ✅ `file3.jpg`: Uploads normally (new file, no override needed)
- ✅ `file4.jpg`: Uploads normally (new file, override checked but not needed)
- ✅ Each file processes independently
- ✅ Queue shows correct status for each file

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

### TC-7: Error Handling - Server Error Recovery

**Objective**: Verify error handling when server returns FILE_EXISTS error during upload.

**Prerequisites**:
- Have an existing file (e.g., `error_test.jpg`)

**Steps**:
1. Navigate to upload page
2. Ensure override checkbox is **NOT checked**
3. Upload `error_test.jpg`
4. Observe error handling

**Expected Results**:
- ✅ If error occurs during upload (not caught by pre-check):
  - Error is caught and handled gracefully
  - Modal appears with retry option
  - User can choose to override or cancel
  - No unhandled server error is shown
  - Page remains functional

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

### TC-8: Clear Queue Functionality

**Objective**: Verify "Clear Queue" button works correctly.

**Steps**:
1. Navigate to upload page
2. Add multiple files to queue
3. Check/uncheck override checkbox
4. Click "Clear Queue" link
5. Verify queue state

**Expected Results**:
- ✅ All files are removed from queue
- ✅ Checkbox state is preserved (not reset)
- ✅ User can add new files after clearing
- ✅ No errors occur

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

### TC-9: Modal Styling and UX

**Objective**: Verify modal popup has proper styling and user experience.

**Steps**:
1. Trigger file exists modal (upload existing file without override)
2. Observe modal appearance and behavior

**Expected Results**:
- ✅ Modal has Django admin-style appearance
- ✅ Modal is centered on screen
- ✅ Modal has semi-transparent overlay background
- ✅ Modal text is readable and properly formatted
- ✅ Buttons are clearly labeled ("Cancel", "Override")
- ✅ Modal can be closed by clicking overlay (optional)
- ✅ Modal is responsive and looks good on different screen sizes

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

### TC-10: Concurrent Upload Attempts

**Objective**: Verify behavior when multiple files with same name are uploaded.

**Steps**:
1. Navigate to upload page
2. Add `concurrent.jpg` to queue (new file)
3. Add `concurrent.jpg` again to queue
4. Upload both

**Expected Results**:
- ✅ Queue shows both files (or replaces first with second)
- ✅ Upload handles duplicates correctly
- ✅ No JavaScript errors occur
- ✅ Files process correctly

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

### TC-11: Large File Upload

**Objective**: Verify upload works with larger files.

**Steps**:
1. Navigate to upload page
2. Upload a file close to MAX_UPLOAD_SIZE limit
3. Verify upload behavior

**Expected Results**:
- ✅ File uploads successfully if under limit
- ✅ Error message shown if file exceeds limit
- ✅ Progress bar shows progress for large files
- ✅ Override functionality works with large files

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

### TC-12: Image File Types

**Objective**: Verify upload works with different image file types.

**Steps**:
1. Upload files with extensions: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`
2. Verify each uploads correctly
3. Test override with each type

**Expected Results**:
- ✅ All supported image types upload successfully
- ✅ Override works with all image types
- ✅ Files are accessible after upload

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

### TC-13: Browser Compatibility

**Objective**: Verify upload UI works in different browsers.

**Browsers to Test**:
- Chrome/Chromium
- Firefox
- Safari (if available)
- Edge

**Steps**:
1. Open upload page in each browser
2. Perform TC-2 (file exists without override - modal test)
3. Verify modal appears and works correctly

**Expected Results**:
- ✅ Upload functionality works in all browsers
- ✅ Modal appears and functions correctly
- ✅ No JavaScript errors in console
- ✅ Styling is consistent across browsers

**Status**: ⬜ Pass / ⬜ Fail / ⬜ N/A

**Notes**:

---

## Test Summary

### Test Execution Date: _______________
### Tester Name: _______________

### Results Summary:
- Total Test Cases: 13
- Passed: ___
- Failed: ___
- Not Applicable: ___
- Pass Rate: ___%

### Critical Issues Found:
1. 
2. 
3. 

### Minor Issues Found:
1. 
2. 
3. 

### Recommendations:
1. 
2. 
3. 

---

## Quick Reference

### Access URLs:
- Admin Login: `http://localhost:8000/admin/`
- FileBrowser Browse: `http://localhost:8000/admin/filebrowser/browse/`
- FileBrowser Upload: `http://localhost:8000/admin/filebrowser/upload/`

### Test File Naming Convention:
- New files: `test_new_[number].jpg`
- Existing files: `test_existing_[number].jpg`
- Override tests: `test_override_[number].jpg`

### Common Issues to Watch For:
- JavaScript console errors
- Modal not appearing
- Override checkbox not working
- File not replacing when override is checked
- Error messages not user-friendly
- Page redirects not working after upload

---

## Notes Section

Use this space for additional observations, screenshots, or issues discovered during testing:

