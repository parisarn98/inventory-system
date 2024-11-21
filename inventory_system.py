import logging
from database import DatabaseManager

logging.basicConfig(
    filename="inventory_updates.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Logging system initialized.")


class Inventory:
    def __init__(self, id, name, quantity, price, item_type):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.item_type = item_type

    def add_and_save_to_db(self, db_manager):
        add_inventory_query = """
        INSERT INTO inventory (name, quantity, price, item_type) 
        VALUES (%s, %s, %s, %s) 
        RETURNING id;
        """
        try:
            cursor = db_manager.connection.cursor()
            cursor.execute(add_inventory_query, (self.name, self.quantity, self.price, self.item_type))
            inventory_id = cursor.fetchone()[0]  # گرفتن ID ایجاد شده
            db_manager.connection.commit()
            logging.info(f"Item '{self.name}' added to inventory with ID {inventory_id}.")
        except Exception as e:
            logging.error(f"Error adding item '{self.name}' to inventory: {e}")
            print(f"Error adding item to inventory: {e}")
            inventory_id = None
        finally:
            cursor.close()

        # Add to specific product tables (digital or physical)
        if inventory_id:
            if self.item_type == "digital":
                self.add_digital_item(db_manager, inventory_id)
            elif self.item_type == "physical":
                self.add_physical_item(db_manager, inventory_id)
            logging.info(f"Item '{self.name}' added to corresponding product table.")
        else:
            logging.error(f"Failed to add item '{self.name}' due to invalid inventory ID.")
            print(f"Failed to add item: {self.name} - Invalid inventory ID.")

    def add_digital_item(self, db_manager, inventory_id):
        raise NotImplementedError("This method should be implemented in subclasses")

    def add_physical_item(self, db_manager, inventory_id):
        raise NotImplementedError("This method should be implemented in subclasses")

    def remove_item(self, item_id):
        query = "DELETE FROM inventory WHERE id = %s"
        self.db_manager.execute_query(query, (item_id,))


class Phisycal_item(Inventory):
    def __init__(self, id, name, quantity, price, weight, dimensions):
        super().__init__(id, name, quantity, price, item_type="physical")
        self.weight = weight
        self.dimensions = dimensions

    def add_physical_item(self, db_manager, inventory_id):
        query = """
        INSERT INTO physical (inventory_id, weight, dimensions)
        VALUES (%s, %s, %s);
        """
        try:
            db_manager.execute_query(query, (inventory_id, self.weight, self.dimensions))
            logging.info(f"Physical item details added for inventory ID {inventory_id}.")
        except Exception as e:
            logging.error(f"Error adding physical item details: {e}")
            print(f"Error adding physical item details: {e}")

    def update_stock(self, item_id, quantity):
        query = "UPDATE inventory SET quantity = %s WHERE id = %s"
        try:
            self.db_manager.execute_query(query, (quantity, item_id))
            logging.info(
                f"Item ID {item_id} updated: New Quantity = {quantity}"
            )
            print("Stock updated successfully.")
        except Exception as e:
            logging.error(f"Error updating item ID {item_id}: {e}")
            print("Failed to update stock.")
            print(f"Physical item with ID {item_id} updated to quantity {quantity}.")


class Digital_item(Inventory):
    def __init__(self, id, name, quantity, price, file_size, download_link):
        super().__init__(id, name, quantity, price, item_type="digital")
        self.file_size = file_size
        self.download_link = download_link

    def add_digital_item(self, db_manager, inventory_id):
        query = """
        INSERT INTO digital (inventory_id, file_size, download_link)
        VALUES (%s, %s, %s);
        """
        try:
            db_manager.execute_query(query, (inventory_id, self.file_size, self.download_link))
            logging.info(f"Digital item details added for inventory ID {inventory_id}.")
        except Exception as e:
            logging.error(f"Error adding digital item details: {e}")
            print(f"Error adding digital item details: {e}")


    def update_stock(self, item_id, quantity):
        query = "UPDATE inventory SET quantity = %s WHERE id = %s"
        try:
            self.db_manager.execute_query(query, (quantity, item_id))
            logging.info(
                f"Item ID {item_id} updated: New Quantity = {quantity}"
            )
            print("Stock updated successfully.")
        except Exception as e:
            logging.error(f"Error updating item ID {item_id}: {e}")
            print("Failed to update stock.")
            print(f"Physical item with ID {item_id} updated to quantity {quantity}.")



new_db_manager = DatabaseManager("inventory", "parisa", "mypassword123", "127.0.0.1", "5432")

digital_item = Digital_item(
    id=None,  # چون ID خودکار ایجاد می‌شود
    name="E-Book: dart Programming",
    quantity=100,
    price=20.00,
    file_size=5.5,  # به گیگابایت
    download_link="https://example2.com/python-ebook"
)
# digital_item.add_and_save_to_db(new_db_manager)

physical_item = Phisycal_item(
    id=None,
    name="Laptop",
    quantity=20,
    price=1000.00,
    weight=2.5,
    dimensions="35x25x2"
)
physical_item.add_and_save_to_db(new_db_manager)