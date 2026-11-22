
def calculate_total_value(df):
    """Return the total value of all stock (Price x Quantity, added up)."""
    return (df['Price'] * df['Quantity']).sum()
 
 
def get_low_stock(df, threshold):
    """Return only the products with a Quantity below the threshold."""
    return df[df['Quantity'] < threshold]
 
 
def filter_by_category(df, category):
    """Return only the products in the chosen category."""
    return df[df['Category'] == category]
 
 
def apply_discount(df, category, percent):
    """Lower the Price of every product in a category by a percent (changes df directly)."""
    rows = df['Category'] == category
    df.loc[rows, 'Price'] = (df.loc[rows, 'Price'] * (1 - percent / 100)).round(2)