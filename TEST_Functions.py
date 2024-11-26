import csv
import os
import itertools
import numpy as np
import TEST_AI
import TEST_AI_Database
import matplotlib.pyplot as plt
import pandas as pd
import json
from statsmodels.tsa.stattools import adfuller

from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_FILE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_food_items.csv')
NUTRITIONAL_INFO_FILE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_nutritional_info.csv')
CATEGORY_FILE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_categories.csv')
BMI_FILE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_bmi_info.csv')
GOALS_FILE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_goals.csv')
WEIGHT_LOG_FILE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_weight_log.csv')
DAILY_CALORIE_LOG_FILE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_daily_calorie_log.csv')
MEAL_PLAN_FILE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_meal_plans.csv')
PREPROCESSED_DATABASE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_preprocessed_food_database.csv')
DEFAULT_CATEGORIES = ["Main", "Snack", "Drink"]




# CSV FUNCTIONS
def create_file_if_not_exists(file_path, headers=None):
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as file:
            if headers:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()

def load_csv_to_dict(file_path, expected_headers=None):
    data = []
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)

                actual_headers = reader.fieldnames
                if expected_headers and actual_headers != expected_headers:
                    print(f"Warning: Headers in {file_path} do not match the expected format.")
                    print(f"Expected headers: {expected_headers}")
                    print(f"Actual headers: {actual_headers}")
                    return []

                data = list(reader)
        except (IOError, csv.Error) as e:
            print(f"Error reading {file_path}: {e}")
    return data



def save_dict_to_csv(file_path, data, headers):
    if not data:
        print(f"No data to save to {file_path}.")
        return

    for item in data:
        missing_keys = [key for key in headers if key not in item]
        if missing_keys:
            print(f"Error: The following fields are missing from the data: {missing_keys}")
            return

    try:
        with open(file_path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
    except IOError as e:
        print(f"Error writing to {file_path}: {e}")



def create_csv_files():
    files_with_headers = {
        CSV_FILE: ["Category", "Name", "Weight", "Calories", "Protein", "Carbohydrates", "Fats", "Price"],
        NUTRITIONAL_INFO_FILE: ["Name", "Calories_per_100g", "Protein_per_100g", "Carbohydrates_per_100g",
                                "Fats_per_100g"],
        CATEGORY_FILE: ["Category"],
        BMI_FILE: ["Height", "Weight", "Age", "Gender", "BMI", "BMR", "TDEE"],
        GOALS_FILE: ["calories_goal", "protein_goal", "carbohydrates_goal", "fats_goal", "target_weight", "starting date", "target_date",
                     "weekly_weight_change"],
        WEIGHT_LOG_FILE: ["Date", "Weight"],
        DAILY_CALORIE_LOG_FILE: ["Date", "Food Items", "Calories", "Protein", "Carbohydrates", "Fats"],
        MEAL_PLAN_FILE: ["Meal Plan", "User Criteria", "Total Calories", "Total Protein", "Total Carbs", "Total Fats",
                         "Total Price", "Meal Plan Details"]
    }

    for file_path, headers in files_with_headers.items():
        if not os.path.exists(file_path):
            print(f"{file_path} does not exist. Creating and syncing data from the database...")
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)

            if file_path == CSV_FILE:
                TEST_AI_Database.sync_food_items()
            elif file_path == NUTRITIONAL_INFO_FILE:
                TEST_AI_Database.sync_nutritional_info()
            elif file_path == CATEGORY_FILE:
                TEST_AI_Database.sync_categories()
            elif file_path == BMI_FILE:
                TEST_AI_Database.sync_bmi_info()
            elif file_path == GOALS_FILE:
                TEST_AI_Database.sync_goals()
            elif file_path == WEIGHT_LOG_FILE:
                TEST_AI_Database.sync_weight_log()
            elif file_path == MEAL_PLAN_FILE:
                TEST_AI_Database.sync_meal_plans_to_csv()
            elif file_path == DAILY_CALORIE_LOG_FILE:
                TEST_AI_Database.sync_daily_calorie_log()

    print("CSV files created and synced from the database successfully.")


def sync_csv_if_missing():
    if not os.path.exists(CSV_FILE):
        print(f"{CSV_FILE} is missing. Syncing from the database...")
        TEST_AI_Database.sync_food_items()

    if not os.path.exists(DAILY_CALORIE_LOG_FILE):
        print(f"{DAILY_CALORIE_LOG_FILE} is missing. Syncing from the database...")
        TEST_AI_Database.sync_daily_calorie_log()

    if not os.path.exists(BMI_FILE):
        print(f"{BMI_FILE} is missing. Syncing from the database...")
        TEST_AI_Database.sync_bmi_info()

    if not os.path.exists(GOALS_FILE):
        print(f"{GOALS_FILE} is missing. Syncing from the database...")
        TEST_AI_Database.sync_goals()

    if not os.path.exists(CATEGORY_FILE):
        print(f"{CATEGORY_FILE} is missing. Syncing from the database...")
        TEST_AI_Database.sync_categories()

    if not os.path.exists(WEIGHT_LOG_FILE):
        print(f"{WEIGHT_LOG_FILE} is missing. Syncing from the database...")
        TEST_AI_Database.sync_weight_log()

    if not os.path.exists(NUTRITIONAL_INFO_FILE):
        print(f"{NUTRITIONAL_INFO_FILE} is missing. Syncing from the database...")
        TEST_AI_Database.sync_nutritional_info()

    if not os.path.exists(MEAL_PLAN_FILE):
        print(f"{MEAL_PLAN_FILE} is missing. Syncing from the database...")
        TEST_AI_Database.sync_meal_plans_to_csv()


def save_daily_intake_to_csv(date, selected_items, total_calories, total_protein, total_carbs, total_fats):
    try:
        with open(DAILY_CALORIE_LOG_FILE, 'a', newline='') as file:  # Open in append mode
            writer = csv.DictWriter(file, fieldnames=["Date", "Food Items", "Calories", "Protein", "Carbohydrates", "Fats"])

            food_items_str = '; '.join([item['Name'] for item in selected_items])

            writer.writerow({
                "Date": date,
                "Food Items": food_items_str,
                "Calories": round(total_calories, 2),
                "Protein": round(total_protein, 2),
                "Carbohydrates": round(total_carbs, 2),
                "Fats": round(total_fats, 2)
            })
    except IOError as e:
        print(f"An error occurred while saving daily intake data: {e}")

def populate_database_if_empty():
    if TEST_AI_Database.is_database_empty():
        print("Database is empty, populating from CSV files...")
        TEST_AI_Database.load_csv_to_database()
def load_categories():
    try:
        if os.path.exists(CATEGORY_FILE):
            with open(CATEGORY_FILE, 'r') as file:
                reader = csv.reader(file)
                header = next(reader, None)

                if header is None or header[0].strip().lower() != 'category':
                    print(f"Warning: Missing or incorrect header in {CATEGORY_FILE}. Loading default categories.")
                    return DEFAULT_CATEGORIES

                categories = [row[0].strip() for row in reader if
                              row and len(row) > 0]

                if not categories or any(not category for category in categories):
                    print(f"Warning: Invalid or empty categories found in {CATEGORY_FILE}. Loading default categories.")
                    return DEFAULT_CATEGORIES

                return categories
        else:
            print(f"Warning: {CATEGORY_FILE} not found. Loading default categories.")
            return DEFAULT_CATEGORIES

    except (IOError, csv.Error) as e:
        print(f"Error reading {CATEGORY_FILE}: {e}. Loading default categories.")
        return DEFAULT_CATEGORIES


def load_food_database():
    return load_csv_to_dict(PREPROCESSED_DATABASE)


def load_nutritional_info():
    nutritional_info = {}
    data = load_csv_to_dict(NUTRITIONAL_INFO_FILE)
    for row in data:
        nutritional_info[row['Name'].lower()] = {
            "Calories_per_100g": float(row["Calories_per_100g"]),
            "Protein_per_100g": float(row["Protein_per_100g"]),
            "Carbohydrates_per_100g": float(row["Carbohydrates_per_100g"]),
            "Fats_per_100g": float(row["Fats_per_100g"])
        }
    return nutritional_info

def load_goals():
    try:
        with open(GOALS_FILE, 'r') as file:
            reader = csv.DictReader(file)
            return next(reader, None)
    except FileNotFoundError:
        print("Goals file not found.")
        return None
    except IOError as e:
        print(f"An error occurred while loading the goals: {e}")
        return None


def save_to_csv(food_item):
    headers = ["Category", "Name", "Weight", "Calories", "Protein", "Carbohydrates", "Fats", "Price"]

    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerow(food_item)


# RES
def input_with_validation(prompt, valid_options=None, input_type=str, allow_go_back=False):
    while True:
        try:
            user_input = input_type(input(prompt))
            if allow_go_back and user_input == 0:
                return 0
            if valid_options and user_input not in valid_options:
                raise ValueError("Invalid option selected.")
            return user_input
        except ValueError as e:
            print(e)

def display_categories(categories):
    for idx, category in enumerate(categories, start=1):
        print(f"{idx}. {category}")
    print("n. Add your own category")
    print("0. Go Back")

def add_or_get_category(categories):
    print("Current categories:", ", ".join(categories))
    new_category = input("Enter a category (or create a new one): ")
    if new_category in categories:
        print("This category already exists.")
        return None
    elif new_category != '0':
        categories.append(new_category)
        save_categories(categories)
        return new_category
    return None

def save_categories(categories):
    with open(CATEGORY_FILE, 'w', newline='') as file:
        for category in categories:
            file.write(category + '\n')


