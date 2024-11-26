import TEST_Functions
import TEST_AI_Database
import TEST_AI
from TEST_AI_Database import initialize_database
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    print("Initializing database...")
    TEST_AI_Database.initialize_database()

    '''print("Checking if the database needs to be populated from CSV files...")'''
    TEST_Functions.populate_database_if_empty()

    print("Importing Preprocessed Food Database...")
    TEST_AI_Database.import_preprocessed_food_database()

    daily_calorie_log_path = '/TESTCODE/TESTCSV/TEST_daily_calorie_log.csv'
    food_data_path = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_food_items.csv')

    DAILY_CALORIE_LOG_FILE = '/TESTCODE/TESTCSV/TEST_daily_calorie_log.csv'
    FOOD_ITEMS_FILE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_food_items.csv')
    GOALS_FILE = '/TESTCODE/TESTCSV/TEST_goals.csv'
    food_items = pd.read_csv(FOOD_ITEMS_FILE)

    categories = TEST_Functions.load_categories()

    while True:
        print("\nMain Menu:")
        print("1. Food & Meal Management")
        print("2. Weight Management")
        print("3. Goal Management")
        print("4. Dashboard")
        print("E. Exit")

        choice = input("Enter your choice: ").strip().lower()

        if choice == '1':
            TEST_Functions.food_and_meal_management_menu(categories)
        elif choice == '2':
            TEST_Functions.weight_management_menu()
        elif choice == '3':
            TEST_Functions.goal_management_menu()
        elif choice == '4':
            TEST_Functions.dashboard_menu()
        elif choice == 'e':
            print("Thank you for using the app :)")
            TEST_AI_Database.sync_all()
            break
        else:
            print("Invalid choice. Please select a valid option.")


if __name__ == '__main__':
    main()
