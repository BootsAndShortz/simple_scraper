import logging
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def costAnalysis(input_file='data_clean.csv', output_file='data_analysis.csv'):
    try:
        # Define the required columns (excluding calculated columns for initial check)
        required_columns = ['Lot No', 'Price', 'sqft', 'cases']
        
        # Read the CSV file
        logger.info(f"Reading input file: {input_file}")
        df = pd.read_csv(input_file)

        # Verify that required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing columns in CSV: {missing_columns}")
            raise ValueError(f"CSV file is missing required columns: {missing_columns}")

        # Clean 'Price' column (remove $ and commas, convert to float)
        logger.info("Cleaning 'Price' column")
        df['Price'] = df['Price'].replace(r'[\$,]', '', regex=True).astype(float)

        # Add 'sqft' column with default NaN if missing
        if 'sqft' not in df.columns:
            df['sqft'] = pd.NA
            logger.info("Added missing 'sqft' column with NaN values")

        # Add 'cases' column with default value 40 if missing
        if 'cases' not in df.columns:
            df['cases'] = 40
            logger.info("Added missing 'cases' column with default value 40")

        # Calculate 'Price/sqft' (handle NaN and division by zero)
        logger.info("Calculating 'Price/sqft'")
        df['Price/sqft'] = df.apply(
            lambda row: row['Price'] / row['sqft'] if pd.notna(row['sqft']) and row['sqft'] != 0 else pd.NA,
            axis=1
        )

        # Calculate 'Price/case' (handle NaN and division by zero)
        logger.info("Calculating 'Price/case'")
        df['Price/case'] = df.apply(
            lambda row: row['Price'] / row['cases'] if pd.notna(row['cases']) and row['cases'] != 0 else pd.NA,
            axis=1
        )

        # Select only the required columns for output
        output_columns = ['Lot No', 'Price', 'sqft', 'cases', 'Price/sqft', 'Price/case']
        df = df[output_columns]

        # Save the updated DataFrame to the output CSV
        logger.info(f"Saving results to: {output_file}")
        df.to_csv(output_file, index=False)

        # Log and display the result
        logger.info("Analysis completed successfully")
        print(df)

    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        raise
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        raise

# Run the function
if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
#        url = input("Please enter a valid auction URL (e.g., https://bids.crauctions.com/auctions/123): ")
#        scrape_auction_page(url, headers)
        costAnalysis()
#        get_sqft_and_clean()
    except Exception as e:
        logger.error(f"Main execution failed: {e}")