import argparse
import csv
import os
from typing import List, Dict, Optional


class Item:
    """Represents an inventory item with unique identification."""
    def __init__(self, name: str, price: float, category: str, quantity: int = 0):
        self.name = name.strip()
        self.price = float(price)
        self.category = category.strip()
        self.quantity = int(quantity)
        self._id = f"{self.name.lower()}_{self.category.lower()}"

    def __str__(self) -> str:
        return f"{self.name} ({self.category}) - Qty: {self.quantity}, Price: {self.price:.2f}€, Total: {self.total():.2f}€"

    def total(self) -> float:
        return self.price * self.quantity

    def to_csv_row(self) -> List[str]:
        return [self.name, str(self.quantity), f"{self.price:.2f}", self.category]

    def get_id(self) -> str:
        return self._id

    def add_quantity(self, amount: int):
        self.quantity += int(amount)

    def update_price(self, new_price: float):
        if new_price > 0:
            self.price = float(new_price)


class InventoryManager:
    """Manages inventory with proper item consolidation and CSV operations."""
    
    def __init__(self):
        self.items: Dict[str, Item] = {}
        self.loaded_files: List[str] = []

    def load_from_csv(self, filename: str) -> bool:
        """Load items from CSV file with proper consolidation."""
        if not os.path.exists(filename):
            print(f"Warning: File '{filename}' not found")
            return False
            
        try:
            with open(filename, 'r', newline='', encoding='utf-8-sig') as file:
                reader = csv.reader(file)
                for row_num, row in enumerate(reader, 1):
                    if len(row) < 4:
                        continue
                    
                    name, qty_str, price_str, category = row[:4]
                    
                    # Clean and validate data
                    try:
                        quantity = int(qty_str)
                        price = float(price_str.replace(',', '.'))
                    except ValueError:
                        print(f"Warning: Invalid data in {filename}, row {row_num}: {row}")
                        continue
                    
                    item_id = f"{name.lower()}_{category.lower()}"
                    
                    if item_id in self.items:
                        # Add to existing item
                        self.items[item_id].add_quantity(quantity)
                    else:
                        # Create new item
                        self.items[item_id] = Item(name, price, category, quantity)
            
            self.loaded_files.append(filename)
            print(f"Successfully loaded '{filename}'")
            return True
            
        except Exception as e:
            print(f"Error loading '{filename}': {e}")
            return False

    def add_item(self, name: str, price: float, category: str, quantity: int = 1) -> bool:
        """Add a new item or update existing one."""
        try:
            item_id = f"{name.lower()}_{category.lower()}"
            
            if item_id in self.items:
                self.items[item_id].add_quantity(quantity)
                print(f"Added {quantity} to existing item: {name} ({category})")
            else:
                self.items[item_id] = Item(name, price, category, quantity)
                print(f"Created new item: {name} ({category})")
            return True
        except Exception as e:
            print(f"Error adding item: {e}")
            return False

    def remove_item(self, name: str, category: str = None) -> bool:
        """Remove an item by name and optionally category."""
        if category:
            item_id = f"{name.lower()}_{category.lower()}"
            if item_id in self.items:
                del self.items[item_id]
                print(f"Removed: {name} ({category})")
                return True
        else:
            # Remove all items with this name
            removed = False
            for item_id, item in list(self.items.items()):
                if item.name.lower() == name.lower():
                    del self.items[item_id]
                    print(f"Removed: {item.name} ({item.category})")
                    removed = True
            return removed
        
        print(f"Item not found: {name}")
        return False

    def search_items(self, query: str) -> List[Item]:
        """Search items by name or category."""
        query = query.lower()
        results = []
        for item in self.items.values():
            if (query in item.name.lower() or 
                query in item.category.lower()):
                results.append(item)
        return results

    def get_sorted_items(self, sort_by: str = "name") -> List[Item]:
        """Get items sorted by specified criteria."""
        items_list = list(self.items.values())
        
        if sort_by == "name":
            items_list.sort(key=lambda x: x.name.lower())
        elif sort_by == "price":
            items_list.sort(key=lambda x: x.price)
        elif sort_by == "quantity":
            items_list.sort(key=lambda x: x.quantity)
        elif sort_by == "category":
            items_list.sort(key=lambda x: x.category.lower())
        elif sort_by == "total":
            items_list.sort(key=lambda x: x.total())
        
        return items_list

    def display_inventory(self, sort_by: str = "name", show_columns: List[str] = None):
        """Display inventory in a formatted table."""
        if not self.items:
            print("Inventory is empty")
            return

        items_list = self.get_sorted_items(sort_by)
        
        # Define columns to show
        if not show_columns:
            show_columns = ["name", "quantity", "price", "category", "total"]
        
        # Create headers
        headers = []
        for col in show_columns:
            if col == "name":
                headers.append("Name")
            elif col == "quantity":
                headers.append("Qty")
            elif col == "price":
                headers.append("Price (€)")
            elif col == "category":
                headers.append("Category")
            elif col == "total":
                headers.append("Total (€)")
        
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for item in items_list:
            row_data = self._get_item_row_data(item, show_columns)
            for i, cell in enumerate(row_data):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Print table
        self._print_table_header(headers, col_widths)
        for item in items_list:
            row_data = self._get_item_row_data(item, show_columns)
            self._print_table_row(row_data, col_widths)
        
        # Print summary
        self._print_summary(items_list)

    def _get_item_row_data(self, item: Item, columns: List[str]) -> List[str]:
        """Get row data for specified columns."""
        data = []
        for col in columns:
            if col == "name":
                data.append(item.name)
            elif col == "quantity":
                data.append(str(item.quantity))
            elif col == "price":
                data.append(f"{item.price:.2f}")
            elif col == "category":
                data.append(item.category)
            elif col == "total":
                data.append(f"{item.total():.2f}")
        return data

    def _print_table_header(self, headers: List[str], widths: List[int]):
        """Print table header with separators."""
        header_row = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
        separator = "-+-".join("-" * w for w in widths)
        print(header_row)
        print(separator)

    def _print_table_row(self, row_data: List[str], widths: List[int]):
        """Print a table row."""
        row = " | ".join(cell.ljust(w) for cell, w in zip(row_data, widths))
        print(row)

    def _print_summary(self, items: List[Item]):
        """Print inventory summary."""
        if not items:
            return
            
        # Category totals
        category_totals = {}
        for item in items:
            cat = item.category
            category_totals[cat] = category_totals.get(cat, 0) + item.total()
        
        print(f"\nSummary:")
        print("─" * 40)
        for category, total in sorted(category_totals.items()):
            print(f"  {category}: {total:.2f} €")
        
        overall_total = sum(category_totals.values())
        item_count = len(items)
        print(f"─" * 40)
        print(f"  Total Items: {item_count}")
        print(f"  Total Value: {overall_total:.2f} €")

    def save_to_csv(self, filename: str = "inventory_export.csv") -> bool:
        """Save current inventory to CSV file."""
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(["Name", "Quantity", "Price (€)", "Category"])
                
                for item in self.get_sorted_items("name"):
                    writer.writerow(item.to_csv_row())
            
            print(f"Inventory saved to '{filename}'")
            return True
        except Exception as e:
            print(f"Error saving to '{filename}': {e}")
            return False

    def get_statistics(self) -> Dict:
        """Get inventory statistics."""
        if not self.items:
            return {"total_items": 0, "total_value": 0, "categories": 0}
        
        total_value = sum(item.total() for item in self.items.values())
        categories = len(set(item.category for item in self.items.values()))
        
        return {
            "total_items": len(self.items),
            "total_value": total_value,
            "categories": categories
        }


