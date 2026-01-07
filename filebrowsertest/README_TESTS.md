# Running FileBrowser Tests

## Quick Start

### Using the test runner script:

```bash
# Run all tests
python run_tests.py

# Run only upload endpoint tests
python run_tests.py upload

# Run only function tests
python run_tests.py functions

# Run with verbose output
python run_tests.py --verbosity=2

# Keep test database (faster for repeated runs)
python run_tests.py --keepdb

# Run specific test class
python run_tests.py app.tests.test_upload_endpoints.FileOverrideTest

# Run specific test method
python run_tests.py app.tests.test_upload_endpoints.FileOverrideTest.test_upload_file_without_override_returns_error
```

### Using Django's manage.py:

```bash
# Run all tests
python manage.py test

# Run all app tests
python manage.py test app.tests

# Run specific test file
python manage.py test app.tests.test_upload_endpoints

# Run specific test class
python manage.py test app.tests.test_upload_endpoints.FileOverrideTest

# Run with options
python manage.py test --verbosity=2 --keepdb
```

## Test Structure

- `app/tests/test_upload_endpoints.py` - Tests for file upload functionality, including override feature
- `app/tests/tests_functions.py` - Tests for filebrowser utility functions

## Test Coverage

The test suite covers:
- File upload with override functionality
- JSON error responses (FILE_EXISTS)
- File replacement when override is enabled
- Edge cases (special characters, unicode filenames, etc.)
- Filebrowser utility functions

## Troubleshooting

If tests fail:
1. Make sure the virtual environment is activated
2. Ensure all dependencies are installed
3. Check that MEDIA_ROOT and STATIC_ROOT are properly configured
4. Verify that the test database can be created