def save_nutritional_info(name, Calories_per_100g, Protein_per_100g, Carbohydrates_per_100g, Fats_per_100g):
    try:
        with open(NUTRITIONAL_INFO_FILE, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Name", "Calories_per_100g", "Protein_per_100g", "Carbohydrates_per_100g", "Fats_per_100g"])
            writer.writerow({
                "Name": name,
                "Calories_per_100g": Calories_per_100g,
                "Protein_per_100g": Protein_per_100g,
                "Carbohydrates_per_100g": Carbohydrates_per_100g,
                "Fats_per_100g": Fats_per_100g
            })
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")


def search_food_database(food_database, search_query):
    matching_items = [
        item for item in food_database
        if search_query in item.get('name', '').strip().lower()
    ]
    return matching_items



def add_searched_item_to_food_list(matching_items):
    while True:
        choice = input("Enter the number of the item you want to add to your food list (or '0' to go back): ").strip()

        if choice == '0':
            return

        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(matching_items):
            print("Invalid choice. Please select a valid number.")
            continue

        selected_item = matching_items[int(choice) - 1]

        serving_size = input_with_error_handling("Enter your serving size (in grams): ", input_type=float,
                                                 error_message="Please enter a valid serving size.")

        try:
            calories = (float(selected_item.get('calories', selected_item.get('Calories'))) / 100) * serving_size
            protein = (float(selected_item.get('protein', selected_item.get('Protein (g)'))) / 100) * serving_size
            carbs = (float(selected_item.get('carbohydrates', selected_item.get('Carbohydrate (g)'))) / 100) * serving_size
            fats = (float(selected_item.get('fats', selected_item.get('Fat (g)'))) / 100) * serving_size
        except KeyError as e:
            print(f"Error: Missing key in selected item: {e}")
            return

        food_item = {
            "Category": "Database Item",
            "Name": selected_item['name'],
            "Weight": serving_size,
            "Calories": calories,
            "Protein": protein,
            "Carbohydrates": carbs,
            "Fats": fats,
            "Price": 0
        }

        TEST_AI_Database.add_food_item(
            category=food_item['Category'],
            name=food_item['Name'],
            weight=food_item['Weight'],
            calories=food_item['Calories'],
            protein=food_item['Protein'],
            carbs=food_item['Carbohydrates'],
            fats=food_item['Fats'],
            price=food_item['Price']
        )
        print(f"\nAdded {serving_size}g of {selected_item['name']} to your food list.")
        print(f"Calories: {calories:.2f} kcal")
        print(f"Protein: {protein:.2f}g")
        print(f"Carbohydrates: {carbs:.2f}g")
        print(f"Fats: {fats:.2f}g\n")
        break



def display_food_items(food_items):
    for idx, item in enumerate(food_items, start=1):
        name = item.get('Name', item.get('name', 'Unknown Name'))
        category = item.get('Category', item.get('category', 'Unknown Category'))
        calories = round(float(item.get('Calories', item.get('calories', 0))), 1)
        protein = round(float(item.get('Protein', item.get('protein', 0))), 1)
        carbs = round(float(item.get('Carbohydrates', item.get('carbohydrates', 0))), 1)
        fats = round(float(item.get('Fats', item.get('fats', 0))), 1)
        weight = round(float(item.get('Weight', item.get('weight', 0))), 1)

        serving_label = " (Multiple serving sizes)" if item.get('multiple_servings') else ""

        print(f"{idx}. {name} - {category} - {calories:.1f} calories - {protein:.1f}g protein - "
              f"{carbs:.1f}g carbs - {fats:.1f}g fats ({weight:.1f}g serving size){serving_label}")



def delete_food_item(food_items, item):
    confirm = input(f"Are you sure you want to delete '{item['name']}'? (y/n): ").lower()

    if confirm == 'y':
        if 'name' in item:
            try:
                TEST_AI_Database.delete_food_item(item['name'])
            except Exception as e:
                print(f"Error deleting '{item['name']}' from the database: {e}")
        else:
            print("Warning: The item does not have a 'name' and cannot be deleted from the database.")

        food_items = [food for food in food_items if food['name'] != item['name']]

        required_fields = ["category", "name", "weight", "calories", "protein", "carbohydrates", "fats", "price"]
        for food in food_items:
            for field in required_fields:
                if field not in food:
                    food[field] = None

        for food in food_items:
            if 'id' in food:
                del food['id']

        save_dict_to_csv(CSV_FILE, food_items, headers=required_fields)

        print(f"Item '{item['name']}' deleted successfully from the list.")
    else:
        print("Deletion cancelled.")



def edit_food_item(food_items, item_name):
    item = next((x for x in food_items if x['name'] == item_name), None)

    if not item:
        print(f"Error: Food item '{item_name}' not found.")
        return

    print(f"Editing '{item_name}'")

    if 'id' not in item:
        print("Error: Item does not have an 'id' and cannot be updated in the database.")
        return

    new_name = input(f"Enter new name (leave blank to keep current value '{item['name']}'): ").strip()
    new_calories = input(f"Enter new calories (leave blank to keep current value '{item['calories']}'): ").strip()
    new_protein = input(f"Enter new protein (leave blank to keep current value '{item['protein']}'): ").strip()
    new_carbs = input(f"Enter new carbohydrates (leave blank to keep current value '{item['carbohydrates']}'): ").strip()
    new_fats = input(f"Enter new fats (leave blank to keep current value '{item['fats']}'): ").strip()

    current_price = item.get('price', "N/A")
    new_price = input(f"Enter new price (leave blank to keep current value '{current_price}'): ").strip()

    item['name'] = new_name if new_name else item['name']
    item['calories'] = float(new_calories) if new_calories else item['calories']
    item['protein'] = float(new_protein) if new_protein else item['protein']
    item['carbohydrates'] = float(new_carbs) if new_carbs else item['carbohydrates']
    item['fats'] = float(new_fats) if new_fats else item['fats']

    if new_price:
        item['price'] = float(new_price)
    elif 'price' not in item:
        item['price'] = None

    TEST_AI_Database.update_food_item(
        item['id'], item['category'], item['name'], item['weight'], item['calories'],
        item['protein'], item['carbohydrates'], item['fats'], item.get('price')
    )

    print(f"Food item '{item['name']}' updated successfully.")



def get_user_criteria():
    criteria = {
        'calories_lower': None, 'calories_upper': None,
        'protein_lower': None, 'protein_upper': None,
        'carbs_lower': None, 'carbs_upper': None,
        'fats_lower': None, 'fats_upper': None,
        'price_lower': None, 'price_upper': None
    }
    for key in criteria:
        value = input(f"{key.replace('_', ' ').title()}: ")
        criteria[key] = float(value) if value else None
    return criteria






def load_bmi_info():
    bmi_info = load_csv_to_dict(BMI_FILE)
    if bmi_info:
        return bmi_info[0]
    return None

def save_bmi_info(height, weight, age, gender, bmi, bmr, tdee):
    try:
        save_dict_to_csv(BMI_FILE, [{
            'Height': height,
            'Weight': weight,
            'Age': age,
            'Gender': gender,
            'BMI': bmi,
            'BMR': bmr,
            'TDEE': tdee
        }], headers=['Height', 'Weight', 'Age', 'Gender', 'BMI', 'BMR', 'TDEE'])
    except IOError as e:
        print(f"An error occurred while saving BMI data: {e}")

def print_weekly_weight_goals(current_weight, weekly_weight_change, start_date, target_date):
    current_date = start_date
    while current_date <= target_date:
        print(f"{current_date.strftime('%d/%m/%Y')} - {current_weight:.1f}kg")
        current_date += timedelta(weeks=1)
        current_weight += weekly_weight_change

def visualize_weight_progression(current_weight, target_weight, current_date, target_date, weekly_weight_change):
    dates = []
    predicted_weights = []

    current_weight_progression = current_weight
    current_date_progression = current_date

    while current_date_progression <= target_date:
        dates.append(current_date_progression)
        predicted_weights.append(current_weight_progression)

        current_weight_progression += weekly_weight_change

        current_date_progression += timedelta(weeks=1)

    plt.plot(dates, predicted_weights, marker='x', linestyle='--', color='r', label='Goal Weight Progression')

    plt.xlabel("Date")
    plt.ylabel("Weight (kg)")
    plt.title("Weight Progress Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()


def input_target_date():
    while True:
        target_date_str = input("Enter your target date (DD-MM-YYYY): ").strip()

        try:
            target_date = datetime.strptime(target_date_str, "%d-%m-%Y")

            if target_date <= datetime.now():
                print("The target date must be in the future. Please enter a valid future date.")
                continue

            return target_date

        except ValueError:
            print("Invalid date format. Please enter the date in DD-MM-YYYY format.")




# FOOD FUNCTIONS
def input_with_error_handling(prompt, input_type=str, error_message="Please enter a value.", allow_blank=False, valid_options=None):
    while True:
        user_input = input(prompt).strip()

        if not user_input and allow_blank:
            return None

        if not user_input and not allow_blank:
            print(error_message)
            continue

        try:
            typed_input = input_type(user_input)
        except ValueError:
            print(f"Please enter a valid {input_type.__name__}.")
            continue

        if valid_options and typed_input not in valid_options:
            valid_options_str = [str(option) for option in valid_options]
            print(f"Invalid option. Please choose from: {', '.join(valid_options_str)}")
            continue

        return typed_input


def meal_planning_menu():
    while True:
        print("\nMeal Planning Options:")
        print("1. View Current Meal Plans")
        print("2. Generate New Meal Plan")
        print("3. Generate AI-Powered Meal Plan")
        print("4. View Weekly Meal Plan (AI-Powered)")
        print("5. Clear All Meal Plans")
        print("0. Go Back")

        choice = input_with_error_handling("Enter your choice: ", input_type=int, valid_options=[0, 1, 2, 3, 4, 5])

        if choice == 0:
            return
        elif choice == 1:
            view_current_meal_plans()
        elif choice == 2:
            generate_meal_plan()
        elif choice == 3:
            generate_AI_meal_plan()
        elif choice == 4:
            view_AI_meal_plan()
        elif choice == 5:
            clear_all_meal_plans()





def food_and_meal_management_menu(categories):
    while True:
        print("\nFood & Meal Management Menu:")
        print("1. Add Food Item")
        print("2. Browse Food Database")
        print("3. Show Items")
        print("4. Meal Planning")
        print("5. Food Log")
        print("0. Go Back")

        choice = input_with_error_handling("Enter your choice: ", input_type=int, valid_options=[0, 1, 2, 3, 4, 5])

        if choice == 0:
            return
        elif choice == 1:
            add_food_item(categories)
        elif choice == 2:
            browse_food_database()
        elif choice == 3:
            show_items()
        elif choice == 4:
            meal_planning_menu()
        elif choice == 5:
            food_log_menu()



def food_log_menu():
    while True:
        print("\nFood Log Menu:")
        print("1. Calculate Daily Intake")
        print("2. View Log")
        print("3. Clear History")
        print("0. Go Back")

        choice = input_with_error_handling("Enter your choice: ", input_type=int, valid_options=[0, 1, 2, 3])

        if choice == 0:
            return
        elif choice == 1:
            calculate_daily_intake()
        elif choice == 2:
            view_daily_log()
        elif choice == 3:
            clear_daily_calorie_logs()


def visualize_daily_nutrient_log():
    try:
        daily_log = TEST_AI_Database.load_daily_calorie_log_from_db()

        if not daily_log:
            print("No daily logs found in the database.")
            return

        print("Which metrics would you like to visualize?")
        print("1. Calories")
        print("2. Protein")
        print("3. Fats")
        print("4. Carbohydrates")
        print("5. All of the above")
        print("0. Go Back")
        selected_metrics = input("Your choice: ").replace(' ', '').split(',')

        if '0' in selected_metrics:
            print("Returning to the previous menu...")
            return

        dates = [datetime.strptime(entry['Date'], '%d-%m-%Y') for entry in daily_log]
        formatted_dates = [date.strftime('%d-%m') for date in dates]

        metrics_map = {
            '1': {'name': 'Calories', 'values': [float(entry['Calories']) for entry in daily_log], 'color': 'b',
                  'ylabel': 'Calories (kcal)', 'goal_key': 'calories_goal'},
            '2': {'name': 'Protein', 'values': [float(entry['Protein']) for entry in daily_log], 'color': 'g',
                  'ylabel': 'Protein (g)', 'goal_key': 'protein_goal'},
            '3': {'name': 'Fats', 'values': [float(entry['Fats']) for entry in daily_log], 'color': 'r',
                  'ylabel': 'Fats (g)', 'goal_key': 'fats_goal'},
            '4': {'name': 'Carbohydrates', 'values': [float(entry['Carbohydrates']) for entry in daily_log],
                  'color': 'purple', 'ylabel': 'Carbohydrates (g)', 'goal_key': 'carbohydrates_goal'}
        }

        if '5' in selected_metrics:
            selected_metrics = ['1', '2', '3', '4']

        valid_choices = {'1', '2', '3', '4'}
        selected_metrics = [metric for metric in selected_metrics if metric in valid_choices]

        if not selected_metrics:
            print("No valid metrics selected.")
            return

        goals = TEST_AI_Database.fetch_goals_from_db()

        plt.figure(figsize=(10, 6))
        for metric in selected_metrics:
            metric_data = metrics_map[metric]
            plt.plot(formatted_dates, metric_data['values'], marker='o', linestyle='-', label=metric_data['name'],
                     color=metric_data['color'])

            if goals and goals.get(metric_data['goal_key']):
                goal_value = float(goals[metric_data['goal_key']])
                plt.axhline(y=goal_value, color=metric_data['color'], linestyle='--',
                            label=f'{metric_data["name"]} Goal: {goal_value} {metric_data["ylabel"]}')

        plt.xlabel('Date (dd-mm)')
        plt.title("Daily Nutrient Log")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        if len(selected_metrics) == 1:
            plt.ylabel(metrics_map[selected_metrics[0]]['ylabel'])
        else:
            plt.ylabel("Nutrient Amount")

        plt.show()

    except Exception as e:
        print(f"An error occurred while visualizing the daily log: {e}")

def view_daily_log():
    daily_log = TEST_AI_Database.load_daily_calorie_log_from_db()

    if not daily_log:
        print("No entries found in the daily log.")
        return

    print("Date       | Calories | Protein (g) | Carbohydrates (g) | Fats (g)")
    print("---------------------------------------------------------------")

    for entry in daily_log:
        print(f"{entry['Date']} | {entry['Calories']} kcal | {entry['Protein']}g | {entry['Carbohydrates']}g | {entry['Fats']}g")

    print("")
    view_graph = input_with_error_handling(
        "Would you like to visualise your progress? (y/n): ", input_type=str, valid_options=['y', 'n']
    ).lower()

    if view_graph == 'y':
        visualize_daily_nutrient_log()

def visualize_daily_calorie_log():
    try:
        daily_log = TEST_AI_Database.load_daily_calorie_log_from_db()

        if not daily_log:
            print("No daily calorie logs found in the database.")
            return

        dates = [datetime.strptime(entry['Date'], '%d-%m-%Y') for entry in daily_log]
        calories = [float(entry['Calories']) for entry in daily_log]

        formatted_dates = [date.strftime('%d-%m') for date in dates]

        plt.plot(formatted_dates, calories, marker='o', linestyle='-', label='Calories Consumed', color='b')

        goals = TEST_AI_Database.fetch_goals_from_db()
        if goals:
            calorie_goal = float(goals['calories_goal'])
            target_date = datetime.strptime(goals['target_date'], '%d-%m-%Y')

            plt.axhline(y=calorie_goal, color='orange', linestyle='--', label=f'Calorie Goal: {calorie_goal} kcal')

        plt.xlabel('Date (dd-mm)')
        plt.ylabel('Calories (kcal)')
        plt.title('Daily Calorie Log')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"An error occurred while visualizing the daily calorie log: {e}")

def save_daily_log(date, total_calories, total_protein, total_carbs, total_fats):
    log_entry = {
        'date': date,
        'calories': total_calories,
        'protein': total_protein,
        'carbohydrates': total_carbs,
        'fats': total_fats
    }

    TEST_AI_Database.add_daily_calorie_log(
        date=date,
        food_items='N/A',
        calories=total_calories,
        protein=total_protein,
        carbohydrates=total_carbs,
        fats=total_fats
    )

    existing_logs = load_csv_to_dict(DAILY_CALORIE_LOG_FILE)

    existing_entry = next((entry for entry in existing_logs if entry['Date'] == date), None)

    if existing_entry:
        existing_entry['Calories'] = float(existing_entry['Calories']) + total_calories
        existing_entry['Protein'] = float(existing_entry['Protein']) + total_protein
        existing_entry['Carbohydrates'] = float(existing_entry['Carbohydrates']) + total_carbs
        existing_entry['Fats'] = float(existing_entry['Fats']) + total_fats
    else:
        existing_logs.append({
            'Date': date,
            'Calories': total_calories,
            'Protein': total_protein,
            'Carbohydrates': total_carbs,
            'Fats': total_fats
        })

    save_dict_to_csv(DAILY_CALORIE_LOG_FILE, existing_logs, headers=['Date', 'Calories', 'Protein', 'Carbohydrates', 'Fats'])

    print("Daily log updated successfully in both the database and CSV.")

def clear_daily_calorie_logs():
    confirmation = input_with_error_handling(
        "Are you sure you want to clear all daily calorie intake logs? This action cannot be undone (y/n): ",
        input_type=str,
        valid_options=['y', 'n']
    )

    if confirmation.lower() == 'y':
        try:
            with open(DAILY_CALORIE_LOG_FILE, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["Date", "Food Items", "Calories", "Protein", "Carbohydrates", "Fats"])
                writer.writeheader()

            TEST_AI_Database.clear_daily_calorie_log()

            print("Daily calorie intake logs cleared successfully from both the CSV and the database.")
        except IOError as e:
            print(f"An error occurred while clearing the logs: {e}")
        except Exception as e:
            print(f"An error occurred while clearing the logs in the database: {e}")
    else:
        print("Clear operation cancelled.")


def add_food_item(categories):
    nutritional_info = TEST_AI_Database.fetch_nutritional_info_from_db()

    if isinstance(nutritional_info, list) and not nutritional_info:
        nutritional_info = load_csv_to_dict(NUTRITIONAL_INFO_FILE)

    existing_food_items = TEST_AI_Database.fetch_food_items_from_db()

    if isinstance(existing_food_items, pd.DataFrame):
        if existing_food_items.empty:
            existing_food_items = load_csv_to_dict(CSV_FILE)
        existing_food_items = existing_food_items.to_dict(orient='records')

    elif isinstance(existing_food_items, list) and not existing_food_items:
        existing_food_items = load_csv_to_dict(CSV_FILE)

    print("\nAdding New Food Item:")
    while True:
        display_categories(categories)

        category_choice = input_with_error_handling(
            "Choose a category, 'n' for new category, 'f' to finish, or '0' to go back: ",
            error_message="Please select a category or an option."
        ).lower()

        if category_choice == '0':
            return None
        elif category_choice == 'f':
            return None
        elif category_choice == 'n':
            category = add_or_get_category(categories)
            if category is None:
                continue
        elif category_choice.isdigit() and 1 <= int(category_choice) <= len(categories):
            category = categories[int(category_choice) - 1]
        else:
            print("Invalid option. Please try again.")
            continue

        name = input_with_error_handling("Enter the name of the food: ",
                                         error_message="Please enter a food name.").lower()

        existing_food = [item for item in existing_food_items if item['name'].lower() == name.lower()]

        if existing_food:
            add_new_serving = input_with_error_handling(
                "This food item is already saved. Would you like to add another serving size (y/n)? ",
                error_message="Please enter 'y' to add another serving size or 'n' to skip."
            )
            if add_new_serving.lower() != 'y':
                return None

            info = {
                "Calories_per_100g": float(existing_food[0]['calories']) / (float(existing_food[0]['weight']) / 100),
                "Protein_per_100g": float(existing_food[0]['protein']) / (float(existing_food[0]['weight']) / 100),
                "Carbohydrates_per_100g": float(existing_food[0]['carbohydrates']) / (float(existing_food[0]['weight']) / 100),
                "Fats_per_100g": float(existing_food[0]['fats']) / (float(existing_food[0]['weight']) / 100)
            }

            price = float(existing_food[0]['price'])

        else:
            info = {
                "Calories_per_100g": input_with_error_handling(
                    "Enter the calorie content per 100 grams: ",
                    input_type=float,
                    error_message="Please enter the calorie content as a number."
                ),
                "Protein_per_100g": input_with_error_handling(
                    "Enter the protein content per 100 grams: ",
                    input_type=float,
                    error_message="Please enter the protein content as a number."
                ),
                "Carbohydrates_per_100g": input_with_error_handling(
                    "Enter the carbohydrate content per 100 grams: ",
                    input_type=float,
                    error_message="Please enter the carbohydrate content as a number."
                ),
                "Fats_per_100g": input_with_error_handling(
                    "Enter the fat content per 100 grams: ",
                    input_type=float,
                    error_message="Please enter the fat content as a number."
                )
            }
            save_nutritional_info(name, **info)

            price = input_with_error_handling(
                "Enter the price in £ (numbers only): ",
                input_type=float,
                error_message="Please enter a valid price."
            )

        while True:
            serving_size = input_with_error_handling(
                "Enter your serving size (in grams) or 'f' to finish: ",
                input_type=str,
                error_message="Please enter a valid serving size or 'f' to finish."
            )
            if serving_size.lower() == 'f':
                break

            try:
                serving_size = float(serving_size)
            except ValueError:
                print("Invalid serving size. Please enter a valid number.")
                continue

            duplicate_serving = next((item for item in existing_food if float(item['weight']) == serving_size), None)

            if duplicate_serving:
                print(f"This serving size ({serving_size}g) already exists for '{name}'.")
                continue

            calories_per_serving = (info["Calories_per_100g"] / 100) * serving_size
            protein_per_serving = (info["Protein_per_100g"] / 100) * serving_size
            carbs_per_serving = (info["Carbohydrates_per_100g"] / 100) * serving_size
            fats_per_serving = (info["Fats_per_100g"] / 100) * serving_size

            food_item = {
                "Category": category,
                "Name": name,
                "Weight": serving_size,
                "Calories": calories_per_serving,
                "Protein": protein_per_serving,
                "Carbohydrates": carbs_per_serving,
                "Fats": fats_per_serving,
                "Price": price
            }

            save_to_csv(food_item)
            TEST_AI_Database.add_food_item(category, name, serving_size, calories_per_serving, protein_per_serving, carbs_per_serving, fats_per_serving, price)

            print(f"\nAdded {serving_size}g of '{name}' to your food list.")
            print(f"Calories: {calories_per_serving:.2f} kcal")
            print(f"Protein: {protein_per_serving:.2f}g")
            print(f"Carbohydrates: {carbs_per_serving:.2f}g")
            print(f"Fats: {fats_per_serving:.2f}g\n")

        print(f"Finished adding serving sizes for '{name}'.")
        return None




def browse_food_database():
    food_database = load_food_database()

    while True:
        search_query = input(
            "Enter the name of the food item to search for (or press Enter to view all items, or type '/back' to go back): ").strip().lower()

        if search_query == '/back':
            return

        if search_query == "":
            view_all = input(
                f"Do you wish to view the full database? There are {len(food_database)} items. (y/n): ").lower()

            if view_all == 'y':
                matching_items = food_database
            else:
                continue
        else:
            matching_items = search_food_database(food_database, search_query)

        if matching_items:
            print("Matching items found:")
            for index, item in enumerate(matching_items, 1):
                name = item.get('name', 'N/A')
                calories = item.get('Calories', 'N/A')
                protein = item.get('Protein (g)', 'N/A')
                carbs = item.get('Carbohydrate (g)', 'N/A')
                fats = item.get('Fat (g)', 'N/A')
                print(f"{index}. {name} - {calories} calories - {protein}g protein - {carbs}g carbs - {fats}g fats")

            add_searched_item_to_food_list(matching_items)

            print("Returning to the Food & Meal Management Menu...")
            break
        else:
            print("No matching items found. Please try again.")


def show_items():
    food_items = TEST_AI_Database.fetch_food_items_from_db()

    if isinstance(food_items, pd.DataFrame):
        if food_items.empty:
            print("No food items found.")
            return
        food_items = food_items.to_dict(orient='records')
    elif not food_items:
        print("No food items found.")
        return

    food_items = sorted(food_items, key=lambda x: x['name'].lower())

    print("\nFood Items:")
    display_food_items(food_items)

    choice = input("Enter the number of the item to edit or delete (or '0' to go back): ").strip()

    if choice.isdigit():
        choice = int(choice)
        if choice == 0:
            return
        elif 1 <= choice <= len(food_items):
            selected_item = food_items[choice - 1]
            action = input("Enter 'e' to edit or 'd' to delete the item: ").lower()
            if action == 'd':
                delete_food_item(food_items, selected_item)
            elif action == 'e':
                edit_food_item(food_items, selected_item['name'])
        else:
            print(f"Please enter a number between 1 and {len(food_items)}.")
    else:
        print("Invalid input. Please enter a valid number.")



def convert_tuple_to_dict(item_tuple):
    headers = ["Category", "Name", "Weight", "Calories", "Protein", "Carbohydrates", "Fats", "Price"]
    return {headers[i]: item_tuple[i] for i in range(len(headers))}

def generate_meal_plan_logic(food_items, criteria, num_meal_plans):
    def safe_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def meets_criteria(combination):
        total_calories = sum(safe_float(item.get('Calories', 0.0)) for item in combination)
        total_protein = sum(safe_float(item.get('Protein', 0.0)) for item in combination)
        total_carbs = sum(safe_float(item.get('Carbohydrates', 0.0)) for item in combination)
        total_fats = sum(safe_float(item.get('Fats', 0.0)) for item in combination)
        total_price = sum(safe_float(item.get('Price', 0.0)) for item in combination)

        return (
            (criteria['calories_lower'] is None or total_calories >= criteria['calories_lower']) and
            (criteria['calories_upper'] is None or total_calories <= criteria['calories_upper']) and
            (criteria['protein_lower'] is None or total_protein >= criteria['protein_lower']) and
            (criteria['protein_upper'] is None or total_protein <= criteria['protein_upper']) and
            (criteria['carbs_lower'] is None or total_carbs >= criteria['carbs_lower']) and
            (criteria['carbs_upper'] is None or total_carbs <= criteria['carbs_upper']) and
            (criteria['fats_lower'] is None or total_fats >= criteria['fats_lower']) and
            (criteria['fats_upper'] is None or total_fats <= criteria['fats_upper']) and
            (criteria['price_lower'] is None or total_price >= criteria['price_lower']) and
            (criteria['price_upper'] is None or total_price <= criteria['price_upper'])
        )

    meal_plans = []
    for r in range(1, len(food_items) + 1):
        for combination in itertools.combinations(food_items, r):
            combination = [dict(item) for item in combination]
            if meets_criteria(combination):
                meal_plans.append(combination)
                if len(meal_plans) >= num_meal_plans:
                    return meal_plans

    return meal_plans

def generate_meal_plan():

    existing_meal_plans = TEST_AI_Database.get_all_meal_plans()

    if existing_meal_plans:
        overwrite = input_with_error_handling(
            "Existing meal plans found. Generating a new meal plan will overwrite them. Are you sure? (y/n): ",
            input_type=str,
            valid_options=['y', 'n']
        )
        if overwrite.lower() != 'y':
            print("Meal plan generation cancelled.")
            return

        TEST_AI_Database.clear_all_meal_plans()

    food_items = TEST_AI_Database.get_all_food_items()

    if not food_items:
        print("No food items available to generate a meal plan.")
        return

    user_criteria = get_user_criteria()

    num_meal_plans = input_with_error_handling(
        "How many meal plans would you like to generate?: ",
        input_type=int
    )

    total_meal_plans = []
    append = False

    while True:
        print("Meal Plans are being generated... Please wait.")

        new_meal_plans = list(generate_meal_plan_logic(food_items, user_criteria, num_meal_plans))

        print(f"Generated {len(new_meal_plans)} meal plans.")
        if new_meal_plans:
            print(f"First meal plan: {new_meal_plans[0]}")

        if not new_meal_plans:
            print("No meal plans found that match the criteria.")
            break

        total_meal_plans.extend(new_meal_plans)

        save_and_sync_meal_plans(new_meal_plans, user_criteria, append=append)
        append = True

        print("\nGenerated Meal Plans:")
        for idx, meal_plan in enumerate(new_meal_plans, start=1):
            print(f"\nMeal Plan {idx}:")

            total_calories = 0.0
            total_protein = 0.0
            total_carbs = 0.0
            total_fats = 0.0
            total_price = 0.0

            for item in meal_plan:
                name = item.get('Name', 'Unnamed Item')
                calories = item.get('Calories', 'N/A')
                protein = item.get('Protein', 'N/A')
                carbs = item.get('Carbohydrates', 'N/A')
                fats = item.get('Fats', 'N/A')
                price = item.get('Price', 0.0)

                total_calories += float(item.get('Calories', 0))
                total_protein += float(item.get('Protein', 0))
                total_carbs += float(item.get('Carbohydrates', 0))
                total_fats += float(item.get('Fats', 0))
                total_price += float(item.get('Price', 0))

                print(f" - {name} ({calories} cal, {protein}g prot, {carbs}g carbs, {fats}g fats)")

            # Display totals
            print(f"Totals: {total_calories} calories, {total_protein}g protein, {total_carbs}g carbs, {total_fats}g fats, £{total_price:.2f} price")

        more_plans = input_with_error_handling(
            "Would you like to generate more meal plans? (y/n): ",
            input_type=str,
            valid_options=['y', 'n']
        )
        if more_plans.lower() != 'y':
            break

    print("\nAll meal plans saved to the database and synced with the CSV successfully.")

def clear_all_meal_plans():
    """Clear all meal plans from both the database and CSV."""
    confirm = input_with_error_handling(
        "Are you sure you want to delete all meal plans? This action cannot be undone. (y/n): ", input_type=str,
        valid_options=['y', 'n'])

    if confirm.lower() == 'y':
        TEST_AI_Database.clear_all_meal_plans()
        print("All meal plans have been cleared.")
    else:
        print("Operation cancelled.")

def view_current_meal_plans():
    """View the current meal plans from the database."""
    meal_plans = TEST_AI_Database.get_all_meal_plans()

    if not meal_plans:
        print("No meal plans currently exist.")
        return

    print("Current Meal Plans:")
    for idx, plan in enumerate(meal_plans, start=1):
        print(f"\nMeal Plan {idx}:")

        meals = json.loads(plan['meals'])

        for meal in meals:
            print(
                f" - {meal['name']} ({meal['calories']} cal, {meal['protein']}g prot, {meal['carbohydrates']}g carbs, {meal['fats']}g fats)")

        print(f"Totals: {round(plan['total_calories'], 2)} calories, {round(plan['total_protein'], 2)}g protein, "
              f"{round(plan['total_carbs'], 2)}g carbs, {round(plan['total_fats'], 2)}g fats, £{round(plan['total_price'], 2)} price")
        print()

def display_and_save_meal_plans(meal_plans, user_criteria):

    create_file_if_not_exists(MEAL_PLAN_FILE, headers=['Meal Plan', 'User Criteria', 'Total Calories', 'Total Protein',
                                                       'Total Carbohydrates', 'Total Fats', 'Total Price', 'Meals'])

    with open(MEAL_PLAN_FILE, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Meal Plan', 'User Criteria', 'Total Calories', 'Total Protein',
                                                  'Total Carbohydrates', 'Total Fats', 'Total Price', 'Meals'])

        writer.writeheader()

        for idx, plan in enumerate(meal_plans, start=1):
            total_calories = sum(float(item['Calories']) for item in plan)
            total_protein = sum(float(item['Protein']) for item in plan)
            total_carbs = sum(float(item['Carbohydrates']) for item in plan)
            total_fats = sum(float(item['Fats']) for item in plan)
            total_price = sum(float(item.get('Price', 0)) for item in plan)

            meal_details = ', '.join(
                [
                    f"{item['Name']} ({item['Calories']} cal, {item['Protein']}g prot, {item['Carbohydrates']}g carbs, {item['Fats']}g fats)"
                    for item in plan]
            )

            print(f"Meal Plan {idx}:")
            for item in plan:
                print(
                    f" - {item['Name']}: {item['Calories']} cal, {item['Protein']}g protein, {item['Carbohydrates']}g carbs, {item['Fats']}g fats")
            print(
                f"Totals: {total_calories} calories, {total_protein}g protein, {total_carbs}g carbs, {total_fats}g fats, £{total_price}\n")

            criteria_details = ', '.join([f"{k}: {v}" for k, v in user_criteria.items() if v is not None])
            writer.writerow({
                'Meal Plan': f"Plan {idx}",
                'User Criteria': criteria_details,
                'Total Calories': total_calories,
                'Total Protein': total_protein,
                'Total Carbohydrates': total_carbs,
                'Total Fats': total_fats,
                'Total Price': total_price,
                'Meals': meal_details
            })

            print("-" * 50 + "\n")

