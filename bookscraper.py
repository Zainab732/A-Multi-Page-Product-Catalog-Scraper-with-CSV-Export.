# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 03:56:34 2025

@author: Zainab
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

# The starting URL for the target website (a sandbox site for scraping practice)
BASE_URL = 'https://books.toscrape.com/catalogue/page-{}.html'
PAGES_TO_SCRAPE = 3 # Increase this for a medium-sized project!

def scrape_book_data(url):
    """
    Fetches the page content and extracts data for all books on that page.
    """
    try:
        # 1. Fetch the HTML content
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    # 2. Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all book articles on the page
    articles = soup.find_all('article', class_='product_pod')

    page_data = []
    for book in articles:
        # Extract Title
        title_tag = book.h3.a
        title = title_tag['title'] if title_tag else 'N/A'

        # Extract Price (clean the currency symbol)
        price_tag = book.find('p', class_='price_color')
        price_text = price_tag.text.strip().replace('£', '') if price_tag else 'N/A'
        
        # Extract Rating (convert class name to a number)
        rating_tag = book.find('p', class_='star-rating')
        rating_class = rating_tag['class'][1] if rating_tag and len(rating_tag['class']) > 1 else 'N/A'
        
        rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        rating = rating_map.get(rating_class, 0)
        
        # Store the extracted data
        page_data.append({
            'Title': title,
            'Price': float(price_text) if price_text != 'N/A' else None,
            'Rating': rating
        })
    
    print(f"-> Successfully scraped {len(page_data)} books from: {url}")
    return page_data

def main_scraper(num_pages):
    """
    Orchestrates the scraping process across multiple pages.
    """
    all_books = []
    
    for page in range(1, num_pages + 1):
        url = BASE_URL.format(page)
        print(f"Scraping Page {page}...")
        
        # Get data from the current page
        data = scrape_book_data(url)
        all_books.extend(data)
        
    return all_books

# --- Execution ---
if __name__ == '__main__':
    print("Starting Web Scraper...")
    
    # Run the scraper
    results = main_scraper(PAGES_TO_SCRAPE)
    
    if results:
        # 3. Export Data using Pandas
        df = pd.DataFrame(results)
        
        # Clean up data types
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['Rating'] = df['Rating'].astype(int)
        
        # Save the DataFrame to a CSV file in the same directory as your script
        output_file = 'scraped_books_catalog.csv'
        df.to_csv(output_file, index=False)
        
        print("\n--- Summary ---")
        print(f"Total books scraped: {len(df)}")
        print(f"Data saved successfully to: {output_file}")
        print("\nFirst 5 rows of data:")
        print(df.head())
    else:
        print("No data was scraped. Check for errors.")