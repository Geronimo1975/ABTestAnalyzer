class Product:
    def __init__(self, name, price, quantity, category=None, sku=None):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.category = category
        self.sku = sku
        self.image_path = None

    def update_quantity(self, new_quantity):
        """Update the quantity of the product"""
        if new_quantity >= 0:
            self.quantity = new_quantity
            return True
        return False

    def update_price(self, new_price):
        """Update the price of the product"""
        if new_price >= 0:
            self.price = new_price
            return True
        return False

    def get_product_info(self):
        """Return a dictionary containing product information"""
        return {
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'category': self.category,
            'sku': self.sku,
            'image_path': self.image_path
        }

    def set_image_path(self, path):
        """Set the path to the product image"""
        self.image_path = path

    def get_stock_value(self):
        """Calculate the total value of the product's stock"""
        return self.price * self.quantity