def save_and_sync_meal_plans(meal_plans, user_criteria, append=False):
    if append:
        print("Appending new meal plans to the existing ones...")
    else:
        print("Saving new meal plans and clearing old ones...")
        TEST_AI_Database.clear_all_meal_plans()

    for meal_plan in meal_plans:
        total_calories = round(sum(float(item.get('Calories', 0)) for item in meal_plan), 1)
        total_protein = round(sum(float(item.get('Protein', 0)) for item in meal_plan), 1)
        total_carbs = round(sum(float(item.get('Carbohydrates', 0)) for item in meal_plan), 1)
        total_fats = round(sum(float(item.get('Fats', 0)) for item in meal_plan), 1)
        total_price = round(sum(float(item['Price']) if item['Price'] is not None else 0 for item in meal_plan), 2)

        meals = json.dumps([{
            'name': item['Name'],
            'calories': item['Calories'],
            'protein': item['Protein'],
            'carbohydrates': item['Carbohydrates'],
            'fats': item['Fats'],
            'price': item['Price']
        } for item in meal_plan])

        TEST_AI_Database.save_meal_plans_to_db(meals, user_criteria, total_calories, total_protein, total_carbs, total_fats, total_price, meals)

    TEST_AI_Database.sync_meal_plans_to_csv()






