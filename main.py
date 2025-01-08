import streamlit as st
import plotly.graph_objects as go
from inventory.inventory_manager import InventoryManager
from scraper import InventoryScraper
import os

def main():
    st.set_page_config(
        page_title="Inventory Management System",
        layout="wide"
    )

    st.title("Warehouse Inventory Management System")

    # Initialize inventory manager
    inventory_manager = InventoryManager()

    # Scraping section
    st.header("Inventory Data Collection")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        Analyze current inventory data from B2B website. 
        Click the button below to fetch fresh inventory data.
        """)

        if st.button("Fetch Latest Inventory Data"):
            with st.spinner("Scraping inventory data..."):
                scraper = InventoryScraper("https://b2b.unimall.lt/")
                inventory_data = scraper.scrape_inventory()
                inventory_manager.add_products(inventory_data) #add scraped data to inventory manager
                inventory_manager.save_to_json() #save after scraping
                st.success(f"Successfully scraped {len(inventory_data)} products!")

    # Load existing inventory data
    inventory_manager.load_from_json()
    products = inventory_manager.get_all_products()

    if products:
        # Display key metrics
        total_value = inventory_manager.get_total_inventory_value()
        low_stock = inventory_manager.get_low_stock_products()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Total Products",
                len(products),
                delta=None
            )
        with col2:
            st.metric(
                "Total Inventory Value",
                f"€{total_value:,.2f}",
                delta=None
            )
        with col3:
            st.metric(
                "Low Stock Items",
                len(low_stock),
                delta=None
            )

        # Product Categories Analysis
        st.subheader("Product Categories")
        categories = {}
        for product in products.values():
            cat = product['category']
            categories[cat] = categories.get(cat, 0) + 1

        fig = go.Figure(data=[go.Pie(
            labels=list(categories.keys()),
            values=list(categories.values()),
            hole=.3
        )])
        fig.update_layout(title="Product Distribution by Category")
        st.plotly_chart(fig, use_container_width=True)

        # Low Stock Alerts
        if low_stock:
            st.subheader("Low Stock Alerts")
            for product in low_stock:
                st.warning(
                    f"**{product['name']}**\n\n"
                    f"Current Stock: {product['quantity']} units\n\n"
                    f"Category: {product['category']}"
                )

        # Product List
        st.subheader("Product List")
        for sku, product in products.items():
            with st.expander(f"{product['name']} ({sku})"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"Category: {product['category']}")
                    st.write(f"Price: €{product['price']:.2f}")
                    st.write(f"Quantity: {product['quantity']}")
                    st.write(f"Total Value: €{product['price'] * product['quantity']:.2f}")
                with col2:
                    if product.get('image_path'):
                        st.image(product['image_path'], width=100)

    else:
        st.info("No inventory data available. Please fetch data using the button above.")

if __name__ == "__main__":
    main()