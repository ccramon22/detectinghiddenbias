#!/usr/bin/env python3


from __future__ import annotations
import argparse
import csv
import itertools
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple, Dict, Set, Optional

@dataclass(frozen=True)
class Basket:
    items: Tuple[int, ...]  # sorted unique ints

def _parse_ints_from_line(line: str) -> List[int]:
    # Accept whitespace, comma, tab-separated.
    line = line.strip()
    if not line:
        return []
    # If line starts with session id + delimiter, keep items only
    # Heuristic: if there is a tab and left side is numeric, treat left side as session id
    if "\t" in line:
        left, right = line.split("\t", 1)
        if left.strip().isdigit():
            line = right.strip()
    # Replace commas with spaces
    line = line.replace(",", " ")
    parts = [p for p in line.split() if p.strip()]
    ints: List[int] = []
    for p in parts:
        # Ignore non-numeric tokens
        if p.isdigit():
            ints.append(int(p))
    return ints

def read_baskets_from_sessions_file(path: Path) -> List[Basket]:
    baskets: List[Basket] = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            items = _parse_ints_from_line(raw)
            if not items:
                continue
            uniq = tuple(sorted(set(items)))
            if len(uniq) >= 1:
                baskets.append(Basket(items=uniq))
    return baskets

def read_baskets_from_retailrocket_events(
    path: Path,
    session_gap_ms: int = 30 * 60 * 1000,  # 30 minutes
    min_events_per_session: int = 2,
    allowed_events: Optional[Set[str]] = None,
) -> List[Basket]:

    if allowed_events is None:
        allowed_events = {"view", "addtocart", "transaction"}

    rows_by_user: Dict[int, List[Tuple[int, int, str]]] = defaultdict(list)  # user -> list[(ts, item, event)]
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        required = {"timestamp", "visitorid", "event", "itemid"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"events.csv missing required columns {required}. Found: {reader.fieldnames}")
        for r in reader:
            ev = (r.get("event") or "").strip().lower()
            if ev not in allowed_events:
                continue
            try:
                ts = int(r["timestamp"])
                uid = int(r["visitorid"])
                item = int(r["itemid"])
            except Exception:
                continue
            rows_by_user[uid].append((ts, item, ev))

    baskets: List[Basket] = []
    for uid, rows in rows_by_user.items():
        rows.sort(key=lambda x: x[0])
        cur_items: Set[int] = set()
        cur_count = 0
        last_ts: Optional[int] = None
        for ts, item, ev in rows:
            if last_ts is None or (ts - last_ts) <= session_gap_ms:
                cur_items.add(item)
                cur_count += 1
            else:
                if cur_count >= min_events_per_session and len(cur_items) >= 1:
                    baskets.append(Basket(items=tuple(sorted(cur_items))))
                cur_items = {item}
                cur_count = 1
            last_ts = ts
        if cur_count >= min_events_per_session and len(cur_items) >= 1:
            baskets.append(Basket(items=tuple(sorted(cur_items))))
    return baskets

def apriori_pairs(baskets: List[Basket], min_support: int) -> Tuple[Counter[int], Counter[Tuple[int,int]], int]:

    n_baskets = len(baskets)
    item_counts: Counter[int] = Counter()
    for b in baskets:
        item_counts.update(b.items)

    frequent_items = {i for i,c in item_counts.items() if c >= min_support}

    pair_counts: Counter[Tuple[int,int]] = Counter()
    for b in baskets:
        items = [i for i in b.items if i in frequent_items]
        if len(items) < 2:
            continue
        for a, c in itertools.combinations(items, 2):
            pair_counts[(a, c)] += 1

    # Filter pairs to min_support
    pair_counts = Counter({p:c for p,c in pair_counts.items() if c >= min_support})
    # Also filter item_counts to frequent items
    item_counts = Counter({i:c for i,c in item_counts.items() if i in frequent_items})
    return item_counts, pair_counts, n_baskets

