import sqlite3
import os
import csv
import json
import bcrypt
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(BASE_DIR, 'DATABASE_TEST.db')

CSV_FOOD_ITEMS = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_food_items.csv')
CSV_NUTRITIONAL_INFO = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_nutritional_info.csv')
CSV_CATEGORIES = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_categories.csv')
CSV_BMI_INFO = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_bmi_info.csv')
CSV_GOALS = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_goals.csv')
CSV_WEIGHT_LOG = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_weight_log.csv')
CSV_DAILY_CALORIE_LOG = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_daily_calorie_log.csv')
CSV_MEAL_PLANS = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_meal_plans.csv')
CSV_PREPROCESSED_FOOD_DATABASE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_preprocessed_food_database.csv')





def initialize_database():

    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} does not exist. Creating a new one...")

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')

        #food_items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            name TEXT NOT NULL,
            weight REAL NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbohydrates REAL NOT NULL,
            fats REAL NOT NULL,
            price REAL
        )
        ''')

        # daily_calorie_log table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_calorie_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            food_items TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbohydrates REAL NOT NULL,
            fats REAL NOT NULL
        )
        ''')

        # bmi_info table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bmi_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            bmi REAL NOT NULL,
            bmr REAL NOT NULL,
            tdee REAL NOT NULL
        )
        ''')

        #goals table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calories_goal REAL NOT NULL,
            protein_goal REAL NOT NULL,
            carbohydrates_goal REAL NOT NULL,
            fats_goal REAL NOT NULL,
            target_weight REAL NOT NULL,
            starting_weight REAL NOT NULL,
            target_date TEXT NOT NULL,
            weekly_weight_change REAL NOT NULL
        )
        ''')

        # categories table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL
        )
        ''')

        # weight_log table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS weight_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            weight REAL NOT NULL
        )
        ''')

        # nutritional_info table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS nutritional_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            calories_per_100g REAL NOT NULL,
            protein_per_100g REAL NOT NULL,
            carbohydrates_per_100g REAL NOT NULL,
            fats_per_100g REAL NOT NULL
        )
        ''')

        # preprocessed_food_database table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS preprocessed_food_database (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbohydrates REAL NOT NULL,
            fats REAL NOT NULL,
            food_id INTEGER
        )
        ''')

        # meal_plans table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_plan TEXT NOT NULL,
            user_criteria TEXT NOT NULL,
            total_calories REAL NOT NULL,
            total_protein REAL NOT NULL,
            total_carbs REAL NOT NULL,
            total_fats REAL NOT NULL,
            total_price REAL NOT NULL,
            meals TEXT NOT NULL
        )
        ''')

        # weekly_meal_plan table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_meal_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            meals TEXT NOT NULL
        )
        ''')

        # weekly_ai_meal_plan table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_ai_meal_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            meal_name TEXT NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbohydrates REAL NOT NULL,
            fats REAL NOT NULL
        )
        ''')

        conn.commit()
        print("Database and tables initialized successfully.")

    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")

    finally:
        if conn:
            conn.close()


def is_table_empty(table_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    result = cursor.fetchone()[0]

    conn.close()

    return result == 0

def is_database_empty():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM food_items")
        food_items_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM bmi_info")
        bmi_info_count = cursor.fetchone()[0]

        if food_items_count == 0 and bmi_info_count == 0:
            return True
        return False

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return True

    finally:
        conn.close()

def import_preprocessed_food_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with open(CSV_PREPROCESSED_FOOD_DATABASE, 'r') as file:
        reader = csv.DictReader(file)


        for row in reader:
            if 'name' in row and 'Calories' in row and 'Protein (g)' in row and 'Carbohydrate (g)' in row and 'Fat (g)' in row:
                food_id = row.get('ID', None)

                cursor.execute('''
                    SELECT * FROM preprocessed_food_database WHERE name = ?
                ''', (row['name'],))

                if cursor.fetchone() is None:

                    cursor.execute('''
                        INSERT INTO preprocessed_food_database (name, calories, protein, carbohydrates, fats, food_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        row['name'],
                        row['Calories'],
                        row['Protein (g)'],
                        row['Carbohydrate (g)'],
                        row['Fat (g)'],
                        food_id
                    ))
            else:
                print(f"Row missing expected keys: {row}")

    conn.commit()
    conn.close()


