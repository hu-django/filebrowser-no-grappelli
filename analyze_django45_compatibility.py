#!/usr/bin/env python3
"""
Manual Django 4/5 compatibility analysis without installing packages.
"""

import os
import re
import sys

def analyze_file_for_compatibility_issues(filepath):
    """Analyze a Python file for Django 4/5 compatibility issues."""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Define patterns to check
        patterns = {
            'ugettext_usage': {
                'pattern': r'ugettext(?!.*except ImportError)',
                'message': 'ugettext is deprecated in Django 4+, should use gettext',
                'severity': 'warning'
            },
            'ugettext_lazy_usage': {
                'pattern': r'ugettext_lazy(?!.*except ImportError)',
                'message': 'ugettext_lazy is deprecated in Django 4+, should use gettext_lazy',
                'severity': 'warning'
            },
            'render_to_response_usage': {
                'pattern': r'render_to_response\(',
                'message': 'render_to_response is deprecated, should use render',
                'severity': 'warning'
            },
            'django_conf_urls': {
                'pattern': r'from django\.conf\.urls import url',
                'message': 'django.conf.urls.url is deprecated, should use django.urls.re_path',
                'severity': 'warning'
            },
            'smart_unicode_usage': {
                'pattern': r'smart_unicode',
                'message': 'smart_unicode is deprecated, should use smart_str',
                'severity': 'error'
            },
            'simplejson_usage': {
                'pattern': r'from django\.utils import simplejson',
                'message': 'django.utils.simplejson is deprecated, should use standard json',
                'severity': 'info'
            },
            'forms_util_usage': {
                'pattern': r'from django\.forms import util(?!.*except ImportError)',
                'message': 'django.forms.util is deprecated, should use django.forms.utils',
                'severity': 'warning'
            }
        }
        
        for line_num, line in enumerate(lines, 1):
            for check_name, check_info in patterns.items():
                if re.search(check_info['pattern'], line):
                    # Check if this is part of a try/except compatibility block
                    context_start = max(0, line_num-5)
                    context_end = min(len(lines), line_num+3)
                    context_lines = lines[context_start:context_end]
                    
                    # Look for try/except patterns in the surrounding context
                    has_try_except = any('try:' in l or 'except ImportError' in l for l in context_lines)
                    is_fallback_line = 'except ImportError' in line or '# Django 3 fallback' in line
                    
                    if has_try_except or is_fallback_line:
                        # This is likely a compatibility shim, which is good
                        continue
                    
                    issues.append({
                        'file': filepath,
                        'line': line_num,
                        'code': line.strip(),
                        'message': check_info['message'],
                        'severity': check_info['severity'],
                        'check': check_name
                    })
        
    except Exception as e:
        issues.append({
            'file': filepath,
            'line': 0,
            'code': '',
            'message': f'Error reading file: {e}',
            'severity': 'error',
            'check': 'file_read_error'
        })
    
    return issues

def analyze_settings_compatibility(settings_path):
    """Analyze Django settings for compatibility issues."""
    issues = []
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for MIDDLEWARE vs MIDDLEWARE_CLASSES
        if 'MIDDLEWARE_CLASSES' in content and 'MIDDLEWARE' not in content:
            issues.append({
                'file': settings_path,
                'message': 'MIDDLEWARE_CLASSES is deprecated, should use MIDDLEWARE',
                'severity': 'warning',
                'check': 'middleware_setting'
            })
        
        # Check for DEFAULT_AUTO_FIELD
        if 'DEFAULT_AUTO_FIELD' not in content:
            issues.append({
                'file': settings_path,
                'message': 'DEFAULT_AUTO_FIELD should be set for Django 3.2+',
                'severity': 'info',
                'check': 'default_auto_field'
            })
        
        # Check TEMPLATES setting structure
        if 'TEMPLATE_DIRS' in content or 'TEMPLATE_LOADERS' in content:
            issues.append({
                'file': settings_path,
                'message': 'Old template settings detected, should use TEMPLATES',
                'severity': 'error',
                'check': 'template_settings'
            })
        
    except Exception as e:
        issues.append({
            'file': settings_path,
            'message': f'Error reading settings: {e}',
            'severity': 'error',
            'check': 'settings_read_error'
        })
    
    return issues

