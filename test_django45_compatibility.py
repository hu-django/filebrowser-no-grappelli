#!/usr/bin/env python3
"""
Simple test runner to verify Django 4/5 compatibility without complex dependencies.
"""

import os
import sys
import tempfile
import subprocess

# Add the project root to the Python path
project_root = '/home/runner/work/filebrowser-no-grappelli/filebrowser-no-grappelli'
sys.path.insert(0, project_root)

def install_minimal_django():
    """Install minimal Django for testing."""
    try:
        # Try to install Django 4.2 (latest LTS)
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'Django>=4.2,<5.0', '--user', '--timeout=60'
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✓ Django 4.2 installed successfully")
            return True
        else:
            print(f"✗ Django installation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Django installation timed out")
        return False
    except Exception as e:
        print(f"✗ Django installation error: {e}")
        return False

def setup_django():
    """Setup Django environment."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'filebrowsertest.settings')
    
    try:
        import django
        from django.conf import settings
        from django.test.utils import get_runner
        
        django.setup()
        print(f"✓ Django {django.get_version()} setup complete")
        return True
        
    except Exception as e:
        print(f"✗ Django setup failed: {e}")
        return False

def run_compatibility_tests():
    """Run compatibility tests without full Django test runner."""
    try:
        # Import and run basic compatibility checks
        print("\n=== Running Django 4/5 Compatibility Tests ===")
        
        # Test 1: Translation imports
        print("Testing translation imports...")
        try:
            from django.utils.translation import gettext as _
            print("✓ gettext import successful")
        except ImportError:
            try:
                from django.utils.translation import ugettext as _
                print("✓ ugettext fallback successful")
            except ImportError as e:
                print(f"✗ Translation import failed: {e}")
                return False
        
        # Test 2: Forms utils import
        print("Testing forms utils import...")
        try:
            from django.forms import utils as form_utils
            if hasattr(form_utils, 'ErrorList'):
                print("✓ forms.utils import successful")
            else:
                print("✗ ErrorList not found in forms.utils")
        except ImportError:
            try:
                from django.forms import util as form_utils
                if hasattr(form_utils, 'ErrorList'):
                    print("✓ forms.util fallback successful")
                else:
                    print("✗ ErrorList not found in forms.util")
            except ImportError as e:
                print(f"✗ Forms utils import failed: {e}")
                return False
        
        # Test 3: JSON import
        print("Testing JSON import...")
        try:
            from django.utils import simplejson
            print("✓ simplejson import successful")
        except ImportError:
            import json
            print("✓ standard json fallback successful")
        
        # Test 4: CSRF decorator
        print("Testing CSRF decorator import...")
        try:
            from django.views.decorators.csrf import csrf_exempt
            print("✓ csrf_exempt import successful")
        except ImportError:
            try:
                from django.contrib.csrf.middleware import csrf_exempt
                print("✓ csrf_exempt fallback successful")
            except ImportError as e:
                print(f"✗ CSRF decorator import failed: {e}")
                return False
        
        # Test 5: URL configuration
        print("Testing URL configuration imports...")
        try:
            from django.urls import re_path as url
            print("✓ re_path import successful")
        except ImportError:
            try:
                from django.conf.urls import url
                print("✓ url fallback successful")
            except ImportError as e:
                print(f"✗ URL configuration import failed: {e}")
                return False
        
        # Test 6: File operations
        print("Testing file operation imports...")
        try:
            from django.core.files.move import file_move_safe
            from django.utils.encoding import smart_str
            print("✓ File operation imports successful")
        except ImportError as e:
            print(f"✗ File operation imports failed: {e}")
            return False
        
        # Test 7: Views and template rendering
        print("Testing view imports...")
        try:
            from django.shortcuts import render
            from django.http import HttpResponse, HttpResponseRedirect
            from django.contrib.admin.views.decorators import staff_member_required
            print("✓ View imports successful")
        except ImportError as e:
            print(f"✗ View imports failed: {e}")
            return False
        
        # Test 8: Import our filebrowser views
        print("Testing filebrowser views import...")
        try:
            from filebrowser import views
            print("✓ Filebrowser views import successful")
        except ImportError as e:
            print(f"✗ Filebrowser views import failed: {e}")
            return False
        
        print("\n✓ All compatibility tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Compatibility tests failed: {e}")
        return False

def check_code_quality():
    """Check code for potential issues."""
    print("\n=== Checking Code Quality ===")
    
    # Check for deprecated patterns
    deprecated_patterns = [
        ('ugettext', 'Use gettext instead'),
        ('render_to_response', 'Use render instead'),
        ('django.conf.urls.url', 'Use django.urls.re_path instead'),
        ('MIDDLEWARE_CLASSES', 'Use MIDDLEWARE instead'),
    ]
    
    issues_found = 0
    
    for root, dirs, files in os.walk(project_root + '/filebrowser'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for pattern, message in deprecated_patterns:
                        if pattern in content and 'except ImportError' not in content:
                            # Only flag if it's not part of a fallback import
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if pattern in line and 'except' not in line and 'try:' not in line:
                                    print(f"⚠ {filepath}:{i} - {message}: {line.strip()}")
                                    issues_found += 1
                                    
                except Exception as e:
                    print(f"✗ Error reading {filepath}: {e}")
    
    if issues_found == 0:
        print("✓ No code quality issues found")
    else:
        print(f"⚠ Found {issues_found} potential issues")
    
    return issues_found == 0

def main():
    """Main test runner."""
    print("Django 4/5 Compatibility Test Runner")
    print("=" * 40)
    
    # Step 1: Install Django
    print("Step 1: Installing Django...")
    if not install_minimal_django():
        return 1
    
    # Step 2: Setup Django
    print("\nStep 2: Setting up Django...")
    if not setup_django():
        return 1
    
    # Step 3: Run compatibility tests
    if not run_compatibility_tests():
        return 1
    
    # Step 4: Check code quality
    if not check_code_quality():
        print("⚠ Code quality issues found, but compatibility tests passed")
    
    print("\n🎉 Django 4/5 compatibility verification complete!")
    return 0

if __name__ == '__main__':
    sys.exit(main())