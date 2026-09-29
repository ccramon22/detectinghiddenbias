# Install dependencies as needed:
# pip install kagglehub[pandas-datasets]
import kagglehub
from kagglehub import KaggleDatasetAdapter

# Set the path to the file you'd like to load
# You need to replace the empty string with an actual file name from the dataset.
# The 'ecommerce-dataset' contains files like 'events.csv', 'category_tree.csv', 'item_properties.csv', etc.
file_path = "events.csv"

# Load the latest version
# This will download the file if it's not already cached locally.
df = kagglehub.load_dataset(
    KaggleDatasetAdapter.PANDAS,
    "retailrocket/ecommerce-dataset",
    file_path,
    # Provide any additional arguments like
    # sql_query or pandas_kwargs. See the
    # documenation for more information:
    # https://github.com/Kaggle/kagglehub/blob/main/README.md#kaggledatasetadapterpandas
)

purchases_df = df[df['event'] == 'transaction']

print("First 10 records:")
print(df.head(10))

print("\nPurchase Data (First 10 Transactions)")
print(purchases_df.head(10))