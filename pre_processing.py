import pandas as pd
import networkx as nx
from itertools import combinations

# load raw data
events = pd.read_csv("events.csv")
item_props = pd.read_csv("item_properties.csv")
categories = pd.read_csv("category_tree.csv")

print(f"{events.shape[0]:,} user interactions across {events.shape[1]} columns.")
print(f"{item_props.shape[0]:,} records (item attributes) across {item_props.shape[1]} columns.")
print(f"{categories.shape[0]:,} category relationships across {categories.shape[1]} columns.\n")

# clean and filter interactions
# keep only view events
filtered = events[events["event"] == "view"].copy()

# remove users with fewer than 3 interactions
user_interaction_counts = filtered.groupby("visitorid")["itemid"].nunique()
valid_users = user_interaction_counts[user_interaction_counts >= 3].index

# remove items viewed by fewer than 3 unique users
item_view_counts = filtered.groupby("itemid")["visitorid"].nunique()
valid_items = item_view_counts[item_view_counts >= 3].index

filtered = filtered[
    filtered["visitorid"].isin(valid_users) &
    filtered["itemid"].isin(valid_items)
]

print(f"{filtered.shape[0]:,} user item interactions remain across {filtered.shape[1]} columns.\n")

# build user–item graph
G_ui = nx.Graph()

# user
G_ui.add_nodes_from(filtered["visitorid"].unique(), bipartite="user")

# items
G_ui.add_nodes_from(filtered["itemid"].unique(), bipartite="item")

# add interactions
for row in filtered.itertuples():
    G_ui.add_edge(row.visitorid, row.itemid)

print("User–Item Graph:")
print(f"{G_ui.number_of_nodes():,} users + items represented")
print(f"{G_ui.number_of_edges():,} user–item interactions")

# build item–item graph
G_item = nx.Graph()

# group items by user to find co-viewed sets
for user, group in filtered.groupby("visitorid"):
    items = group["itemid"].unique()

    # add edges between each item pair
    for i, j in combinations(items, 2):
        if G_item.has_edge(i, j):
            G_item[i][j]["weight"] += 1
        else:
            G_item.add_edge(i, j, weight=1)

print("Item–Item Graph:")
print(f"{G_item.number_of_nodes():,} items")
print(f"{G_item.number_of_edges():,} items frequently seen together")

# compute item popularity
item_popularity = filtered.groupby("itemid")["visitorid"].nunique().to_dict()

# attach popularity to item nodes
nx.set_node_attributes(G_item, item_popularity, name="popularity")
print("\nPopularity items:\n")

for item, pop in list(item_popularity.items())[:10]:
    print(f"• Item {item} was viewed by {pop} different users")

# prepare itemsets for association mining
baskets = (
    filtered.groupby("visitorid")["itemid"]
    .apply(list)
    .tolist()
)

print("\n")
print(len(baskets), "sets of items viewed by users")
print("Example of user's viewed list:",
      [f"item {i}" for i in baskets[0]] if len(baskets) > 0 else "No baskets found")
