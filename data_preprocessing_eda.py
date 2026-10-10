"""
PromoSense - Data Preprocessing and Exploratory Data Analysis (EDA)
Purpose:
    Clean the Flipkart product dataset and export CSV files for Oracle APEX dashboards.

Expected input:
    flipkart_com-ecommerce_sample.csv

Output:
    cleaned_data_exports/
        00_SUMMARY_REPORT.txt
        01_cleaned_flipkart_products.csv
        02_price_distribution.csv
        03_category_summary.csv
        04_brand_summary.csv
        05_discount_analysis.csv
        06_price_band_segmentation.csv
        07_category_priceband_matrix.csv
        08_rating_distribution.csv
        09_category_discount_tier.csv
        10_correlation_analysis.csv
        11_top_15_categories.csv
        12_top_20_brands.csv
        13_category_brand_performance.csv

Install requirements:
    python -m pip install pandas numpy
"""

# ============================================================
# IMPORTS
# ============================================================

from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np


# ============================================================
# STEP 1: DEFINE THE PROBLEM AND BUSINESS OBJECTIVES
# ============================================================
# PromoSense studies product prices, listed discounts, categories,
# brands, and ratings. These outputs support descriptive dashboards.
#
# IMPORTANT LIMITATION:
# This dataset contains retail and discounted prices, but it does not
# contain actual sales, conversion, costs, or profit margins. Therefore,
# this script does NOT calculate actual profit or prove that discounts
# cause higher sales. Those questions require additional data or an
# explicitly designed experiment.


# ============================================================
# STEP 2: SET FILE PATHS AND LOAD THE DATA
# ============================================================

# Use the folder containing this Python script as the project folder.
PROJECT_DIR = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_DIR / "flipkart_com-ecommerce_sample.csv"
OUTPUT_DIR = PROJECT_DIR / "cleaned_data_exports"

# Create the output folder automatically if it does not exist.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 72)
print("PROMOSENSE: DATA PREPROCESSING AND EDA")
print("=" * 72)

# Stop with a clear message if the input file is missing.
if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"\nInput CSV was not found:\n{INPUT_FILE}\n"
        "Place flipkart_com-ecommerce_sample.csv in the same folder "
        "as data_preprocessing_eda.py and run the script again."
    )

# Read the CSV. UTF-8 is attempted first; a common alternative is tried
# if the file contains a different text encoding.
try:
    raw_df = pd.read_csv(INPUT_FILE, encoding="utf-8")
except UnicodeDecodeError:
    raw_df = pd.read_csv(INPUT_FILE, encoding="latin-1")

print(f"\nInput file: {INPUT_FILE.name}")
print(f"Original dataset size: {raw_df.shape[0]} rows x {raw_df.shape[1]} columns")


# ============================================================
# STEP 3: INSPECT THE DATA BEFORE CLEANING
# ============================================================

print("\n" + "=" * 72)
print("STEP 3: INITIAL DATA INSPECTION")
print("=" * 72)

print("\nAvailable columns:")
print(raw_df.columns.tolist())

print("\nFirst five rows:")
print(raw_df.head())

print("\nData types before cleaning:")
print(raw_df.dtypes)

print("\nMissing values before cleaning:")
print(raw_df.isna().sum())

print("\nBasic numeric summary before cleaning:")
print(raw_df.describe(include="all").transpose())


# ============================================================
# STEP 4: SELECT, STANDARDIZE, AND CLEAN REQUIRED COLUMNS
# ============================================================

print("\n" + "=" * 72)
print("STEP 4: DATA CLEANING AND DATA QUALITY")
print("=" * 72)

# These are the six columns identified in the PromoSense project plan.
required_columns = [
    "product_name",
    "product_category_tree",
    "retail_price",
    "discounted_price",
    "brand",
    "overall_rating",
]

# Remove accidental spaces around column names before checking them.
raw_df.columns = raw_df.columns.astype(str).str.strip()

# Verify that all required columns exist before selecting them.
missing_columns = [col for col in required_columns if col not in raw_df.columns]
if missing_columns:
    raise ValueError(
        "The input CSV is missing required columns: "
        + ", ".join(missing_columns)
        + "\nAvailable columns: "
        + ", ".join(raw_df.columns)
    )

