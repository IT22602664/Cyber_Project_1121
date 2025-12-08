# Quick Start Guide - Mouse Movement Analysis

## 🚀 Getting Started (3 Simple Steps)

### Step 1: Install Dependencies
```bash
cd "Mouse Movement Analysis"
pip install -r requirements.txt
```

### Step 2: Train the Model
```bash
python train.py
```

**What to expect**:
- Training will take ~10-15 minutes
- You should see loss values decreasing (NOT `nan`)
- Best model will be saved to `models/checkpoints/best_model.pth`
- Training history plot saved to `logs/training_history.png`

**Good training output**:
```
Epoch 1/100: 100%|████████| 811/811 [00:29<00:00, 27.46it/s, loss=0.8234]
Epoch 1/100 - Train Loss: 0.8234, Val Loss: 0.7123
New best model saved! Val Loss: 0.7123
```

**Bad training output** (if you see this, see Troubleshooting below):
```
Epoch 1/100: 100%|████████| 811/811 [00:29<00:00, 27.46it/s, loss=nan]
Epoch 1/100 - Train Loss: nan, Val Loss: nan
```

### Step 3: Test the Model
```bash
python test.py
```

**Expected output**:
```
======================================================================
MOUSE MOVEMENT ANALYSIS - TEST RESULTS
======================================================================
Dataset: Balabit Mouse Dynamics Challenge
Total Samples: 8500
Genuine Samples: 7500 (88.2%)
Impostor Samples: 1000 (11.8%)
----------------------------------------------------------------------
PERFORMANCE METRICS:
----------------------------------------------------------------------
Accuracy:   0.8750 (87.50%)
Precision:  0.8923 (89.23%)
Recall:     0.8654 (86.54%)
F1 Score:   0.8787 (87.87%)
AUC:        0.9234 (92.34%)
EER:        0.1250 (12.50%)
----------------------------------------------------------------------
INTERPRETATION:
----------------------------------------------------------------------
✓ EXCELLENT: Accuracy meets target (≥85%)
✓ EXCELLENT: EER meets target (≤15%)
✓ EXCELLENT: AUC meets target (≥0.85%)
======================================================================
Results saved to: logs
======================================================================
```

---

## 📊 Understanding the Metrics

### Accuracy
- **What it is**: Percentage of correct predictions
- **Target**: ≥85%
- **Interpretation**: 
  - ≥85% = Excellent
  - 75-85% = Good
  - <75% = Needs improvement

### Precision
- **What it is**: Of all predicted genuine users, how many were actually genuine
- **Formula**: True Positives / (True Positives + False Positives)
- **Target**: ≥85%

### Recall
- **What it is**: Of all actual genuine users, how many were correctly identified
- **Formula**: True Positives / (True Positives + False Negatives)
- **Target**: ≥85%

### F1 Score
- **What it is**: Harmonic mean of precision and recall
- **Formula**: 2 × (Precision × Recall) / (Precision + Recall)
- **Target**: ≥85%

### AUC (Area Under Curve)
- **What it is**: Overall model quality (0.0 to 1.0)
- **Target**: ≥0.85
- **Interpretation**:
  - 0.9-1.0 = Excellent
  - 0.8-0.9 = Good
  - 0.7-0.8 = Fair
  - <0.7 = Poor

### EER (Equal Error Rate)
- **What it is**: Point where false accept rate = false reject rate
- **Target**: ≤15%
- **Interpretation**: Lower is better

---

## 🔧 Troubleshooting

### Problem 1: NaN Losses During Training

**Symptoms**:
```
Epoch 1/100 - Train Loss: nan, Val Loss: nan
```

**Solution**:
```bash
# 1. Run diagnostic tool
python diagnose_data.py

# 2. Check for data issues in output
# 3. If issues found, the fixes in the code should handle them
# 4. If still failing, reduce learning rate in config.yaml:
#    learning_rate: 0.00001  # Even lower
```

### Problem 2: ValueError - Scaler not fitted

**Symptoms**:
```
ValueError: Scaler not fitted. Call with fit=True first.
```

**Solution**:
```bash
# This means you're using an old checkpoint without the scaler
# Re-run training to create a new checkpoint with the scaler:
python train.py

# The new checkpoint will include the fitted scaler
```

### Problem 3: FileNotFoundError - best_model.pth not found

**Symptoms**:
```
FileNotFoundError: Checkpoint not found: models/checkpoints\best_model.pth
```

**Solution**:
```bash
# This means training didn't complete successfully
# Re-run training:
python train.py

# The test script will now automatically use the latest checkpoint if best_model.pth is missing
```

### Problem 3: Low Accuracy (<75%)

**Possible causes**:
- Not enough training epochs
- Learning rate too high or too low
- Data quality issues

**Solutions**:
1. Train for more epochs (edit `config.yaml`: `epochs: 200`)
2. Adjust learning rate (try `0.0001` or `0.00001`)
3. Check data with `python diagnose_data.py`

### Problem 4: Out of Memory

**Symptoms**:
```
RuntimeError: CUDA out of memory
```

**Solution**:
Edit `config.yaml`:
```yaml
batch_size: 16  # Reduce from 32
```

---

## 📁 Output Files

After training and testing, you'll have:

```
Mouse Movement Analysis/
├── models/
│   └── checkpoints/
│       ├── best_model.pth          # Best model (lowest val loss)
│       ├── checkpoint_epoch_10.pth # Checkpoint at epoch 10
│       ├── checkpoint_epoch_20.pth # Checkpoint at epoch 20
│       └── ...
├── logs/
│   ├── training_history.png        # Loss curves
│   ├── test_results.txt            # Detailed test results
│   ├── roc_curve.png              # ROC curve visualization
│   ├── score_distribution.png     # Score histograms
│   └── training_YYYY-MM-DD.log    # Training logs
└── templates/
    └── user_*.pkl                  # User behavioral templates
```

---

## 🎯 Next Steps

After successful training and testing:

### 1. Start the API Server
```bash
# Windows:
start_api.bat

# Linux/Mac:
./start_api.sh
```

### 2. Test the API
```bash
# Open browser to:
http://localhost:8003/docs

# Or test with curl:
curl http://localhost:8003/health
```

### 3. Integrate with Your MERN Stack
See `DOCUMENTATION.md` for complete integration guide with React and Node.js examples.

---

## 📚 Additional Resources

- **DOCUMENTATION.md** - Complete technical documentation
- **FIXES_APPLIED.md** - Details of all fixes applied
- **PROJECT_EXPLANATION.md** - Simple explanation of the project
- **IMPLEMENTATION_SUMMARY.md** - Quick reference

---

## ✅ Checklist

Before deploying to production:

- [ ] Training completed without NaN losses
- [ ] Accuracy ≥ 75% (target: ≥85%)
- [ ] EER ≤ 25% (target: ≤15%)
- [ ] AUC ≥ 0.75 (target: ≥0.85%)
- [ ] API server starts successfully
- [ ] Health check endpoint responds
- [ ] Integration tested with frontend

---

## 🆘 Need Help?

1. Check `FIXES_APPLIED.md` for common issues
2. Run `python diagnose_data.py` to check data
3. Review logs in `logs/` directory
4. Check `DOCUMENTATION.md` for detailed explanations

---

**Good luck! 🚀**

