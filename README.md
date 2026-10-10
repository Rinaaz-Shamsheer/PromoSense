# PromoSense : Data Preprocessing and Exploratory Data Analysis

## 1. Project Overview

PromoSense is a data analysis project that uses the Flipkart products dataset to explore product pricing, discounts, categories, brands, and customer ratings.

The project uses Python for data preprocessing and Exploratory Data Analysis (EDA). The processed data and analysis summaries are exported as CSV files for use in an Oracle APEX dashboard.

**Main objective:** Analyze historical product pricing and discount patterns to generate insights that can support pricing and promotional decisions.

## 2. Technologies Used

- **Python** — Data preprocessing and analysis
- **Pandas** — Data manipulation and analysis
- **NumPy** — Numerical operations
- **Oracle APEX** — Dashboard development and visualization
- **CSV** — Data storage and transfer between Python and Oracle APEX

## 3. Project Structure

```text
PromoSense/
│
├── data_preprocessing_eda.py
├── flipkart_com-ecommerce_sample.csv
│
└── cleaned_data_exports/
    ├── 01_cleaned_flipkart_products.csv
    ├── 02_price_distribution.csv
    ├── 03_category_summary.csv
    ├── 04_brand_summary.csv
    ├── 05_discount_analysis.csv
    ├── 06_price_band_segmentation.csv
    ├── 07_category_priceband_matrix.csv
    ├── 08_rating_distribution.csv
    ├── 09_category_discount_tier.csv
    ├── 10_correlation_analysis.csv
    ├── 10b_correlation_coefficients.csv
    ├── 11_top_15_categories.csv
    ├── 12_top_20_brands.csv
    ├── 13_category_brand_performance.csv
    └── 00_SUMMARY_REPORT.txt
```

## 4. Dataset

**Dataset:** `flipkart_com-ecommerce_sample.csv`

The dataset contains product information such as:

- Product name
- Product category
- Retail price
- Discounted price
- Brand
- Overall rating

These columns are used to study pricing patterns, calculate discounts, compare product categories, and explore ratings.

## 5. Installation and Setup

### Prerequisites

- Python 3.9 or newer recommended
- The Flipkart dataset CSV file
- An Oracle APEX workspace for dashboard development

### Install Required Libraries

Open Command Prompt or a terminal and run:

```bash
python -m pip install pandas numpy
```

If the `python` command is not recognized on Windows, try:

```bash
py -m pip install pandas numpy
```

## 6. How to Run the Project

### Step 1: Run the Python Script

```bash
python data_preprocessing_eda.py
```

### Step 2: Check the Outputs

After successful execution, the script creates a folder named `cleaned_data_exports` containing the cleaned dataset, EDA summaries, and a summary report.

Run the script again whenever the original dataset changes.

## 7. Data Preprocessing

The preprocessing stage performs the following operations:

1. Loads the original CSV dataset.
2. Inspects column names, data types, missing values, and descriptive statistics.
3. Cleans text values and converts price and rating columns into numeric values.
4. Removes rows with missing product names or prices.
5. Removes rows containing non-positive prices.
6. Removes rows where the discounted price exceeds the retail price, based on the project's data-cleaning assumption.
7. Removes duplicate rows.
8. Marks ratings outside the expected range of 1–5 as missing.
9. Handles missing category and brand values.
10. Creates additional features for further analysis.

### Feature Engineering

The script creates the following columns:

- `product_id` — Generated identifier for the cleaned dataset.
- `primary_category` — Main category extracted from the category hierarchy.
- `discount_amount` — Difference between retail price and discounted price.
- `historical_discount_pct` — Discount fraction between 0 and 1.
- `historical_discount_percent` — Discount percentage between 0 and 100.
- `price_band` — Product segment: Budget, Mid-Range, or Premium.
- `discount_tier` — Group of products based on discount percentage.
- `retail_price_outlier_flag` — Indicates whether the retail price is an outlier using the IQR method.

## 8. Exploratory Data Analysis

The EDA stage studies the following areas:

### Price Analysis
- Retail and discounted price statistics
- Price distributions
- Discount amounts
- Price outliers

### Category Analysis
- Product counts by category
- Average retail and discounted prices
- Average discount percentages
- Category-wise rating comparisons
- Category and price-band segmentation

### Brand Analysis
- Product counts by brand
- Average prices by brand
- Average discount percentages
- Average ratings by brand

### Discount Analysis
- Distribution of discount percentages
- Product counts by discount tier
- Category-wise discount comparisons
- Correlations between numerical variables

### Rating Analysis
- Distribution of product ratings
- Average ratings across price bands
- Category-wise rating comparisons

## 9. Output Files

The generated CSV files can be used to create reports and visualizations.

| Output | Purpose |
|---|---|
| `01_cleaned_flipkart_products.csv` | Cleaned product-level data |
| `02_price_distribution.csv` | Price distribution analysis |
| `03_category_summary.csv` | Category-wise product and pricing summary |
| `04_brand_summary.csv` | Brand-wise product and pricing summary |
| `05_discount_analysis.csv` | Discount analysis |
| `06_price_band_segmentation.csv` | Comparison of price segments |
| `07_category_priceband_matrix.csv` | Category versus price-band comparison |
| `08_rating_distribution.csv` | Rating distribution |
| `09_category_discount_tier.csv` | Category and discount-tier analysis |
| `10_correlation_analysis.csv` | Correlation-related analysis |
| `10b_correlation_coefficients.csv` | Numerical correlation coefficients |
| `11_top_15_categories.csv` | Top categories by product count |
| `12_top_20_brands.csv` | Top brands by product count |
| `13_category_brand_performance.csv` | Category and brand comparison |
| `00_SUMMARY_REPORT.txt` | Summary of the preprocessing and analysis |


## 10. Oracle APEX Dashboard

The generated CSV files can be imported into Oracle APEX and used to create a dashboard.

### Suggested Dashboard Components

- **KPI Cards:** Total products, average retail price, average discounted price, and average discount percentage.
- **Category Chart:** Compare product counts or average discounts by category.
- **Brand Analysis:** Compare brands by product count, price, and rating.
- **Price Distribution Chart:** Show how products are distributed across price ranges.
- **Discount Analysis Chart:** Display the number of products in each discount tier.
- **Rating Chart:** Show the distribution of product ratings.
- **Product Report:** Display product names, categories, prices, discounts, and ratings.

### Importing CSV Files

1. Open your Oracle APEX workspace.
2. Navigate to SQL Workshop and locate the CSV data-loading option.
3. Upload the required CSV files and load them into database tables.
4. Open App Builder and create or edit the PromoSense application.
5. Add charts, reports, and KPI cards using the imported tables.

The exact menu labels may vary depending on your Oracle APEX version.

## 11. Limitations

- Price bands are based on the retail-price distribution of the dataset and are not universal market categories.
- Missing ratings are not replaced with guessed values.
- Price outliers are flagged rather than automatically removed.
- Historical listed discounts do not establish whether a discount caused an increase in sales or profit.
- The dataset does not provide the actual sales, conversion, or profit outcomes required to evaluate promotional effectiveness conclusively.

A proper A/B discount experiment would require treatment and control groups, along with suitable outcome data such as purchases, conversion rates, or profit.

## 12. Conclusion

PromoSense transforms raw Flipkart product data into a cleaned dataset and structured EDA summaries. These outputs can be imported into Oracle APEX to create an interactive dashboard for exploring product pricing, discounts, categories, brands, and ratings.

The project provides a foundation for further pricing experiments and promotional analysis when suitable sales or experiment-outcome data becomes available.