# Select only the required columns and create an independent copy.
df = raw_df[required_columns].copy()

# Convert text fields to consistent strings and trim unnecessary spaces.
for column in ["product_name", "product_category_tree", "brand"]:
    df[column] = df[column].astype("string").str.strip()

# Treat blank strings and common text placeholders as missing values.
missing_text_values = ["", "nan", "none", "null", "na", "n/a"]
for column in ["product_name", "product_category_tree", "brand"]:
    df[column] = df[column].mask(
        df[column].str.lower().isin(missing_text_values), pd.NA
    )

# Convert price and rating columns to numeric values.
# Values that cannot be converted become NaN and are handled below.
for column in ["retail_price", "discounted_price", "overall_rating"]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Record cleaning counts so the report can explain what changed.
initial_row_count = len(df)

# Remove rows with no usable product name.
before = len(df)
df = df.dropna(subset=["product_name"])
removed_missing_name = before - len(df)

# Remove rows without a valid retail or discounted price.
before = len(df)
df = df.dropna(subset=["retail_price", "discounted_price"])
removed_missing_prices = before - len(df)

# Remove prices that are zero or negative.
before = len(df)
df = df[(df["retail_price"] > 0) & (df["discounted_price"] > 0)].copy()
removed_nonpositive_prices = before - len(df)

# Remove records where the discounted price exceeds the retail price.
# This follows the project's assumption that discounted_price is a sale
# price and retail_price is the original/listed price.
before = len(df)
df = df[df["discounted_price"] <= df["retail_price"]].copy()
removed_discount_logic = before - len(df)

# Remove exact duplicate rows after basic text/numeric cleaning.
before = len(df)
df = df.drop_duplicates().copy()
removed_duplicates = before - len(df)

# Ratings outside the expected 1-to-5 range are treated as missing,
# not used as valid ratings. Products remain in the dataset.
invalid_rating_mask = (
    df["overall_rating"].notna()
    & ~df["overall_rating"].between(1, 5)
)
invalid_rating_count = int(invalid_rating_mask.sum())
df.loc[invalid_rating_mask, "overall_rating"] = np.nan

# Fill missing category and brand labels for grouping in dashboards.
df["product_category_tree"] = df["product_category_tree"].fillna("Unknown")
df["brand"] = df["brand"].fillna("Unknown")

# Normalize repeated whitespace in text fields.
for column in ["product_name", "product_category_tree", "brand"]:
    df[column] = df[column].astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

print(f"Original rows: {initial_row_count}")
print(f"Rows removed for missing product name: {removed_missing_name}")
print(f"Rows removed for missing prices: {removed_missing_prices}")
print(f"Rows removed for zero/negative prices: {removed_nonpositive_prices}")
print(f"Rows removed because discounted price > retail price: {removed_discount_logic}")
print(f"Duplicate rows removed: {removed_duplicates}")
print(f"Invalid ratings changed to missing: {invalid_rating_count}")
print(f"Rows remaining after cleaning: {len(df)}")

if df.empty:
    raise ValueError(
        "No rows remain after cleaning. Check the source CSV and its values."
    )


# ============================================================
# STEP 5: FEATURE ENGINEERING AND DATA TRANSFORMATION
# ============================================================

print("\n" + "=" * 72)
print("STEP 5: FEATURE ENGINEERING AND DATA TRANSFORMATION")
print("=" * 72)

# Extract the first category from a hierarchy such as:
# ["Electronics >> Audio >> Headphones"]
# or "Electronics >> Audio >> Headphones".
def get_primary_category(category_text):
    """Return the first category in a Flipkart category hierarchy."""
    if pd.isna(category_text):
        return "Unknown"

    text = str(category_text).strip()

    # Remove common list-like brackets and quotation marks.
    text = text.strip("[]'\" ")

    # Keep only the first level before the hierarchy separator.
    primary = text.split(">>")[0].strip().strip("[]'\" ")

    return primary if primary else "Unknown"