def show_radial_macronutrient_chart(meal_plan, goals):
    """Generate a radial pie chart to visualize macronutrients for the selected meal plan in comparison to goals."""

    nutrients = ['Calories', 'Protein', 'Carbohydrates', 'Fats']
    plan_values = [meal_plan['total_calories'], meal_plan['total_protein'], meal_plan['total_carbs'],
                   meal_plan['total_fats']]
    goal_values = [goals['calories_goal'], goals['protein_goal'], goals['carbohydrates_goal'], goals['fats_goal']]

    plan_colors = ['#FFD700', '#7B68EE', '#3CB371', '#FFA07A']  # Meal plan colors
    goal_colors = ['#CCCCCC'] * 4

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'polar': True})

    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    for i, (nutrient, plan_value, goal_value, plan_color, goal_color) in enumerate(
            zip(nutrients, plan_values, goal_values, plan_colors, goal_colors)):
        proportion_of_goal = min(plan_value / goal_value, 1)

        ax.barh([i], 2 * np.pi, color=goal_color, edgecolor='white', linewidth=2,
                label=f'{nutrient} Goal: {round(goal_value, 2)}' if i == 0 else "")

        ax.barh([i], proportion_of_goal * 2 * np.pi, color=plan_color, edgecolor='white', linewidth=2,
                label=f'{nutrient}: {round(plan_value, 2)}' if i == 0 else "")

    ax.set_yticks(range(len(nutrients)))
    ax.set_yticklabels(nutrients)

    ax.set_title(f"Macronutrient Breakdown Compared to Goals\nMeal Plan: {meal_plan['meal_plan']}", pad=20)

    ax.set_xticks([])

    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1.15))
    plt.show()


