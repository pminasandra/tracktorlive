#!/usr/bin/env python3
import os
import sys
import re
from pathlib import Path

def parse_front_matter(text):
    """
    Return a dict of key: value from the first YAML-style front matter block.
    Only handles simple 'key: value' lines (no nested YAML).
    """
    # Match content between the first pair of --- lines at start of file
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, flags=re.DOTALL)
    if not m:
        return {}
    block = m.group(1)
    meta = {}
    for line in block.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta

def nice_title(raw_title: str) -> str:
    # Replace underscores with spaces and Title Case
    return raw_title.replace("_", " ").title()

def collect_entries(root: Path):
    rows = []
    # Loop immediate subdirectories
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        # Find first .md file inside this directory
        md_files = sorted(p for p in entry.iterdir() if p.suffix.lower() == ".md" and p.is_file())
        if not md_files:
            continue
        md_path = md_files[0]
        try:
            text = md_path.read_text(encoding="utf-8")
        except Exception:
            continue
        meta = parse_front_matter(text)
        title_key = meta.get("title") or md_path.stem
        description = meta.get("description", "").rstrip(".")
        link_text = nice_title(title_key)
        rel_link = md_path.as_posix()  # relative path from root
        rows.append((link_text, description, rel_link))
    # Sort by display title
    rows.sort(key=lambda r: r[0].lower())
    return rows

def emit_table(rows):
    print("| Title | Description |")
    print("|---|---|")
    for link_text, description, rel_link in rows:
        print(f"| [{link_text}]({rel_link}) | {description} |")

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    rows = collect_entries(root)
    emit_table(rows)

if __name__ == "__main__":
    main()

