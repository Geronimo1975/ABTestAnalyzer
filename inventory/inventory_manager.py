import json
from .product import Product
import pandas as pd

class InventoryManager:
    def __init__(self):
        self.products = {}  # Dictionary to store products with SKU as key

    def add_product(self, product):
        """Add a new product to the inventory"""
        if product.sku and product.sku not in self.products:
            self.products[product.sku] = product
            return True
        return False

    def add_products(self, products_data):
        """Add multiple products from scraped data"""
        for product_data in products_data:
            product = Product(
                name=product_data['name'],
                price=product_data['price'],
                quantity=product_data['stock'],
                category=product_data['category'],
                sku=product_data['sku']
            )
            if product_data.get('local_image_path'):
                product.set_image_path(product_data['local_image_path'])
            self.add_product(product)

    def remove_product(self, sku):
        """Remove a product from the inventory"""
        if sku in self.products:
            del self.products[sku]
            return True
        return False

    def update_product_quantity(self, sku, new_quantity):
        """Update the quantity of a product"""
        if sku in self.products:
            return self.products[sku].update_quantity(new_quantity)
        return False

    def get_product_info(self, sku):
        """Get information about a specific product"""
        if sku in self.products:
            return self.products[sku].get_product_info()
        return None

    def get_all_products(self):
        """Get information about all products"""
        return {sku: product.get_product_info() for sku, product in self.products.items()}

    def get_total_inventory_value(self):
        """Calculate the total value of all inventory"""
        return sum(product.get_stock_value() for product in self.products.values())

    def get_low_stock_products(self, threshold=10):
        """Get list of products with stock below threshold"""
        return [product.get_product_info() for product in self.products.values() 
                if product.quantity <= threshold]

    def get_products_by_category(self, category):
        """Get all products in a specific category"""
        return {sku: product.get_product_info() 
                for sku, product in self.products.items() 
                if product.category == category}

    def save_to_json(self, filename='inventory_data.json'):
        """Save inventory data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.get_all_products(), f, indent=2)

    def load_from_json(self, filename='inventory_data.json'):
        """Load inventory data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.products = {}
                for sku, info in data.items():
                    product = Product(
                        name=info['name'],
                        price=info['price'],
                        quantity=info['quantity'],
                        category=info['category'],
                        sku=sku
                    )
                    if info.get('image_path'):
                        product.set_image_path(info['image_path'])
                    self.products[sku] = product
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def export_to_excel(self, filename, filters=None):
        """
        Export inventory data to Excel with optional filters
        filters: dict with keys as column names and values as filter conditions
        """
        # Get all products data
        products_data = self.get_all_products()

        # Convert to DataFrame
        df = pd.DataFrame.from_dict(products_data, orient='index')

        # Apply filters if provided
        if filters:
            for column, condition in filters.items():
                if column in df.columns:
                    if isinstance(condition, (list, tuple)):
                        df = df[df[column].isin(condition)]
                    elif isinstance(condition, dict):
                        if 'min' in condition:
                            df = df[df[column] >= condition['min']]
                        if 'max' in condition:
                            df = df[df[column] <= condition['max']]
                    else:
                        df = df[df[column] == condition]

        # Save to Excel
        df.to_excel(filename, index=True, index_label='SKU')
        return True