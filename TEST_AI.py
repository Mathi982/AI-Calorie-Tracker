import pandas as pd
import numpy as np
import random
import warnings
from pmdarima import auto_arima
from sklearn.exceptions import ConvergenceWarning
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
import os
from statsmodels.tsa.stattools import adfuller

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


def load_calorie_log(file_path):
    return pd.read_csv(file_path)


def load_food_items(file_path):
    return pd.read_csv(file_path)


def load_goals(file_path):
    try:
        goals_df = pd.read_csv(file_path)
        if not goals_df.empty:
            return goals_df.iloc[-1]
        else:
            return None
    except FileNotFoundError:
        return None


def clean_daily_calorie_log(daily_calorie_log):
    daily_calorie_log['Food Items'] = daily_calorie_log['Food Items'].str.split(';')
    return daily_calorie_log.explode('Food Items').reset_index(drop=True)


def merge_with_food_items(cleaned_log, food_items):
    merged_log = pd.merge(cleaned_log, food_items, how='left', left_on='Food Items', right_on='Name')

    merged_log['Calories'] = merged_log['Calories_y'].fillna(merged_log['Calories_x'])
    merged_log['Protein'] = merged_log['Protein_y'].fillna(merged_log['Protein_x'])
    merged_log['Carbohydrates'] = merged_log['Carbohydrates_y'].fillna(merged_log['Carbohydrates_x'])
    merged_log['Fats'] = merged_log['Fats_y'].fillna(merged_log['Fats_x'])

    merged_log = merged_log[['Date', 'Food Items', 'Calories', 'Protein', 'Carbohydrates', 'Fats']]

    return merged_log

def normalize_macros(df):
    df = df.rename(columns={
        'Calories': 'calories',
        'Protein': 'protein',
        'Carbohydrates': 'carbohydrates',
        'Fats': 'fats'
    })

    df[['calories', 'protein', 'carbohydrates', 'fats']] = df[['calories', 'protein', 'carbohydrates', 'fats']].apply(
        lambda x: (x - x.min()) / (x.max() - x.min())
    )
    return df




def tune_knn_hyperparameters(food_items, target_macros, min_n=1, max_n=20):

    food_items = food_items.rename(columns={
        'Calories': 'calories',
        'Protein': 'protein',
        'Carbohydrates': 'carbohydrates',
        'Fats': 'fats'
    })

    X = food_items[['calories', 'protein', 'carbohydrates', 'fats']].values
    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

    best_n = min_n
    best_rmse = float('inf')
    best_metric = 'euclidean'
    best_weights = [1, 1, 1, 1]

    weight_options = [
        [1, 1, 1, 1],
        [2, 1, 1, 1],
        [1, 2, 1, 1],
        [1, 1, 2, 1],
        [1, 1, 1, 2],
        [2, 2, 1, 1],
    ]

    for metric in ['euclidean', 'manhattan']:
        for n in range(min_n, max_n + 1):
            for weights in weight_options:
                weighted_X_train = X_train * weights
                weighted_X_test = X_test * weights

                knn = NearestNeighbors(n_neighbors=n, metric=metric)
                knn.fit(weighted_X_train)

                distances, indices = knn.kneighbors(weighted_X_test)
                predicted_macros = weighted_X_train[indices].mean(axis=1)

                rmse = np.sqrt(mean_squared_error(weighted_X_test, predicted_macros))
                print(f"n_neighbors = {n}, metric = {metric}, weights = {weights}: RMSE = {rmse:.4f}")

                if rmse < best_rmse:
                    best_rmse = rmse
                    best_n = n
                    best_metric = metric
                    best_weights = weights

    print(
        f"Best n_neighbors: {best_n}, Best Metric: {best_metric}, Best Weights: {best_weights}, with RMSE: {best_rmse:.4f}")
    return best_n, best_metric, best_weights


def knn_recommendation_with_weights(food_items, n_neighbors=5, weights=None, metric='euclidean'):


    food_items = food_items.rename(columns={
        'Calories': 'calories',
        'Protein': 'protein',
        'Carbohydrates': 'carbohydrates',
        'Fats': 'fats'
    })

    X = food_items[['calories', 'protein', 'carbohydrates', 'fats']].values

    if weights is not None:
        X = X * weights

    knn = NearestNeighbors(n_neighbors=n_neighbors, metric=metric)
    knn.fit(X)

    return knn


