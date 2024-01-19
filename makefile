# create executable using pyinstaller 

make: 
	pyinstaller --onefile --windowed --icon=chart.ico --name=ChartMonitor --noconfirm main.py
