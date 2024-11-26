import pandas as pd
import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
import TEST_Functions
import TEST_AI_Database
import os
import TEST_AI
import sqlite3
from TEST_Functions import add_food_item, load_categories

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(BASE_DIR, 'DATABASE_TEST.db')
CSV_FILE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_food_items.csv')
GOALS_FILE = os.path.join(BASE_DIR, 'TESTCSV', 'TEST_goals.csv')
app = Flask(__name__)
app.secret_key = os.urandom(24)

def initialize_app():
    print("Initializing database...")
    TEST_AI_Database.initialize_database()

    print("Checking if the database needs to be populated from CSV files...")
    TEST_Functions.populate_database_if_empty()

    print("Importing Preprocessed Food Database...")
    TEST_AI_Database.import_preprocessed_food_database()

    print("App initialization completed successfully.")



# Main route (Welcome Page)
@app.route('/', methods=['GET'])
def welcome():
    return render_template('welcome_page.html')
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    weight_history = TEST_AI_Database.load_weight_log_from_db()
    daily_log = TEST_AI_Database.load_daily_calorie_log_from_db()
    meal_plans = TEST_AI_Database.get_all_meal_plans()
    user_goals = TEST_AI_Database.fetch_goals_from_db()


    print(f"DEBUG: Daily log fetched: {daily_log}")
    print(f"DEBUG: Meal plans fetched: {meal_plans}")

    return render_template(
        'dashboard_menu.html',
        weight_history=weight_history,
        daily_log=daily_log,
        meal_plans=meal_plans,
        user_goals=user_goals
    )



### FOOD AND MEAL MANAGEMENT
@app.route('/food')
def food_menu():
    return render_template('food_menu.html')


#ADD FOOD ITEM
@app.route('/add_food', methods=['GET', 'POST'])
def add_food():
    categories = load_categories()

    if request.method == 'POST':
        category = request.form.get('category')
        name = request.form.get('name').lower()

        existing_food_items = TEST_AI_Database.fetch_food_items_from_db()

        if not existing_food_items.empty:
            existing_food = existing_food_items[existing_food_items['name'].str.lower() == name]
            if not existing_food.empty:
                return redirect(url_for('add_serving', name=name, category=category))

        return redirect(url_for('enter_macros', name=name, category=category))

    return render_template('add_food.html', categories=categories)


@app.route('/enter_macros', methods=['GET', 'POST'])
def enter_macros():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        calories_per_100g = float(request.form['calories_per_100g'])
        protein_per_100g = float(request.form['protein_per_100g'])
        carbs_per_100g = float(request.form['carbs_per_100g'])
        fats_per_100g = float(request.form['fats_per_100g'])

        TEST_AI_Database.add_nutritional_info(name, calories_per_100g, protein_per_100g, carbs_per_100g, fats_per_100g)

        TEST_AI_Database.sync_food_items()

        return redirect(url_for('add_serving', name=name, category=category))

    name = request.args.get('name')
    category = request.args.get('category')
    return render_template('enter_macros.html', name=name, category=category)




## PREPROCESSED DATABASE (BROWSE FOOD DATABASE)
@app.route('/browse_food', methods=['GET', 'POST'])
def browse_food():
    if request.method == 'POST':
        if 'view_all' in request.form:
            food_database = TEST_Functions.load_food_database()
            for item in food_database:
                item['calories'] = item.get('Calories', 'N/A')
                item['protein'] = item.get('Protein (g)', 'N/A')
                item['carbohydrates'] = item.get('Carbohydrate (g)', 'N/A')
                item['fats'] = item.get('Fat (g)', 'N/A')
            return render_template('browse_food.html', food_items=food_database, display_table=True)

        elif 'food_search' in request.form:
            search_term = request.form['food_search'].lower()
            matching_items = TEST_AI_Database.search_preprocessed_food_items(search_term)
            if matching_items:
                return render_template('browse_food.html', food_items=matching_items, display_table=True)
            else:
                return render_template('browse_food.html', error="No matching items found. Try again.")

    return render_template('browse_food.html')

@app.route('/add_food_item_from_database', methods=['POST'])
def add_food_item_from_database():
    food_name = request.form.get('food_name')
    calories_per_100g = float(request.form.get('calories'))
    protein_per_100g = float(request.form.get('protein'))
    carbs_per_100g = float(request.form.get('carbs'))
    fats_per_100g = float(request.form.get('fats'))

    if request.method == 'POST':
        serving_size = float(request.form.get('serving_size'))

        calories_per_serving = (calories_per_100g / 100) * serving_size
        protein_per_serving = (protein_per_100g / 100) * serving_size
        carbs_per_serving = (carbs_per_100g / 100) * serving_size
        fats_per_serving = (fats_per_100g / 100) * serving_size

        category = "Database item"

        TEST_AI_Database.add_food_item(category, food_name, serving_size,
                                       calories_per_serving, protein_per_serving,
                                       carbs_per_serving, fats_per_serving, price=0)

        TEST_AI_Database.sync_food_items()

        return render_template('confirm_addition.html',
                               name=food_name, serving_size=serving_size,
                               calories=calories_per_serving, protein=protein_per_serving,
                               carbs=carbs_per_serving, fats=fats_per_serving)

    return render_template('add_serving.html')