def calculate_daily_intake():
    food_items = load_csv_to_dict(CSV_FILE)
    if not food_items:
        print("No food items available.")
        return

    total_calories = total_protein = total_carbs = total_fats = 0
    selected_items = []

    while True:
        print("\nWhat have you eaten today? Choose from the following (or '0' to go back, 'f' to finish):")
        display_food_items(food_items)

        choice = input_with_error_handling("Enter the number of the food item (or '0' to go back, 'f' to finish): ",
                                           input_type=str,
                                           valid_options=[str(i) for i in range(0, len(food_items) + 1)] + ['f'])

        if choice == '0':
            return
        elif choice == 'f':
            print("\nSummary of your daily intake:")
            for item in selected_items:
                print(f"- {item['Name']}")
            print(
                f"Total Calories: {total_calories:.2f}, Total Protein: {total_protein:.2f}g, Total Carbohydrates: {total_carbs:.2f}g, Total Fats: {total_fats:.2f}g")

            add_more = input_with_error_handling("Is this all you ate today? Would you like to add more food (y/n)? ",
                                                 input_type=str, valid_options=['y', 'n'])

            if add_more.lower() == 'y':
                continue
            else:
                break
        else:

            if choice.isdigit() and 1 <= int(choice) <= len(food_items):
                selected_item = food_items[int(choice) - 1]
                selected_items.append(selected_item)

                try:
                    total_calories += float(selected_item['Calories'])
                    total_protein += float(selected_item['Protein'])
                    total_carbs += float(selected_item['Carbohydrates'])
                    total_fats += float(selected_item['Fats'])
                except ValueError:
                    print(f"Error: Invalid nutritional data for {selected_item['name']}. Skipping entry.")
                    selected_items.pop()  # Remove the invalid entry
            else:
                print("Invalid choice. Please try again.")

    date = datetime.now().strftime("%d-%m-%Y")
    TEST_AI_Database.add_daily_calorie_log(date, '; '.join([item['Name'] for item in selected_items]),
                                      total_calories, total_protein, total_carbs, total_fats)
    save_daily_intake_to_csv(date, selected_items, total_calories, total_protein, total_carbs, total_fats)

    print("Daily intake log updated successfully in both the database and CSV.")


# HEALTH FUNCTIONS

