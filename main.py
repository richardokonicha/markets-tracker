import datetime
import pytz
import tkinter as tk
from tkinter import ttk
import requests
from twelvedata import TDClient
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define API keys and URLs
# TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY')
TWELVE_DATA_API_KEY="11867f060b4248c0b45e281f9a1bd852"
BITCOIN_PRICE_URL = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"

class MarketsTrackerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("MarketsTracker")
        root.geometry('1000x800')
        root.iconbitmap('chart.ico')
        self.timezones = {
            "New York": "America/New_York",
            "London": "Europe/London",
            "Tokyo": "Asia/Tokyo",
            "Hong Kong": "Asia/Hong_Kong",
            "Sydney": "Australia/Sydney",
            "Paris": "Europe/Paris",
            "Los Angeles": "America/Los_Angeles",
            "Dubai": "Asia/Dubai"
        }
        # root.resizable(False, False)
        self.check_api_key()
        self.setup_ui()
        self.master.after(1000, self.update_all)

    def check_api_key(self):
        if TWELVE_DATA_API_KEY is None:
            raise ValueError("Please set the TWELVE_DATA_API_KEY environment variable.")

    def setup_ui(self):
        self.create_always_on_top_toggle(row=0, column=0)
        self.create_timezones(row=1, column=0)
        self.create_local_time_label(row=len(self.timezones)+2, column=0)
        self.create_bitcoin_price_label(row=len(self.timezones)+3, column=0)
        self.create_city_dropdown(row=len(self.timezones)+4, column=0)
        self.create_chart_frame(row=1, column=12)
        self.create_etf_buttons(row=len(self.timezones)+2, column=14)

    def create_timezones(self, row=0, column=0):
        self.clock_labels = {}
        self.countdown_labels = {}
        self.timezones = {
            "New York": "America/New_York",
            "London": "Europe/London",
            "Tokyo": "Asia/Tokyo",
            "Hong Kong": "Asia/Hong_Kong",
            "Sydney": "Australia/Sydney",
            "Paris": "Europe/Paris",
            "Los Angeles": "America/Los_Angeles",
            "Dubai": "Asia/Dubai"
        }
        self.target_time = datetime.time(8, 0, 0)
        row = 1
            
        for city in self.timezones.keys():
            # Label for City Name
            label = tk.Label(self.master, text=city, font=("Arial", 16, "bold"))
            label.grid(row=row, column=0, padx=(10, 2), pady=5, sticky='w')

            # Clock Label
            clock_label = tk.Label(self.master, text="", font=("Arial", 14, "bold"))
            clock_label.grid(row=row, column=1, padx=2, pady=5)
            self.clock_labels[city] = clock_label

            # Countdown Label
            countdown_label = tk.Label(self.master, text="", font=("Arial", 14, "bold"))
            countdown_label.grid(row=row, column=2, padx=2, pady=5)
            self.countdown_labels[city] = countdown_label

            row += 1

    def create_city_dropdown(self, row=0, column=0):
        self.city_combo = ttk.Combobox(self.master, values=list(self.timezones.keys()), state="readonly")
        self.city_combo.grid(row=row, column=column, columnspan=3, padx=10, pady=10, sticky='w')
        self.city_combo.current(0)

    def create_local_time_label(self,row=8, column=0):
        self.local_time_label = tk.Label(self.master, text="Local Time: ", font=("Arial", 16))
        self.local_time_label.grid(row=row, column=column, columnspan=3, padx=10, pady=10, sticky='w')

    def create_bitcoin_price_label(self, row=8, column=0):
        self.bitcoin_price_label = tk.Label(self.master, text="Bitcoin Price: ", font=("Arial", 16))
        self.bitcoin_price_label.grid(row=row, column=column, columnspan=3, padx=10, pady=10, sticky='w')

    def create_always_on_top_toggle(self, row=0, column=0):
        self.always_on_top_button = tk.Button(self.master, text="Enable Always on Top", command=self.toggle_always_on_top)
        self.always_on_top_button.grid(row=row, column=column, columnspan=3, padx=10, pady=10)

    def toggle_always_on_top(self):
        topmost = not self.master.attributes("-topmost")
        self.always_on_top_button.config(text="Disable Always on Top" if topmost else "Enable Always on Top")
        self.master.attributes("-topmost", topmost)
            
    def create_chart_frame(self, row=0, column=0, left_margin=40):
        self.chart_frame = tk.Frame(self.master)
        self.chart_frame.grid(row=row, column=column, rowspan=len(self.timezones)+1, columnspan=6, sticky='nsew', padx=(left_margin, 10), pady=10)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().grid(row=row, column=column, rowspan=len(self.timezones)+1, columnspan=6, sticky='nsew')

    def update_etf_chart(self, symbol):
        data = self.get_etf_data(symbol)
        self.fig.clf()
        if data:
            times = [point['datetime'] for point in data]
            values = [point['close'] for point in data]
            ax = self.fig.add_subplot(111)
            ax.plot(times, values, label=symbol)
            ax.set_xlabel('Time')
            ax.set_ylabel('Closing Price')
            ax.set_title(f'{symbol} Price Chart')
            ax.legend()
            self.canvas.draw()

    def get_etf_data(self, symbol):
        try:
            client = TDClient(apikey=TWELVE_DATA_API_KEY)
            response = client.time_series(
                symbol=symbol,
                interval="1min",
                outputsize=30
            )
            data = response.as_json()
            return data
        except Exception as e:
            print(f"Error fetching ETF data for {symbol}: {str(e)}")
            return []

    def update_clocks(self):
        current_datetime = datetime.datetime.now(pytz.utc)
        for city, timezone in self.timezones.items():
            tz = pytz.timezone(timezone)
            current_time = current_datetime.astimezone(tz)
            self.clock_labels[city].config(text=current_time.strftime("%H:%M:%S"))
            target_datetime = datetime.datetime.combine(current_datetime, self.target_time).astimezone(tz)
            if current_time.time() > self.target_time:
                target_datetime += datetime.timedelta(days=1)
            remaining_time = int((target_datetime - current_time).total_seconds())
            countdown_text = f"{remaining_time//3600:02d}:{(remaining_time%3600)//60:02d}:{remaining_time%60:02d}"
            self.countdown_labels[city].config(text=countdown_text if remaining_time > 0 else "")

    def update_bitcoin_price(self):
        try:
            response = requests.get(BITCOIN_PRICE_URL)
            data = response.json()
            price = data['bpi']['USD']['rate']
            self.bitcoin_price_label.config(text=f"Bitcoin Price: {price}")
        except Exception as e:
            self.bitcoin_price_label.config(text="Bitcoin Price: Error")
            print("Error fetching Bitcoin price:", str(e))


    def create_etf_buttons(self, row=1, column=12, max_frame_width=300):
        self.etf_symbols = ['IBIT', 'FBTC', 'BITB', 'ARKB', 'EZBC', 'BTCO', 'Other1', 'Other2']
        self.etf_buttons = {}

        button_frame = tk.Frame(self.master, width=max_frame_width)
        button_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        # Configure three columns with equal weight
        for i in range(3):
            button_frame.columnconfigure(i, weight=1)

        # Calculate the number of rows needed
        num_rows = (len(self.etf_symbols) + 2) // 3

        for i, symbol in enumerate(self.etf_symbols):
            # Calculate row and column for the button
            button_row = i // 3
            button_column = i % 3

            button = tk.Button(button_frame, text=f"{symbol} Price", font=("Arial", 12),
                               command=lambda s=symbol: self.update_etf_chart(s), width=15)
            button.grid(row=button_row, column=button_column, padx=5, pady=5, sticky="nsew")
            self.etf_buttons[symbol] = button

            # Add label for percentage change
            pct_change_label = tk.Label(button_frame, text="", font=("Arial", 10))
            pct_change_label.grid(row=button_row + 1, column=button_column, padx=5, pady=5, sticky="nsew")
            self.etf_buttons[f"{symbol}_pct_change"] = pct_change_label

        # Center the grid within the frame
        for i in range(3):
            button_frame.grid_columnconfigure(i, weight=1)

        # Set uniform weight for each row
        for i in range(num_rows):
            button_frame.grid_rowconfigure(i, weight=1)

    def update_all(self):
        self.update_clocks()
        self.update_bitcoin_price()
        self.update_etf_prices_and_changes()
        self.master.after(5000, self.update_all)

    def update_etf_prices_and_changes(self):
        for symbol in self.etf_symbols:
            data = self.get_etf_data(symbol)
            if data:
                # Convert prices to float to ensure they are numeric
                current_price = float(data[-1]['close'])
                previous_price = float(data[-2]['close'])

                # Calculate percentage change
                pct_change = ((current_price - previous_price) / previous_price) * 100

                # Update labels with formatted values
                self.etf_buttons[f"{symbol}_pct_change"].config(text=f"% Change: {pct_change:.2f}%")
                self.etf_buttons[symbol].config(text=f"{symbol} Price\n{current_price:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MarketsTrackerApp(root)
    root.mainloop()