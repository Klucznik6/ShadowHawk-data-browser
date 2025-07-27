import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

def create_sample_database():
    """Create a sample database with test data"""
    
    # Create SQLite database
    conn = sqlite3.connect('sample_data.db')
    
    # Sample employees data
    employees_data = []
    departments = ['HR', 'Engineering', 'Sales', 'Marketing', 'Finance']
    first_names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    
    for i in range(1, 101):  # 100 employees
        employee = {
            'employee_id': i,
            'first_name': random.choice(first_names),
            'last_name': random.choice(last_names),
            'department': random.choice(departments),
            'salary': random.randint(30000, 120000),
            'hire_date': (datetime.now() - timedelta(days=random.randint(30, 2000))).strftime('%Y-%m-%d'),
            'email': f'employee{i}@company.com',
            'active': random.choice([True, False])
        }
        employees_data.append(employee)
    
    # Create employees DataFrame and save to database
    df_employees = pd.DataFrame(employees_data)
    df_employees.to_sql('employees', conn, if_exists='replace', index=False)
    
    # Sample sales data
    sales_data = []
    products = ['Laptop', 'Desktop', 'Monitor', 'Keyboard', 'Mouse', 'Printer', 'Scanner', 'Tablet', 'Phone', 'Headphones']
    
    for i in range(1, 501):  # 500 sales records
        sale = {
            'sale_id': i,
            'employee_id': random.randint(1, 100),
            'product': random.choice(products),
            'quantity': random.randint(1, 10),
            'unit_price': round(random.uniform(50, 2000), 2),
            'sale_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
            'customer_id': random.randint(1000, 9999)
        }
        sale['total_amount'] = round(sale['quantity'] * sale['unit_price'], 2)
        sales_data.append(sale)
    
    # Create sales DataFrame and save to database
    df_sales = pd.DataFrame(sales_data)
    df_sales.to_sql('sales', conn, if_exists='replace', index=False)
    
    # Sample customer data
    customers_data = []
    companies = ['TechCorp', 'DataSoft', 'CloudInc', 'WebSystems', 'InfoTech', 'DigitalFlow', 'SmartData', 'NextGen', 'TechFlow', 'DataCore']
    
    for i in range(1000, 1201):  # 200 customers
        customer = {
            'customer_id': i,
            'company_name': f"{random.choice(companies)} #{i-999}",
            'contact_name': f"{random.choice(first_names)} {random.choice(last_names)}",
            'email': f'contact{i}@customer.com',
            'phone': f'555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
            'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']),
            'country': 'USA',
            'created_date': (datetime.now() - timedelta(days=random.randint(1, 1000))).strftime('%Y-%m-%d')
        }
        customers_data.append(customer)
    
    # Create customers DataFrame and save to database
    df_customers = pd.DataFrame(customers_data)
    df_customers.to_sql('customers', conn, if_exists='replace', index=False)
    
    # Sample inventory data
    inventory_data = []
    for product in products:
        inventory = {
            'product_name': product,
            'stock_quantity': random.randint(0, 1000),
            'reorder_level': random.randint(10, 100),
            'unit_cost': round(random.uniform(20, 1000), 2),
            'supplier': f"Supplier_{random.randint(1, 10)}",
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        inventory_data.append(inventory)
    
    # Create inventory DataFrame and save to database
    df_inventory = pd.DataFrame(inventory_data)
    df_inventory.to_sql('inventory', conn, if_exists='replace', index=False)
    
    conn.close()
    print("Sample database 'sample_data.db' created successfully!")
    print("Tables created:")
    print("- employees (100 records)")
    print("- sales (500 records)")
    print("- customers (200 records)")
    print("- inventory (10 records)")

if __name__ == "__main__":
    create_sample_database()
