def rupees(amount):
    return f"₹{amount:,.0f}"

def price_of(product):
    return product["price"]

def price_range(product):
    low = product.get("price_low", round(product["price"] * 0.90))
    high = product.get("price_high", round(product["price"] * 1.10))
    if product["price"] == 0:
        return "Included / not needed"
    return f"{rupees(low)} - {rupees(high)}"