def apriori_triples(
    baskets: List[Basket],
    frequent_items: Set[int],
    frequent_pairs: Set[Tuple[int,int]],
    min_support: int
) -> Counter[Tuple[int,int,int]]:

    triple_counts: Counter[Tuple[int,int,int]] = Counter()
    fpair = set(frequent_pairs)

    for b in baskets:
        items = [i for i in b.items if i in frequent_items]
        if len(items) < 3:
            continue
        # Candidate triples; prune by frequent pairs
        for a,b_,c in itertools.combinations(items, 3):
            if (a,b_) in fpair and (a,c) in fpair and (b_,c) in fpair:
                triple_counts[(a,b_,c)] += 1

    triple_counts = Counter({t:c for t,c in triple_counts.items() if c >= min_support})
    return triple_counts

def write_top(counter, out_path: Path, header: List[str], top_n: int, n_baskets: int):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    items = counter.most_common(top_n)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header + ["support_fraction"])
        for k, c in items:
            frac = c / n_baskets if n_baskets else 0.0
            if isinstance(k, tuple):
                w.writerow(list(k) + [c, f"{frac:.8f}"])
            else:
                w.writerow([k, c, f"{frac:.8f}"])

def write_pair_rules(
    item_counts: Counter[int],
    pair_counts: Counter[Tuple[int,int]],
    out_path: Path,
    n_baskets: int,
    top_n: int
):

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pr = {i: (c / n_baskets if n_baskets else 0.0) for i, c in item_counts.items()}

    rows = []
    for (a,b), sup_ab in pair_counts.items():
        sup_a = item_counts.get(a, 0)
        sup_b = item_counts.get(b, 0)
        if sup_a:
            conf = sup_ab / sup_a
            interest = conf - pr.get(b, 0.0)
            rows.append((a, b, sup_ab, conf, interest))
        if sup_b:
            conf = sup_ab / sup_b
            interest = conf - pr.get(a, 0.0)
            rows.append((b, a, sup_ab, conf, interest))

    # Sort by interest desc then confidence desc
    rows.sort(key=lambda r: (r[4], r[3], r[2]), reverse=True)
    rows = rows[:top_n]

    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["A", "B", "support(A,B)", "confidence(A->B)", "interest(A->B)"])
        for a,b,sup_ab,conf,interest in rows:
            w.writerow([a, b, sup_ab, f"{conf:.6f}", f"{interest:.6f}"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions", type=str, help="Path to sessions basket file (one basket per line).")
    ap.add_argument("--events", type=str, help="Path to RetailRocket events.csv (will sessionize).")
    ap.add_argument("--min_support", type=int, default=50, help="Minimum support count (>= 1).")
    ap.add_argument("--top_n", type=int, default=50, help="Number of rows to output per file.")
    ap.add_argument("--max_k", type=int, default=2, choices=[2,3], help="Mine pairs (2) or pairs+triples (3).")
    ap.add_argument("--out_dir", type=str, default="out_itemsets", help="Output directory.")
    ap.add_argument("--session_gap_minutes", type=int, default=30, help="Only used for events.csv input.")
    args = ap.parse_args()

    if not args.sessions and not args.events:
        ap.error("Provide --sessions or --events")

    if args.sessions:
        baskets = read_baskets_from_sessions_file(Path(args.sessions))
    else:
        baskets = read_baskets_from_retailrocket_events(
            Path(args.events),
            session_gap_ms=args.session_gap_minutes * 60 * 1000
        )

    if not baskets:
        raise SystemExit("No baskets found. Check input format / path.")

    out_dir = Path(args.out_dir)
    item_counts, pair_counts, n_baskets = apriori_pairs(baskets, args.min_support)

    write_top(item_counts, out_dir / "frequent_items.csv", ["item", "support_count"], args.top_n, n_baskets)
    write_top(pair_counts, out_dir / "frequent_pairs.csv", ["item1", "item2", "support_count"], args.top_n, n_baskets)
    write_pair_rules(item_counts, pair_counts, out_dir / "rules_pairs.csv", n_baskets, args.top_n)

    if args.max_k == 3:
        frequent_items = set(item_counts.keys())
        frequent_pairs = set(pair_counts.keys())
        triple_counts = apriori_triples(baskets, frequent_items, frequent_pairs, args.min_support)
        write_top(triple_counts, out_dir / "frequent_triples.csv", ["item1", "item2", "item3", "support_count"], args.top_n, n_baskets)

    print(f"Done. baskets={n_baskets}, frequent_items={len(item_counts)}, frequent_pairs={len(pair_counts)}")

if __name__ == "__main__":
    main()
