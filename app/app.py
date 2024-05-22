from flask import Flask, request, jsonify
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)
DATABASE = '/app/data/stock.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fuel_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pump_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            client TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fuel_restock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pump_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/usePump', methods=['POST'])
def use_pump():
    init_db()
    data = request.get_json()
    pump_id = data.get('pump_id')
    amount = data.get('amount')
    client = data.get('client')

    if not pump_id or amount is None or not client:
        return jsonify({"error": "pump_id, amount, and client are required"}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO fuel_usage (pump_id, amount, client, timestamp) VALUES (?, ?, ?, ?)', (pump_id, amount, client, datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({"message": "Pump usage recorded successfully"}), 200


@app.route('/restockFuel', methods=['POST'])
def restock_fuel():
    init_db()
    data = request.get_json()
    pump_id = data.get('pump_id')
    amount = data.get('amount')

    if not pump_id or amount is None:
        return jsonify({"error": "pump_id and amount are required"}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO fuel_restock (pump_id, amount, timestamp) VALUES (?, ?, ?)', (pump_id, amount, datetime.now()))
    conn.commit()
    conn.close()
    return jsonify({"message": "Fuel restocked successfully"}), 200


@app.route('/assessFuel', methods=['POST'])
def assess_fuel():
    init_db()
    data = request.get_json()
    pump_id = data.get('pump_id')
    predictions = data.get('predictions')  # List of dicts with 'ds' and 'yhat'

    print(pump_id)
    print(predictions)

    if not pump_id or not predictions:
        return jsonify({"error": "pump_id and predictions are required"}), 400

    # Load fuel usage and restock data
    conn = sqlite3.connect(DATABASE)
    fuel_usage = pd.read_sql_query('SELECT * FROM fuel_usage WHERE pump_id = ?', conn, params=(pump_id,))
    fuel_restock = pd.read_sql_query('SELECT * FROM fuel_restock WHERE pump_id = ?', conn, params=(pump_id,))
    conn.close()

    total_used = fuel_usage['amount'].sum()
    total_restocked = fuel_restock['amount'].sum()
    current_stock = total_restocked - total_used

    fuel_usage['timestamp'] = pd.to_datetime(fuel_usage['timestamp'])
    daily_usage = fuel_usage.set_index('timestamp').resample('D').sum()
    avg_daily_consumption = daily_usage['amount'].mean()

    predictions_df = pd.DataFrame(predictions)
    predictions_df['ds'] = pd.to_datetime(predictions_df['ds'], format='%a, %d %b %Y %H:%M:%S GMT')

    # Predict future consumption
    decision = "Wait"
    days_ahead = 7
    predicted_consumption = avg_daily_consumption * days_ahead

    # Determine if we need to restock
    if current_stock < predicted_consumption:
        for i in range(days_ahead):
            future_date = datetime.now() + timedelta(days=i)
            future_date_str = future_date.strftime('%Y-%m-%d')

            # Get the predicted price for the future date
            future_price = predictions_df[predictions_df['ds'].dt.strftime('%Y-%m-%d') == future_date_str]['yhat'].values[0]

            # Calculate the future stock level
            future_stock = current_stock - (avg_daily_consumption * (i + 1))

            if future_stock < 1000:
                decision = "Buy Now"
                # Check if the price is expected to decrease before the stock falls below the margin
                for j in range(i + 1, days_ahead):
                    later_date = datetime.now() + timedelta(days=j)
                    later_date_str = later_date.strftime('%Y-%m-%d')
                    later_price = predictions_df[predictions_df['ds'].dt.strftime('%Y-%m-%d') == later_date_str]['yhat'].values[0]

                    if later_price < future_price:
                        decision = "Wait"
                        break

                break

    return jsonify({"current_stock": current_stock, "average_daily_consumption": avg_daily_consumption, "decision": decision}), 200



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