def recommend_meals_for_day_knn(food_items, knn_model, target_macros, used_foods=set(), portion_size=100):
    current_totals = {'calories': 0, 'protein': 0, 'carbohydrates': 0, 'fats': 0}
    selected_meals = []

    food_items = food_items.sample(frac=1).reset_index(drop=True)

    for _, food in food_items.iterrows():
        if food['Name'] in used_foods:
            continue

        scaled_food = scale_portion(food, portion_size)

        if (current_totals['calories'] + scaled_food['Calories'] <= target_macros['calories'] and
                current_totals['protein'] + scaled_food['Protein'] <= target_macros['protein']):
            selected_meals.append(scaled_food)
            used_foods.add(food['Name'])
            current_totals['calories'] += scaled_food['Calories']
            current_totals['protein'] += scaled_food['Protein']
            current_totals['carbohydrates'] += scaled_food['Carbohydrates']
            current_totals['fats'] += scaled_food['Fats']

        if current_totals['calories'] >= target_macros['calories'] or \
                current_totals['protein'] >= target_macros['protein']:
            break

    return selected_meals, current_totals, used_foods


def scale_portion(food_item, portion_size):
    scale_factor = portion_size / 100
    food_item = food_item.copy()
    food_item['Calories'] *= scale_factor
    food_item['Protein'] *= scale_factor
    food_item['Carbohydrates'] *= scale_factor
    food_item['Fats'] *= scale_factor
    return food_item


def generate_weekly_meal_plan_knn(food_items, knn_model, target_macros, portion_size=100):
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_meal_plan = {}
    used_foods = set()

    for day in days_of_week:
        meals_for_day, totals, used_foods = recommend_meals_for_day_knn(food_items, knn_model, target_macros, used_foods, portion_size)
        weekly_meal_plan[day] = {
            'meals': meals_for_day,
            'totals': totals
        }
        print(f"\n{day}:")
        for meal in meals_for_day:
            print(f"{meal['Name']} - Calories: {meal['Calories']:.2f} kcal, "
                  f"Protein: {meal['Protein']:.2f} g, Carbs: {meal['Carbohydrates']:.2f} g, "
                  f"Fats: {meal['Fats']:.2f} g")
        print(f"Total for {day}: Calories: {totals['calories']:.2f} kcal, Protein: {totals['protein']:.2f} g, "
              f"Carbs: {totals['carbohydrates']:.2f} g, Fats: {totals['fats']:.2f} g")

    return weekly_meal_plan


def get_user_macros():
    print("Enter your target macros (leave blank for default values):")

    calories = input("Target Calories: ")
    protein = input("Target Protein (g): ")
    carbohydrates = input("Target Carbohydrates (g): ")
    fats = input("Target Fats (g): ")

    calories = float(calories) if calories else 2000
    protein = float(protein) if protein else 100
    carbohydrates = float(carbohydrates) if carbohydrates else 250
    fats = float(fats) if fats else 50

    return {
        'calories': calories,
        'protein': protein,
        'carbohydrates': carbohydrates,
        'fats': fats
    }


def get_macros_based_on_goals(goals_file):
    recent_goal = load_goals(goals_file)

    if recent_goal is not None:
        print(f"Your recently set goals are: {recent_goal['calories_goal']} calories, "
              f"{recent_goal['protein_goal']} protein, {recent_goal['carbohydrates_goal']} carbs, "
              f"{recent_goal['fats_goal']} fats.")
        use_recent_goal = input("Would you like to use these goals or set your own macros for the week? (y/n): ").strip().lower()


        if use_recent_goal == 'n':
            return get_user_macros()

        else:
            return {
                'calories': recent_goal['calories_goal'],
                'protein': recent_goal['protein_goal'],
                'carbohydrates': recent_goal['carbohydrates_goal'],
                'fats': recent_goal['fats_goal']
            }

    else:
        print("No recent goals found.")
        return get_user_macros()




# WEIGHT PREDICTION

warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def prepare_weight_trend_data():
    weight_log = pd.read_csv(WEIGHT_LOG_FILE)

    weight_log['Date'] = pd.to_datetime(weight_log['Date'], dayfirst=True)
    weight_log.set_index('Date', inplace=True)

    weight_log_daily = weight_log.resample('D').interpolate(method='linear')

    return weight_log_daily['Weight']

def train_weight_trend_model():
    """Train an AutoARIMA model to predict weight trends."""
    weight_series = prepare_weight_trend_data()

    if weight_series is None or len(weight_series) < 10:
        print("Insufficient data for AutoARIMA model training.")
        return None

    try:
        model = auto_arima(
            weight_series,
            seasonal=False,
            trace=False,
            error_action='ignore',
            suppress_warnings=True,
            stepwise=True
        )
        return model
    except Exception as e:
        print(f"Error training AutoARIMA model: {e}")
        return None

## WEIGHT PREDICTION
def predict_future_weight(model, steps=30):
    """Predict future weight for the next 'steps' days."""
    if model is None:
        print("Model is not trained.")
        return None

    try:
        forecast = model.predict(n_periods=steps)

        last_date = model.arima_res_.data.dates[-1]
        future_dates = pd.date_range(start=last_date, periods=steps + 1, freq='D')[1:]

        forecast_rounded = pd.Series(forecast, index=future_dates).round(2)

        return forecast_rounded

    except Exception as e:
        print(f"Error during weight prediction: {e}")
        return None


