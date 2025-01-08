import json
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

class InventoryAnalyzer:
    def __init__(self, json_file_path='inventory_data.json'):
        self.json_file_path = json_file_path
        self.load_data()
        
    def load_data(self):
        """Load inventory data from JSON file"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            self.df = pd.DataFrame(self.data)
        except Exception as e:
            print(f"Error loading inventory data: {str(e)}")
            self.data = []
            self.df = pd.DataFrame()
            
    def get_stock_metrics(self):
        """Calculate stock-related metrics"""
        if self.df.empty:
            return {}
            
        return {
            'total_products': len(self.df),
            'total_stock': self.df['stock'].sum(),
            'avg_stock_per_product': self.df['stock'].mean(),
            'out_of_stock_count': len(self.df[self.df['stock'] == 0]),
            'categories': self.df['category'].value_counts().to_dict()
        }
        
    def create_category_distribution_chart(self):
        """Create a pie chart of product distribution by category"""
        if self.df.empty:
            return None
            
        category_counts = self.df['category'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=category_counts.index,
            values=category_counts.values,
            hole=.3
        )])
        
        fig.update_layout(
            title="Product Distribution by Category",
            height=400
        )
        
        return fig
        
    def create_stock_level_chart(self):
        """Create a bar chart of stock levels by category"""
        if self.df.empty:
            return None
            
        stock_by_category = self.df.groupby('category')['stock'].sum()
        
        fig = go.Figure(data=[go.Bar(
            x=stock_by_category.index,
            y=stock_by_category.values,
            text=stock_by_category.values,
            textposition='auto',
        )])
        
        fig.update_layout(
            title="Stock Levels by Category",
            xaxis_title="Category",
            yaxis_title="Total Stock",
            height=400
        )
        
        return fig
        
    def get_low_stock_alerts(self, threshold=10):
        """Identify products with low stock"""
        if self.df.empty:
            return []
            
        low_stock = self.df[self.df['stock'] <= threshold].sort_values('stock')
        return low_stock.to_dict('records')
        
    def get_inventory_value(self):
        """Calculate total inventory value"""
        if self.df.empty:
            return 0
            
        return (self.df['stock'] * self.df['price']).sum()
        
    def get_inventory_health_score(self):
        """Calculate overall inventory health score (0-100)"""
        if self.df.empty:
            return 0
            
        # Factors to consider:
        # 1. Stock distribution (variance)
        # 2. Out of stock percentage
        # 3. Category diversity
        
        total_products = len(self.df)
        out_of_stock = len(self.df[self.df['stock'] == 0])
        stock_variance = self.df['stock'].var()
        category_count = len(self.df['category'].unique())
        
        # Calculate component scores
        stock_score = max(0, 100 - (out_of_stock / total_products * 100))
        diversity_score = min(100, category_count * 10)
        distribution_score = max(0, 100 - (stock_variance / 1000))  # Normalize variance
        
        # Weighted average
        health_score = (stock_score * 0.4 + diversity_score * 0.3 + distribution_score * 0.3)
        
        return round(health_score, 2)

def main():
    analyzer = InventoryAnalyzer()
    metrics = analyzer.get_stock_metrics()
    
    print("\nInventory Analysis Summary:")
    print(f"Total Products: {metrics['total_products']}")
    print(f"Total Stock: {metrics['total_stock']}")
    print(f"Average Stock per Product: {metrics['avg_stock_per_product']:.2f}")
    print(f"Out of Stock Products: {metrics['out_of_stock_count']}")
    
    health_score = analyzer.get_inventory_health_score()
    print(f"\nInventory Health Score: {health_score}/100")
    
    total_value = analyzer.get_inventory_value()
    print(f"Total Inventory Value: €{total_value:,.2f}")
    
    low_stock = analyzer.get_low_stock_alerts()
    if low_stock:
        print("\nLow Stock Alerts:")
        for product in low_stock:
            print(f"- {product['name']}: {product['stock']} units remaining")

if __name__ == "__main__":
    main()