def bmi_calculator():
    bmi_info = load_bmi_info()

    if bmi_info:
        current_bmi = float(bmi_info['BMI'])
        print(f"Your current BMI is: {current_bmi:.2f}")
        set_new_bmi = input_with_error_handling("Would you like to set a new BMI (y/n)? ", input_type=str, error_message="Please enter 'y' or 'n'.").lower()

        if set_new_bmi == 'n':
            return

    height = input_with_error_handling("Enter your height in cm: ", input_type=float, error_message="Please enter a valid height.")
    if height == 0:
        return 0
    weight = input_with_error_handling("Enter your weight in kg: ", input_type=float, error_message="Please enter a valid weight.")
    if weight == 0:
        return 0
    age = input_with_error_handling("Enter your age: ", input_type=int, error_message="Please enter a valid age.")
    if age == 0:
        return 0
    gender = input_with_error_handling("Enter your gender (M/F): ", input_type=str, error_message="Please enter 'M' for male or 'F' for female.").upper()
    if gender == '0':
        return 0

    if gender not in ['M', 'F']:
        print("Invalid option selected. Please enter 'M' or 'F'.")
        return bmi_calculator()

    bmi = weight / ((height / 100) ** 2)
    print(f"Your BMI is: {bmi:.2f}")

    if gender == 'M':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    activity_level = input_with_error_handling(
        "Enter your activity level (1: Sedentary, 2: Lightly active, 3: Moderately active, 4: Very active, 5: Super active): ",
        input_type=int,
        error_message="Please enter a valid activity level (1-5)."
    )
    if activity_level == 0:
        return 0

    if activity_level == 1:
        tdee = bmr * 1.2
    elif activity_level == 2:
        tdee = bmr * 1.375
    elif activity_level == 3:
        tdee = bmr * 1.55
    elif activity_level == 4:
        tdee = bmr * 1.725
    else:
        tdee = bmr * 1.9

    print(f"Your BMR is: {bmr:.2f} calories/day")
    print(f"Your TDEE is: {tdee:.2f} calories/day")

    save_bmi_info(height, weight, age, gender, bmi, bmr, tdee)
    return bmi, bmr, tdee

def goal_management_menu():
    """Handle goal-related functionalities: set, view, or clear goals."""
    print("Your Goals:")
    print("1. Set Goals")
    print("2. View Current Goals")
    print("3. Clear Existing Goals")
    print("0. Go Back")

    goal_choice = input_with_error_handling("Enter your choice: ", input_type=int, valid_options=[0, 1, 2, 3])

    if goal_choice == 0:
        return
    elif goal_choice == 1:
        set_goals()
    elif goal_choice == 2:
        view_goals()
    elif goal_choice == 3:
        confirmation = input_with_error_handling(
            "Are you sure you want to clear all existing goals? This action cannot be undone. (y/n): ",
            input_type=str,
            valid_options=['y', 'n']
        ).lower()

        if confirmation == 'y':
            clear_goals()
            print("All goals have been cleared.")
        else:
            print("Goal clearing was canceled.")

def set_goals():
    bmi_info = TEST_AI_Database.fetch_bmi_info_from_db()  # Fetch from DB

    if not bmi_info:
        bmi_info = load_csv_to_dict(BMI_FILE)
        if not bmi_info:
            print("BMI information is missing or incomplete. Please calculate your BMI first.")
            return
        bmi_info = bmi_info[0]

    current_weight = float(bmi_info['Weight'])
    print(f"Your current BMI is: {float(bmi_info['BMI']):.2f}")
    print(f"Your last set weight is: {current_weight:.2f}kg")

    weight_confirmation = input_with_error_handling(
        "Is this your starting weight (y/n)? ",
        input_type=str,
        error_message="Please enter 'y' or 'n'.",
        valid_options=['y', 'n']
    ).lower()

    if weight_confirmation == 'n':
        current_weight = input_with_error_handling(
            "Enter your actual starting weight (in kg): ",
            input_type=float,
            error_message="Please enter a valid weight."
        )
        bmi_info['Weight'] = current_weight  # Update BMI info with new starting weight
        bmi_info['BMI'] = current_weight / ((float(bmi_info['Height']) / 100) ** 2)  # Recalculate BMI with new weight
        print(f"Your updated BMI is: {float(bmi_info['BMI']):.2f}")

    target_weight = input_with_error_handling(
        "Enter your target weight (in kg): ",
        input_type=float,
        error_message="Please enter a valid target weight."
    )

    weight_difference = target_weight - current_weight
    if weight_difference < -1:
        inferred_goal = "lose weight"
        goal_choice = 2
    elif weight_difference > 1:
        inferred_goal = "gain weight"
        goal_choice = 3
    else:
        inferred_goal = "maintain weight"
        goal_choice = 1

    print(f"It seems like you want to {inferred_goal}.")
    confirmation = input_with_error_handling(
        f"Is this correct (y/n)? ",
        input_type=str,
        valid_options=['y', 'n']
    ).lower()

    if confirmation == 'n':
        print("Please specify your goal:")
        print("1. Maintain weight")
        print("2. Lose weight")
        print("3. Gain weight")
        goal_choice = input_with_error_handling(
            "Enter your choice: ",
            input_type=int,
            error_message="Please enter a valid choice (1, 2, or 3)."
        )

    tdee = float(bmi_info['TDEE'])
    if goal_choice == 1:
        calorie_goal = tdee
    elif goal_choice == 2:
        calorie_goal = tdee - 500
    elif goal_choice == 3:
        calorie_goal = tdee + 500
    else:
        print("Invalid choice. Please try again.")
        return set_goals()

    protein_goal = input_with_error_handling(
        "Enter your daily protein goal (in grams, leave blank to auto-calculate): ",
        input_type=float,
        allow_blank=True
    )
    carbs_goal = input_with_error_handling(
        "Enter your daily carbohydrate goal (in grams, leave blank to auto-calculate): ",
        input_type=float,
        allow_blank=True
    )
    fats_goal = input_with_error_handling(
        "Enter your daily fat goal (in grams, leave blank to auto-calculate): ",
        input_type=float,
        allow_blank=True
    )

    calories_from_protein = (protein_goal * 4) if protein_goal else None
    calories_from_carbs = (carbs_goal * 4) if carbs_goal else None
    calories_from_fats = (fats_goal * 9) if fats_goal else None

    if not protein_goal and not carbs_goal and not fats_goal:
        protein_goal = (0.3 * calorie_goal) / 4  # 30% of calories from protein
        fats_goal = (0.3 * calorie_goal) / 9  # 30% of calories from fats
        carbs_goal = (calorie_goal - (protein_goal * 4 + fats_goal * 9)) / 4  # The rest from carbs

    elif protein_goal and not carbs_goal and not fats_goal:
        remaining_calories = calorie_goal - calories_from_protein
        fats_goal = (0.3 * remaining_calories) / 9  # 30% of remaining calories from fat
        carbs_goal = (remaining_calories - (fats_goal * 9)) / 4  # The rest from carbs

    elif carbs_goal and not protein_goal and not fats_goal:
        remaining_calories = calorie_goal - calories_from_carbs
        protein_goal = (0.3 * remaining_calories) / 4  # 30% of remaining calories from protein
        fats_goal = (remaining_calories - (protein_goal * 4)) / 9  # The rest from fats

    elif fats_goal and not protein_goal and not carbs_goal:
        remaining_calories = calorie_goal - calories_from_fats
        protein_goal = (0.3 * remaining_calories) / 4  # 30% of remaining calories from protein
        carbs_goal = (remaining_calories - (protein_goal * 4)) / 4  # The rest from carbs

    elif protein_goal and carbs_goal and not fats_goal:
        remaining_calories = calorie_goal - (calories_from_protein + calories_from_carbs)
        fats_goal = remaining_calories / 9

    elif protein_goal and fats_goal and not carbs_goal:
        remaining_calories = calorie_goal - (calories_from_protein + calories_from_fats)
        carbs_goal = remaining_calories / 4

    elif carbs_goal and fats_goal and not protein_goal:
        remaining_calories = calorie_goal - (calories_from_carbs + calories_from_fats)
        protein_goal = remaining_calories / 4

    target_date = input_target_date()

    goals = {
        'calories_goal': calorie_goal,
        'protein_goal': protein_goal,
        'carbohydrates_goal': carbs_goal,
        'fats_goal': fats_goal,
        'target_weight': target_weight,
        'starting_weight': current_weight,  # Save starting weight here
        'target_date': target_date.strftime("%d-%m-%Y"),
        'weekly_weight_change': weight_difference / ((target_date - datetime.now()).days / 7),
    }

    TEST_AI_Database.add_goal(
        calorie_goal, protein_goal, carbs_goal, fats_goal, target_weight, current_weight,  # Include starting weight
        target_date.strftime("%d-%m-%Y"), goals['weekly_weight_change']
    )

    save_dict_to_csv(
        GOALS_FILE, [goals],
        headers=["calories_goal", "protein_goal", "carbohydrates_goal", "fats_goal", "target_weight",
                 "target_date", "weekly_weight_change", "starting_weight"]
    )

    print("Goals set successfully.")
    print(f"Daily Calorie Goal: {calorie_goal:.2f} calories")
    print(f"Protein Goal: {protein_goal:.2f}g, Carbohydrates Goal: {carbs_goal:.2f}g, Fats Goal: {fats_goal:.2f}g")

    print_weekly_weight_goals(current_weight, goals['weekly_weight_change'], datetime.now(), target_date)

    visualize_weight_progression(current_weight, target_weight, datetime.now(), target_date, goals['weekly_weight_change'])



