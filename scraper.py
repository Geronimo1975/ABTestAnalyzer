import trafilatura
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
from urllib.parse import urljoin
import time

class InventoryScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_page_content(self, url):
        """Safely get page content with retry mechanism"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    print(f"Failed to fetch {url}: {str(e)}")
                    return None
                time.sleep(1)  # Wait before retrying
                
    def extract_product_data(self, html):
        """Extract product information from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Adjust these selectors based on the actual website structure
        product_elements = soup.select('.product-item')  # Update selector
        
        for element in product_elements:
            try:
                product = {
                    'name': element.select_one('.product-name').text.strip(),
                    'sku': element.get('data-sku', ''),
                    'price': float(element.select_one('.price').text.strip().replace('€', '').replace(',', '.')),
                    'stock': int(element.select_one('.stock').text.strip().split()[0]),
                    'image_url': urljoin(self.base_url, element.select_one('img')['src']),
                    'category': element.select_one('.category').text.strip(),
                    'scraped_at': datetime.now().isoformat()
                }
                products.append(product)
            except (AttributeError, ValueError, KeyError) as e:
                print(f"Error extracting product data: {str(e)}")
                continue
                
        return products
    
    def download_image(self, image_url, product_sku):
        """Download and save product image"""
        try:
            response = self.session.get(image_url)
            response.raise_for_status()
            
            # Create images directory if it doesn't exist
            os.makedirs('product_images', exist_ok=True)
            
            # Save image
            image_path = f'product_images/{product_sku}.jpg'
            with open(image_path, 'wb') as f:
                f.write(response.content)
            return image_path
        except Exception as e:
            print(f"Error downloading image {image_url}: {str(e)}")
            return None
    
    def scrape_inventory(self):
        """Main scraping function"""
        print("Starting inventory scrape...")
        
        # Get main page content
        html = self.get_page_content(self.base_url)
        if not html:
            return []
        
        # Extract product data
        products = self.extract_product_data(html)
        
        # Download images
        for product in products:
            image_path = self.download_image(product['image_url'], product['sku'])
            if image_path:
                product['local_image_path'] = image_path
        
        # Save data to JSON
        with open('inventory_data.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        print(f"Scraping completed. Found {len(products)} products.")
        return products

def main():
    base_url = "https://b2b.unimall.lt/"
    scraper = InventoryScraper(base_url)
    inventory_data = scraper.scrape_inventory()
    
    # Print summary
    if inventory_data:
        print("\nInventory Summary:")
        categories = {}
        total_stock = 0
        
        for product in inventory_data:
            categories[product['category']] = categories.get(product['category'], 0) + 1
            total_stock += product['stock']
        
        print(f"\nTotal Products: {len(inventory_data)}")
        print(f"Total Stock Items: {total_stock}")
        print("\nProducts by Category:")
        for category, count in categories.items():
            print(f"- {category}: {count} products")

if __name__ == "__main__":
    main()
