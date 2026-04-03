# Training RANGARD on Real Ransomware Samples

## Quick Start

### Step 1: Collect Real Samples (Choose One)

**Option A: From MalwareBazaar (Recommended)**
```bash
# Get free API key from https://bazaar.abuse.ch/api/
# Register → Generate API key

python scripts/download_real_samples.py \
  --bazaar-api-key YOUR_API_KEY \
  --num-ransomware 100 \
  --num-clean 200
```

**Option B: Use Existing Samples**
```bash
# If you already have samples, organize them:
# data/real_samples/
# ├── clean/
# │   ├── file1.exe
# │   ├── file2.pdf
# │   └── ...
# └── ransomware/
#     ├── ransom_sample1.bin
#     ├── ransom_sample2.bin
#     └── ...
```

**Option C: Collect from System (Safe)**
```bash
# Collects real Windows/Program Files (no malware)
python scripts/download_real_samples.py \
  --collect-clean-only \
  --num-clean 200
```

---

### Step 2: Train the Model

```bash
python scripts/train_real_model.py train \
  --clean-dir data/real_samples/clean \
  --ransom-dir data/real_samples/ransomware \
  --save-report
```

**Output:**
- `app/ml/model/ransomware_rf.joblib` - Trained model
- `app/ml/model/ransomware_rf_report.json` - Training metrics

---

### Step 3: Evaluate the Model

```bash
# View feature importances
python scripts/train_real_model.py eval
```

---

### Step 4: Test Detection

```bash
# Test on a single file
python scripts/train_real_model.py test \
  --file path/to/your/file.exe
```

---

## Getting Real Samples

### MalwareBazaar (Recommended ⭐)
- **Website:** https://bazaar.abuse.ch/
- **What:** Free malware samples (500+ families)
- **How:** 
  1. Create free account
  2. Generate API key in settings
  3. Use script above

### Alternative Sources
- **VirusTotal:** https://virustotal.com (requires API key)
- **TheZoo:** https://github.com/ytisf/theZoo (educational)
- **System Files:** Use your own Windows/Program Files

---

## Safety Guidelines

✅ **Safe Operations**
- Reading files as binary (no execution)
- Feature extraction (statistical analysis)
- Training ML models
- All in isolated environment

❌ **Never Do**
- Execute malware samples
- Copy to shared network
- Remove from isolated directory
- Share across machines

---

## Expected Results

With **150+ real samples**, you should see:
- **Accuracy:** 85-95% on test set
- **False positives:** < 5%
- **Detection speed:** ~50-100ms per file
- **Top features:**
  1. Entropy (randomness)
  2. Ransomware strings
  3. PE header characteristics
  4. Byte distribution

---

## Troubleshooting

**"No samples found"**
```bash
# Check directory contents
ls -la data/real_samples/clean/
ls -la data/real_samples/ransomware/
```

**"Not enough samples"**
- Need minimum 10 total samples (5+ per class recommended)
- Download more from MalwareBazaar or collect from system

**"API connection failed"**
- Verify API key is correct
- Check internet connection
- Try again in a few minutes

**"File too large"**
- Script automatically skips files > 100MB
- This is normal for system files

---

## Model Performance Tips

1. **More samples = Better accuracy**
   - 50+ samples: Good
   - 100+ samples: Very good
   - 500+ samples: Excellent

2. **Balanced dataset**
   - Aim for ~equal clean and ransomware files
   - Current script collects 200 clean, 100 ransomware

3. **Diverse sample types**
   - Mix of PE executables, documents, archives
   - Different ransomware families
   - Real-world file patterns

4. **Regular retraining**
   - Retrain monthly with new samples
   - Adapt to emerging ransomware families
   - Improve false positive rates

---

## Next Steps

1. ✅ Collect real samples (15 minutes)
2. ✅ Train model (5-10 minutes)
3. ✅ Evaluate metrics (1 minute)
4. ✅ Test on your files (ongoing)
5. Restart backend to use new model
   ```bash
   # Kill old backend
   taskkill /F /IM python.exe
   
   # Restart
   python c:\Users\abc\Desktop\Rangard\rangard\run.py
   ```

---

## Questions?

- Check logs: `app/ml/model/ransomware_rf_report.json`
- Feature list: `app/ml/detector.py` (FEATURE_COLUMNS)
- Sample code: `scripts/train_real_model.py`
