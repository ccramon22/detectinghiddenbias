# Itemset Mining (Apriori-style)

This folder mines **frequent itemsets** from user **session baskets**, using the Apriori ideas from lecture.

## Input options

### Option A: Sessions file (recommended if you already built sessions)
One line = one basket/session.

Accepted formats (examples):
- `123\t461686 320130 447661`
- `461686,320130,447661`
- `461686 320130 447661`

Run:
```bash
python itemset_mining.py --sessions path/to/sessions.txt --min_support 50 --top_n 50 --max_k 2
```

### Option B: RetailRocket events.csv (auto sessionization)
RetailRocket events.csv columns:
`timestamp, visitorid, event, itemid, transactionid`

Run (30-minute gap sessionization):
```bash
python itemset_mining.py --events path/to/events.csv --session_gap_minutes 30 --min_support 50 --top_n 50 --max_k 2
```

## Outputs (written to `out_itemsets/` by default)

- `frequent_items.csv`: top frequent single items
- `frequent_pairs.csv`: top frequent pairs (most important)
- `frequent_triples.csv`: (optional if `--max_k 3`)
- `rules_pairs.csv`: top association rules from pairs, ranked by **interest**

Definitions used (from class):
- support(I) = # baskets containing itemset I
- confidence(A -> B) = support(A,B) / support(A)
- interest(A -> B) = confidence(A -> B) - Pr[B]

## Suggested slide content (what to report)

1) Your min_support choice and why  
2) Top frequent pairs (support counts)  
3) Optional top rules with confidence/interest  
4) Bias angle: are top pairs mostly within the same category or cross-category?
