import sqlite3
import os
import re
from datetime import datetime

# --- Config ---
DESKTOP = os.path.expanduser("~/Desktop")
STICKY_DB = os.path.join(DESKTOP, "plum.sqlite")
VAULT = "C:/Users/dazch/nova/vault"

# --- Folder routing by note index (1-based) ---
ROUTING = {
    1:  "inbox",
    2:  "architecture",
    3:  "architecture",
    4:  "inbox",
    5:  "inbox",
    6:  None,          # skip - basic info
    7:  "insights",
    8:  "architecture",
    9:  "inbox",
    10: "architecture",
    11: "architecture",
    12: "insights",
    13: "architecture",
    14: "architecture",
    15: "architecture",
    16: "sessions",
    17: "sessions",
    18: "identity",
    19: "identity",
    20: None,          # skip - empty
    21: "inbox",
    22: "inbox",
    23: "sessions",
    24: "identity",
}

def clean_text(text):
    if not text:
        return ""
    # Remove \id=<uuid> markers
    text = re.sub(r'\\id=[a-f0-9\-]{36}', '', text)
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text

def convert_timestamp(ts):
    if not ts:
        return "Unknown"
    try:
        # Windows FILETIME: 100-nanosecond intervals since 1601-01-01
        EPOCH_DIFF = 11644473600  # seconds between 1601 and 1970
        seconds = (int(ts) / 10_000_000) - EPOCH_DIFF
        return datetime.utcfromtimestamp(seconds).strftime("%Y-%m-%d %H:%M UTC")
    except:
        return str(ts)

def slugify(title):
    title = title.lower()
    title = re.sub(r'[^a-z0-9\s\-]', '', title)
    title = re.sub(r'\s+', '-', title.strip())
    return title[:60]

def extract_title(text):
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and len(line) > 3:
            return line[:60]
    return "untitled"

def ensure_folders():
    folders = ["architecture", "insights", "sessions", "inbox", 
               "identity", "projects"]
    for folder in folders:
        path = os.path.join(VAULT, folder)
        os.makedirs(path, exist_ok=True)
        print(f"  ✓ {path}")

def export_notes():
    conn = sqlite3.connect(STICKY_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Text, CreatedAt, UpdatedAt FROM Note")
    rows = cursor.fetchall()
    conn.close()

    exported = 0
    skipped = 0

    for i, row in enumerate(rows):
        index = i + 1
        note_id, text, created, updated = row

        destination = ROUTING.get(index)
        if destination is None:
            print(f"[{index}] SKIP")
            skipped += 1
            continue

        clean = clean_text(text)
        if not clean:
            print(f"[{index}] SKIP (empty after clean)")
            skipped += 1
            continue

        title = extract_title(clean)
        slug = slugify(title)
        created_str = convert_timestamp(created)
        updated_str = convert_timestamp(updated)

        # Build markdown
        md = f"""---
source: sticky-notes
exported: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
created: {created_str}
updated: {updated_str}
original_id: {note_id}
---

# {title}

{clean}
"""

        filename = f"sticky-{index:02d}-{slug}.md"
        filepath = os.path.join(VAULT, destination, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md)

        print(f"[{index}] → vault/{destination}/{filename}")
        exported += 1

    print(f"\nDone. {exported} exported, {skipped} skipped.")

if __name__ == "__main__":
    print("Creating vault folders...\n")
    ensure_folders()
    print("\nExporting notes...\n")
    export_notes()
