#!/usr/bin/env python3
"""
Comprehensive Security Audit for Telegram Session Management
Checks current security status and potential vulnerabilities
"""

import os
import subprocess
import glob
from pathlib import Path
import json

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def check_git_ignore_effectiveness():
    """Test if sensitive files are properly ignored"""
    print("🔍 Testing .gitignore effectiveness...")
    
    sensitive_patterns = [
        "stable_string_session.txt",
        "telegram_bot/stable_string_session.txt", 
        ".env",
        "accounts_config.json"
    ]
    
    results = {}
    for pattern in sensitive_patterns:
        stdout, stderr, code = run_command(f"git check-ignore {pattern}")
        if code == 0:
            results[pattern] = "✅ IGNORED"
        else:
            results[pattern] = "🚨 NOT IGNORED"
    
    return results

def find_sensitive_files():
    """Find all potentially sensitive files"""
    print("🔍 Scanning for sensitive files...")
    
    patterns = [
        "*session*.txt",
        "*.session", 
        "*token*",
        "*secret*",
        "*.env",
        "*backup*.tar.gz"
    ]
    
    found_files = []
    for pattern in patterns:
        files = glob.glob(pattern, recursive=False)
        files.extend(glob.glob(f"**/{pattern}", recursive=True))
        found_files.extend(files)
    
    return list(set(found_files))

def check_file_permissions():
    """Check file permissions for sensitive files"""
    print("🔍 Checking file permissions...")
    
    sensitive_files = [
        "stable_string_session.txt",
        "telegram_bot/stable_string_session.txt",
        ".env"
    ]
    
    results = {}
    for file_path in sensitive_files:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            perms = oct(stat.st_mode)[-3:]
            if perms == "600":
                results[file_path] = f"✅ SECURE ({perms})"
            elif perms in ["644", "664"]:
                results[file_path] = f"⚠️ READABLE ({perms})"
            else:
                results[file_path] = f"🚨 UNSAFE ({perms})"
        else:
            results[file_path] = "✅ NOT FOUND"
    
    return results

def check_git_history():
    """Check if sensitive data exists in git history"""
    print("🔍 Scanning git history for sensitive data...")
    
    sensitive_searches = [
        "1ApWapzMBu4P",  # Session token prefix
        "almazomam.*@gmail.com.*tataronrails78",  # Account credentials
        "7956300223:AA",  # Bot token prefix
        "29950132",  # API ID
        "e0bf78283481e2341805e3e4e90d289a"  # API Hash
    ]
    
    results = {}
    for search in sensitive_searches:
        stdout, stderr, code = run_command(f'git rev-list --all | xargs git grep -l "{search}" 2>/dev/null')
        if stdout:
            results[search] = f"🚨 FOUND: {len(stdout.splitlines())} files"
        else:
            results[search] = "✅ NOT FOUND"
    
    return results

def check_backup_contents():
    """Check contents of backup files"""
    print("🔍 Analyzing backup files...")
    
    backup_files = glob.glob("**/*backup*.tar.gz", recursive=True)
    results = {}
    
    for backup in backup_files:
        stdout, stderr, code = run_command(f"tar -tzf {backup} | grep -E '(session\\.txt|\\.env|accounts_config\\.json)'")
        if stdout:
            results[backup] = f"🚨 CONTAINS: {stdout.replace(chr(10), ', ')}"
        else:
            results[backup] = "✅ CLEAN"
    
    return results

def main():
    print("🛡️ COMPREHENSIVE TELEGRAM SESSION SECURITY AUDIT")
    print("=" * 60)
    
    # 1. Git ignore effectiveness
    print("\n1. .GITIGNORE PROTECTION STATUS")
    print("-" * 40)
    ignore_results = check_git_ignore_effectiveness()
    for file, status in ignore_results.items():
        print(f"   {file}: {status}")
    
    # 2. Sensitive files scan
    print("\n2. SENSITIVE FILES DISCOVERED")
    print("-" * 40)
    sensitive_files = find_sensitive_files()
    for file in sensitive_files:
        if os.path.isfile(file):
            size = os.path.getsize(file)
            print(f"   📄 {file} ({size} bytes)")
    
    # 3. File permissions
    print("\n3. FILE PERMISSIONS AUDIT")
    print("-" * 40)
    perm_results = check_file_permissions()
    for file, status in perm_results.items():
        print(f"   {file}: {status}")
    
    # 4. Git history scan
    print("\n4. GIT HISTORY SECURITY SCAN")
    print("-" * 40)
    history_results = check_git_history()
    for search, status in history_results.items():
        print(f"   {search[:20]}...: {status}")
    
    # 5. Backup analysis
    print("\n5. BACKUP FILE SECURITY ANALYSIS")
    print("-" * 40)
    backup_results = check_backup_contents()
    for backup, status in backup_results.items():
        print(f"   {backup}: {status}")
    
    # 6. Overall security score
    print("\n6. SECURITY SCORE CALCULATION")
    print("-" * 40)
    
    total_checks = 0
    passed_checks = 0
    
    # Count ignore checks
    for status in ignore_results.values():
        total_checks += 1
        if "✅" in status:
            passed_checks += 1
    
    # Count history checks  
    for status in history_results.values():
        total_checks += 1
        if "✅" in status:
            passed_checks += 1
    
    # Count backup checks
    for status in backup_results.values():
        total_checks += 1
        if "✅" in status:
            passed_checks += 1
    
    score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    print(f"   Security Score: {score:.1f}% ({passed_checks}/{total_checks} checks passed)")
    
    if score >= 90:
        print("   🟢 EXCELLENT: Strong security posture")
    elif score >= 75:
        print("   🟡 GOOD: Minor security improvements needed") 
    elif score >= 50:
        print("   🟠 FAIR: Significant security gaps exist")
    else:
        print("   🔴 POOR: Critical security vulnerabilities")
    
    # 7. Recommendations
    print("\n7. SECURITY RECOMMENDATIONS")
    print("-" * 40)
    
    recommendations = []
    
    # Check for unprotected files
    for file, status in ignore_results.items():
        if "🚨" in status:
            recommendations.append(f"Add {file} to .gitignore")
    
    # Check for backup issues
    for backup, status in backup_results.items():
        if "🚨" in status:
            recommendations.append(f"Remove sensitive data from {backup}")
    
    # Check for history issues
    for search, status in history_results.items():
        if "🚨" in status:
            recommendations.append(f"Clean git history of {search[:15]}...")
    
    # Check for permission issues
    for file, status in perm_results.items():
        if "🚨" in status or "⚠️" in status:
            recommendations.append(f"Secure permissions for {file} (chmod 600)")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print("   ✅ No immediate security actions required")
    
    print("\n" + "=" * 60)
    print("🛡️ SECURITY AUDIT COMPLETE")

if __name__ == "__main__":
    main()