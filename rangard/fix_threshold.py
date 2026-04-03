with open('app/ml/detector.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Make thresholds stricter so more files get flagged
content = content.replace(
    "if score < 0.15: return 'clean'",
    "if score < 0.08: return 'clean'"
)
content = content.replace(
    "if score < 0.35: return 'low'",
    "if score < 0.25: return 'low'"
)
content = content.replace(
    "if score < 0.55: return 'medium'",
    "if score < 0.45: return 'medium'"
)
content = content.replace(
    "if score < 0.75: return 'high'",
    "if score < 0.65: return 'high'"
)

with open('app/ml/detector.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Thresholds updated - system will be more sensitive now!")