# AI-Powered Calorie Tracking Application

## Overview
This project is a calorie tracking application designed to help users monitor their nutritional intake, track weight progress, and receive personalised meal recommendations. The application uses machine learning techniques and a user-friendly web interface to make it easy for users to manage their diet and meet health goals.

## Features
- **User-Friendly Web Interface**: Built with Flask, HTML, CSS, and JavaScript to provide an interactive experience for managing food and weight logs.
- **Dynamic Food Database**: Stores and manages user food intake using SQLite, supporting robust CRUD operations for data entry and retrieval.
- **Personalised Meal Recommendations**: Implements K-Nearest Neighbors (KNN) to suggest meals based on a user's dietary history and preferences.
- **Weight Trend Prediction**: Uses ARIMA time-series modeling to predict future weight trends and help users with proactive weight management.
- **Visualisation Tools**: Generates graphical visualisations of nutrient intake and weight progression to help users better understand their dietary habits.

## Tech Stack
- **Backend**: Python (Flask), SQLite for data storage
- **Frontend**: HTML, CSS, JavaScript
- **Machine Learning**: KNN, ARIMA
- **Data Visualisation**: Matplotlib, Pandas

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd calorie-tracker-app
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python TEST_Main.py
   ```
5. Open your browser and navigate to `http://localhost:5000` to interact with the web interface.

## Project Structure
- **TEST_Main.py**: The main entry point of the application, containing the core loop for managing menus and user interaction.
- **TEST_Functions.py**: Contains utility functions for handling user inputs, file operations, and data synchronisation.
- **TEST_AI.py**: Implements machine learning algorithms like KNN and ARIMA for meal recommendations and weight predictions.
- **TEST_AI_Database.py**: Manages database operations, including initialising tables, syncing data, and importing food information.
- **DATABASE_TEST.db**: SQLite database file storing user information, meal logs, weight data, and goals.

## Usage
1. **Logging Food**: Users can log daily food intake by selecting items from the pre-processed food database or adding new items manually.
2. **Managing Weight**: Track weight changes and visualise progress over time.
3. **Setting Goals**: Define calorie, protein, carbohydrates, and fat goals, and generate personalised meal plans accordingly.
4. **Meal Recommendations**: Get AI-powered meal suggestions that fit within the user's dietary preferences and goals.

## Future Improvements
- Mobile application integration to enhance accessibility.
- Adding image recognition for food items to make logging easier.
- Expanding the food database with more diverse food items and cuisines.
