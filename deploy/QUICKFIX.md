# 🚨 URGENT FIX - langchain_community Error

## Problem

```
ERROR - Kesalahan internal: No module named 'langchain_community'
```

## Solution

Di server Azure VM, jalankan:

```bash
ssh viona@<YOUR_VM_IP>

# Jalankan quick fix script
cd /opt/proposal-reviewer/deploy
chmod +x quickfix.sh
sudo ./quickfix.sh
```

## Manual Fix (jika script gagal)

```bash
# 1. Stop service
sudo systemctl stop proposal-reviewer

# 2. Pull latest code
cd /opt/proposal-reviewer
sudo -u viona git pull

# 3. Install dependencies
sudo -u viona bash -c "source venv/bin/activate && pip install pypdf"

# 4. Restart service
sudo systemctl restart proposal-reviewer

# 5. Check logs
sudo journalctl -u proposal-reviewer -f
```

## Test

```bash
# Test endpoint
curl http://localhost:8000/api/kesehatan

# Expected: {"status":"sehat","versi":"1.0.0"}
```

## Root Cause

Aplikasi menggunakan `langchain_community` untuk load PDF, tapi package tidak ada di requirements.txt.

**Fixed by:** Mengganti `langchain_community.document_loaders.PyPDFLoader` dengan `pypdf.PdfReader` yang sudah ada di requirements.