@app.route('/add_serving', methods=['GET', 'POST'])
def add_serving():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        serving_size = float(request.form.get('serving_size'))

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT calories, protein, carbohydrates, fats
            FROM preprocessed_food_database
            WHERE name = ?
        ''', (name,))
        food_item = cursor.fetchone()
        conn.close()

        if food_item:
            calories_per_100g, protein_per_100g, carbs_per_100g, fats_per_100g = food_item
        else:
            food_items = TEST_AI_Database.fetch_nutritional_info_from_db()
            existing_item = next((item for item in food_items if item['Name'].lower() == name.lower()), None)

            if existing_item:
                calories_per_100g = existing_item['Calories_per_100g']
                protein_per_100g = existing_item['Protein_per_100g']
                carbs_per_100g = existing_item['Carbohydrates_per_100g']
                fats_per_100g = existing_item['Fats_per_100g']
            else:
                calories_per_100g = float(request.form.get('calories_per_100g'))
                protein_per_100g = float(request.form.get('protein_per_100g'))
                carbs_per_100g = float(request.form.get('carbs_per_100g'))
                fats_per_100g = float(request.form.get('fats_per_100g'))

                TEST_AI_Database.add_nutritional_info(name, calories_per_100g, protein_per_100g, carbs_per_100g, fats_per_100g)

        calories = (calories_per_100g / 100) * serving_size
        protein = (protein_per_100g / 100) * serving_size
        carbs = (carbs_per_100g / 100) * serving_size
        fats = (fats_per_100g / 100) * serving_size

        TEST_AI_Database.add_food_item(category, name, serving_size, calories, protein, carbs, fats, price=0)

        TEST_AI_Database.sync_food_items()

        return render_template('confirm_addition.html',
                               name=name, serving_size=serving_size,
                               calories=calories, protein=protein, carbs=carbs, fats=fats)

    else:
        name = request.args.get('name')
        category = request.args.get('category', 'Database Item')
        return render_template('add_serving.html', name=name, category=category)






### SHOW ITEMS
@app.route('/show_items', methods=['GET'])
def show_items():
    """Route to display the list of food items."""
    food_items = TEST_AI_Database.fetch_food_items_from_db()

    # Handle empty case
    if isinstance(food_items, pd.DataFrame) and not food_items.empty:
        food_items = food_items.to_dict(orient='records')
    elif not food_items:
        food_items = []

    return render_template('show_items.html', food_items=food_items)


@app.route('/delete_food_item', methods=['POST'])
def delete_food_item():
    """Delete a food item."""
    food_name = request.form.get('name')

    if not food_name:
        flash("No food item provided to delete.", 'danger')
        return redirect(url_for('show_items'))

    try:
        TEST_AI_Database.delete_food_item(food_name)
        flash(f"Food item '{food_name}' deleted successfully.", 'success')
    except Exception as e:
        flash(f"Error deleting food item: {str(e)}", 'danger')

    return redirect(url_for('show_items'))


@app.route('/edit_food_item', methods=['GET', 'POST'])
def edit_food_item():
    if request.method == 'POST':
        original_name = request.form['original_name']
        new_name = request.form['name']

        new_calories = request.form['calories']
        new_protein = request.form['protein']
        new_carbohydrates = request.form['carbohydrates']
        new_fats = request.form['fats']

        food_items = TEST_AI_Database.get_all_food_items()
        current_food_item = next((item for item in food_items if item['Name'].lower() == original_name.lower()), None)

        if current_food_item:
            calories = float(new_calories) if new_calories else current_food_item['Calories']
            protein = float(new_protein) if new_protein else current_food_item['Protein']
            carbs = float(new_carbohydrates) if new_carbohydrates else current_food_item['Carbohydrates']
            fats = float(new_fats) if new_fats else current_food_item['Fats']

            TEST_AI_Database.update_food_item(
                original_name=original_name,
                category=current_food_item['Category'],
                new_name=new_name,
                weight=current_food_item['Weight'],
                calories=calories,
                protein=protein,
                carbs=carbs,
                fats=fats
            )

            flash(f"Food item '{new_name}' updated successfully!", 'success')
            return redirect(url_for('show_items'))
        else:
            flash(f"Food item '{original_name}' not found.", 'danger')
            return redirect(url_for('show_items'))

    food_name = request.args.get('name')
    food_items = TEST_AI_Database.get_all_food_items()
    food_item = next((item for item in food_items if item['Name'].lower() == food_name.lower()), None)

    if food_item:
        return render_template('edit_food_item.html', food_item=food_item)
    else:
        flash(f"Food item '{food_name}' not found.", 'danger')
        return redirect(url_for('show_items'))





#### MEAL PLANNING
@app.route('/meal_planning')
def meal_planning():
    return render_template('meal_planning.html')

@app.route('/generate_meal_plan', methods=['GET', 'POST'])
def generate_meal_plan():
    existing_meal_plans = TEST_AI_Database.get_all_meal_plans()

    if request.method == 'POST':

        if 'overwrite' in request.form:
            TEST_AI_Database.clear_all_meal_plans()
            existing_meal_plans = None
            return render_template('generate_meal_plan.html', existing_meal_plans=False)

        def parse_float(value):
            try:
                return float(value) if value else None
            except ValueError:
                return None
        criteria = {
            'calories_lower': parse_float(request.form.get('calories_lower')),
            'calories_upper': parse_float(request.form.get('calories_upper')),
            'protein_lower': parse_float(request.form.get('protein_lower')),
            'protein_upper': parse_float(request.form.get('protein_upper')),
            'carbs_lower': parse_float(request.form.get('carbs_lower')),
            'carbs_upper': parse_float(request.form.get('carbs_upper')),
            'fats_lower': parse_float(request.form.get('fats_lower')),
            'fats_upper': parse_float(request.form.get('fats_upper')),
            'price_lower': parse_float(request.form.get('price_lower')),
            'price_upper': parse_float(request.form.get('price_upper')),
        }

        num_meal_plans = int(request.form.get('num_meal_plans', 1))

        meal_plans = TEST_Functions.generate_meal_plan_logic(
            TEST_AI_Database.get_all_food_items(), criteria, num_meal_plans
        )

        TEST_Functions.save_and_sync_meal_plans(meal_plans, criteria)

        return render_template('generate_meal_plan.html', meal_plans_generated=True, meal_plans=meal_plans)

    if existing_meal_plans:
        return render_template('generate_meal_plan.html', existing_meal_plans=True)

    return render_template('generate_meal_plan.html')


@app.route('/view_meal_plans')
def view_meal_plans():
    meal_plans = TEST_AI_Database.get_all_meal_plans()

    if meal_plans:
        for plan in meal_plans:
            plan['meals'] = json.loads(plan['meals'])

    return render_template('view_meal_plans.html', meal_plans=meal_plans)

@app.route('/check_meal_plans', methods=['GET', 'POST'])
def check_meal_plans():
    """Check if meal plans already exist and ask the user if they want to overwrite."""
    existing_meal_plans = TEST_AI_Database.get_all_meal_plans()

    if request.method == 'POST':
        if 'overwrite' in request.form and request.form['overwrite'] == 'yes':
            TEST_AI_Database.clear_all_meal_plans()  # Clear existing meal plans
            return redirect(url_for('generate_meal_plan_form'))
        else:
            flash("You chose not to overwrite existing meal plans.", 'info')
            return redirect(url_for('check_meal_plans'))

    return render_template('check_meal_plans.html', has_meal_plans=bool(existing_meal_plans))

@app.route('/overwrite_meal_plans', methods=['POST'])
def overwrite_meal_plans():
    TEST_AI_Database.clear_all_meal_plans()
    return redirect('/generate_meal_plan')


@app.route('/generate_ai_meal_plan', methods=['GET', 'POST'])
def generate_ai_meal_plan():

    existing_ai_meal_plans = TEST_AI_Database.fetch_weekly_AI_meal_plan()

    goals = None

    if request.method == 'POST' and 'overwrite_handled' not in session:
        if existing_ai_meal_plans and 'overwrite' not in request.form:
            return render_template('generate_ai_meal_plan.html', existing_ai_meal_plans=True)

    if request.method == 'POST':
        if 'overwrite' in request.form:
            TEST_AI_Database.clear_weekly_meal_plans()
            existing_ai_meal_plans = None
            session['overwrite_handled'] = True

        use_goals = request.form.get('use_goals')

        if use_goals == 'yes':
            goals = TEST_AI_Database.fetch_goals_from_db()

            if goals is None:
                goals = {
                    'calories_goal': 2000,
                    'protein_goal': 100,
                    'carbohydrates_goal': 250,
                    'fats_goal': 50
                }

            ai_meal_plan = TEST_AI.generate_weekly_meal_plan_knn(
                food_items=TEST_AI.load_food_items(CSV_FILE),
                knn_model=TEST_AI.knn_recommendation_with_weights(
                    TEST_AI.normalize_macros(TEST_AI.load_food_items(CSV_FILE))
                ),
                target_macros={
                    'calories': goals['calories_goal'],
                    'protein': goals['protein_goal'],
                    'carbohydrates': goals['carbohydrates_goal'],
                    'fats': goals['fats_goal']
                }
            )

            TEST_AI_Database.save_weekly_AI_meal_plan_to_db(ai_meal_plan)

            return render_template('generate_ai_meal_plan.html', meal_plans_generated=True, ai_meal_plan=ai_meal_plan)

        elif use_goals == 'no':
            return render_template('generate_ai_meal_plan.html', custom_goal_form=True)

        elif 'custom_goals' in request.form:
            goals = {
                'calories_goal': float(request.form.get('calories_goal', 2000)),
                'protein_goal': float(request.form.get('protein_goal', 100)),
                'carbohydrates_goal': float(request.form.get('carbohydrates_goal', 250)),
                'fats_goal': float(request.form.get('fats_goal', 50))
            }

            ai_meal_plan = TEST_AI.generate_weekly_meal_plan_knn(
                food_items=TEST_AI.load_food_items(CSV_FILE),
                knn_model=TEST_AI.knn_recommendation_with_weights(
                    TEST_AI.normalize_macros(TEST_AI.load_food_items(CSV_FILE))
                ),
                target_macros={
                    'calories': goals['calories_goal'],
                    'protein': goals['protein_goal'],
                    'carbohydrates': goals['carbohydrates_goal'],
                    'fats': goals['fats_goal']
                }
            )

            TEST_AI_Database.save_weekly_AI_meal_plan_to_db(ai_meal_plan)

            return render_template('generate_ai_meal_plan.html', meal_plans_generated=True, ai_meal_plan=ai_meal_plan)

    if goals is None:
        goals = TEST_AI_Database.fetch_goals_from_db() or {
            'calories_goal': 2000,
            'protein_goal': 100,
            'carbohydrates_goal': 250,
            'fats_goal': 50
        }

    return render_template('generate_ai_meal_plan.html', goals=goals, existing_ai_meal_plans=existing_ai_meal_plans)

@app.route('/view_ai_meal_plan')
def view_ai_meal_plan():
    # Fetch the AI-generated meal plan from the database
    ai_meal_plan, total_macros = TEST_AI_Database.fetch_weekly_AI_meal_plan()

    if not ai_meal_plan:
        flash('No AI meal plan found. Please generate one!', 'warning')
        return redirect('/generate_ai_meal_plan')

    return render_template('view_ai_meal_plan.html', ai_meal_plan=ai_meal_plan)

@app.route('/clear_meal_plans', methods=['POST'])
def clear_meal_plans():
    TEST_AI_Database.clear_all_meal_plans()

    TEST_AI_Database.clear_weekly_meal_plans()

    return render_template('meal_planning.html', success_message="All meal plans cleared!")




### FOOD LOGGING
@app.route('/food_log', methods=['GET'])
def food_log_menu():
    """Display the food log menu with options."""
    return render_template('food_log.html')


@app.route('/calculate_daily_intake', methods=['GET', 'POST'])
def calculate_daily_intake():

    food_items = TEST_Functions.load_csv_to_dict(CSV_FILE)
    user_goals = TEST_AI_Database.fetch_goals_from_db()

    print("DEBUG: Fetched food items: ", food_items)
    print("DEBUG: Fetched user goals: ", user_goals)

    goal_calories = user_goals['calories_goal']
    goal_protein = user_goals['protein_goal']
    goal_carbs = user_goals['carbohydrates_goal']
    goal_fats = user_goals['fats_goal']

    if request.method == 'POST':

        print("DEBUG: Raw form data: ", request.form)
        selected_food_quantities = request.form.getlist('food_items[]')

        print("DEBUG: Received form data (quantities): ", selected_food_quantities)

        if not selected_food_quantities or all(q == '0' for q in selected_food_quantities):
            print("DEBUG: No valid food items selected.")
            return render_template('calculate_daily_intake.html',
                                   food_items=food_items,
                                   meal_log_updated=False,
                                   goal_calories=goal_calories,
                                   goal_protein=goal_protein,
                                   goal_carbs=goal_carbs,
                                   goal_fats=goal_fats,
                                   success_message="No valid food items selected.")

        food_items = TEST_AI_Database.fetch_food_items_from_db()
        print("DEBUG: Fetched food items for POST processing: ", food_items)

        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        selected_items = []

        for idx, quantity in enumerate(selected_food_quantities):
            quantity = int(quantity)
            if quantity > 0:  #
                selected_item = food_items.iloc[idx]

                print(f"DEBUG: Processing item '{selected_item['name']}' with quantity {quantity}")

                selected_items.append({
                    'Name': selected_item['name'],
                    'Calories': selected_item['calories'],
                    'Protein': selected_item['protein'],
                    'Carbohydrates': selected_item['carbohydrates'],
                    'Fats': selected_item['fats'],
                    'Quantity': quantity
                })

                total_calories += float(selected_item['calories']) * quantity
                total_protein += float(selected_item['protein']) * quantity
                total_carbs += float(selected_item['carbohydrates']) * quantity
                total_fats += float(selected_item['fats']) * quantity

                print(f"DEBUG: Running totals after adding {selected_item['name']}:")
                print(
                    f"       Calories: {total_calories}, Protein: {total_protein}, Carbs: {total_carbs}, Fats: {total_fats}")

        print("DEBUG: Final accumulated totals:")
        print(
            f"       Total Calories: {total_calories}, Total Protein: {total_protein}, Total Carbs: {total_carbs}, Total Fats: {total_fats}")

        date = datetime.now().strftime('%d-%m-%Y')

        try:
            food_items_string = "; ".join([item['Name'] for item in selected_items])
            date = datetime.now().strftime('%d-%m-%Y')  # Ensure date is in a string format

            TEST_AI_Database.add_daily_calorie_log(
                date,
                food_items_string,
                float(total_calories),
                float(total_protein),
                float(total_carbs),
                float(total_fats)
            )
            print(f"DEBUG: Data saved to database for date {date}.")
        except Exception as e:
            print(f"ERROR: Failed to save to the database. Reason: {e}")
            return render_template('calculate_daily_intake.html',
                                   food_items=food_items,
                                   meal_log_updated=False,
                                   goal_calories=goal_calories,
                                   goal_protein=goal_protein,
                                   goal_carbs=goal_carbs,
                                   goal_fats=goal_fats,
                                   success_message="Failed to save to database.")

        try:
            TEST_Functions.save_daily_intake_to_csv(date, selected_items, total_calories, total_protein, total_carbs,
                                                    total_fats)
            print(f"DEBUG: Data saved to CSV for date {date}.")
        except Exception as e:
            print(f"ERROR: Failed to save to CSV. Reason: {e}")
            return render_template('calculate_daily_intake.html',
                                   food_items=food_items,
                                   meal_log_updated=False,
                                   goal_calories=goal_calories,
                                   goal_protein=goal_protein,
                                   goal_carbs=goal_carbs,
                                   goal_fats=goal_fats,
                                   success_message="Failed to save to CSV.")

        try:
            TEST_AI_Database.sync_daily_calorie_log()
            print("DEBUG: Log synced successfully.")
        except Exception as e:
            print(f"ERROR: Failed to sync log. Reason: {e}")
            return render_template('calculate_daily_intake.html',
                                   food_items=food_items,
                                   meal_log_updated=False,
                                   goal_calories=goal_calories,
                                   goal_protein=goal_protein,
                                   goal_carbs=goal_carbs,
                                   goal_fats=goal_fats,
                                   success_message="Failed to sync log.")

        meal_log_updated = True

        return render_template('calculate_daily_intake.html',
                               food_items=food_items,  # Keep table populated
                               meal_log_updated=meal_log_updated,  # Success flag
                               goal_calories=goal_calories,
                               goal_protein=goal_protein,
                               goal_carbs=goal_carbs,
                               goal_fats=goal_fats,
                               success_message="Success, Log has been updated!")

    print("DEBUG: GET request - Rendering the daily intake page.")
    return render_template('calculate_daily_intake.html',
                           food_items=food_items,
                           meal_log_updated=False,
                           goal_calories=goal_calories,
                           goal_protein=goal_protein,
                           goal_carbs=goal_carbs,
                           goal_fats=goal_fats)

@app.route('/view_log', methods=['GET'])
def view_daily_log():
    daily_log = TEST_AI_Database.load_daily_calorie_log_from_db()

    if not daily_log:
        flash('No daily logs found.', 'error')
        return redirect(url_for('food_menu'))

    return render_template('view_food_log.html', daily_log=daily_log)

@app.route('/select_log_entry', methods=['POST'])
def select_log_entry():
    """Handle the selection of a specific log entry for visualization."""
    selected_date = request.form['log_id']
    all_logs = TEST_AI_Database.load_daily_calorie_log_from_db()
    selected_log = next((log for log in all_logs if log['Date'] == selected_date), None)

    if not selected_log:
        flash('No log entry found for the selected date.', 'error')
        return redirect(url_for('view_daily_log'))

    user_goals = TEST_AI_Database.fetch_goals_from_db()

    return render_template('view_food_log.html',
                           daily_log=all_logs,  # Load all logs
                           selected_log=selected_log,  # Pass the selected log entry
                           goal_calories=user_goals['calories_goal'],
                           goal_protein=user_goals['protein_goal'],
                           goal_carbs=user_goals['carbohydrates_goal'],
                           goal_fats=user_goals['fats_goal'])

def clear_food_log():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM daily_calorie_log")
        conn.commit()

def clear_weight_history():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM weight_log")  # Assuming your weight history is stored in 'weight_history' table
        conn.commit()





### WEIGHT MANAGEMENT
@app.route('/weight')
def weight_menu():
    return render_template('weight_menu.html')

@app.route('/log_weight', methods=['GET', 'POST'])
def log_weight():
    if request.method == 'POST':
        # Get the entered weight from the form
        weight = request.form.get('weight')

        # Check if the weight was entered correctly
        if not weight:
            flash('Please enter a valid weight.', 'error')
            return redirect('/log_weight')

        try:
            # Convert weight to float for validation
            weight = float(weight)
        except ValueError:
            flash('Please enter a valid numeric weight.', 'error')
            return redirect('/log_weight')

        # Save the weight entry in the database but wait for confirmation
        return render_template('log_weight.html', weight=weight, weight_confirmed=True)

    # Fetch the weight history from the database to display in the table
    weight_history = TEST_AI_Database.load_weight_log_from_db()

    # Render the initial log weight form
    return render_template('log_weight.html', weight_confirmed=False, weight_history=weight_history)


@app.route('/confirm_weight', methods=['POST'])
def confirm_weight():
    # Get the confirmed weight from the hidden field in the confirmation form
    confirmed_weight = request.form['confirmed_weight']

    # Get the user's confirmation decision (yes or no)
    confirm = request.form['confirm']

    if confirm == 'yes':
        # If the user confirmed, log the weight using the function
        date = datetime.now().strftime("%d-%m-%Y")
        try:
            # Log weight in the CSV and database
            TEST_AI_Database.add_weight_log(date, confirmed_weight)
            return render_template('log_weight.html', success=True)
        except Exception as e:
            return render_template('log_weight.html', error=str(e), weight_confirmed=False)
    else:
        # If the user did not confirm, redirect back to the weight logging page
        return redirect(url_for('log_weight'))

@app.route('/visualise_weight_progress', methods=['GET', 'POST'])
def visualise_weight():
    # Load weight history from the database
    weight_history = TEST_AI_Database.load_weight_log_from_db()

    # Load goals from the database or wherever they are stored
    goals = TEST_AI_Database.fetch_goals_from_db()

    if not goals:
        flash('No goals found. Please set your goals first.', 'error')
        return render_template('visualise_weight_progress.html', weight_history=weight_history, predicted_weight=None)

    # Extract the starting weight, target weight, and other relevant variables from the goals data
    starting_weight = float(goals.get('starting_weight'))  # Use starting weight from goals, not logged weight
    target_weight = float(goals['target_weight'])
    target_date = datetime.strptime(goals['target_date'], "%d-%m-%Y")
    weekly_weight_change = float(goals['weekly_weight_change'])

    # Calculate the predicted weight progression based on the starting weight from the goals
    predicted_progression = calculate_weekly_progression(starting_weight, target_weight, target_date)

    if request.method == 'POST':
        return render_template('visualise_weight_progress.html', weight_history=weight_history, predicted_weight=predicted_progression)

    return render_template('visualise_weight_progress.html', weight_history=weight_history, predicted_weight=predicted_progression)

@app.route('/get_weight_data', methods=['GET'])
def get_weight_data():
    weight_history = TEST_AI_Database.load_weight_log_from_db()
    return jsonify(weight_history)

@app.route('/get_arima_prediction', methods=['GET'])
def get_arima_prediction():
    """Fetch the ARIMA weight prediction data."""

    weight_log = TEST_AI_Database.load_weight_log_from_db()
    if not weight_log:
        return jsonify({"error": "No weight log data available."}), 404

    goals = TEST_AI_Database.fetch_goals_from_db()
    if not goals:
        return jsonify({"error": "No goals found. Please set your goals first."}), 404

    last_logged_date = datetime.strptime(weight_log[-1]['Date'], "%d-%m-%Y")

    target_date = datetime.strptime(goals['target_date'], "%d-%m-%Y")

    days_to_target = (target_date - last_logged_date).days

    if days_to_target <= 0:
        return jsonify({"error": "Target date must be in the future."}), 400

    model = TEST_AI.train_weight_trend_model()
    if model is None:
        return jsonify({"error": "Failed to train the ARIMA model."}), 500

    predicted_weights = TEST_AI.predict_future_weight(model, steps=days_to_target)
    if predicted_weights is None:
        return jsonify({"error": "Failed to predict future weight."}), 500

    predicted_data = [{"date": date.strftime("%d-%m-%Y"), "weight": weight} for date, weight in predicted_weights.items()]

    return jsonify(predicted_data)

@app.route('/bmi_calculator', methods=['GET', 'POST'])
def bmi_calculator():
    current_bmi_info = TEST_AI_Database.fetch_bmi_info_from_db()

    if request.method == 'POST':
        try:
            height = float(request.form.get('height'))
            weight = float(request.form.get('weight'))
            age = int(request.form.get('age'))
            gender = request.form.get('gender').upper()
            activity_level = int(request.form.get('activity_level'))

            if gender not in ['M', 'F']:
                raise ValueError("Invalid gender")

            height_m = height / 100

            bmi = weight / (height_m ** 2)

            if gender == 'M':
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

            activity_levels = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
            if activity_level in activity_levels:
                tdee = bmr * activity_levels[activity_level]
            else:
                raise ValueError("Invalid activity level")

            if current_bmi_info:
                bmi_id = current_bmi_info['id']
                TEST_AI_Database.update_bmi_info(bmi_id, height, weight, age, gender, bmi, bmr, tdee)
            else:
                TEST_AI_Database.add_bmi_info(height, weight, age, gender, bmi, bmr, tdee)

            current_bmi_info = TEST_AI_Database.fetch_bmi_info_from_db()

            return render_template('bmi_calculator.html', current_bmi_info=current_bmi_info, bmi=bmi, bmr=bmr, tdee=tdee, success=True)

        except ValueError as e:
            return render_template('bmi_calculator.html', current_bmi_info=current_bmi_info, error=str(e))

    return render_template('bmi_calculator.html', current_bmi_info=current_bmi_info)











##### GOAL MANAGEMENT
@app.route('/goals')
def goal_menu():
    return render_template('goal_menu.html')

@app.route('/set_goals', methods=['GET', 'POST'])
@app.route('/set_goals', methods=['GET', 'POST'])
def set_goals():
    bmi_info = TEST_AI_Database.fetch_bmi_info_from_db()
    existing_goals = load_existing_goals()

    success = False
    error = None

    current_weight = bmi_info['Weight'] if bmi_info else 0
    if request.method == 'POST':
        try:
            starting_weight = request.form.get('starting_weight', current_weight)
            if starting_weight:
                starting_weight = float(request.form['starting_weight'])

            target_weight = float(request.form['target_weight'])

            weight_change_goal = 'lose' if target_weight < starting_weight else 'gain'

            protein_goal = request.form.get('protein_goal') or calculate_protein_goal(target_weight)
            carbs_goal = request.form.get('carbs_goal') or calculate_carbs_goal(target_weight)
            fats_goal = request.form.get('fats_goal') or calculate_fats_goal(target_weight)

            target_date_str = request.form.get('target_date')
            try:
                target_date = datetime.strptime(target_date_str, "%d-%m-%Y")
            except ValueError:
                error = "Invalid date format. Please enter the date in DD-MM-YYYY format."
                return render_template('set_goals.html', current_bmi_info=bmi_info, error=error)

            daily_calories = calculate_calories(target_weight, starting_weight, target_date)

            weekly_weight_progression = calculate_weekly_progression(starting_weight, target_weight, target_date)

            if len(weekly_weight_progression) >= 2:
                first_week_weight = weekly_weight_progression[0][1]
                second_week_weight = weekly_weight_progression[1][1]
                weekly_weight_change = first_week_weight - second_week_weight
            else:
                weekly_weight_change = 0

            if weight_change_goal == 'lose':
                weekly_weight_change = -abs(weekly_weight_change)
            else:
                weekly_weight_change = abs(weekly_weight_change)

            new_goal = {
                'calories_goal': daily_calories,
                'protein_goal': protein_goal,
                'carbohydrates_goal': carbs_goal,
                'fats_goal': fats_goal,
                'target_weight': target_weight,
                'starting_weight': starting_weight,
                'target_date': target_date_str,
                'weekly_weight_change': weekly_weight_change
            }

            TEST_AI_Database.add_goal(
                new_goal['calories_goal'], new_goal['protein_goal'], new_goal['carbohydrates_goal'],
                new_goal['fats_goal'], new_goal['target_weight'], new_goal['starting_weight'], new_goal['target_date'],
                new_goal['weekly_weight_change']
            )

            TEST_Functions.save_dict_to_csv(GOALS_FILE, [new_goal],
                                            headers=["calories_goal", "protein_goal", "carbohydrates_goal", "fats_goal",
                                                     "target_weight", "starting_weight", "target_date", "weekly_weight_change"])

            success = True

        except Exception as e:
            print(f"Error saving goals: {e}")
            error = "There was an issue saving your goals. Please try again."

        return render_template('set_goals.html', current_bmi_info=bmi_info, success=success,
                               error=error, weekly_weight_progression=weekly_weight_progression)

    return render_template('set_goals.html', current_bmi_info=bmi_info, existing_goals=existing_goals)


def calculate_weekly_progression(starting_weight, target_weight, target_date):
    current_date = datetime.now()

    weeks_remaining = (target_date - current_date).days // 7

    if weeks_remaining == 0:
        return []

    if starting_weight > target_weight:
        weekly_weight_change = (starting_weight - target_weight) / weeks_remaining
    else:
        weekly_weight_change = (target_weight - starting_weight) / weeks_remaining

    weekly_progression = []

    for week in range(weeks_remaining + 1):
        future_date = current_date + timedelta(weeks=week)
        if starting_weight > target_weight:
            future_weight = starting_weight - (week * weekly_weight_change)
        else:
            future_weight = starting_weight + (week * weekly_weight_change)

        weekly_progression.append((future_date.strftime("%d-%m-%Y"), future_weight))

    return weekly_progression

def calculate_protein_goal(target_weight):
    return target_weight * 2.0

def calculate_carbs_goal(target_weight):
    return target_weight * 4.0

def calculate_fats_goal(target_weight):
    return target_weight * 1.0

def calculate_calories(target_weight, starting_weight, target_date):
    bmr = 370 + (21.6 * (target_weight / (1.2 if starting_weight > target_weight else 1.0)))
    tdee = bmr * 1.2
    return round(tdee, 2)

def load_existing_goals():
    """Check if existing goals are already set by checking the goals file."""
    goals_data = TEST_Functions.load_csv_to_dict(GOALS_FILE)
    return goals_data[-1] if goals_data else None

@app.route('/view_goals')
def view_goals():
    """Fetch and display the latest goal from the database or CSV."""

    goals = TEST_AI_Database.fetch_goals_from_db()

    if not goals:
        goals = TEST_Functions.load_csv_to_dict(GOALS_FILE)
        if not goals:
            flash('No goals found', 'error')
            return render_template('view_goals.html', current_goals=None)

    latest_goal = goals[-1] if isinstance(goals, list) else goals

    calorie_goal = float(latest_goal.get('calories_goal', 0))
    protein_goal = float(latest_goal.get('protein_goal', 0))
    carbs_goal = float(latest_goal.get('carbohydrates_goal', 0))
    fats_goal = float(latest_goal.get('fats_goal', 0))
    target_weight = float(latest_goal.get('target_weight', 0))
    starting_weight = float(latest_goal.get('starting_weight', 0))
    target_date_str = latest_goal.get('target_date', None)
    weekly_weight_change = float(latest_goal.get('weekly_weight_change', 0))

    target_date = None
    if target_date_str:
        try:
            target_date = datetime.strptime(target_date_str, "%d-%m-%Y")
        except ValueError:
            flash('Invalid target date format', 'error')

    weekly_progression = calculate_weekly_progression(starting_weight, target_weight, target_date)

    current_goals = {
        'calories_goal': calorie_goal,
        'protein_goal': protein_goal,
        'carbohydrates_goal': carbs_goal,
        'fats_goal': fats_goal,
        'target_weight': target_weight,
        'starting_weight': starting_weight,
        'target_date': target_date_str,
        'weekly_weight_change': weekly_weight_change
    }

    return render_template('view_goals.html', current_goals=current_goals, weekly_progression=weekly_progression)


@app.route('/clear_goals', methods=['POST'])
def clear_goals():
    TEST_AI_Database.delete_goals_from_db()
    flash("Goals cleared successfully!", "success")
    return redirect(url_for('goal_menu'))




@app.route('/visualize_weight_log')
def visualize_weight_log():
    try:
        weight_history = TEST_AI_Database.load_weight_log_from_db()

        if not weight_history:
            flash('No weight history found.', 'warning')
            return redirect(url_for('dashboard'))

        dates = [row['Date'] for row in weight_history]
        weights = [row['Weight'] for row in weight_history]

        return render_template('visualize_weight_log.html', dates=dates, weights=weights)

    except Exception as e:
        flash(f"Error visualizing weight log: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))


@app.route('/visualize_calorie_log')
def visualize_calorie_log():
    try:
        daily_log = TEST_AI_Database.load_daily_calorie_log_from_db()

        if not daily_log:
            flash('No entries found in the daily log.', 'warning')
            return redirect(url_for('dashboard'))

        dates = [entry['Date'] for entry in daily_log]
        calories = [entry['Calories'] for entry in daily_log]
        proteins = [entry['Protein'] for entry in daily_log]
        carbs = [entry['Carbohydrates'] for entry in daily_log]
        fats = [entry['Fats'] for entry in daily_log]

        return render_template('visualize_calorie_log.html', dates=dates, calories=calories, proteins=proteins, carbs=carbs, fats=fats)

    except Exception as e:
        flash(f"Error visualizing calorie log: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))


@app.route('/visualize_meal_plan/<int:meal_plan_id>')
def visualize_meal_plan(meal_plan_id):
    try:
        meal_plans = TEST_AI_Database.get_all_meal_plans()

        if not meal_plans or meal_plan_id >= len(meal_plans):
            flash('Meal plan not found.', 'warning')
            return redirect(url_for('dashboard'))

        selected_plan = meal_plans[meal_plan_id - 1]

        goals = TEST_AI_Database.fetch_goals_from_db()

        if not goals:
            flash('Please set your goals before visualizing a meal plan.', 'warning')
            return redirect(url_for('dashboard'))

        return render_template('visualize_meal_plan.html', plan=selected_plan, goals=goals)

    except Exception as e:
        flash(f"Error visualizing meal plan: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))



if __name__ == '__main__':
    initialize_app()

    app.run(debug=True, port=5001)