def interactive_add_item(inventory: InventoryManager):
    """Interactive function to add items."""
    print("\nAdd New Item")
    print("─" * 30)
    
    name = input("Item name: ").strip()
    if not name:
        print("Error: Name cannot be empty")
        return
    
    # Check if item exists
    existing = inventory.search_items(name)
    if existing:
        print(f"\nFound {len(existing)} existing item(s) with similar name:")
        for i, item in enumerate(existing, 1):
            print(f"  {i}. {item.name} ({item.category}) - Qty: {item.quantity}")
        
        choice = input("\nAdd to existing item? (y/n): ").lower()
        if choice == 'y':
            if len(existing) == 1:
                item = existing[0]
                try:
                    qty = int(input(f"Quantity to add to '{item.name}': "))
                    inventory.add_item(item.name, item.price, item.category, qty)
                except ValueError:
                    print("Error: Invalid quantity")
                return
            else:
                try:
                    idx = int(input("Select item number: ")) - 1
                    if 0 <= idx < len(existing):
                        item = existing[idx]
                        qty = int(input(f"Quantity to add to '{item.name}': "))
                        inventory.add_item(item.name, item.price, item.category, qty)
                    else:
                        print("Error: Invalid selection")
                except (ValueError, IndexError):
                    print("Error: Invalid input")
                return
    
    # Add new item
    try:
        price = float(input("Unit price (€): ").replace(',', '.'))
        category = input("Category: ").strip()
        quantity = int(input("Quantity: "))
        
        if price <= 0 or quantity < 0:
            print("Error: Price must be positive and quantity non-negative")
            return
        
        inventory.add_item(name, price, category, quantity)
        
    except ValueError:
        print("Error: Invalid input values")


