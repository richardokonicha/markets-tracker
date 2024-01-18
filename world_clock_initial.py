import datetime
import pytz
import requests
import tkinter as tk
from tkinter import ttk

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
target_time = datetime.time(8, 0, 0)  # Set the target time to 8:00 AM

# Function to update the clock labels and countdown timers
def update_clocks():
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()

    for city, timezone in timezones.items():
        current_time = current_datetime.astimezone(pytz.timezone(timezone)).time()
        time_label = clock_labels[city]
        time_label.config(text=current_time.strftime("%H:%M:%S"))

        # Calculate the remaining time until the target time
        target_datetime = datetime.datetime.combine(current_date, target_time)
        if current_time > target_time:
            target_datetime += datetime.timedelta(days=1)  # Add 1 day if the target time has already passed

        remaining_time = target_datetime - datetime.datetime.combine(current_date, current_time)
        remaining_time -= datetime.timedelta(microseconds=remaining_time.microseconds)  # Remove microseconds
        countdown_label = countdown_labels[city]

        # Display the countdown timer only if there is one hour or less remaining
        if remaining_time.total_seconds() / 3600 <= 1:
            countdown_label.config(text=str(remaining_time))
            # Change countdown timer color to red if remaining time is less than 30 minutes
            if remaining_time.total_seconds() / 60 <= 30:
                countdown_label.config(fg="red")
            else:
                countdown_label.config(fg="black")
        else:
            countdown_label.config(text="")

    # Get local time in selected location
    selected_city = city_combo.get()
    if selected_city in timezones:
        selected_timezone = timezones[selected_city]
        local_timezone = pytz.timezone(selected_timezone)
        local_time = current_datetime.astimezone(local_timezone).time()
        local_time_label.config(text="Local Time: " + local_time.strftime("%H:%M:%S"))

    # Fetch and update Bitcoin price
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
    root.attributes("-topmost", not root.attributes("-topmost"))  # Toggle the "always on top" feature
    if root.attributes("-topmost"):
        always_on_top_button.config(text="Disable Always on Top")
    else:
        always_on_top_button.config(text="Enable Always on Top")

# Create the Tkinter window
root = tk.Tk()
root.title("World Clock & Countdown")

# Create a dictionary to store the clock labels and countdown labels
clock_labels = {}
countdown_labels = {}

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
city_combo.current(0)  # Set the default selection to the first city
city_combo.grid(row=row, column=0, columnspan=3, padx=10, pady=10)

# Create a label to display the local time
local_time_label = tk.Label(root, text="Local Time: ", font=("Arial", 16))
local_time_label.grid(row=row+1, column=0, columnspan=3, padx=10, pady=10)

# Create a label to display the Bitcoin price
bitcoin_price_label = tk.Label(root, text="Bitcoin Price: ", font=("Arial", 16))
bitcoin_price_label.grid(row=row+2, column=0, columnspan=3, padx=10, pady=10)

# Make the GUI flash for 5s every 30m
def flash_gui():
    current_minute = datetime.datetime.now().minute
    if current_minute == 0 or current_minute == 30:
        root.configure(background="blue")
        root.after(3000, lambda: root.configure(background="white"))
    root.after(60000, flash_gui)

def toggle_background_color():
    current_bg_color = root.cget("background")
    if current_bg_color == "white":
        root.configure(background="green")
    else:
        root.configure(background="white")
    root.after(100, toggle_background_color)

# Create a button to toggle the "always on top" feature
always_on_top_button = tk.Button(root, text="Enable Always on Top", command=toggle_always_on_top)
always_on_top_button.grid(row=row+3, column=0, columnspan=3, padx=10, pady=10)

# Start updating the clock labels and countdown labels
update_clocks()

# Run the Tkinter event loop
root.mainloop()
