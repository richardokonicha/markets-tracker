## Chart Monitor

This application provides real-time updates on Bitcoin price and prices of various ETFs (Exchange-Traded Funds). It uses the Python Tkinter library for its graphical user interface, and PyInstaller for creating a stand-alone executable.

### Makefile
The Makefile makes use of PyInstaller. When run, it generates a single executable file named "ChartMonitor". Here are the options used:
- `--onefile`: Creates one bundle as an executable.
- `--windowed`: Prevents a console window from being displayed when the application is run.
- `--icon`: Sets the icon of the application.
- `--name`: Sets the name of the executable.

### Usage

1. Clone/download the repo.
2. Navigate to the cloned directory.
3. Run `make`
4. Run the generated executable in the `dist` folder.

This creates an executable named "ChartMonitor". The application shows the current time and Bitcoin price. For each of the displayed ETFs, prices can be fetched by clicking the associated button.

**Note:** The application needs an active internet connection to fetch current prices.

## Main Python File (main.py)

The main Python file (main.py) is responsible for creating the application user interface and handling the interactions. It uses the `Tkinter` library for creating the user interface and the `requests` library to fetch the latest Bitcoin and ETFs prices from the internet.

The application displays the current time, updated every second.

The Bitcoin price is fetched and displayed, with updates happening every 5 seconds.

Various ETFs are displayed as buttons. Clicking on an ETF button triggers a fetch for the current price and price changes for that ETF, which are then displayed.

The main application runs in an infinite loop, waiting for user interactions and updating the various components as necessary.