df["primary_category"] = df["product_category_tree"].apply(get_primary_category)

# Calculate the absolute discount amount.
df["discount_amount"] = (
    df["retail_price"] - df["discounted_price"]
).round(2)

# Calculate the discount as a fraction between 0 and 1.
# Example: 0.20 means a 20% discount.
df["historical_discount_pct"] = (
    (df["retail_price"] - df["discounted_price"]) / df["retail_price"]
).clip(0, 1)

# Calculate a percentage column for convenient chart labels.
df["historical_discount_percent"] = (
    df["historical_discount_pct"] * 100
).round(2)

# Assign Budget, Mid-Range, and Premium using retail-price tertiles.
# The thresholds are based on this dataset, not fixed currency limits.
price_q33 = df["retail_price"].quantile(1 / 3)
price_q67 = df["retail_price"].quantile(2 / 3)

def categorize_price_band(price):
    """Assign a product to a relative retail-price band."""
    if price <= price_q33:
        return "Budget"
    elif price <= price_q67:
        return "Mid-Range"
    return "Premium"


df["price_band"] = df["retail_price"].apply(categorize_price_band)

# Group discounts into tiers for category-level comparisons.
def categorize_discount_tier(discount_fraction):
    """Convert a discount fraction to a readable discount tier."""
    percent = discount_fraction * 100
    if percent < 10:
        return "0-10%"
    elif percent < 20:
        return "10-20%"
    elif percent < 30:
        return "20-30%"
    elif percent < 40:
        return "30-40%"
    return "40%+"


df["discount_tier"] = df["historical_discount_pct"].apply(
    categorize_discount_tier
)

# Generate a stable ID for this cleaned export. This ID is a row identifier
# for dashboard joins, not an original Flipkart product ID.
df = df.reset_index(drop=True)
df.insert(0, "product_id", np.arange(1, len(df) + 1))

print(f"Price-band thresholds: Budget <= {price_q33:.2f}; "
      f"Mid-Range <= {price_q67:.2f}; Premium > {price_q67:.2f}")
print("Added: primary_category, discount_amount, historical_discount_pct,")
print("       historical_discount_percent, price_band, discount_tier, product_id")


# ============================================================
# STEP 6: STATISTICAL EDA AND OUTLIER CHECKS
# ============================================================

print("\n" + "=" * 72)
print("STEP 6: STATISTICAL EDA AND OUTLIER ANALYSIS")
print("=" * 72)

numeric_columns = [
    "retail_price",
    "discounted_price",
    "discount_amount",
    "historical_discount_pct",
    "overall_rating",
]

print("\nDescriptive statistics:")
print(df[numeric_columns].describe().round(2))

print("\nMedian values:")
print(df[numeric_columns].median(numeric_only=True).round(2))

print("\nStandard deviation:")
print(df[numeric_columns].std(numeric_only=True).round(2))

print("\nSkewness:")
print(df[numeric_columns].skew(numeric_only=True).round(2))

# Use the IQR rule to flag unusual retail-price observations.
# Outliers are flagged for investigation, not removed automatically.
q1 = df["retail_price"].quantile(0.25)
q3 = df["retail_price"].quantile(0.75)
iqr = q3 - q1
lower_iqr_bound = q1 - 1.5 * iqr
upper_iqr_bound = q3 + 1.5 * iqr

df["retail_price_outlier_flag"] = (
    (df["retail_price"] < lower_iqr_bound)
    | (df["retail_price"] > upper_iqr_bound)
)

outlier_count = int(df["retail_price_outlier_flag"].sum())

print(f"\nRetail-price IQR lower bound: {lower_iqr_bound:.2f}")
print(f"Retail-price IQR upper bound: {upper_iqr_bound:.2f}")
print(f"Retail-price outliers flagged (not removed): {outlier_count}")

# Calculate correlations among numeric columns. Correlation measures
# association, not causation.
correlation_matrix = df[
    ["retail_price", "discounted_price", "discount_amount",
     "historical_discount_pct", "overall_rating"]
].corr(numeric_only=True).round(4)

