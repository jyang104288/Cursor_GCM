import pandas as pd
from bs4 import BeautifulSoup  # Import BeautifulSoup
from urllib.parse import urlparse
import requests  # Import requests to fetch HTML content

def extract_home_site_address():
    # Load the Excel file
    file_path = r"C:\Users\104288\UL Solutions\GMA - Global Market Access - AI POC\Raw_Data_1.xlsx"
    # Read all sheets into a dictionary of DataFrames
    all_sheets = pd.read_excel(file_path, sheet_name=None)
    
    # Access the specific sheets you want to modify
    df_source = all_sheets['sourceURL']
    df_valid = all_sheets['valid']  # Assuming 'valid' is the name of the tab with valid URLs

    # Initialize lists to store extracted URLs and announce text
    extracted_urls = []
    announce_texts = []
    home_sites = []  # List to store extracted home sites

    # Get valid URLs from the 'valid' tab
    valid_urls = [url.lower().rstrip('/') for url in df_valid['valid_url'].tolist()]  # Normalize valid URLs

    # Iterate through the 'link' column for existing URLs
    for html_content in df_source['link']:
        # Convert to string and handle NaN values
        html_str = str(html_content) if pd.notna(html_content) else ""
        
        # Check if html_str is a URL
        if html_str.startswith("http://") or html_str.startswith("https://"):
            # Extract the home site address directly from the URL
            parsed_url = urlparse(html_str)  # Parse the URL
            home_site = f"{parsed_url.scheme}://{parsed_url.netloc}"  # Construct home site address
            extracted_urls.append(home_site)  # Store the home site
            announce_texts.append("")  # Append empty text as per your requirement
            home_sites.append(home_site)  # Store the home site
        else:
            extracted_urls.append(None)  # Not a valid URL format
            announce_texts.append("")  # Append empty text
            home_sites.append(None)

    # Add the extracted URLs and announce text to the DataFrame
    df_source['URL'] = extracted_urls
    df_source['AnnounceText'] = announce_texts  # New column for plain text

    # Create the 'ExtractableURL' column based on the match with valid URLs from the 'valid' tab
    df_source['ExtractableURL'] = df_source['URL'].apply(
        lambda x: 'Yes' if x and x.lower().rstrip('/').replace('https://', 'http://') in valid_urls else 'No'  # Normalize to http
    )  # Added normalization to http

    # Save the updated DataFrame back to the original Excel file without overwriting other sheets
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_source.to_excel(writer, sheet_name='sourceURL', index=False)

# Call the function
extract_home_site_address()
