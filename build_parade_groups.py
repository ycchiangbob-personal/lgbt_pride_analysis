#!/usr/bin/env python3
"""Parse taiwan-pride-parade-teams-2019-2025.md → parade_groups.json"""

import re, json

MD = "taiwan-pride-parade-teams-2019-2025.md"
OUT = "parade_groups.json"

TEAM_COLORS = ["紅色", "橙色", "黃色", "綠色", "藍色", "紫色"]
COLOR_ORDER = {c: i for i, c in enumerate(TEAM_COLORS)}

def split_names(text):
    """Split by 、 but not inside parentheses."""
    names, buf, depth = [], [], 0
    for ch in text:
        if ch in "（(":
            depth += 1
            buf.append(ch)
        elif ch in "）)":
            depth -= 1
            buf.append(ch)
        elif ch == "、" and depth == 0:
            s = "".join(buf).strip()
            if s:
                names.append(s)
            buf = []
        else:
            buf.append(ch)
    s = "".join(buf).strip()
    if s:
        names.append(s)
    return names

def parse_md(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()

    result = {}

    # Split into year blocks by ## headings
    year_blocks = re.split(r'\n(?=## \d{4})', text)
    for block in year_blocks:
        m = re.match(r'## (\d{4})', block)
        if not m:
            continue
        year = int(m.group(1))

        # 2021 special: no team colors
        if year == 2021:
            m2 = re.search(r'\*\*參與團體[^：]*：\*\*\s*(.+)', block)
            if m2:
                entries = split_names(m2.group(1).strip())
                result[year] = {"all": {"全體參與": entries}}
            continue

        year_data = {}

        # Split into team-color blocks by ### headings
        color_blocks = re.split(r'\n(?=### )', block)
        for cb in color_blocks:
            # Find color
            color = None
            for c in TEAM_COLORS:
                if c in cb:
                    color = c
                    break
            if not color:
                continue

            sections = {}
            for sec_name in ["社團車", "商業車", "隊伍"]:
                pat = rf'\*\*{sec_name}[：:]\*\*\s*(.+?)(?=\n\*\*|\n###|\n##|\n---|\Z)'
                sm = re.search(pat, cb, re.DOTALL)
                if sm:
                    raw = sm.group(1).strip().replace("\n", "")
                    entries = split_names(raw)
                    sections[sec_name] = entries
                else:
                    sections[sec_name] = []

            year_data[color] = sections

        # Sort by canonical color order
        year_data = dict(sorted(year_data.items(), key=lambda x: COLOR_ORDER.get(x[0], 99)))
        result[year] = year_data

    return dict(sorted(result.items()))

data = parse_md(MD)

# Print summary
for yr, yr_data in data.items():
    if "all" in yr_data:
        total = sum(len(v) for v in yr_data["all"].values())
        print(f"{yr}: 2021 special — {total} entries")
    else:
        commercial = sum(len(s.get("商業車", [])) for s in yr_data.values())
        ngo = sum(len(s.get("社團車", [])) for s in yr_data.values())
        teams = sum(len(s.get("隊伍", [])) for s in yr_data.values())
        print(f"{yr}: {len(yr_data)} colors | 商業車={commercial} 社團車={ngo} 隊伍={teams}")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nWrote {OUT}")