print("\nCorrelation matrix:")
print(correlation_matrix)


# ============================================================
# STEP 7: CREATE DASHBOARD-READY CSV FILES
# ============================================================

print("\n" + "=" * 72)
print("STEP 7: CREATE CSV DATASETS FOR ORACLE APEX")
print("=" * 72)

# Helper function saves each output with consistent UTF-8 encoding.
def save_csv(dataframe, filename):
    """Save a dataframe to the output folder and print its dimensions."""
    output_path = OUTPUT_DIR / filename
    dataframe.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved {filename}: {len(dataframe)} rows x {len(dataframe.columns)} columns")
    return output_path


# ------------------------------------------------------------
# OUTPUT 01: MAIN CLEANED PRODUCT DATASET
# ------------------------------------------------------------
# Use this file for product-level reports, filters, and drill-downs.
save_csv(df, "01_cleaned_flipkart_products.csv")


# ------------------------------------------------------------
# OUTPUT 02: PRICE DISTRIBUTION
# ------------------------------------------------------------
# Use for histograms, retail-vs-discounted price comparisons, and
# scatter plots. APEX charts can group prices into bins if needed.
price_distribution = df[
    [
        "product_id", "product_name", "primary_category", "brand",
        "retail_price", "discounted_price", "discount_amount",
        "historical_discount_pct", "historical_discount_percent",
        "price_band",
    ]
].copy()
save_csv(price_distribution, "02_price_distribution.csv")


# ------------------------------------------------------------
# OUTPUT 03: CATEGORY SUMMARY
# ------------------------------------------------------------
# Use for product count, average price, average discount, and rating
# comparisons by primary category.
category_summary = df.groupby("primary_category", dropna=False).agg(
    product_count=("product_id", "count"),
    avg_retail_price=("retail_price", "mean"),
    median_retail_price=("retail_price", "median"),
    min_retail_price=("retail_price", "min"),
    max_retail_price=("retail_price", "max"),
    std_retail_price=("retail_price", "std"),
    avg_discounted_price=("discounted_price", "mean"),
    avg_discount_amount=("discount_amount", "mean"),
    avg_discount_pct=("historical_discount_pct", "mean"),
    avg_rating=("overall_rating", "mean"),
    rated_product_count=("overall_rating", "count"),
).reset_index().round(2)
category_summary = category_summary.rename(
    columns={"primary_category": "category"}
)
save_csv(category_summary, "03_category_summary.csv")


# ------------------------------------------------------------
# OUTPUT 04: BRAND SUMMARY
# ------------------------------------------------------------
# Use for top-brand charts and comparison of average listed prices,
# discounts, and ratings.
brand_summary = df.groupby("brand", dropna=False).agg(
    product_count=("product_id", "count"),
    avg_retail_price=("retail_price", "mean"),
    min_retail_price=("retail_price", "min"),
    max_retail_price=("retail_price", "max"),
    avg_discounted_price=("discounted_price", "mean"),
    avg_discount_pct=("historical_discount_pct", "mean"),
    avg_rating=("overall_rating", "mean"),
    rated_product_count=("overall_rating", "count"),
).reset_index().round(2)
brand_summary = brand_summary.sort_values(
    ["product_count", "brand"], ascending=[False, True]
)
save_csv(brand_summary, "04_brand_summary.csv")


# ------------------------------------------------------------
# OUTPUT 05: DISCOUNT ANALYSIS
# ------------------------------------------------------------
# One row per product, sorted from largest discount to smallest.
discount_analysis = df[
    [
        "product_id", "product_name", "primary_category", "brand",
        "retail_price", "discounted_price", "discount_amount",
        "historical_discount_pct", "historical_discount_percent",
        "discount_tier", "overall_rating",
    ]
].sort_values("historical_discount_pct", ascending=False)
save_csv(discount_analysis, "05_discount_analysis.csv")


