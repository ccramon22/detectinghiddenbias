# Detecting Hidden Bias in Recommendation graphs using pagerank and itemsets

## Overview
This project analyzes user viewing behavior to construct recommendation graphs and identify potential bias in recommendation systems.
## Dataset Source
This project uses the RetailRocket E-commerce Dataset, a real-world e-commerce interaction dataset containing user behavior, item metadata, and category information.
Dataset URL: https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset
## Data Files
The script expects the following CSV files in the same directory:
	•	events.csv – user interactions (must include visitorid, itemid, event)
	•	item_properties.csv – item metadata
	•	category_tree.csv – category relationships
Required columns in events.csv:
visitorid
itemid
event
## Objectives
The project aims to:
 
- Analyze user viewing behavior.
- Build graph-based representations of user-item interactions.
- Identify highly popular items that may introduce recommendation bias.
- Explore item co-view relationships.
- Create a foundation for future recommendation and bias-detection research.
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
