import streamlit as st
import pandas as pd
import numpy as np
import myutils

#let the user upload their inventory CSV file
uploaded_file = st.file_uploader("Upload your inventory CSV", type="csv")

# session_state to keep data saved
if 'new_df' not in st.session_state:
    st.session_state.new_df = None

# Only read the file once, and don't crash if it's broken
if uploaded_file is not None and st.session_state.new_df is None:
    try:
        st.session_state.new_df = pd.read_csv(uploaded_file, dtype={'SKU': str})
    except Exception:
        st.error("Could not read that file. Please upload a valid CSV.")

# Stop here until a file is loaded
if st.session_state.new_df is None:
    st.info("Please upload your inventory CSV to start.")
    st.stop()

#assigning the inventory data to be used
new_df = st.session_state.new_df

#allows the user chooses the low stock range
threshold = st.sidebar.number_input("Low stock warning below", min_value=0, value=5)

st.title ('Fruit Store Inventory Management :mango:')

navigation = st.pills("Navigation",
        ("Home Page", "Add Product", "Update Stock", 'Search/Filter', 'Inventory View', "Discount"), default = "Home Page")

# Home Page: show the full inventory
if navigation == 'Home Page':
    st.dataframe(new_df)

#Add Product: form to add a new item
if navigation == 'Add Product':
    st.title ('Add Product to Inventory :banana:')

    with st.form("Form to Add Product "):
        Product = st.text_input('What is the item name ?', value=None, placeholder="Type a name...")

        SKU = st.text_input(
        "What is the SKU of the product?", value=None, placeholder="Type a number...")

        Price = st.number_input(
        "What is the Price of the product?", value=None, placeholder="Type a number...")

        Quantity = st.number_input(
        "What is the current quantity of the product?", value=None, min_value=0, placeholder="Type a number...")

        Category = st.selectbox(
        "what is the category of the product?",
        ('fruit', 'vegetable', 'other')
    )

    # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
    if submitted:
        # Check the inputs before saving
        if not Product or not SKU or Price is None or Quantity is None:
            st.error("Please fill in every field.")
        elif Price <= 0:
            st.error("Price must be more than 0.")
        elif SKU in new_df['SKU'].values:
            st.error("That SKU already exists.")
        else:
            # Builds a row for the new product
            new_row = pd.DataFrame({
            'Product' : [Product], 'SKU' : [SKU], 'Price' : [Price], 'Quantity' : [Quantity], 'Category' : [Category]})

            st.session_state.new_df = pd.concat([new_df, new_row], ignore_index=True)
            st.success(f"{Product} added!")
            st.dataframe(st.session_state.new_df)

# Update Stock: find a product and edit it    
if navigation == 'Update Stock':
    st.title ('Update Stock of Inventory :grapes:')  
    
  # Search by SKU
    SKU_update = st.text_input(
        "enter the SKU of the product you want to edit", placeholder="enter an SKU...")
    if st.button('Click to search SKU'):
        st.session_state.edited_df = new_df[new_df['SKU'] == SKU_update].copy()

    # Search by name
    name_update = st.text_input(
        "enter the name of the product you want to edit", placeholder="enter a name...")
    if st.button('Click to search name'):
        st.session_state.edited_df = new_df[new_df['Product'] == name_update].copy()

    # Show the search result below both searches, in an editable table
    if 'edited_df' in st.session_state:
        edited_df = st.data_editor(st.session_state.edited_df)

        # One save button for either search
        if st.button('Save changes to this product'):
            new_df.update(edited_df)
            st.success("Changes saved successfully!") 
            
    st.subheader('Or you can use the full Data frame.')  
    edited_df = st.data_editor(new_df)
    buttonsc = st.button('click to save changes')
    if buttonsc == True:
        st.session_state.new_df = edited_df
        st.success("Changes saved!")

# Search/Filter: show products in one category
if navigation == 'Search/Filter':
    st.title ('Search or Filter the products by category :avocado:')

    st.header('filter by Category')
    # Dropdown with every category in the data
    categories = new_df['Category'].unique()
    selected_category = st.selectbox("Select Category", categories)

    # Keep only the rows in the chosen category
    filtered_df = myutils.filter_by_category(new_df, selected_category)
    st.subheader(f"inventory for {selected_category}")

    st.dataframe(filtered_df)

if navigation == 'Inventory View':
    st.title ('Inventory View of complete store catalog :carrot:')
    
    # Total value of everything in stock
    total_value = myutils.calculate_total_value(new_df)
    st.metric("Total inventory value", f"${total_value:,.2f}")

    # Low stock warning
    low_stock = myutils.get_low_stock(new_df, threshold)
    if len(low_stock) > 0:
        st.warning(f"Low stock! {len(low_stock)} item(s) below {threshold}:")
        st.dataframe(low_stock)

    st.dataframe(new_df)

# Discount (Phase 3): put a whole category on sale
if navigation == 'Discount':
    st.title('Discount Calculator :tangerine:')

    # Pick which category to put on sale and how much off
    discount_category = st.selectbox("Choose a category to discount", new_df['Category'].unique())
    percent = st.slider("Discount %", min_value=5, max_value=90, value=20, step=5)

    # Lower the prices only when the button is clicked
    if st.button('Apply discount'):
        myutils.apply_discount(new_df, discount_category, percent)
        st.success(f"{percent}% off all {discount_category}!")

    # Show the products in that category
    st.dataframe(myutils.filter_by_category(new_df, discount_category))

st.sidebar.download_button("Download inventory CSV",
        st.session_state.new_df.to_csv(index=False),
        file_name="inventory_tracker.csv")
