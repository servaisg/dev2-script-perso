import argparse
import csv


class Product:
    """Represents a product in the inventory."""
    def __init__(self, name, price, category, quantity=0):
        """
        Initialize a Product instance.
        
        Pre: name is a non-empty string
             price is a valid number (float or string that can be converted to float)
             category is a non-empty string
             quantity is a non-negative integer (defaults to 0)
        
        Post: self.name is set to name
              self.price is set to float(price)
              self.category is set to category
              self.quantity is set to int(quantity)
        """
        self.name = name
        self.price = float(price)
        self.category = category
        self.quantity = int(quantity)

    def total(self):
        """
        Calculate the total value of this product.
        
        Pre: self.price and self.quantity = int
        
        Post: returns the product of price and quantity as a float
        """
        return self.price * self.quantity

    def to_row(self):
        """
        Convert product to a list representation for CSV output.
        
        Pre: self.name, self.quantity, self.price, self.category are not None
        
        Post: returns a list with [name, quantity, formatted_price, category, formatted_total]
        """
        return [self.name, self.quantity, f"{self.price:.2f}", self.category, f"{self.total():.2f}"]


class Inventory:
    """Manages a collection of products."""
    def __init__(self):
        """
        Initialize an Inventory instance.
        
        Pre: /
        
        Post:
            - self.products is initialized as an empty list
        """
        self.products = []

    def add_product(self, product):
        """
        Add a product to the inventory or update quantity if product exists.
        
        Pre: product.name and product.category are non-empty strings
        
        Post: if product with same name and category exists, its quantity is increased
              if product doesn't exist, it is added to self.products
        """
        for p in self.products:
            if p.name.lower() == product.name.lower() and p.category.lower() == product.category.lower():
                p.quantity += product.quantity
                return
        self.products.append(product)

    def remove_product(self, name):
        """
        Remove a product from the inventory by name.
        
        Pre: name is a string
        
        Post: if product with matching name exists, it is removed from self.products
              returns True if product was found and removed, False otherwise
        """
        for i, p in enumerate(self.products):
            if p.name.lower() == name.lower():
                del self.products[i]
                return True
        return False

    def sort_by_name(self):
        """
        Sort products alphabetically by name (case-insensitive).
        
        Pre: self.products is not empty
        
        Post: self.products is sorted by product name in ascending order
        """
        self.products.sort(key=self.get_name)

    def sort_by_price(self):
        """
        Sort products by price in ascending order.
        
        Pre: self.products is not empty
        
        Post: self.products is sorted by product price in ascending order
        """
        self.products.sort(key=self.get_price)

    def sort_by_quantity(self):
        """
        Sort products by quantity in ascending order.
        
        Pre: self.products.get_quantity() = float
        
        Post: self.products is sorted by product quantity in ascending order
        """
        self.products.sort(key=self.get_quantity)

    def sort_by_category(self):
        """
        Sort products alphabetically by category (case-insensitive).
        
        Pre: self.products is not empty
        
        Post: self.products is sorted by product category in ascending order
        """
        self.products.sort(key=self.get_category)

    # Sorting key functions
    def get_name(self, product):
        """
        Get the lowercase name of a product for sorting.
        
        Pre: product.name is not None
        
        Post: returns the lowercase version of product.name
        """
        return product.name.lower()

    def get_price(self, product):
        """
        Get the price of a product for sorting.
        
        Pre: product.price is not None
        
        Post: returns product.price
        """
        return product.price

    def get_quantity(self, product):
        """
        Get the quantity of a product for sorting.
        
        Pre: product.quantity is a float
        
        Post: returns product.quantity
        """
        return product.quantity

    def get_category(self, product):
        """
        Get the lowercase category of a product for sorting.
        
        Pre: product.category is not None
        
        Post: returns the lowercase version of product.category
        """
        return product.category.lower()

    def view(self, sort_key=None):
        """
        Display the inventory in a formatted table.
        
        Pre: sort_key is None or one of: "name", "price", "quantity", "category"
             self.products is not empty
        
        Post: prints a formatted table of all products
              prints category totals and overall inventory value
              if sort_key is provided, products are sorted before display
        """
        if sort_key == "name":
            self.sort_by_name()
        elif sort_key == "price":
            self.sort_by_price()
        elif sort_key == "quantity":
            self.sort_by_quantity()
        elif sort_key == "category":
            self.sort_by_category()

        headers = ["Name", "Quantity", "Price (€)", "Category", "Total (€)"]
        column_widths = [len(h) for h in headers]
        for p in self.products:
            row = p.to_row()
            column_widths = [max(len(str(cell)), column_widths[i]) for i, cell in enumerate(row)]

        def format_row(row):
            return " | ".join(str(cell).ljust(column_widths[i]) for i, cell in enumerate(row))

        print(format_row(headers))
        print("-+-".join("-" * w for w in column_widths))
        for p in self.products:
            print(format_row(p.to_row()))

        # Totals by category
        totals = {}
        for p in self.products:
            cat = p.category
            totals[cat] = totals.get(cat, 0) + p.total()

        print("\nCategory Totals:")
        for cat, total in totals.items():
            print(f"{cat}: {total:.2f} €")
        overall = sum(totals.values())
        print(f"\nOverall Inventory Value: {overall:.2f} €\n")

    def save_csv(self, filename="inventory.csv"):
        """
        Save the inventory to a CSV file.
        
        Pre: filename is a valid string representing a file path
             self.products is not empty
        
        Post: creates or overwrites filename with inventory data in CSV format
              file is encoded in utf-8-sig with proper line endings
        
        """
        with open(filename, mode="w", newline='', encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Quantity", "Price (€)", "Category", "Total (€)"])
            for p in self.products:
                writer.writerow(p.to_row())

    def load_csv(self, filename):
        """
        Load products from a CSV file into the inventory.
        
        Pre: filename is a valid string representing an existing file path
             file contains CSV data with at least 4 columns: name, quantity, price, category
        
        Post: products from the CSV file are added to self.products
              existing products with same name and category have quantities merged
        """
        with open(filename, newline='', encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 4:
                    continue
                name, quantity, price, category = row[:4]
                price = price.replace(",", ".")
                self.add_product(Product(name.strip(), float(price), category.strip(), int(quantity)))


def main():
    """
    Main function to run the inventory management system.
    
    Pre: command line arguments are provided for CSV files to load
         CSV files exist and are readable
    
    Post: inventory management interface is displayed
          user can interact with the system until choosing to quit
          final inventory state is saved to inventory.csv
    """
    parser = argparse.ArgumentParser(description="Inventory management")
    parser.add_argument("files", nargs="+", help="CSV files to load")
    args = parser.parse_args()

    inventory = Inventory()
    for file in args.files:
        inventory.load_csv(file)

    while True:
        action = input("Options: [a]dd, [r]emove, [s]earch, [v]iew, [q]uit\nChoose action: ").lower()
        if action == "a":
            name = input("Product name: ")
            quantity = int(input("Quantity: "))
            price = input("Price: ").replace(",", ".")
            category = input("Category: ")
            inventory.add_product(Product(name, float(price), category, quantity))
        elif action == "r":
            name = input("Product name to remove: ")
            if not inventory.remove_product(name):
                print("Product not found.")
        elif action == "s":
            term = input("Search term (name or category): ").lower()
            results = [p for p in inventory.products if term in p.name.lower() or term in p.category.lower()]
            for p in results:
                print(p.to_row())
        elif action == "v":
            sort = input("Sort by (name/price/quantity/category) or leave blank: ").lower()
            inventory.view(sort_key=sort)
        elif action == "q":
            print("Saving inventory and exiting...")
            inventory.save_csv()
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