# ------------------------------------------------------------
# OUTPUT 06: PRICE-BAND SEGMENTATION
# ------------------------------------------------------------
# Use for Budget / Mid-Range / Premium distribution and KPI cards.
price_band_order = ["Budget", "Mid-Range", "Premium"]
price_band_summary = df.groupby("price_band").agg(
    product_count=("product_id", "count"),
    avg_retail_price=("retail_price", "mean"),
    min_retail_price=("retail_price", "min"),
    max_retail_price=("retail_price", "max"),
    avg_discount_pct=("historical_discount_pct", "mean"),
    avg_discounted_price=("discounted_price", "mean"),
    avg_rating=("overall_rating", "mean"),
).reindex(price_band_order).reset_index().round(2)
price_band_summary["product_percentage"] = (
    price_band_summary["product_count"] / len(df) * 100
).round(2)
save_csv(price_band_summary, "06_price_band_segmentation.csv")


# ------------------------------------------------------------
# OUTPUT 07: CATEGORY X PRICE-BAND MATRIX
# ------------------------------------------------------------
# Each row is a category; columns show product counts by price band.
category_priceband_matrix = pd.crosstab(
    df["primary_category"], df["price_band"]
)
for band in price_band_order:
    if band not in category_priceband_matrix.columns:
        category_priceband_matrix[band] = 0
category_priceband_matrix = category_priceband_matrix[
    price_band_order
].reset_index().rename(columns={"primary_category": "category"})
save_csv(category_priceband_matrix, "07_category_priceband_matrix.csv")


# ------------------------------------------------------------
# OUTPUT 08: RATING DISTRIBUTION
# ------------------------------------------------------------
# Group ratings into exact rating values for a bar chart.
# Missing or invalid ratings are excluded from this distribution.
rating_data = df[df["overall_rating"].notna()].copy()
rating_summary = rating_data.groupby("overall_rating").agg(
    product_count=("product_id", "count")
).reset_index().rename(columns={"overall_rating": "rating"})
rating_summary = rating_summary.sort_values("rating")
save_csv(rating_summary, "08_rating_distribution.csv")


# ------------------------------------------------------------
# OUTPUT 09: CATEGORY X DISCOUNT-TIER MATRIX
# ------------------------------------------------------------
# Use for stacked bars or a heatmap of discount tiers by category.
discount_tier_order = ["0-10%", "10-20%", "20-30%", "30-40%", "40%+"]
category_discount_tier = pd.crosstab(
    df["primary_category"], df["discount_tier"]
)
for tier in discount_tier_order:
    if tier not in category_discount_tier.columns:
        category_discount_tier[tier] = 0
category_discount_tier = category_discount_tier[
    discount_tier_order
].reset_index().rename(columns={"primary_category": "category"})
save_csv(category_discount_tier, "09_category_discount_tier.csv")


# ------------------------------------------------------------
# OUTPUT 10: CORRELATION / SCATTER-PLOT DATA
# ------------------------------------------------------------
# Keep rows with valid ratings for analyses involving rating.
# The main cleaned dataset still retains products with missing ratings.
correlation_data = df[
    [
        "product_id", "retail_price", "discounted_price",
        "discount_amount", "historical_discount_pct",
        "overall_rating", "primary_category", "price_band",
    ]
].copy()
save_csv(correlation_data, "10_correlation_analysis.csv")

# Save an additional correlation coefficient table to make numeric
# relationships available to APEX or for documenting EDA results.
correlation_output = correlation_matrix.rename_axis("variable").reset_index()
save_csv(correlation_output, "10b_correlation_coefficients.csv")


# ------------------------------------------------------------
# OUTPUT 11: TOP 15 CATEGORIES
# ------------------------------------------------------------
# Percentage is calculated against the entire cleaned dataset, so
# the top 15 percentages do not necessarily add up to 100%.
top_categories = (
    df["primary_category"].value_counts().head(15)
    .rename_axis("category").reset_index(name="product_count")
)
top_categories["percentage_of_all_products"] = (
    top_categories["product_count"] / len(df) * 100
).round(2)
save_csv(top_categories, "11_top_15_categories.csv")


