import streamlit as st
import plotly.graph_objects as go
from inventory.inventory_manager import InventoryManager
from scraper import InventoryScraper
import os
from tempfile import NamedTemporaryFile

def create_product_comparison_chart(product1, product2, metric):
    """Create a bar chart comparing two products"""
    fig = go.Figure(data=[
        go.Bar(name=product1['name'], x=[metric], y=[product1[metric]]),
        go.Bar(name=product2['name'], x=[metric], y=[product2[metric]])
    ])
    fig.update_layout(barmode='group', height=300)
    return fig

def main():
    st.set_page_config(
        page_title="Inventory Management System",
        layout="wide"
    )

    st.title("Warehouse Inventory Management System")

    # Initialize inventory manager
    inventory_manager = InventoryManager()

    # Add tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Inventory Overview", "Product Comparison", "Export Data"])

    with tab1:
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
                    inventory_manager.add_products(inventory_data)
                    inventory_manager.save_to_json()
                    st.success(f"Successfully scraped {len(inventory_data)} products!")

        # Load existing inventory data
        inventory_manager.load_from_json()
        products = inventory_manager.get_all_products()

        if not products:
            st.info("No inventory data available. Please fetch data using the button above.")
            return

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

    with tab2:
        st.header("Product Comparison")

        if not products:
            st.info("Please fetch inventory data first to enable product comparison.")
            return

        # Product selection
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Product 1")
            product1_sku = st.selectbox(
                "Select first product",
                options=list(products.keys()),
                format_func=lambda x: products[x]['name']
            )
            product1 = products[product1_sku]

        with col2:
            st.subheader("Product 2")
            remaining_skus = [sku for sku in products.keys() if sku != product1_sku]
            product2_sku = st.selectbox(
                "Select second product",
                options=remaining_skus,
                format_func=lambda x: products[x]['name']
            )
            product2 = products[product2_sku]

        # Comparison metrics
        st.subheader("Comparison Analysis")

        # Basic information comparison
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### {product1['name']}")
            st.write(f"**Category:** {product1['category']}")
            st.write(f"**Price:** €{product1['price']:.2f}")
            st.write(f"**Quantity:** {product1['quantity']}")
            st.write(f"**Total Value:** €{product1['price'] * product1['quantity']:.2f}")
            if product1.get('image_path'):
                st.image(product1['image_path'], width=200)

        with col2:
            st.markdown(f"### {product2['name']}")
            st.write(f"**Category:** {product2['category']}")
            st.write(f"**Price:** €{product2['price']:.2f}")
            st.write(f"**Quantity:** {product2['quantity']}")
            st.write(f"**Total Value:** €{product2['price'] * product2['quantity']:.2f}")
            if product2.get('image_path'):
                st.image(product2['image_path'], width=200)

        # Visual comparisons
        st.subheader("Visual Comparisons")

        # Price comparison
        st.write("#### Price Comparison")
        price_chart = create_product_comparison_chart(product1, product2, 'price')
        st.plotly_chart(price_chart, use_container_width=True)

        # Quantity comparison
        st.write("#### Quantity Comparison")
        quantity_chart = create_product_comparison_chart(product1, product2, 'quantity')
        st.plotly_chart(quantity_chart, use_container_width=True)

        # Additional analysis
        st.subheader("Additional Analysis")

        # Calculate and display price difference
        price_diff = ((product2['price'] - product1['price']) / product1['price']) * 100
        st.metric(
            "Price Difference",
            f"€{abs(product2['price'] - product1['price']):.2f}",
            f"{price_diff:+.1f}%"
        )

        # Calculate and display stock level difference
        stock_diff = ((product2['quantity'] - product1['quantity']) / product1['quantity']) * 100
        st.metric(
            "Stock Level Difference",
            f"{abs(product2['quantity'] - product1['quantity'])} units",
            f"{stock_diff:+.1f}%"
        )

    with tab3:
        st.header("Export Inventory Data")

        # Load inventory data
        inventory_manager.load_from_json()
        products = inventory_manager.get_all_products()

        if not products:
            st.info("No inventory data available. Please fetch data first.")
            return

        st.write("Configure your export filters:")

        # Get unique categories
        categories = set(p['category'] for p in products.values())

        # Filter section
        with st.expander("Export Filters", expanded=True):
            # Category filter
            selected_categories = st.multiselect(
                "Select Categories",
                options=list(categories),
                default=list(categories)
            )

            # Price range filter
            price_min = min(p['price'] for p in products.values())
            price_max = max(p['price'] for p in products.values())
            price_range = st.slider(
                "Price Range (€)",
                min_value=float(price_min),
                max_value=float(price_max),
                value=(float(price_min), float(price_max))
            )

            # Stock level filter
            stock_min = min(p['quantity'] for p in products.values())
            stock_max = max(p['quantity'] for p in products.values())
            stock_range = st.slider(
                "Stock Level Range",
                min_value=int(stock_min),
                max_value=int(stock_max),
                value=(int(stock_min), int(stock_max))
            )

        # Create filters dictionary
        filters = {
            'category': selected_categories,
            'price': {'min': price_range[0], 'max': price_range[1]},
            'quantity': {'min': stock_range[0], 'max': stock_range[1]}
        }

        if st.button("Generate Excel Export"):
            try:
                # Create a temporary file
                with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                    # Export to Excel
                    inventory_manager.export_to_excel(tmp.name, filters)

                    # Read the file for download
                    with open(tmp.name, 'rb') as f:
                        excel_data = f.read()

                    # Clean up the temporary file
                    os.unlink(tmp.name)

                    # Create download button
                    st.download_button(
                        label="Download Excel File",
                        data=excel_data,
                        file_name="inventory_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    st.success("Export generated successfully!")
            except Exception as e:
                st.error(f"Error generating export: {str(e)}")

if __name__ == "__main__":
    main()