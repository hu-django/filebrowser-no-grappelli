#!/usr/bin/env python
"""
Test runner script for filebrowser tests.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py upload             # Run only upload endpoint tests
    python run_tests.py functions         # Run only function tests
    python run_tests.py --verbosity=2      # Run with verbose output
    python run_tests.py --keepdb          # Keep test database
"""

import os
import sys

if __name__ == "__main__":
    # Add the project root to the path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "filebrowsertest.settings")
    
    import django
    django.setup()
    
    from django.core.management import call_command
    from django.test.utils import get_runner
    from django.conf import settings
    
    # Parse command line arguments
    test_labels = []
    test_options = []
    
    for arg in sys.argv[1:]:
        if arg.startswith('--'):
            test_options.append(arg)
        elif arg in ['upload', 'functions']:
            # Map shorthand to full test paths
            if arg == 'upload':
                test_labels.append('app.tests.test_upload_endpoints')
            elif arg == 'functions':
                test_labels.append('app.tests.tests_functions')
        else:
            test_labels.append(arg)
    
    # Default to all tests if none specified
    if not test_labels:
        test_labels = ['app.tests']
    
    # Build test command
    test_args = test_labels + test_options
    
    print("=" * 70)
    print("Running filebrowser tests")
    print("=" * 70)
    print(f"Test labels: {test_labels}")
    print(f"Options: {test_options}")
    print("=" * 70)
    print()
    
    # Run tests
    try:
        call_command('test', *test_args, verbosity=2)
    except SystemExit:
        # Django test command exits with SystemExit, which is normal
        pass