def fetch_food_items_from_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        print("Fetching all food items from the database...")

        query = "SELECT id, category, name, weight, calories, protein, carbohydrates, fats, price FROM food_items"
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print("No food items found in the database.")
            return pd.DataFrame()

        columns = ['id', 'category', 'name', 'weight', 'calories', 'protein', 'carbohydrates', 'fats', 'price']
        food_items_df = pd.DataFrame(rows, columns=columns)

        return food_items_df

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()

    finally:
        conn.close()




def fetch_bmi_info_from_db():
    """Fetch BMI information from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, height, weight, age, gender, bmi, bmr, tdee FROM bmi_info LIMIT 1")
        row = cursor.fetchone()

        if row is None:
            return None

        bmi_info = {
            'id': row[0],
            'Height': row[1],
            'Weight': row[2],
            'Age': row[3],
            'Gender': row[4],
            'BMI': row[5],
            'BMR': row[6],
            'TDEE': row[7]
        }

        return bmi_info

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

    finally:
        conn.close()



def fetch_nutritional_info_from_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name, calories_per_100g, protein_per_100g, carbohydrates_per_100g, fats_per_100g FROM nutritional_info")
        rows = cursor.fetchall()

        if not rows:
            return None

        nutritional_info = []
        for row in rows:
            nutritional_info.append({
                'Name': row[0],
                'Calories_per_100g': row[1],
                'Protein_per_100g': row[2],
                'Carbohydrates_per_100g': row[3],
                'Fats_per_100g': row[4]
            })

        return nutritional_info

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

    finally:
        conn.close()

def load_csv_to_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Load food_items from CSV to DB
    with open(CSV_FOOD_ITEMS, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                    SELECT * FROM food_items WHERE 
                    category = ? AND name = ? AND weight = ? AND calories = ? AND protein = ? AND carbohydrates = ? AND fats = ? AND price = ?
                ''', (
            row['Category'], row['Name'], row['Weight'], row['Calories'], row['Protein'], row['Carbohydrates'],
            row['Fats'], row['Price']))

            if cursor.fetchone() is None:
                cursor.execute('''
                        INSERT INTO food_items (category, name, weight, calories, protein, carbohydrates, fats, price)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                    row['Category'], row['Name'], row['Weight'], row['Calories'], row['Protein'], row['Carbohydrates'],
                    row['Fats'], row['Price']))

    # Load daily_calorie_log from CSV to DB
    with open(CSV_DAILY_CALORIE_LOG, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                SELECT * FROM daily_calorie_log WHERE 
                date = ? AND food_items = ? AND calories = ? AND protein = ? AND carbohydrates = ? AND fats = ?
            ''', (row['Date'], row['Food Items'], row['Calories'], row['Protein'], row['Carbohydrates'], row['Fats']))

            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO daily_calorie_log (date, food_items, calories, protein, carbohydrates, fats)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                row['Date'], row['Food Items'], row['Calories'], row['Protein'], row['Carbohydrates'], row['Fats']))

    # Load bmi_info from CSV to DB
    with open(CSV_BMI_INFO, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                SELECT * FROM bmi_info WHERE 
                height = ? AND weight = ? AND age = ? AND gender = ? AND bmi = ? AND bmr = ? AND tdee = ?
            ''', (row['Height'], row['Weight'], row['Age'], row['Gender'], row['BMI'], row['BMR'], row['TDEE']))

            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO bmi_info (height, weight, age, gender, bmi, bmr, tdee)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (row['Height'], row['Weight'], row['Age'], row['Gender'], row['BMI'], row['BMR'], row['TDEE']))

    # Load categories from CSV to DB
    with open(CSV_CATEGORIES, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                SELECT * FROM categories WHERE 
                category = ?
            ''', (row['Category'],))

            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO categories (category)
                    VALUES (?)
                ''', (row['Category'],))

        # Load goals from CSV to DB
        with open(CSV_GOALS, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                starting_weight = row.get('starting_weight', 0)

                cursor.execute('''
                    SELECT * FROM goals WHERE 
                    calories_goal = ? AND protein_goal = ? AND carbohydrates_goal = ? AND fats_goal = ? AND target_weight = ? AND starting_weight = ? AND target_date = ? AND weekly_weight_change = ?
                ''', (row['calories_goal'], row['protein_goal'], row['carbohydrates_goal'], row['fats_goal'],
                      row['target_weight'], starting_weight, row['target_date'], row['weekly_weight_change']))

                if cursor.fetchone() is None:
                    cursor.execute('''
                        INSERT INTO goals (calories_goal, protein_goal, carbohydrates_goal, fats_goal, target_weight, starting_weight, target_date, weekly_weight_change)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (row['calories_goal'], row['protein_goal'], row['carbohydrates_goal'], row['fats_goal'],
                          row['target_weight'], starting_weight, row['target_date'], row['weekly_weight_change']))

    # Load weight_log from CSV to DB
    with open(CSV_WEIGHT_LOG, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                SELECT * FROM weight_log WHERE 
                date = ? AND weight = ?
            ''', (row['Date'], row['Weight']))

            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO weight_log (date, weight)
                    VALUES (?, ?)
                ''', (row['Date'], row['Weight']))

    # Load nutritional_info from CSV to DB
    with open(CSV_NUTRITIONAL_INFO, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''
                SELECT * FROM nutritional_info WHERE 
                name = ? AND calories_per_100g = ? AND protein_per_100g = ? AND carbohydrates_per_100g = ? AND fats_per_100g = ?
            ''', (row['Name'], row['Calories_per_100g'], row['Protein_per_100g'], row['Carbohydrates_per_100g'],
                  row['Fats_per_100g']))

            if cursor.fetchone() is None:
                cursor.execute('''
                    INSERT INTO nutritional_info (name, calories_per_100g, protein_per_100g, carbohydrates_per_100g, fats_per_100g)
                    VALUES (?, ?, ?, ?, ?)
                ''', (row['Name'], row['Calories_per_100g'], row['Protein_per_100g'], row['Carbohydrates_per_100g'],
                      row['Fats_per_100g']))

        # Load meal_plans from CSV to DB
        with open(CSV_MEAL_PLANS, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cursor.execute('''
                    SELECT * FROM meal_plans WHERE 
                    meal_plan = ? AND user_criteria = ? AND total_calories = ? AND total_protein = ? AND total_carbs = ? AND total_fats = ? AND total_price = ? AND meals = ?
                ''', (
                row['Meal Plan'], row['User Criteria'], row['Total Calories'], row['Total Protein'], row['Total Carbs'],
                row['Total Fats'], row['Total Price'], row['Meals']))

                if cursor.fetchone() is None:
                    cursor.execute('''
                        INSERT INTO meal_plans (meal_plan, user_criteria, total_calories, total_protein, total_carbs, total_fats, total_price, meals)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (row['Meal Plan'], row['User Criteria'], row['Total Calories'], row['Total Protein'],
                          row['Total Carbs'], row['Total Fats'], row['Total Price'], row['Meals']))

        conn.commit()
        conn.close()

    print("CSV data loaded into the database without duplication.")

def load_daily_calorie_log_from_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT date, food_items, calories, protein, carbohydrates, fats FROM daily_calorie_log")
        rows = cursor.fetchall()

        if not rows:
            return None

        daily_log = []
        for row in rows:
            daily_log.append({
                'Date': row[0],
                'Food Items': row[1],
                'Calories': row[2],
                'Protein': row[3],
                'Carbohydrates': row[4],
                'Fats': row[5]
            })

        return daily_log

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

    finally:
        conn.close()

def sync_nutritional_info():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT name, calories_per_100g, protein_per_100g, carbohydrates_per_100g, fats_per_100g FROM nutritional_info")
    rows = cursor.fetchall()

    with open(CSV_NUTRITIONAL_INFO, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Calories_per_100g', 'Protein_per_100g', 'Carbohydrates_per_100g', 'Fats_per_100g'])
        writer.writerows(rows)

    conn.close()
    print("Nutritional information synced to CSV successfully.")

def add_nutritional_info(name, calories_per_100g, protein_per_100g, carbohydrates_per_100g, fats_per_100g):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO nutritional_info (name, calories_per_100g, protein_per_100g, carbohydrates_per_100g, fats_per_100g)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, calories_per_100g, protein_per_100g, carbohydrates_per_100g, fats_per_100g))

    conn.commit()
    conn.close()

    sync_nutritional_info()
    print(f"Nutritional information for '{name}' added successfully and synced.")




def sync_categories():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT category FROM categories")
    rows = cursor.fetchall()

    with open(CSV_CATEGORIES, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Category'])
        writer.writerows(rows)

    conn.close()
    print("Categories synced to CSV successfully.")

def add_category(category):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO categories (category)
        VALUES (?)
    ''', (category,))

    conn.commit()
    conn.close()

    sync_categories()
    print(f"Category '{category}' added successfully and synced.")



def sync_food_items():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT category, name, weight, calories, protein, carbohydrates, fats, price FROM food_items")
    rows = cursor.fetchall()

    food_items = []
    for row in rows:
        item = {
            'Category': row[0],
            'Name': row[1],
            'Weight': row[2],
            'Calories': row[3],
            'Protein': row[4],
            'Carbohydrates': row[5],
            'Fats': row[6],
            'Price': row[7] if row[7] is not None else ''
        }
        food_items.append(item)

    with open(CSV_FOOD_ITEMS, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Category', 'Name', 'Weight', 'Calories', 'Protein', 'Carbohydrates', 'Fats', 'Price'])
        writer.writeheader()
        writer.writerows(food_items)

    conn.close()
    print("Food items synced to CSV successfully.")




def get_all_food_items():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT category, name, weight, calories, protein, carbohydrates, fats, price FROM food_items")
        rows = cursor.fetchall()

        if not rows:
            return None

        food_items = []
        for row in rows:
            food_items.append({
                'Category': row[0],
                'Name': row[1],
                'Weight': row[2],
                'Calories': row[3],
                'Protein': row[4],
                'Carbohydrates': row[5],
                'Fats': row[6],
                'Price': row[7]
            })

        return food_items

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

    finally:
        conn.close()


def search_preprocessed_food_items(search_term):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT name, calories, protein, carbohydrates, fats
        FROM preprocessed_food_database
        WHERE name LIKE ?
    ''', ('%' + search_term + '%',))

    results = cursor.fetchall()
    conn.close()

    if results:
        print("Matching items found:")
        for idx, item in enumerate(results, start=1):
            print(f"{idx}. {item[0]} - {item[1]} calories - {item[2]}g protein - {item[3]}g carbs - {item[4]}g fats")
    else:
        print("No matching items found.")

    food_items = [
        {'name': row[0], 'calories': row[1], 'protein': row[2], 'carbohydrates': row[3], 'fats': row[4]}
        for row in results
    ]
    return food_items


def add_food_item(category, name, serving_size, calories, protein, carbs, fats, price):
    """Add a food item to both the database and CSV."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO food_items (category, name, weight, calories, protein, carbohydrates, fats, price)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (category, name, serving_size, calories, protein, carbs, fats, price))

    conn.commit()

    print(f"Food item '{name}' with serving size {serving_size}g added to the database.")

    sync_food_items()

    print(f"Food item '{name}' with serving size {serving_size}g synced to CSV successfully.")

    conn.close()




