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
TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY')
BITCOIN_PRICE_URL = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"

class MarketsTrackerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("MarketsTracker")
        self.check_api_key()
        self.setup_ui()
        self.master.after(1000, self.update_all)

    def check_api_key(self):
        if TWELVE_DATA_API_KEY is None:
            raise ValueError("Please set the TWELVE_DATA_API_KEY environment variable.")

    def setup_ui(self):
        self.create_timezones()
        self.create_city_dropdown()
        self.create_local_time_label()
        self.create_bitcoin_price_label()
        self.create_always_on_top_toggle()
        self.create_etf_buttons()

    def create_timezones(self):
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
        row = 0
        for city in self.timezones.keys():
            label = tk.Label(self.master, text=city, font=("Arial", 24))
            label.grid(row=row, column=0, padx=10, pady=10)

            clock_label = tk.Label(self.master, text="", font=("Arial", 24, "bold"))
            clock_label.grid(row=row, column=1, padx=10, pady=10)
            self.clock_labels[city] = clock_label

            countdown_label = tk.Label(self.master, text="", font=("Arial", 24, "bold"))
            countdown_label.grid(row=row, column=2, padx=10, pady=10)
            self.countdown_labels[city] = countdown_label
            row += 1

    def create_city_dropdown(self):
        self.city_combo = ttk.Combobox(self.master, values=list(self.timezones.keys()), state="readonly")
        self.city_combo.grid(row=7, column=0, columnspan=3, padx=10, pady=10)
        self.city_combo.current(0)

    def create_local_time_label(self):
        self.local_time_label = tk.Label(self.master, text="Local Time: ", font=("Arial", 16))
        self.local_time_label.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

    def create_bitcoin_price_label(self):
        self.bitcoin_price_label = tk.Label(self.master, text="Bitcoin Price: ", font=("Arial", 16))
        self.bitcoin_price_label.grid(row=9, column=0, columnspan=3, padx=10, pady=10)

    def create_always_on_top_toggle(self):
        self.always_on_top_button = tk.Button(self.master, text="Enable Always on Top", command=self.toggle_always_on_top)
        self.always_on_top_button.grid(row=10, column=0, columnspan=3, padx=10, pady=10)

    def toggle_always_on_top(self):
        topmost = not self.master.attributes("-topmost")
        self.always_on_top_button.config(text="Disable Always on Top" if topmost else "Enable Always on Top")
        self.master.attributes("-topmost", topmost)

    def create_etf_buttons(self):
        self.etf_symbols = ['IBIT', 'FBTC', 'BITB', 'ARKB', 'EZBC', 'BTCO', 'Other1', 'Other2']
        self.etf_buttons = {}
        row = 6
        for i, symbol in enumerate(self.etf_symbols):
            button = tk.Button(self.master, text=f"{symbol} Price", font=("Arial", 16),
                               command=lambda s=symbol: self.update_etf_chart(s))
            button.grid(row=row+int(i/4), column=i % 4, padx=5, pady=5, sticky="ew")
            self.etf_buttons[symbol] = button

        self.chart_frame = tk.Frame(self.master)
        self.chart_frame.grid(row=row+2, column=0, columnspan=4, sticky='nsew', padx=10, pady=10)
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame) 
        self.canvas.get_tk_widget().grid(row=row+3, column=0, columnspan=4, sticky='nsew')

    def update_all(self):
        self.update_clocks()
        self.update_bitcoin_price()
        self.master.after(1000, self.update_all)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = MarketsTrackerApp(root)
    root.mainloop()