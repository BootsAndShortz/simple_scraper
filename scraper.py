import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_url(url):
    """Validate that the URL is well-formed and uses HTTP/HTTPS."""
    try:
        result = urlparse(url)
        if not all([result.scheme in ('http', 'https'), result.netloc]):
            raise ValueError("Invalid URL: Must be HTTP/HTTPS and include a domain.")
        return True
    except ValueError as e:
        logger.error(f"URL validation failed: {e}")
        raise

def extract_lot_data(lot, base_url):
    """Extract data from a single lot element."""
    lot_id = lot.get('data-lotid', '')
    lot_number = lot.get('data-lotnumber', '')

    try:
        lot_num_int = int(lot_number)
        if not (lot_num_int-1 <= lot_num_int <= lot_num_int+1):
            logger.debug(f"Skipping lot {lot_number}: Out of range ({lot_num_int-1} - {lot_num_int+1}))")
            return None
    except ValueError:
        logger.warning(f"Invalid lot number: {lot_number}")
        return None

    data = {
        'Lot ID': lot_id,
        'Lot No': lot_number,
        'Title': '',
        'Lot Details Link': '',
        'Price': '',
        'UPC': '',
        'Brand': '',
        'Model': '',
        'Color Family': '',
        'Color/Finish': '',
        'Commercial/Residential': '',
        'Edge Type': '',
        'Pieces Per Case': '',
        'Plank Length': '',
        'Plank Width': '',
        'Product Weight (lb.)': '',
        'Approximate Plank Size (in.)': '',
        'Product Length (in.)': '',
        'Product Thickness (mm)': '',
        'Product Width (in.)': '',
        'Wear Layer Thickness (mil)': ''
    }

    # Extract title
    title_selectors = [
        ('div', {'class': 'title'}),
        ('div', {'class': re.compile('lot.*title.*', re.I)}),
        ('div', {'class': re.compile('lot.*title.*', re.I)})
    ]
    for tag, attrs in title_selectors:
        title_element = lot.find(tag, attrs)
        if title_element:
            data['Title'] = title_element.text.strip()
            logger.debug(f"Found title for lot {lot_number}: {data['Title'][:50]}...")
            break
    else:
        logger.warning(f"No title found for lot {lot_number}")

    # Extract lot details link
    link_element = lot.find('a', href=True)
    if link_element:
        href = link_element['href']
        data['Lot Details Link'] = f"https://bids.crauctions.com{href}" if href.startswith('/') else href
        logger.debug(f"Found lot link for lot {lot_number}")

    # Extract Price
    bid_selectors = [
        ('span', {'class': 'current-bid'}),
        ('div', {'class': 'winning-bid-amount'}),
        ('span', {'class': re.compile('bid.*', re.I)})
    ]
    for tag, attrs in bid_selectors:
        bid_element = lot.find(tag, attrs)
        if bid_element:
            data['Price'] = bid_element.text.strip()
            logger.debug(f"Found Price for lot {lot_number}: {data['Price']}")
            break
    else:
        logger.warning(f"No Price found for lot {lot_number}")

    # Extract description fields
    description_sections = lot.find_all(['div', 'p', 'span'], class_=re.compile('description|details|lot.*|info.*', re.I))
    description_text = ' '.join(section.text.strip() for section in description_sections if section.text.strip())

    if description_text:
        fields = {
            'UPC': r'UPC[:\s]*([^\n,;]+)',
            'Brand': r'Brand[:\s]*([^\n,;]+)',
            'Model': r'Model[:\s]*([^\n,;]+)',
            'Color Family': r'Color Family[:\s]*([^\n,;]+)',
            'Color/Finish': r'Color/Finish[:\s]*([^\n,;]+)',
            'Commercial/Residential': r'Commercial\s*/\s*Residential[:\s]*([^\n,;]+)',
            'Edge Type': r'Edge Type[:\s]*([^\n,;]+)',
            'Pieces Per Case': r'Pieces Per Case[:\s]*([^\n,;]+)',
            'Plank Length': r'Plank Length[:\s]*([^\n,;]+)',
            'Plank Width': r'Plank Width[:\s]*([^\n,;]+)',
            'Product Weight (lb.)': r'Product Weight\s*\(lb\.\)[:\s]*([^\n,;]+)',
            'Approximate Plank Size (in.)': r'Approximate Plank Size\s*\(in\.\)[:\s]*([^\n,;]+)',
            'Product Length (in.)': r'Product Length\s*\(in\.\)[:\s]*([^\n,;]+)',
            'Product Thickness (mm)': r'Product Thickness\s*\(mm\)[:\s]*([^\n,;]+)',
            'Product Width (in.)': r'Product Width\s*\(in\.\)[:\s]*([^\n,;]+)',
            'Wear Layer Thickness (mil)': r'Wear Layer Thickness\s*\(mil\)[:\s]*([^\n,;]+)'
        }
        for key, pattern in fields.items():
            match = re.search(pattern, description_text, re.IGNORECASE)
            if match:
                data[key] = match.group(1).strip()
                logger.debug(f"Found {key} for lot {lot_number}")

    return data

