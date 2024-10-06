import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
import requests

# OpenWeatherMap API Key (replace 'your_api_key' with your actual API key)
API_KEY = 'your_openweathermap_api_key'
CITY = 'your_city'


# Function to get real-time temperature from OpenWeatherMap API
def get_real_time_temperature():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['main']['temp']
    else:
        return None


# Simulated historical data (or real data from smart meter systems can be used)
data = {
    'temperature': [30, 22, 28, 25, 35, 19, 15, 40, 30, 33],
    'consumption': [220, 180, 210, 195, 240, 170, 160, 260, 230, 250],
    'time_of_day': [10, 8, 9, 12, 6, 8, 5, 15, 10, 13],
    'day_of_week': [1, 2, 3, 4, 5, 6, 7, 1, 2, 3],
}

df = pd.DataFrame(data)

# Training the Linear Regression model
X = df[['temperature', 'time_of_day', 'day_of_week']]
y = df['consumption']
model = LinearRegression()
model.fit(X, y)


# Function to generate energy plan based on user inputs
def generate_energy_plan(temperature, time_of_day, day_of_week):
    user_input = np.array([[temperature, time_of_day, day_of_week]])
    predicted_consumption = model.predict(user_input)

    if predicted_consumption < 180:
        recommendation = "Your energy usage is efficient. Maintain your current settings."
    elif 180 <= predicted_consumption < 230:
        recommendation = "Consider reducing energy usage by limiting appliance use."
    else:
        recommendation = "High energy usage! Shift non-essential appliances to off-peak hours."

    return predicted_consumption[0], recommendation


# Function to show graph
def show_graph(prediction):
    temperatures = df['temperature']
    consumptions = df['consumption']

    plt.figure(figsize=(10, 6))
    plt.plot(temperatures, consumptions, label="Historical Consumption", color='green', linewidth=2)
    plt.scatter([float(entry_temperature.get())], [prediction], color='pink', label="Predicted Consumption", s=100)
    plt.xlabel("Temperature (Celsius)")
    plt.ylabel("Energy Consumption (kWh)")
    plt.title("Energy Consumption vs. Temperature")
    plt.grid(True)
    plt.legend()
    plt.show()


# Function for handling user input
def on_submit():
    try:
        temperature = float(entry_temperature.get())
        time_of_day = int(entry_time.get())
        day_of_week = int(entry_day.get())

        consumption, recommendation = generate_energy_plan(temperature, time_of_day, day_of_week)
        result_text.set(f"Predicted Consumption: {consumption:.2f} kWh\nRecommendation: {recommendation}")
        show_graph(consumption)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")


# Setting up the GUI with Tkinter
app = tk.Tk()
app.title("Smart Energy Optimizer")
app.geometry("1000x700")  # Fullscreen for hackathon
app.configure(bg='#f0f0f5')

# Header
header = tk.Label(app, text="AI-Driven Smart Energy Optimizer", font=('Helvetica', 26, 'bold'), bg='#f0f0f5',
                  fg='darkblue')
header.pack(pady=20)

# Real-time temperature display
temperature_label = tk.Label(app, text="Fetching real-time temperature...", font=('Arial', 14), bg='#f0f0f5')
temperature_label.pack()

# Input Section
input_frame = tk.Frame(app, bg='#f0f0f5')
input_frame.pack(pady=10)

tk.Label(input_frame, text="Current Temperature (°C):", font=('Arial', 14), bg='#f0f0f5').grid(row=0, column=0, padx=10,
                                                                                               pady=10, sticky='e')
entry_temperature = tk.Entry(input_frame, font=('Arial', 14))
entry_temperature.grid(row=0, column=1, padx=10, pady=10)

tk.Label(input_frame, text="Time of Day (0-23):", font=('Arial', 14), bg='#f0f0f5').grid(row=1, column=0, padx=10,
                                                                                         pady=10, sticky='e')
entry_time = tk.Entry(input_frame, font=('Arial', 14))
entry_time.grid(row=1, column=1, padx=10, pady=10)

tk.Label(input_frame, text="Day of Week (1=Monday, 7=Sunday):", font=('Arial', 14), bg='#f0f0f5').grid(row=2, column=0,
                                                                                                       padx=10, pady=10,
                                                                                                       sticky='e')
entry_day = tk.Entry(input_frame, font=('Arial', 14))
entry_day.grid(row=2, column=1, padx=10, pady=10)

# Submit Button
submit_button = tk.Button(app, text="Generate Energy Plan", font=('Arial', 14, 'bold'), bg='#4CAF50', fg='white',
                          command=on_submit)
submit_button.pack(pady=20)

# Result Display
result_text = tk.StringVar()
result_label = tk.Label(app, textvariable=result_text, font=('Arial', 14), bg='#f0f0f5', fg='black')
result_label.pack(pady=20)


# Run real-time temperature fetching
def update_temperature():
    temp = get_real_time_temperature()
    if temp:
        temperature_label.config(text=f"Current Temperature in {CITY}: {temp}°C")
    else:
        temperature_label.config(text="Unable to fetch real-time temperature.")
    app.after(60000, update_temperature)  # Update every minute


update_temperature()

app.mainloop()