def check_compatibility_shims(filepath):
    """Check if file has proper compatibility shims."""
    compatibility_patterns = [
        r'try:\s*from django\.utils\.translation import gettext',
        r'except ImportError:\s*from django\.utils\.translation import ugettext',
        r'try:\s*from django\.forms import utils',
        r'except ImportError.*from django\.forms import util',
        r'try:\s*from django\.utils import simplejson',
        r'except ImportError.*import json',
    ]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        shims_found = 0
        for pattern in compatibility_patterns:
            if re.search(pattern, content, re.MULTILINE | re.DOTALL):
                shims_found += 1
        
        return shims_found
        
    except Exception:
        return 0

def main():
    """Main analysis function."""
    print("Django 4/5 Compatibility Analysis")
    print("=" * 40)
    
    project_root = '/home/runner/work/filebrowser-no-grappelli/filebrowser-no-grappelli'
    
    # Files to analyze
    files_to_check = []
    
    # Find all Python files in filebrowser
    for root, dirs, files in os.walk(os.path.join(project_root, 'filebrowser')):
        for file in files:
            if file.endswith('.py'):
                files_to_check.append(os.path.join(root, file))
    
    # Add settings file
    settings_file = os.path.join(project_root, 'filebrowsertest', 'settings.py')
    if os.path.exists(settings_file):
        files_to_check.append(settings_file)
    
    all_issues = []
    shim_count = 0
    
    print(f"Analyzing {len(files_to_check)} files...")
    
    for filepath in files_to_check:
        print(f"  Checking {os.path.relpath(filepath, project_root)}...")
        
        if filepath.endswith('settings.py'):
            issues = analyze_settings_compatibility(filepath)
        else:
            issues = analyze_file_for_compatibility_issues(filepath)
            shim_count += check_compatibility_shims(filepath)
        
        all_issues.extend(issues)
    
    # Report results
    print(f"\nAnalysis Results:")
    print(f"=" * 20)
    
    # Group issues by severity
    by_severity = {'error': [], 'warning': [], 'info': []}
    for issue in all_issues:
        by_severity[issue['severity']].append(issue)
    
    # Report errors
    if by_severity['error']:
        print(f"\n❌ ERRORS ({len(by_severity['error'])}):")
        for issue in by_severity['error']:
            print(f"  {os.path.relpath(issue['file'], project_root)}:{issue.get('line', '?')}")
            print(f"    {issue['message']}")
            if issue.get('code'):
                print(f"    Code: {issue['code']}")
    
    # Report warnings
    if by_severity['warning']:
        print(f"\n⚠️  WARNINGS ({len(by_severity['warning'])}):")
        for issue in by_severity['warning']:
            print(f"  {os.path.relpath(issue['file'], project_root)}:{issue.get('line', '?')}")
            print(f"    {issue['message']}")
            if issue.get('code'):
                print(f"    Code: {issue['code']}")
    
    # Report info
    if by_severity['info']:
        print(f"\n💡 INFO ({len(by_severity['info'])}):")
        for issue in by_severity['info']:
            print(f"  {os.path.relpath(issue['file'], project_root)}:{issue.get('line', '?')}")
            print(f"    {issue['message']}")
    
    # Report compatibility shims
    print(f"\n✅ COMPATIBILITY:")
    print(f"  Found {shim_count} compatibility shims")
    
    # Overall assessment
    print(f"\n📊 SUMMARY:")
    print(f"  Files analyzed: {len(files_to_check)}")
    print(f"  Errors: {len(by_severity['error'])}")
    print(f"  Warnings: {len(by_severity['warning'])}")
    print(f"  Info: {len(by_severity['info'])}")
    print(f"  Compatibility shims: {shim_count}")
    
    # Recommendations
    print(f"\n📋 RECOMMENDATIONS:")
    
    if by_severity['error']:
        print("  🔴 CRITICAL: Fix errors before upgrading to Django 4/5")
    elif by_severity['warning']:
        print("  🟡 MODERATE: Address warnings for better Django 4/5 compatibility")
    else:
        print("  🟢 GOOD: No critical issues found")
    
    if shim_count > 0:
        print("  ✅ Compatibility shims are present - good for gradual migration")
    else:
        print("  ⚠️ No compatibility shims found - may cause issues during upgrade")
    
    print("\n🎯 NEXT STEPS:")
    print("  1. Run unit tests for upload endpoints")
    print("  2. Test admin UI manually")
    print("  3. Consider upgrading Django version constraints")
    print("  4. Test with Django 5.x in development environment")
    
    return 0 if not by_severity['error'] else 1

if __name__ == '__main__':
    sys.exit(main())