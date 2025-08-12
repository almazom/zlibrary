# Security Guidelines

## 🚨 CRITICAL: Sensitive Files Management

### **NEVER COMMIT TO GIT:**
- ❌ `*.session` files (Telegram session data)
- ❌ `*string_session*.txt` (Authentication tokens)
- ❌ `.env` files (Environment variables)
- ❌ `accounts_config.json` (Z-Library credentials)
- ❌ Any file containing passwords, tokens, or API keys

### **EXPOSED CREDENTIALS SECURITY BREACH:**

**Date**: 2025-08-12  
**Issue**: Telegram session files were accidentally committed to git  
**Impact**: Active Telegram session exposed in repository history  
**Status**: FIXED - Files removed from index and added to .gitignore  

### **Immediate Actions Taken:**
1. ✅ Removed `stable_string_session.txt` from git index
2. ✅ Removed `accounts_config.json` from git index  
3. ✅ Updated `.gitignore` with comprehensive security patterns
4. ✅ Created template files for secure configuration

### **Security Best Practices:**

#### **1. Session Management**
```bash
# Generate new session when needed
python3 telegram_bot/generate_string_session.py

# Store in secure location (NOT in git)
echo "session_string_here" > stable_string_session.txt
```

#### **2. Environment Configuration**
```bash
# Copy template and fill with real values
cp .env.template .env
# Edit .env with your actual credentials
# NEVER commit .env to git
```

#### **3. Account Configuration**
```bash
# Copy template and add real accounts
cp accounts_config.json.template accounts_config.json
# Add your Z-Library account credentials
# NEVER commit accounts_config.json to git
```

### **Git Security Patterns:**

#### **.gitignore Protections**
```
# SECURITY CRITICAL - Sensitive files
*string_session*.txt
*session*.txt
stable_string_session.txt
telegram_bot/stable_string_session.txt
accounts_config.json
*token*
*secret*
*key*
test_results/
account_test_results_*.json
.env
.env.*
```

#### **Pre-commit Checks**
Always run before committing:
```bash
# Check for sensitive patterns
git diff --cached | grep -E "(password|token|session|secret|key)"

# Verify .gitignore is working
git status | grep -E "(session|token|\.env|accounts_config)"
```

### **Credential Rotation Schedule:**

| Credential Type | Rotation Frequency | Last Rotated |
|-----------------|-------------------|--------------|
| Telegram Bot Token | 90 days | TBD |
| String Session | 30 days | 2025-08-12 |
| Z-Library Passwords | 60 days | TBD |
| API Hash/ID | Only if compromised | N/A |

### **Incident Response:**

#### **If Credentials Are Exposed:**
1. 🚨 **Immediate**: Revoke/regenerate exposed credentials
2. 📧 **Notify**: Security team of the breach
3. 🔍 **Audit**: Check git history for other exposures
4. 📝 **Document**: Update this file with incident details
5. 🔄 **Rotate**: All related credentials as precaution

#### **Git History Cleanup:**
```bash
# If sensitive files were committed, use git filter-branch
# WARNING: This rewrites history and affects all clones
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch stable_string_session.txt' \
  --prune-empty --tag-name-filter cat -- --all
```

### **Monitoring:**

#### **Regular Security Audits:**
- Weekly: Check git status for sensitive files
- Monthly: Review .gitignore effectiveness
- Quarterly: Rotate all credentials
- Annually: Full security assessment

#### **Automated Checks:**
```bash
# Add to pre-commit hook
#!/bin/bash
if git diff --cached --name-only | grep -E "(session|token|\.env|accounts_config)"; then
    echo "🚨 SECURITY: Sensitive files detected in commit!"
    exit 1
fi
```

### **Recovery Instructions:**

#### **Session Recovery**
If session files are lost:
1. Run `python3 telegram_bot/generate_string_session.py`
2. Authenticate with phone number
3. Save new session securely (outside git)

#### **Account Recovery**
If accounts_config.json is lost:
1. Copy from `accounts_config.json.template`
2. Re-enter Z-Library credentials
3. Test with `python3 test_all_zlib_accounts.py`

---
**Last Updated**: 2025-08-12  
**Next Review**: 2025-09-12  
**Security Contact**: Project maintainer