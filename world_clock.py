import datetime
import pytz
import tkinter as tk
from tkinter import ttk
import requests
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
from dotenv import load_dotenv
from twelvedata import TDClient

# Ensure environment variables are loaded
load_dotenv()


TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY')
BITCOIN_PRICE_URL = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"


class MarketsTrackerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("MarketsTracker")
        self.master.geometry('800x600+50+50')
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
        self.check_api_key()
        self.etf_symbols = ['IBIT', 'FBTC', 'BITB', 'ARKB', 'EZBC', 'BTCO', 'Other1', 'Other2']
        self.etf_buttons = {}
        self.etf_change_labels = {}
        self.previous_etf_prices = {}
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
        self.target_time = datetime.time(8, 0, 0)
        row = 1
            
        for city, timezone in self.timezones.items():
            label = tk.Label(self.master, text=city, font=("Arial", 16, "bold"))
            label.grid(row=row, column=0, padx=(10, 2), pady=5, sticky='w')

            clock_label = tk.Label(self.master, text="", font=("Arial", 14, "bold"))
            clock_label.grid(row=row, column=1, padx=2, pady=5)
            self.clock_labels[city] = clock_label

            countdown_label = tk.Label(self.master, text="", font=("Arial", 14, "bold"))
            countdown_label.grid(row=row, column=2, padx=2, pady=5)
            self.countdown_labels[city] = countdown_label

            row += 1

    def create_city_dropdown(self, row=0, column=0):
        self.city_combo = ttk.Combobox(self.master, values=list(self.timezones.keys()), state="readonly")
        self.city_combo.grid(row=row, column=column, columnspan=3, padx=10, pady=10, sticky='w')
        self.city_combo.current(0)

    def create_local_time_label(self, row=8, column=0):
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

    def create_etf_buttons(self, row, column, max_frame_width=300):
        button_frame = tk.Frame(self.master, width=max_frame_width)
        button_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        for i in range(3):
            button_frame.columnconfigure(i, weight=1)
        num_rows = (len(self.etf_symbols) + 2) // 3

        for i, symbol in enumerate(self.etf_symbols):
            button_row = i // 3
            button_column = i % 3
            button = tk.Button(button_frame, text=f"{symbol} Price", font=("Arial", 12),
                               command=lambda s=symbol: self.update_etf_chart(s), width=15)
            button.grid(row=button_row, column=button_column, padx=5, pady=5, sticky="nsew")
            self.etf_buttons[symbol] = button

            change_label = tk.Label(button_frame, text="", font=("Arial", 9))
            change_label.grid(row=button_row + 1, column=button_column, padx=5, pady=1)
            self.etf_change_labels[symbol] = change_label

        for i in range(num_rows):
            button_frame.grid_rowconfigure(i, weight=1)

    def create_chart_frame(self, row, column, left_margin=40):
        self.chart_frame = tk.Frame(self.master)
        self.chart_frame.grid(row=row, column=column, rowspan=len(self.timezones)+1, columnspan=6, sticky='nsew', padx=(left_margin, 10), pady=10)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().grid(row=row, column=column, rowspan=len(self.timezones)+1, columnspan=6, sticky='nsew')

    def update_all(self):
        self.update_clocks()
        self.update_bitcoin_price()
        self.master.after(1000, self.update_all)

    # def update_etf_chart(self, symbol):
    #     data = self.get_etf_data(symbol)
    #     self.fig.clf()

    #     if data:
    #         times = [datetime.datetime.strptime(point['datetime'], '%Y-%m-%dT%H:%M:%S%z') for point in data]
    #         values = [float(point['close']) for point in data]

    #         if symbol not in self.previous_etf_prices:
    #             self.previous_etf_prices[symbol] = values[0]

    #         percent_change = ((values[-1] - self.previous_etf_prices[symbol]) / self.previous_etf_prices[symbol]) * 100
    #         self.etf_change_labels[symbol].config(text=f"{percent_change:+.2f}%")
    #         self.previous_etf_prices[symbol] = values[-1]

    #         ax = self.fig.add_subplot(111)
    #         ax.plot(times, values, label=symbol)
    #         ax.set_xlabel('Time')
    #         ax.set_ylabel('Price USD')
    #         ax.legend()
    #         ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    #         ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    #         self.fig.autofmt_xdate()
    #     else:
    #         ax = self.fig.add_subplot(111)
    #         ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

    #     self.canvas.draw()

    def update_etf_chart(self, symbol):
        data = self.get_etf_data(symbol)
        self.fig.clf()

        if data:
            # Adjust the strptime format to match the data being read
            times = [datetime.datetime.strptime(point['datetime'], '%Y-%m-%d %H:%M:%S') for point in data]
            values = [float(point['close']) for point in data]

            if symbol not in self.previous_etf_prices:
                self.previous_etf_prices[symbol] = values[0]

            percent_change = ((values[-1] - self.previous_etf_prices[symbol]) / self.previous_etf_prices[symbol]) * 100
            self.etf_change_labels[symbol].config(text=f"{percent_change:+.2f}%")
            self.previous_etf_prices[symbol] = values[-1]

            ax = self.fig.add_subplot(111)
            ax.plot(times, values, label=symbol)
            ax.set_xlabel('Time')
            ax.set_ylabel('Price USD')
            ax.legend()
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
            self.fig.autofmt_xdate()
        else:
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

        self.canvas.draw()

        def get_etf_data(self, symbol):
            try:
                td = TDClient(apikey=TWELVE_DATA_API_KEY)
                ts = td.time_series(symbol=symbol, interval="1min", outputsize=5, timezone="America/New_York").as_json()
                return ts
            except Exception as e:
                print(f"Error fetching ETF data for {symbol}: {str(e)}")
                return None

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
            print("Error fetching Bitcoin price:", str(e))
            self.bitcoin_price_label.config(text="Bitcoin Price: Error fetching data")


if __name__ == "__main__":
    root = tk.Tk()
    app = MarketsTrackerApp(root)
    root.mainloop()