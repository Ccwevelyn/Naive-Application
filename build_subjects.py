# -*- coding: utf-8 -*-
"""Attach QS 2026 subject ranks to the schools already in data.js."""
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from build_schools import ALIASES, bare_norm, fold, norm

ROOT = Path(__file__).resolve().parent
TOOLS = Path(r"C:\Users\Asus\.cursor\projects\c-Users-Asus-Desktop-Naive-Appliation\agent-tools")

SUBJECTS = [
    ("cs", "计算机", "Computer Science", TOOLS / "241bd55a-be06-4d13-9c96-bd549622abf2.txt"),
    ("ee", "电气与电子", "Electrical Engineering", TOOLS / "ef40290c-c8d8-4b27-894b-853d5ca1977e.txt"),
    ("mech", "机械与制造", "Mechanical Engineering", None),
    ("business", "商业与管理", "Business and Management", TOOLS / "13108b5e-fce7-4674-96e9-5c6d1cc48022.txt"),
    ("econ", "经济学", "Economics", TOOLS / "ecd27e90-4343-4eb1-9d7a-a2c51d420a55.txt"),
    ("math", "数学", "Mathematics", TOOLS / "9a3d5e6f-b7ef-4212-861b-25968f477f68.txt"),
    ("physics", "物理与天文", "Physics and Astronomy", TOOLS / "d700eb4a-e597-4d29-aa87-968c66d44ec2.txt"),
    ("chem", "化学", "Chemistry", TOOLS / "359bd8e9-dbbf-4083-b0d0-9a6aa0c7ce7a.txt"),
    ("medicine", "医学", "Medicine", TOOLS / "68adb210-5012-4e78-9b7a-82f418f67508.txt"),
    ("bio", "生物科学", "Biological Sciences", TOOLS / "984be177-af76-4a70-af67-d02fb8e4ebd2.txt"),
]

ROW = re.compile(r"^\|\s*(\d+)\s*\|[^|]*\|\s*([^|]+?)\s*\|")


def load_schools():
    raw = (ROOT / "data.js").read_text(encoding="utf-8")
    data = json.loads(raw.split("=", 1)[1].rstrip().rstrip(";"))
    return data["schools"]


def indexes(schools):
    exact = {}
    for school in schools:
        keys = {norm(school["en"]), bare_norm(school["en"])}
        for alias in ALIASES.get(school["en"], []):
            keys.add(norm(alias))
            keys.add(bare_norm(alias))
        for key in keys:
            exact.setdefault(key, school["id"])
    return exact


def find_id(name, exact, schools):
    for key in (norm(name), bare_norm(name)):
        if key in exact:
            return exact[key]
    tokens = set(bare_norm(name).split())
    best = None
    best_score = 0
    for school in schools:
        other = set(bare_norm(school["en"]).split())
        if len(tokens) < 2 or len(other) < 2:
            continue
        inter = tokens & other
        union = tokens | other
        score = len(inter) / len(union)
        smaller, larger = (tokens, other) if len(tokens) <= len(other) else (other, tokens)
        if len(smaller) >= 3 and smaller <= larger:
            score = max(score, 0.92)
        elif SequenceMatcher(None, bare_norm(name), bare_norm(school["en"])).ratio() >= 0.9:
            score = max(score, 0.9)
        if score > best_score:
            best_score = score
            best = school["id"]
    if best_score >= 0.88:
        return best
    return None


def parse_table(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ROW.match(line)
        if not match:
            continue
        rank = int(match.group(1))
        name = re.sub(r"\s+", " ", match.group(2)).strip()
        if name.upper() == "INSTITUTION" or rank > 1000:
            continue
        rows.append((rank, name))
    return rows


def main():
    schools = load_schools()
    exact = indexes(schools)
    catalog = []
    ranks = {}
    for sid, zh, en, path in SUBJECTS:
        if path is None or not path.exists():
            continue
        table = parse_table(path)
        if len(table) < 20:
            print("skip", sid, "rows", len(table))
            continue
        mapped = {}
        missed = []
        for rank, name in table:
            school_id = find_id(name, exact, schools)
            if school_id and school_id not in mapped:
                mapped[school_id] = rank
            elif not school_id:
                missed.append(name)
        catalog.append({"id": sid, "zh": zh, "en": en, "source": "QS 2026"})
        ranks[sid] = mapped
        print(f"{sid}: table {len(table)} matched {len(mapped)} outside-list {len(missed)}")
    payload = {"list": catalog, "ranks": ranks}
    text = "window.NAIVE_SUBJECTS = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (ROOT / "subjects.js").write_text(text, encoding="utf-8")
    cs = ranks.get("cs", {})
    by_id = {school["id"]: school["en"] for school in schools}
    print("cs sample", [(by_id[i], r) for i, r in list(cs.items())[:8]])


if __name__ == "__main__":
    main()
