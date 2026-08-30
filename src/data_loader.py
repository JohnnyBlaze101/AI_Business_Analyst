import pandas as pd


def load_data():
    sales = pd.read_csv("data/sales.csv")
    marketing = pd.read_csv("data/marketing.csv")
    product = pd.read_csv("data/product.csv")

    return sales, marketing, product

sales, marketing, product = load_data()

print(sales.head())
print()
print(marketing.head())
print()
print(product.head())