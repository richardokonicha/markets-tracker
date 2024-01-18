import datetime
import pytz
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import requests
from twelvedata import TDClient
import os
from dotenv import load_dotenv

load_dotenv()

# Twelve Data API key
API_KEY = os.environ.get("TWELVE_DATA_API_KEY")

# Check if the API key is available
if API_KEY is None:
    raise ValueError("API key not found. Please set the TWELVE_DATA_API_KEY environment variable.")
# Function to fetch ETF data
def get_etf_data(symbol):
    try:
        client = TDClient(apikey=API_KEY)
        response = client.time_series(
            symbol=symbol,
            interval="1min",
            outputsize=30  # Number of data points for the chart
        )
        data = response.as_json()
        return data
    except Exception as e:
        print(f"Error fetching ETF data for {symbol}: {str(e)}")
        return []

# Function to update the ETF chart
def update_etf_chart(symbol):
    data = get_etf_data(symbol)

    if data:
        times = [point['datetime'] for point in data]
        values = [point['close'] for point in data]
        plt.plot(times, values, label=symbol)
        plt.xlabel('Time')
        plt.ylabel('Closing Price')
        plt.title(f'{symbol} Price Chart')
        plt.legend()
        plt.show()

# Function to update the clock labels, countdown timers, and ETF prices
def update_clocks():
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()

    # Update World Clocks
    for city, timezone in timezones.items():
        current_time = current_datetime.astimezone(pytz.timezone(timezone)).time()
        time_label = clock_labels[city]
        time_label.config(text=current_time.strftime("%H:%M:%S"))

        target_datetime = datetime.datetime.combine(current_date, target_time)
        if current_time > target_time:
            target_datetime += datetime.timedelta(days=1)

        remaining_time = target_datetime - datetime.datetime.combine(current_date, current_time)
        remaining_time -= datetime.timedelta(microseconds=remaining_time.microseconds)
        countdown_label = countdown_labels[city]

        if remaining_time.total_seconds() / 3600 <= 1:
            countdown_label.config(text=str(remaining_time))
            if remaining_time.total_seconds() / 60 <= 30:
                countdown_label.config(fg="red")
            else:
                countdown_label.config(fg="black")
        else:
            countdown_label.config(text="")

    selected_city = city_combo.get()
    if selected_city in timezones:
        selected_timezone = timezones[selected_city]
        local_timezone = pytz.timezone(selected_timezone)
        local_time = current_datetime.astimezone(local_timezone).time()
        local_time_label.config(text="Local Time: " + local_time.strftime("%H:%M:%S"))

    bitcoin_price = get_bitcoin_price()
    bitcoin_price_label.config(text="Bitcoin Price: " + bitcoin_price)

    root.after(1000, update_clocks)

# Function to fetch live Bitcoin price
def get_bitcoin_price():
    try:
        response = requests.get("https://api.coindesk.com/v1/bpi/currentprice/BTC.json")
        data = response.json()
        price = data["bpi"]["USD"]["rate"]
        return price
    except Exception as e:
        print("Error fetching Bitcoin price:", str(e))
        return "N/A"

# Function to toggle "always on top" feature
def toggle_always_on_top():
    root.attributes("-topmost", not root.attributes("-topmost"))
    if root.attributes("-topmost"):
        always_on_top_button.config(text="Disable Always on Top")
    else:
        always_on_top_button.config(text="Enable Always on Top")

# Create the Tkinter window
root = tk.Tk()
root.title("MarketsTracker")

# Create a dictionary to store the clock labels and countdown labels
clock_labels = {}
countdown_labels = {}

# Define the timezones and target times for the countdown
timezones = {
    "New York": "America/New_York",
    "London": "Europe/London",
    "Tokyo": "Asia/Tokyo",
    "Hong Kong": "Asia/Hong_Kong",
    "Sydney": "Australia/Sydney",
    "Paris": "Europe/Paris",
    "Los Angeles": "America/Los_Angeles",
    "Dubai": "Asia/Dubai"
}
target_time = datetime.time(8, 0, 0)

# Create and place the clock labels and countdown labels on the window
row = 0
for city in timezones.keys():
    label = tk.Label(root, text=city, font=("Arial", 24))
    label.grid(row=row, column=0, padx=10, pady=10)
    clock_label = tk.Label(root, text="", font=("Arial", 24, "bold"))
    clock_label.grid(row=row, column=1, padx=10, pady=10)
    clock_labels[city] = clock_label
    countdown_label = tk.Label(root, text="", font=("Arial", 24, "bold"))
    countdown_label.grid(row=row, column=2, padx=10, pady=10)
    countdown_labels[city] = countdown_label
    row += 1

# Create a combo box to select the city
city_combo = ttk.Combobox(root, values=list(timezones.keys()), font=("Arial", 16))
city_combo.current(0)
city_combo.grid(row=row, column=0, columnspan=3, padx=10, pady=10)

# Create a label to display the local time
local_time_label = tk.Label(root, text="Local Time: ", font=("Arial", 16))
local_time_label.grid(row=row+1, column=0, columnspan=3, padx=10, pady=10)

# Create a label to display the Bitcoin price
bitcoin_price_label = tk.Label(root, text="Bitcoin Price: ", font=("Arial", 16))
bitcoin_price_label.grid(row=row+2, column=0, columnspan=3, padx=10, pady=10)

# Create a button to toggle the "always on top" feature
always_on_top_button = tk.Button(root, text="Enable Always on Top", command=toggle_always_on_top)
always_on_top_button.grid(row=row+3, column=0, columnspan=3, padx=10, pady=10)

# //
# Create and place the ETF labels on the window
etf_buttons = {}  # Use buttons instead of labels
etf_symbols = ['IBIT', 'FBTC', 'BITB', 'ARKB', 'EZBC', 'BTCO', 'Other1', 'Other2']
# etf_symbols = ['IBIT', 'FBTC']

row += 4
# Create clickable buttons for ETF symbols
for symbol in etf_symbols:
    button = tk.Button(root, text=f"{symbol} Price", font=("Arial", 16), command=lambda s=symbol: update_etf_chart(s))
    button.grid(row=row, column=etf_symbols.index(symbol), padx=2, pady=2)
    etf_buttons[symbol] = button
    # row += 1j

# Create a combo box to select the ETF symbol
# etf_symbol_combo = ttk.Combobox(root, values=etf_symbols, font=("Arial", 16))
# etf_symbol_combo.current(0)
# etf_symbol_combo.grid(row=row+1, column=0, columnspan=len(etf_symbols), padx=10, pady=10)

# # Create a button to update the ETF chart
# update_etf_chart_button = tk.Button(root, text="Update ETF Chart", command=lambda: update_etf_chart(etf_symbol_combo.get()))
# update_etf_chart_button.grid(row=row+1, column=0, columnspan=len(etf_symbols), padx=10, pady=10)

# Start updating the clock labels and countdown labels
update_clocks()

# Run the Tkinter event loop
root.mainloop()