# ------------------------------------------------------------
# OUTPUT 12: TOP 20 BRANDS
# ------------------------------------------------------------
# Percentage is calculated against all cleaned products.
top_brands = (
    df["brand"].value_counts().head(20)
    .rename_axis("brand").reset_index(name="product_count")
)
top_brands["percentage_of_all_products"] = (
    top_brands["product_count"] / len(df) * 100
).round(2)
save_csv(top_brands, "12_top_20_brands.csv")


# ------------------------------------------------------------
# OUTPUT 13: CATEGORY-BRAND PERFORMANCE
# ------------------------------------------------------------
# Restrict to the ten largest categories and ten largest brands to
# keep this comparison compact enough for dashboards.
top_10_categories = df["primary_category"].value_counts().head(10).index
top_10_brands = df["brand"].value_counts().head(10).index

category_brand_performance = df[
    df["primary_category"].isin(top_10_categories)
    & df["brand"].isin(top_10_brands)
].groupby(["primary_category", "brand"]).agg(
    product_count=("product_id", "count"),
    avg_retail_price=("retail_price", "mean"),
    avg_discount_pct=("historical_discount_pct", "mean"),
    avg_rating=("overall_rating", "mean"),
).reset_index().round(2).rename(
    columns={"primary_category": "category"}
)
save_csv(category_brand_performance, "13_category_brand_performance.csv")


# ============================================================
# STEP 8: GENERATE THE SUMMARY REPORT AND QUALITY CHECKS
# ============================================================

print("\n" + "=" * 72)
print("STEP 8: SUMMARY REPORT AND OUTPUT VALIDATION")
print("=" * 72)

# Calculate the main descriptive metrics used in the report.
average_rating = df["overall_rating"].mean()
rated_count = int(df["overall_rating"].notna().sum())
rating_coverage = rated_count / len(df) * 100
top_category = df["primary_category"].value_counts().idxmax()
top_category_count = int(df["primary_category"].value_counts().max())
top_brand = df["brand"].value_counts().idxmax()
top_brand_count = int(df["brand"].value_counts().max())

# These are expected deliverables. The extra correlation coefficient
# file is also included for convenience.
expected_files = [
    "01_cleaned_flipkart_products.csv",
    "02_price_distribution.csv",
    "03_category_summary.csv",
    "04_brand_summary.csv",
    "05_discount_analysis.csv",
    "06_price_band_segmentation.csv",
    "07_category_priceband_matrix.csv",
    "08_rating_distribution.csv",
    "09_category_discount_tier.csv",
    "10_correlation_analysis.csv",
    "10b_correlation_coefficients.csv",
    "11_top_15_categories.csv",
    "12_top_20_brands.csv",
    "13_category_brand_performance.csv",
]

# Missing values can remain in overall_rating by design. Category and
# brand labels are filled to make grouped dashboard tables easier.
missing_by_column = df.isna().sum()
report_lines = [
    "PROMOSENSE - DATA PREPROCESSING AND EDA SUMMARY REPORT",
    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    "",
    "1. DATASET OVERVIEW",
    f"Input file: {INPUT_FILE.name}",
    f"Rows in original selected dataset: {initial_row_count:,}",
    f"Rows after cleaning: {len(df):,}",
    f"Columns in cleaned dataset: {len(df.columns)}",
    "",
    "2. CLEANING ACTIONS",
    f"Rows removed for missing product name: {removed_missing_name:,}",
    f"Rows removed for missing prices: {removed_missing_prices:,}",
    f"Rows removed for non-positive prices: {removed_nonpositive_prices:,}",
    f"Rows removed for discounted price above retail price: {removed_discount_logic:,}",
    f"Exact duplicate rows removed: {removed_duplicates:,}",
    f"Invalid ratings changed to missing: {invalid_rating_count:,}",
    f"Retail-price outliers flagged (not deleted): {outlier_count:,}",
    "",
    "3. PRICING METRICS",
    f"Average retail price: {df['retail_price'].mean():,.2f}",
    f"Median retail price: {df['retail_price'].median():,.2f}",
    f"Average discounted price: {df['discounted_price'].mean():,.2f}",
    f"Average discount amount: {df['discount_amount'].mean():,.2f}",
    f"Average discount percentage: {df['historical_discount_pct'].mean() * 100:.2f}%",
    f"Minimum discount percentage: {df['historical_discount_pct'].min() * 100:.2f}%",
    f"Maximum discount percentage: {df['historical_discount_pct'].max() * 100:.2f}%",
    "",
    "4. CATEGORY AND BRAND OVERVIEW",
    f"Number of categories: {df['primary_category'].nunique():,}",
    f"Most common category: {top_category} ({top_category_count:,} products)",
    f"Number of brands, including Unknown: {df['brand'].nunique():,}",
    f"Most common brand: {top_brand} ({top_brand_count:,} products)",
    "",
    "5. RATINGS",
    f"Products with valid ratings: {rated_count:,}",
    f"Rating coverage: {rating_coverage:.2f}%",
    f"Average rating: {average_rating:.2f}" if pd.notna(average_rating)
    else "Average rating: Not available",
    "",
    "6. PRICE BAND THRESHOLDS",
    f"33.33rd percentile retail price: {price_q33:.2f}",
    f"66.67th percentile retail price: {price_q67:.2f}",
    "Note: bands are relative to this dataset and may change when the data changes.",
    "",
    "7. REMAINING MISSING VALUES",
]
for column, count in missing_by_column.items():
    report_lines.append(f"{column}: {int(count):,}")