def scrape_auction_page(url, headers):
    """Scrape auction page and return lot data."""
    try:
        validate_url(url)
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        lot_elements = soup.find_all('div', class_='lot', attrs={'data-lotnumber': True})
        if not lot_elements:
            logger.error("No lot elements found on the page")
            raise ValueError("No lots found")

        lot_data_list = []
        for lot in lot_elements:
            lot_data = extract_lot_data(lot, url)
            if lot_data:
                lot_data_list.append(lot_data)

        if not lot_data_list:
            logger.warning(f"No valid lots found in range '({lot_num_int-1} - {lot_num_int+1}")
            return None

        df = pd.DataFrame(lot_data_list)
        df.to_csv('data_all.csv', index=False)
        logger.info("Data saved to data_all.csv")
        return df

    except Exception as e:
        logger.error(f"Error fetching auction page: {e}")
        raise

def trim_data_all_csv(input_file='data_all.csv', output_file='data_trimmed.csv'):
    """Trim CSV to specified columns."""
    columns_to_keep = {'Lot ID', 'Lot No', 'Title', 'Price', 'UPC', 'Brand', 'Model', 'Lot Details Link'}
    try:
        logger.info(f"Reading input file: {input_file}")
        df = pd.read_csv(input_file)

        missing_columns = columns_to_keep - set(df.columns)
        if missing_columns:
            logger.error(f"Missing columns in CSV: {missing_columns}")
            raise ValueError(f"CSV file is missing required columns: {missing_columns}")

        trimmed_df = df[list(columns_to_keep)]
        trimmed_df.to_csv(output_file, index=False)
        logger.info(f"Trimmed data saved to: {output_file} with {len(trimmed_df)} rows")
        return trimmed_df

    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        raise
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        raise

def get_sqft(title):
    """Extract square footage from title."""
    if not isinstance(title, str):
        logger.warning(f"Invalid title format (not a string): {title}")
        return pd.NA

    # More robust regex for sqft
    match = re.search(r'Approx\s*(\d+\.?\d*)\s*SQ\s*FT', title, re.IGNORECASE)
    if match:
        try:
            sqft = float(match.group(1))
            logger.debug(f"Extracted sqft: {sqft} from title: {title[:50]}...")
            return sqft
        except ValueError:
            logger.warning(f"Could not convert to number in title: {title[:50]}...")
            return pd.NA
    logger.debug(f"No sqft pattern found in title: {title[:50]}...")
    return pd.NA

def get_sqft_and_clean(input_file='data_trimmed.csv', output_file='data_clean.csv'):
    """Extract sqft from Title and trim to specified columns."""
    columns_to_keep = {'Lot No', 'Price', 'sqft', 'cases'}
    try:
        logger.info(f"Reading input file: {input_file}")
        df = pd.read_csv(input_file)

        # Ensure required columns exist
        if 'Title' not in df.columns:
            logger.error("Missing 'Title' column in input CSV")
            raise ValueError("CSV file is missing required 'Title' column")

        if 'sqft' not in df.columns:
            df['sqft'] = pd.NA
            logger.info("Added missing 'sqft' column")
        if 'cases' not in df.columns:
            df['cases'] = pd.NA  # Default to NaN instead of hardcoded 40
            logger.info("Added missing 'cases' column")

        # Extract sqft
        df['sqft'] = df['Title'].apply(get_sqft)
        successful_extractions = df['sqft'].notna().sum()
        logger.info(f"Extracted sqft for {successful_extractions} rows")

        # Trim DataFrame
        missing_columns = columns_to_keep - set(df.columns)
        if missing_columns:
            logger.error(f"Missing columns in CSV: {missing_columns}")
            raise ValueError(f"CSV file is missing required columns: {missing_columns}")

        trimmed_df = df[list(columns_to_keep)]
        trimmed_df.to_csv(output_file, index=False)
        logger.info(f"Trimmed data with sqft saved to: {output_file} with {len(trimmed_df)} rows")
        return trimmed_df

    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        raise
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        raise

if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        url = input("Please enter a valid auction URL (e.g., https://bids.crauctions.com/auctions/123): ")
        scrape_auction_page(url, headers)
        trim_data_all_csv()
        get_sqft_and_clean()
    except Exception as e:
        logger.error(f"Main execution failed: {e}")