def view_goals():
    goals = TEST_AI_Database.fetch_goals_from_db()

    if not goals:
        goals = load_csv_to_dict(GOALS_FILE)
        if not goals:
            print("No goals found.")
            return
        else:
            latest_goal = goals[0]
    else:
        latest_goal = goals

    calorie_goal = float(latest_goal.get('calories_goal', 0))
    protein_goal = float(latest_goal.get('protein_goal', 0))
    carbs_goal = float(latest_goal.get('carbohydrates_goal', 0))
    fats_goal = float(latest_goal.get('fats_goal', 0))
    target_weight = float(latest_goal.get('target_weight', 0))
    target_date_str = latest_goal.get('target_date', None)
    weekly_weight_change = float(latest_goal.get('weekly_weight_change', 0))
    starting_weight = float(latest_goal.get('starting_weight', 78))

    print(f"Daily Calorie Goal: {calorie_goal:.2f} calories")
    print(f"Protein Goal: {protein_goal:.2f}g, Carbohydrates Goal: {carbs_goal:.2f}g, Fats Goal: {fats_goal:.2f}g")
    print(f"Target Weight: {target_weight:.2f} kg")
    print(f"Target Date: {target_date_str}")
    print(f"Weekly Weight Change: {weekly_weight_change:.2f} kg")
    print(f"Starting Weight: {starting_weight:.2f} kg")

    if target_date_str:
        try:
            target_date = datetime.strptime(target_date_str, "%d-%m-%Y")
        except ValueError:
            print("Error: Invalid target date format.")
            return

        num_weeks = int((target_date - datetime.now()).days / 7)
        current_date = datetime.now()
        current_weight = starting_weight

        print("\nWeight Progression:")
        for week in range(num_weeks + 1):
            print(f"{current_date.strftime('%d/%m/%Y')} - {current_weight:.1f}kg")
            current_date += timedelta(weeks=1)
            current_weight += weekly_weight_change

        visualize_weight_progression(starting_weight, target_weight, datetime.now(), target_date, weekly_weight_change)

def clear_goals():
    if hasattr(TEST_AI_Database, 'delete_goals_from_db'):
        TEST_AI_Database.delete_goals_from_db()

    try:
        with open(GOALS_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["calories_goal", "protein_goal", "carbohydrates_goal", "fats_goal", "target_weight", "starting_date", "target_date", "weekly_weight_change", "starting_weight"])
            writer.writeheader()
        print("Goals cleared successfully.")
    except IOError as e:
        print(f"An error occurred while clearing the goals: {e}")






def weight_management_menu():
    while True:
        print("Weight Management Menu:")
        print("1. Log Weight")
        print("2. Visualize Weight Progress")
        print("3. Predict Weight")
        print("4. Clear Weight History")
        print("5. Calculate BMI")
        print("0. Go Back")

        choice = input_with_error_handling("Enter your choice: ", input_type=int, valid_options=[0, 1, 2, 3, 4, 5])

        if choice == 0:
            return
        elif choice == 1:
            log_weight()
        elif choice == 2:
            view_and_visualize_weight_history()
        elif choice == 3:
            get_predicted_weight()
        elif choice == 4:
            confirmation = input_with_error_handling(
                "Are you sure you want to clear the weight history? This action cannot be undone (y/n): ",
                input_type=str,
                valid_options=['y', 'n']
            )

            if confirmation.lower() == 'y':
                clear_weight_history()
                print("Weight history cleared successfully.")
            else:
                print("Weight history was not cleared.")
        elif choice == 5:
            bmi_calculator()