report_lines.extend([
    "",
    "8. OUTPUT FILES",
])
for filename in expected_files:
    path = OUTPUT_DIR / filename
    if path.exists():
        report_lines.append(
            f"OK - {filename} ({path.stat().st_size / 1024:.2f} KB)"
        )
    else:
        report_lines.append(f"MISSING - {filename}")

report_lines.extend([
    "",
    "9. ORACLE APEX DASHBOARD SUGGESTIONS",
    "03_category_summary.csv: bar charts for product count and average prices by category.",
    "04_brand_summary.csv: top brands and average rating comparisons.",
    "05_discount_analysis.csv: largest discount amounts and percentages.",
    "06_price_band_segmentation.csv: Budget/Mid-Range/Premium distribution.",
    "07_category_priceband_matrix.csv: category versus price-band heatmap or stacked bars.",
    "08_rating_distribution.csv: product rating frequency chart.",
    "09_category_discount_tier.csv: discount tier comparison by category.",
    "10_correlation_analysis.csv: scatter plots of prices, discounts, and ratings.",
    "11_top_15_categories.csv: most represented categories.",
    "12_top_20_brands.csv: most represented brands.",
    "13_category_brand_performance.csv: compare leading brands within leading categories.",
    "",
    "10. INTERPRETATION AND LIMITATIONS",
    "This dataset describes listed prices, discounts, categories, brands, and ratings.",
    "It does not by itself contain actual sales, conversion, cost, or profit data.",
    "Listed discounts must not be interpreted as proof of increased sales or profitability.",
    "Correlation does not establish causation. An A/B test needs a defined treatment,",
    "control group, outcome metric, sample-size plan, and experiment data.",
    "",
    "END OF REPORT",
])

report_text = "\n".join(report_lines)
report_path = OUTPUT_DIR / "00_SUMMARY_REPORT.txt"
report_path.write_text(report_text, encoding="utf-8")

# Validate that every expected file exists and can be read back.
print("\nOutput file validation:")
all_outputs_valid = True
for filename in expected_files:
    path = OUTPUT_DIR / filename
    if path.exists():
        try:
            # Read a small amount to verify the CSV is parseable.
            pd.read_csv(path, nrows=5)
            print(f"OK: {filename} ({path.stat().st_size / 1024:.2f} KB)")
        except Exception as error:
            all_outputs_valid = False
            print(f"ERROR reading {filename}: {error}")
    else:
        all_outputs_valid = False
        print(f"MISSING: {filename}")

print(f"\nSummary report saved: {report_path}")
print("\n" + "=" * 72)
if all_outputs_valid:
    print("SUCCESS: EDA complete. Output CSV files are ready for Oracle APEX import.")
else:
    print("WARNING: EDA finished, but one or more output files need checking.")
print(f"Output folder: {OUTPUT_DIR}")
print("=" * 72)