def interactive_remove_item(inventory: InventoryManager):
    """Interactive function to remove items."""
    print("\nRemove Item")
    print("─" * 30)
    
    name = input("Item name to remove: ").strip()
    if not name:
        print("Error: Name cannot be empty")
        return
    
    found = inventory.search_items(name)
    if not found:
        print(f"Error: No items found matching '{name}'")
        return
    
    if len(found) == 1:
        item = found[0]
        confirm = input(f"Remove '{item.name}' ({item.category})? (y/n): ").lower()
        if confirm == 'y':
            inventory.remove_item(item.name, item.category)
    else:
        print(f"\nFound {len(found)} items:")
        for i, item in enumerate(found, 1):
            print(f"  {i}. {item.name} ({item.category}) - Qty: {item.quantity}")
        
        try:
            choice = input("\nRemove all or select specific item? (all/number): ").lower()
            if choice == 'all':
                confirm = input("Remove all matching items? (y/n): ").lower()
                if confirm == 'y':
                    for item in found:
                        inventory.remove_item(item.name, item.category)
            else:
                idx = int(choice) - 1
                if 0 <= idx < len(found):
                    item = found[idx]
                    confirm = input(f"Remove '{item.name}' ({item.category})? (y/n): ").lower()
                    if confirm == 'y':
                        inventory.remove_item(item.name, item.category)
                else:
                    print("Error: Invalid selection")
        except ValueError:
            print("Error: Invalid input")


def interactive_search(inventory: InventoryManager):
    """Interactive search function."""
    print("\nSearch Items")
    print("─" * 30)
    
    query = input("Search term: ").strip()
    if not query:
        print("Error: Search term cannot be empty")
        return
    
    results = inventory.search_items(query)
    if results:
        print(f"\nFound {len(results)} item(s):")
        print("─" * 50)
        for item in results:
            print(f"  {item}")
    else:
        print(f"Error: No items found matching '{query}'")


def interactive_view(inventory: InventoryManager):
    """Interactive view function."""
    print("\nView Inventory")
    print("─" * 30)
    
    # Sort options
    sort_options = {
        "1": "name", "2": "price", "3": "quantity", 
        "4": "category", "5": "total", "6": "none"
    }
    
    print("Sort by:")
    print("  1. Name    2. Price    3. Quantity")
    print("  4. Category 5. Total    6. No sort")
    
    sort_choice = input("Choice (1-6): ").strip()
    sort_by = sort_options.get(sort_choice, "name")
    
    # Column selection
    print("\nAvailable columns: name, quantity, price, category, total")
    columns_input = input("Columns to show (space-separated, or 'all'): ").strip()
    
    if columns_input.lower() == 'all' or not columns_input:
        show_columns = None
    else:
        show_columns = columns_input.split()
    
    print("\n" + "=" * 60)
    inventory.display_inventory(sort_by, show_columns)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="Advanced Inventory Management System")
    parser.add_argument("files", nargs="*", help="CSV files to load")
    args = parser.parse_args()

    # Initialize inventory
    inventory = InventoryManager()
    
    # Load files
    if args.files:
        print("Loading files...")
        for file in args.files:
            inventory.load_from_csv(file)
        
        stats = inventory.get_statistics()
        print(f"\nSuccessfully loaded {stats['total_items']} items from {len(args.files)} file(s)")
        print(f"   Total value: {stats['total_value']:.2f} €")
        print(f"   Categories: {stats['categories']}")
    else:
        print("Starting with empty inventory")

    # Main menu loop
    while True:
        print("\n" + "=" * 50)
        print("INVENTORY MANAGEMENT SYSTEM")
        print("=" * 50)
        print("1. Add item")
        print("2. Remove item") 
        print("3. Search items")
        print("4. View inventory")
        print("5. Save to CSV")
        print("6. Statistics")
        print("0. Exit")
        print("─" * 50)
        
        choice = input("Select option (0-6): ").strip()
        
        if choice == "1":
            interactive_add_item(inventory)
        elif choice == "2":
            interactive_remove_item(inventory)
        elif choice == "3":
            interactive_search(inventory)
        elif choice == "4":
            interactive_view(inventory)
        elif choice == "5":
            filename = input("Save filename (default: inventory_export.csv): ").strip()
            if not filename:
                filename = "inventory_export.csv"
            inventory.save_to_csv(filename)
        elif choice == "6":
            stats = inventory.get_statistics()
            print(f"\nInventory Statistics:")
            print(f"   Total items: {stats['total_items']}")
            print(f"   Total value: {stats['total_value']:.2f} €")
            print(f"   Categories: {stats['categories']}")
        elif choice == "0":
            print("\nGoodbye! Don't forget to save your changes.")
            break
        else:
            print("Error: Invalid option. Please try again.")


if __name__ == "__main__":
    main()