def update_food_item(original_name, category, new_name, weight, calories, protein, carbs, fats, price=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        if price is None:
            cursor.execute('''
                UPDATE food_items
                SET category = ?, name = ?, weight = ?, calories = ?, protein = ?, carbohydrates = ?, fats = ?
                WHERE name = ?
            ''', (category, new_name, weight, calories, protein, carbs, fats, original_name))
        else:
            cursor.execute('''
                UPDATE food_items
                SET category = ?, name = ?, weight = ?, calories = ?, protein = ?, carbohydrates = ?, fats = ?, price = ?
                WHERE name = ?
            ''', (category, new_name, weight, calories, protein, carbs, fats, price, original_name))

        conn.commit()

        sync_food_items()  # Ensure changes are reflected in the CSV file

        print(f"Food item '{original_name}' updated successfully and synced.")

    except sqlite3.Error as e:
        print(f"Database error while updating food item: {e}")

    finally:
        conn.close()




def delete_food_item(name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT id FROM food_items WHERE name = ?', (name,))
        result = cursor.fetchone()

        if result:
            item_id = result[0]

            cursor.execute('DELETE FROM food_items WHERE id = ?', (item_id,))
            conn.commit()

            cursor.execute('SELECT id FROM food_items WHERE name = ?', (name,))
            deleted_check = cursor.fetchone()

            if deleted_check is None:
                print(f"Item '{name}' successfully deleted from the database.")
            else:
                print(f"Failed to delete '{name}' from the database.")

            sync_food_items()

        else:
            print(f"Warning: Item '{name}' not found in the database.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


def sync_daily_calorie_log():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT Date, food_items, calories, protein, carbohydrates, fats FROM daily_calorie_log")
    rows = cursor.fetchall()

    with open(CSV_DAILY_CALORIE_LOG, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Food Items', 'Calories', 'Protein', 'Carbohydrates', 'Fats'])
        writer.writerows(rows)

    conn.close()
    print("Daily calorie log synced to CSV successfully.")


def add_daily_calorie_log(date, food_items, calories, protein, carbs, fats):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO daily_calorie_log (date, food_items, calories, protein, carbohydrates, fats)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (date, food_items, calories, protein, carbs, fats))

    conn.commit()
    conn.close()
    print(f"Daily calorie log for {date} added successfully and synced.")



def update_daily_calorie_log(log_id, date, food_items, calories, protein, carbs, fats):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Update the database
    cursor.execute('''
        UPDATE daily_calorie_log
        SET date = ?, food_items = ?, calories = ?, protein = ?, carbohydrates = ?, fats = ?
        WHERE id = ?
    ''', (date, food_items, calories, protein, carbs, fats, log_id))

    conn.commit()
    conn.close()

    sync_daily_calorie_log()
    print(f"Daily calorie log ID {log_id} updated successfully and synced.")

def delete_daily_calorie_log(log_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM daily_calorie_log WHERE id = ?', (log_id,))

    conn.commit()
    conn.close()

    sync_daily_calorie_log()
    print(f"Daily calorie log ID {log_id} deleted successfully and synced.")

def clear_daily_calorie_log():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM daily_calorie_log")
        conn.commit()
        print("Daily calorie log cleared successfully.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        conn.close()




def sync_bmi_info():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT height, weight, age, gender, bmi, bmr, tdee FROM bmi_info")
    rows = cursor.fetchall()

    with open(CSV_BMI_INFO, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Height', 'Weight', 'Age', 'Gender', 'BMI', 'BMR', 'TDEE'])
        writer.writerows(rows)

    conn.close()
    print("BMI info synced to CSV successfully.")

def add_bmi_info(height, weight, age, gender, bmi, bmr, tdee):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO bmi_info (height, weight, age, gender, bmi, bmr, tdee)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (height, weight, age, gender, bmi, bmr, tdee))

    conn.commit()
    conn.close()

    sync_bmi_info()
    print(f"BMI info for height {height}, weight {weight} added successfully and synced.")

def update_bmi_info(bmi_id, height, weight, age, gender, bmi, bmr, tdee):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE bmi_info
        SET height = ?, weight = ?, age = ?, gender = ?, bmi = ?, bmr = ?, tdee = ?
        WHERE id = ?
    ''', (height, weight, age, gender, bmi, bmr, tdee, bmi_id))

    conn.commit()
    conn.close()

    sync_bmi_info()
    print(f"BMI info ID {bmi_id} updated successfully and synced.")

def delete_bmi_info(bmi_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM bmi_info WHERE id = ?', (bmi_id,))

    conn.commit()
    conn.close()

    sync_bmi_info()
    print(f"BMI info ID {bmi_id} deleted successfully and synced.")



def sync_goals():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT calories_goal, protein_goal, carbohydrates_goal, fats_goal, target_weight, starting_weight, target_date, weekly_weight_change FROM goals")
    rows = cursor.fetchall()

    with open(CSV_GOALS, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['calories_goal', 'protein_goal', 'carbohydrates_goal', 'fats_goal', 'target_weight', 'starting_weight', 'target_date', 'weekly_weight_change'])
        writer.writerows(rows)

    conn.close()
    print("Goals synced to CSV successfully.")

def add_goal(calories_goal, protein_goal, carbohydrates_goal, fats_goal, target_weight, starting_weight, target_date, weekly_weight_change):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM goals')
    goal_count = cursor.fetchone()[0]

    if goal_count > 0:
        cursor.execute('''
            UPDATE goals
            SET calories_goal = ?, protein_goal = ?, carbohydrates_goal = ?, fats_goal = ?, 
                target_weight = ?, starting_weight = ?, target_date = ?, weekly_weight_change = ?
        ''', (calories_goal, protein_goal, carbohydrates_goal, fats_goal, target_weight, starting_weight, target_date, weekly_weight_change))
    else:
        cursor.execute('''
            INSERT INTO goals (calories_goal, protein_goal, carbohydrates_goal, fats_goal, target_weight, starting_weight, target_date, weekly_weight_change)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (calories_goal, protein_goal, carbohydrates_goal, fats_goal, target_weight, starting_weight, target_date, weekly_weight_change))

    conn.commit()
    conn.close()

    sync_goals()
    print(f"Goal added or updated successfully and synced.")


def update_goal(goal_id, calories_goal, protein_goal, carbohydrates_goal, fats_goal, target_weight, starting_weight, target_date, weekly_weight_change):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE goals
        SET calories_goal = ?, protein_goal = ?, carbohydrates_goal = ?, fats_goal = ?, target_weight = ?, starting_weight = ?, target_date = ?, weekly_weight_change = ?
        WHERE id = ?
    ''', (calories_goal, protein_goal, carbohydrates_goal, fats_goal, target_weight, starting_weight, target_date, weekly_weight_change, goal_id))

    conn.commit()
    conn.close()

    sync_goals()
    print(f"Goal ID {goal_id} updated successfully and synced.")

def delete_goal(goal_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM goals WHERE id = ?', (goal_id,))

    conn.commit()
    conn.close()

    sync_goals()
    print(f"Goal ID {goal_id} deleted successfully and synced.")



def sync_weight_log():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT Date, weight FROM weight_log")
        rows = cursor.fetchall()

        with open(CSV_WEIGHT_LOG, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Weight'])
            writer.writerows(rows)

        print("Weight log synced to CSV successfully.")
    except sqlite3.Error as e:
        print(f"Database error during sync: {e}")
    except Exception as e:
        print(f"General error during sync: {e}")
    finally:
        conn.close()

def load_weight_log_from_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT Date, weight FROM weight_log")
        rows = cursor.fetchall()

        if not rows:
            return None

        weight_log = []
        for row in rows:
            weight_log.append({
                'Date': row[0],
                'Weight': row[1]
            })

        return weight_log

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

    finally:
        conn.close()

def add_weight_log(date, weight):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO weight_log (Date, weight)
            VALUES (?, ?)
        ''', (date, weight))

        conn.commit()
        sync_weight_log()
        print(f"Weight log added successfully and synced.")
    except sqlite3.Error as e:
        print(f"Database error while adding log: {e}")
    finally:
        conn.close()

def update_weight_log(log_id, date, weight):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE weight_log
            SET Date = ?, weight = ?
            WHERE id = ?
        ''', (date, weight, log_id))

        conn.commit()
        sync_weight_log()
        print(f"Weight log ID {log_id} updated successfully and synced.")
    except sqlite3.Error as e:
        print(f"Database error while updating log: {e}")
    finally:
        conn.close()

def delete_weight_log(log_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM weight_log WHERE id = ?', (log_id,))

        conn.commit()
        sync_weight_log()
        print(f"Weight log ID {log_id} deleted successfully and synced.")
    except sqlite3.Error as e:
        print(f"Database error while deleting log: {e}")
    finally:
        conn.close()

def clear_weight_log():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM weight_log")
        conn.commit()
        print("Weight log cleared successfully.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        conn.close()





def sync_meal_plans_to_csv():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT meal_plan, user_criteria, total_calories, total_protein, total_carbs, total_fats, total_price, meals 
            FROM meal_plans
        ''')
        meal_plans = cursor.fetchall()

        with open(CSV_MEAL_PLANS, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Meal Plan', 'User Criteria', 'Total Calories', 'Total Protein', 'Total Carbs', 'Total Fats', 'Total Price', 'Meals'])
            writer.writerows(meal_plans)

        print("Meal plans synced to CSV successfully.")
    except Exception as e:
        print(f"Error while syncing meal plans to CSV: {e}")
    finally:
        conn.close()

def get_all_meal_plans():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT meal_plan, total_calories, total_protein, total_carbs, total_fats, total_price, meals
            FROM meal_plans
        ''')

        meal_plans = cursor.fetchall()

        if not meal_plans:
            return None

        meal_plan_list = []
        for row in meal_plans:
            meal_plan = {
                "meal_plan": row[0],
                "total_calories": row[1],
                "total_protein": row[2],
                "total_carbs": row[3],
                "total_fats": row[4],
                "total_price": row[5],
                "meals": row[6]
            }
            meal_plan_list.append(meal_plan)

        return meal_plan_list

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

    finally:
        conn.close()

def clear_all_meal_plans():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM meal_plans")
        conn.commit()
        print("Old meal plans cleared from the database successfully.")
    except sqlite3.Error as e:
        print(f"Database error while clearing meal plans: {e}")
    finally:
        conn.close()

def save_meal_plans_to_db(meal_plan, user_criteria, total_calories, total_protein, total_carbs, total_fats, total_price, meals):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO meal_plans (meal_plan, user_criteria, total_calories, total_protein, total_carbs, total_fats, total_price, meals)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (meal_plan, str(user_criteria), float(total_calories), float(total_protein),
              float(total_carbs), float(total_fats), float(total_price), meals))  # 'meals' added here

        conn.commit()
        print("Meal plans saved successfully to the database.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def import_meal_plans_from_csv():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with open('/TESTCODE/TESTCSV/TEST_meal_plans.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get('Meal Plan') and row.get('Meals'):
                cursor.execute('''
                    INSERT INTO meal_plans (meal_plan, user_criteria, total_calories, total_protein, total_carbs, total_fats, total_price, meals)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (row['Meal Plan'], row['User Criteria'], row['Total Calories'], row['Total Protein'],
                      row['Total Carbs'], row['Total Fats'], row['Total Price'],
                      row['Meals']))

    conn.commit()
    conn.close()

    print("Meal plans successfully imported into the database.")


def sync_all():
    sync_food_items()
    sync_daily_calorie_log()
    sync_bmi_info()
    sync_goals()
    sync_nutritional_info()
    sync_categories()
    sync_weight_log()
    sync_meal_plans_to_csv()

    print("All data synced successfully!")





# AI STUFF
def fetch_user_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT date, food_items, calories, protein, carbohydrates, fats
        FROM daily_calorie_log
    ''')

    user_history = cursor.fetchall()
    conn.close()

    if user_history:
        history_list = []
        for row in user_history:
            history_list.append({
                'date': row[0],
                'food_items': row[1],
                'calories': row[2],
                'protein': row[3],
                'carbohydrates': row[4],
                'fats': row[5]
            })
        return history_list
    else:
        return []

def fetch_goals_from_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Fetch the goals (no user_id filtering)
    cursor.execute('''
        SELECT calories_goal, protein_goal, carbohydrates_goal, fats_goal, target_weight, starting_weight, target_date, weekly_weight_change
        FROM goals
        LIMIT 1
    ''')

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            'calories_goal': row[0],
            'protein_goal': row[1],
            'carbohydrates_goal': row[2],
            'fats_goal': row[3],
            'target_weight': row[4],
            'starting_weight': row[5],
            'target_date': row[6],
            'weekly_weight_change': row[7]
        }
    else:
        return None


## MEAL RECOMMENDATION
def store_daily_meal_plan(day, daily_meal_plan):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO weekly_meal_plan (day, meals)
            VALUES (?, ?)
        ''', (day, str(daily_meal_plan)))

        conn.commit()
        print(f"{day}'s meal plan stored successfully.")

    except sqlite3.Error as e:
        print(f"Database error while storing {day}'s meal plan: {e}")

    finally:
        conn.close()

def clear_weekly_meal_plans():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM weekly_meal_plan")
    conn.commit()

    conn.close()

def save_weekly_AI_meal_plan_to_db(weekly_meal_plan):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM weekly_ai_meal_plan')

    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    for day in days_of_week:
        if day in weekly_meal_plan:
            for meal in weekly_meal_plan[day]['meals']:
                cursor.execute('''INSERT INTO weekly_ai_meal_plan (day, meal_name, calories, protein, carbohydrates, fats)
                                  VALUES (?, ?, ?, ?, ?, ?)''',
                               (day, meal['Name'], meal['Calories'], meal['Protein'], meal['Carbohydrates'], meal['Fats']))

    conn.commit()
    conn.close()

    print("Weekly AI meal plan saved to the database successfully.")


def fetch_weekly_AI_meal_plan():

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute('''SELECT day, meal_name, calories, protein, carbohydrates, fats 
                          FROM weekly_ai_meal_plan 
                          ORDER BY CASE 
                              WHEN day = 'Monday' THEN 1
                              WHEN day = 'Tuesday' THEN 2
                              WHEN day = 'Wednesday' THEN 3
                              WHEN day = 'Thursday' THEN 4
                              WHEN day = 'Friday' THEN 5
                              WHEN day = 'Saturday' THEN 6
                              WHEN day = 'Sunday' THEN 7
                          END''')
        rows = cursor.fetchall()

    if not rows:
        return None, None

    meal_plan = {}
    total_macros = {'calories': 0, 'protein': 0, 'carbohydrates': 0, 'fats': 0}

    for row in rows:
        day, meal_name, calories, protein, carbohydrates, fats = row

        if day not in meal_plan:
            meal_plan[day] = {'meals': [], 'daily_totals': {'calories': 0, 'protein': 0, 'carbohydrates': 0, 'fats': 0}}

        meal_plan[day]['meals'].append({
            'name': meal_name,
            'calories': calories,
            'protein': protein,
            'carbohydrates': carbohydrates,
            'fats': fats
        })

        meal_plan[day]['daily_totals']['calories'] += calories
        meal_plan[day]['daily_totals']['protein'] += protein
        meal_plan[day]['daily_totals']['carbohydrates'] += carbohydrates
        meal_plan[day]['daily_totals']['fats'] += fats

    return meal_plan, total_macros



## CALORIE PREDICTION

def fetch_user_profile_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('SELECT height, weight, age, gender, bmr, tdee FROM bmi_info LIMIT 1')
    row = cursor.fetchone()

    conn.close()

    if row:
        return {
            'weight': row[1],
            'height': row[0],
            'age': row[2],
            'gender': row[3],
            'bmr': row[4],
            'tdee': row[5]
        }
    else:
        return None


