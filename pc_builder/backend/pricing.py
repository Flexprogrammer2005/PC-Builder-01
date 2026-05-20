def rupees(amount):
    return f"₹{amount:,.0f}"


def price_of(product):
    return product["price"]


def price_range(product):
    low = product.get("price_low", round(product["price"] * 0.88))
    high = product.get("price_high", round(product["price"] * 1.15))
    if product["price"] == 0:
        return "Included / not needed"
    return f"{rupees(low)} - {rupees(high)}"