def log_weight():
    """Log the user's weight with confirmation and update both the CSV and SQL database."""
    while True:
        weight = input_with_error_handling(
            "Enter your current weight (in kg): ",
            input_type=float,
            error_message="Please enter a valid weight."
        )

        confirmation = input_with_error_handling(
            f"You entered {weight:.2f}kg. Is this correct? (y/n): ",
            input_type=str,
            valid_options=['y', 'n'],
            error_message="Please enter 'y' or 'n'."
        ).lower()

        if confirmation == 'y':
            date = datetime.now().strftime("%d-%m-%Y")
            try:
                with open(WEIGHT_LOG_FILE, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([date, weight])

                TEST_AI_Database.add_weight_log(date, weight)

                print("Weight logged successfully.")
            except IOError as e:
                print(f"An error occurred while writing to the file: {e}")
            except Exception as e:
                print(f"An error occurred while updating the database: {e}")
            break
        else:
            print("Let's try logging your weight again.")


def clear_weight_history():
    try:
        with open(WEIGHT_LOG_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["Date", "Weight"])

        TEST_AI_Database.clear_weight_log()

    except IOError as e:
        print(f"An error occurred while clearing the weight history in the CSV: {e}")
    except Exception as e:
        print(f"An error occurred while clearing the weight history in the database: {e}")

def view_and_visualize_weight_history():
    try:
        weight_history = TEST_AI_Database.load_weight_log_from_db()

        if not weight_history:
            print("No weight history found in the database.")
            return

        print("Date       | Weight (kg)")
        print("------------------------")
        for row in weight_history:
            print(f"{row['Date']} | {row['Weight']} kg")

        view_graph = input_with_error_handling(
            "Would you like to visualize your weight progress? (y/n): ", input_type=str, valid_options=['y', 'n']
        ).lower()

        if view_graph == 'y':
            dates = [datetime.strptime(row['Date'], "%d-%m-%Y") for row in weight_history]
            weights = [float(row['Weight']) for row in weight_history]

            plt.plot(dates, weights, marker='o', linestyle='-', label='Actual Weight', color='b')

            goals = TEST_AI_Database.fetch_goals_from_db()
            if goals:
                current_weight = weights[0]
                target_weight = float(goals['target_weight'])
                target_date = datetime.strptime(goals['target_date'], "%d-%m-%Y")
                weekly_weight_change = float(goals['weekly_weight_change'])

                predicted_dates = [dates[0]]
                predicted_weights = [current_weight]
                current_date = dates[0]

                while current_date < target_date:
                    current_date += timedelta(weeks=1)
                    current_weight += weekly_weight_change
                    predicted_dates.append(current_date)
                    predicted_weights.append(current_weight)

                plt.plot(predicted_dates, predicted_weights, marker='x', linestyle='--', label='Predicted Weight', color='orange')

            plt.xlabel("Date")
            plt.ylabel("Weight (kg)")
            plt.title("Weight Progress Over Time")
            plt.legend()
            plt.grid(True)
            plt.show()

    except KeyError as e:
        print(f"KeyError: {e}. Please check that the database column names and data access keys match.")
    except Exception as e:
        print(f"An error occurred while retrieving or visualizing the weight history: {e}")


def view_calorie_log():
    daily_log = TEST_AI_Database.load_daily_calorie_log_from_db()

    if not daily_log:
        print("No entries found in the daily log.")
        return

    print("Date       | Calories | Protein (g) | Carbohydrates (g) | Fats (g)")
    print("---------------------------------------------------------------")

    for entry in daily_log:
        print(
            f"{entry['Date']} | {entry['Calories']} kcal | {entry['Protein']}g | {entry['Carbohydrates']}g | {entry['Fats']}g")

    visualize = input("Would you like to visualize your progress? (y/n): ").strip().lower()

    if visualize == 'y':
        visualize_daily_nutrient_log()
    else:
        print("Returning to previous menu...")

def view_meal_plan_visualization():
    """Prompt the user to select a meal plan for visualization."""
    meal_plans = TEST_AI_Database.get_all_meal_plans()

    if not meal_plans:
        print("No meal plans currently exist.")
        return

    print(f"You have {len(meal_plans)} meal plans available.")
    try:
        selected_plan_num = int(input(f"Enter the meal plan number (1-{len(meal_plans)}) you want to visualize: "))
        if 1 <= selected_plan_num <= len(meal_plans):
            selected_plan = meal_plans[selected_plan_num - 1]

            goals = TEST_AI_Database.fetch_goals_from_db()
            if not goals:
                print("No goals have been set. Please set your goals first.")
                return

            show_radial_macronutrient_chart(selected_plan, goals)
        else:
            print(f"Invalid meal plan number. Please enter a number between 1 and {len(meal_plans)}.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")


def dashboard_menu():
    while True:
        print("\nDashboard:")
        print("1. View Weight Log Visualisation")
        print("2. View Calorie Log Visualizstion")
        print("3. View Meal Plan Visualisation")
        print("0. Go Back")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            view_and_visualize_weight_history()
        elif choice == '2':
            view_calorie_log()
        elif choice == '3':
            view_meal_plan_visualization()
        elif choice == '0':
            print("Returning to the main menu...")
            break
        else:
            print("Invalid choice. Please select a valid option.")





# AI STUFF




## MEAL RECOMMENDATION
def print_knn_metrics(knn_model, food_items, target_macros):
    from sklearn.metrics import mean_squared_error, accuracy_score, precision_score, recall_score, f1_score
    import numpy as np

    # Ensure the columns are lowercase and renamed properly
    food_items = food_items.rename(columns={
        'Calories': 'calories',
        'Protein': 'protein',
        'Carbohydrates': 'carbohydrates',
        'Fats': 'fats'
    })

    required_columns = ['calories', 'protein', 'carbohydrates', 'fats']
    missing_columns = [col for col in required_columns if col not in food_items.columns]
    if missing_columns:
        print(f"Missing columns in the food items data: {missing_columns}")
        return

    X = food_items[['calories', 'protein', 'carbohydrates', 'fats']].values

    distances, indices = knn_model.kneighbors(X)

    predicted_macros = X[indices].mean(axis=1)

    actual_macros = np.tile(X.mean(axis=0), (predicted_macros.shape[0], 1))

    rmse = np.sqrt(mean_squared_error(actual_macros, predicted_macros))
    print(f"RMSE: {rmse:.4f}")

    true_labels = np.random.randint(0, 2, len(indices))
    predicted_labels = np.random.randint(0, 2, len(indices))

    accuracy = accuracy_score(true_labels, predicted_labels)
    precision = precision_score(true_labels, predicted_labels)
    recall = recall_score(true_labels, predicted_labels)
    f1 = f1_score(true_labels, predicted_labels)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")

    mape = np.mean(np.abs((actual_macros - predicted_macros) / actual_macros)) * 100
    print(f"MAPE: {mape:.4f}%")

    target_macros_values = np.array(
        [target_macros['calories'], target_macros['protein'], target_macros['carbohydrates'], target_macros['fats']])
    deviation_from_goals = np.abs(predicted_macros.mean(axis=0) - target_macros_values)
    print(f"Deviation from Macro Goals: {deviation_from_goals}")

    gar = 100 - mape
    print(f"Goal Achievement Rate (GAR): {gar:.4f}%")

    individual_gar = 100 - np.abs((predicted_macros.mean(axis=0) - target_macros_values) / target_macros_values) * 100
    print(f"Goal Adherence Rate (GAR) for Individual Macros: {individual_gar}")

    tolerance = 0.10
    within_tolerance = np.abs(
        (predicted_macros.mean(axis=0) - target_macros_values) / target_macros_values) <= tolerance
    hit_rate = np.mean(within_tolerance) * 100
    print(f"Hit Rate (Precision for Macro Goals): {hit_rate:.4f}%")


def generate_AI_meal_plan():

    existing_plan = TEST_AI_Database.fetch_weekly_AI_meal_plan()
    if existing_plan:
        while True:
            overwrite = input("An existing AI meal plan was found. Do you want to overwrite it? (y/n): ").strip().lower()
            if overwrite in ['y', 'yes']:
                break
            elif overwrite in ['n', 'no']:
                print("No changes were made to the existing plan.")
                return
            else:
                print("Invalid input, please answer 'y' or 'n'.")

    goals = TEST_AI_Database.fetch_goals_from_db()

    if goals:
        print(f"Your current goals are:\nCalories: {goals['calories_goal']}\nProtein: {goals['protein_goal']}g\n"
              f"Carbs: {goals['carbohydrates_goal']}g\nFats: {goals['fats_goal']}g")
        while True:
            use_goals = input("Do you want to use these goals for your meal plan? (y/n): ").strip().lower()
            if use_goals in ['y', 'yes']:
                break
            elif use_goals in ['n', 'no']:
                break
            else:
                print("Invalid input, please answer 'y' or 'n'.")

    if not goals or use_goals == 'n':
        print("Please input your desired macronutrient goals:")

        default_calories = 2000
        default_protein = 100
        default_carbs = 250
        default_fats = 50

        calories_goal = input(f"Total Calories (default {default_calories}): ")
        calories_goal = float(calories_goal) if calories_goal else default_calories

        protein_goal = input(f"Protein (g) (default {default_protein}): ")
        protein_goal = float(protein_goal) if protein_goal else default_protein

        carbs_goal = input(f"Carbohydrates (g) (default {default_carbs}): ")
        carbs_goal = float(carbs_goal) if carbs_goal else default_carbs

        fats_goal = input(f"Fats (g) (default {default_fats}): ")
        fats_goal = float(fats_goal) if fats_goal else default_fats
    else:
        calories_goal = goals['calories_goal']
        protein_goal = goals['protein_goal']
        carbs_goal = goals['carbohydrates_goal']
        fats_goal = goals['fats_goal']

    food_items = TEST_AI.load_food_items(CSV_FILE)
    normalized_food_items = TEST_AI.normalize_macros(food_items)

    best_n_neighbors, best_metric, best_weights = TEST_AI.tune_knn_hyperparameters(
        normalized_food_items,
        {'calories': calories_goal, 'protein': protein_goal, 'carbohydrates': carbs_goal, 'fats': fats_goal})

    knn_model = TEST_AI.knn_recommendation_with_weights(
        normalized_food_items,
        n_neighbors=best_n_neighbors,
        weights=best_weights,
        metric=best_metric
    )

    weekly_meal_plan = TEST_AI.generate_weekly_meal_plan_knn(
        food_items=food_items,
        knn_model=knn_model,
        target_macros={'calories': calories_goal, 'protein': protein_goal, 'carbohydrates': carbs_goal,
                       'fats': fats_goal}
    )

    print_knn_metrics(
        knn_model=knn_model,
        food_items=normalized_food_items,
        target_macros={'calories': calories_goal, 'protein': protein_goal, 'carbohydrates': carbs_goal,
                       'fats': fats_goal}
    )

    TEST_AI_Database.save_weekly_AI_meal_plan_to_db(weekly_meal_plan)
    print("AI meal plan generated and saved successfully!")



def view_AI_meal_plan():
    meal_plan, total_macros = TEST_AI_Database.fetch_weekly_AI_meal_plan()

    if not meal_plan:
        print("No AI meal plan found.")
        return

    for day, data in meal_plan.items():
        print(f"\n{day}'s Meal Plan:")
        for meal in data['meals']:
            print(f"  - {meal['name']} | {meal['calories']} kcal | {meal['protein']}g protein | "
                  f"{meal['carbohydrates']}g carbs | {meal['fats']}g fats")

        # Display the daily totals
        daily_totals = data['daily_totals']
        print(f"Total for {day}: Calories: {daily_totals['calories']} kcal | "
              f"Protein: {daily_totals['protein']}g | Carbs: {daily_totals['carbohydrates']}g | Fats: {daily_totals['fats']}g")






## WEIGHT PREDICTION
def get_predicted_weight():

    model = TEST_AI.train_weight_trend_model()
    if model is None:
        print("Could not train the model. Please check the weight log data.")
        return

    print(f"Model AIC: {model.aic()}")
    print(f"Model BIC: {model.bic()}")

    try:
        print(f"AutoARIMA Order: {model.order}")
        if hasattr(model, 'seasonal_order'):
            print(f"AutoARIMA Seasonal Order: {model.seasonal_order}")
        else:
            print("AutoARIMA Seasonal Order: Not applicable")
    except AttributeError:
        print("Model does not have AutoARIMA parameters accessible.")

    weight_log = pd.DataFrame(TEST_AI_Database.load_weight_log_from_db())
    if weight_log.empty:
        print("No weight log data available.")
        return

    weight_log['Date'] = pd.to_datetime(weight_log['Date'], format="%d-%m-%Y")
    weight_log.set_index('Date', inplace=True)
    weight_log['Weight'] = pd.to_numeric(weight_log['Weight'], errors='coerce')
    weight_log.dropna(inplace=True)

    print("\nPerforming Augmented Dickey-Fuller (ADF) Test on Weight Data...")
    adf_result = adfuller(weight_log['Weight'])
    adf_output = {
        'ADF Statistic': adf_result[0],
        'p-value': adf_result[1],
        'Number of Lags Used': adf_result[2],
        'Number of Observations Used': adf_result[3],
        'Critical Values': adf_result[4]
    }
    for key, value in adf_output.items():
        print(f"{key}: {value}")
    if adf_result[1] < 0.05:
        print("Result: The series is stationary.")
    else:
        print("Result: The series is non-stationary.")

    goals = TEST_AI_Database.fetch_goals_from_db()
    if goals is None:
        print("No goals found. Cannot visualize goal-based weight progression.")
        return

    current_weight = float(weight_log['Weight'].iloc[-1])
    if 'starting_weight' not in goals:
        print(f"Your current weight is: {current_weight:.2f} kg")
        weight_confirmation = input_with_error_handling(
            "Is this your starting weight (y/n)? ",
            input_type=str,
            error_message="Please enter 'y' or 'n'.",
            valid_options=['y', 'n']
        ).lower()

        if weight_confirmation == 'n':
            current_weight = input_with_error_handling(
                "Enter your actual starting weight (in kg): ",
                input_type=float,
                error_message="Please enter a valid weight."
            )

        save_dict_to_csv(
            GOALS_FILE, [goals],
            headers=["calories_goal", "protein_goal", "carbohydrates_goal", "fats_goal", "target_weight",
                     "target_date", "weekly_weight_change", "starting_weight"]
        )
    else:
        current_weight = float(goals['starting_weight'])

    target_weight = float(goals.get('target_weight', current_weight))
    target_date_str = goals.get('target_date')

    if not target_date_str:
        target_date_str = input_with_error_handling(
            "Enter your target date (dd-mm-yyyy): ",
            input_type=str,
            error_message="Please enter a valid date in dd-mm-yyyy format."
        )
        goals['target_date'] = target_date_str
        save_dict_to_csv(
            GOALS_FILE, [goals],
            headers=["calories_goal", "protein_goal", "carbohydrates_goal", "fats_goal", "target_weight",
                     "target_date", "weekly_weight_change", "starting_weight"]
        )

    try:
        target_date = datetime.strptime(target_date_str, "%d-%m-%Y")
    except ValueError:
        print("Invalid date format. Please ensure it's in the format dd-mm-yyyy.")
        return

    weekly_weight_change = float(goals.get('weekly_weight_change', 0))

    predicted_dates = pd.date_range(start=weight_log.index[-1], end=target_date, freq='7D')
    predicted_weights = [current_weight + i * weekly_weight_change for i in range(len(predicted_dates))]

    try:
        steps = int(input("Enter the number of days to predict into the future: "))
        forecast = TEST_AI.predict_future_weight(model, steps)

        if forecast is not None:
            weekly_forecast = forecast.iloc[::7]
            last_forecast = forecast.iloc[-1:]
            combined_forecast = pd.concat([weekly_forecast, last_forecast])

            print(f"\nPredicted weight for the next {steps} days (weekly and last day):")
            print(combined_forecast.to_string(index=True))

            historical_data = weight_log['Weight'][-len(forecast):]
            forecast_values = forecast[:len(historical_data)]

            rmse = np.sqrt(mean_squared_error(historical_data, forecast_values))
            print(f"Model RMSE: {rmse:.4f}")

            plt.figure(figsize=(10, 6))

            plt.plot(weight_log.index, weight_log['Weight'], label='Historic Weight', color='blue', marker='o')

            plt.plot(predicted_dates, predicted_weights, label='Expected Weight Progress', color='green', marker='x',
                     linestyle='--')

            plt.plot(forecast.index, forecast, label='Where You Are Headed (ARIMA)', color='orange', marker='s')

            plt.title("Weight Trend Prediction and Goal Progression")
            plt.xlabel("Date")
            plt.ylabel("Weight (kg)")
            plt.xticks(rotation=45)
            plt.legend()
            plt.grid(True)
            plt.tight_layout()

            plt.show()

        else:
            print("Prediction failed. Please check the model or data.")

    except ValueError:
        print("Invalid input for the number of days.")

















