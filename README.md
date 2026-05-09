# Detecting Hidden Bias in Recommendation graphs using pagerank and itemsets

## Overview
This script analyzes user viewing behavior to build:
	•	A User–Item graph showing which users viewed which items
	•	An Item–Item graph showing items that are frequently viewed together
It also identifies the top 5 most viewed items and creates user-level item lists.
## Data Files
The script expects the following CSV files in the same directory:
	•	events.csv – user interactions (must include visitorid, itemid, event)
	•	item_properties.csv – item metadata
	•	category_tree.csv – category relationships
## Requirements
	•	Python 3
	•	Libraries: pip install pandas networkx
## What the Script Does
	1	Loads the datasets and prints basic statistics
	2	Keeps only view events
	3	Filters out users and items with fewer than 3 interactions
	4	Builds a User–Item bipartite graph
	5	Builds an iem–Item co-view graph ( number of shared users)
	6	Prints the top 5 most viewed items
	7	Creates lists of items viewed by each user
## Output
The script prints:
	•	Dataset sizes before and after filtering
	•	Number of nodes and edges in each graph
	•	Top 5 most viewed items
	•	Number of user item lists and one example
