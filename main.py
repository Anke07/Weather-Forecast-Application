"""A simple desktop weather forecast application built with Tkinter."""

import threading
import tkinter as tk
from tkinter import messagebox, ttk

import requests

from weather_service import WeatherService, WeatherServiceError, weather_description


class WeatherApp:
    BACKGROUND = "#eef4f8"
    CARD = "#ffffff"
    PRIMARY = "#176b87"
    TEXT = "#18323f"
    MUTED = "#607985"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Weather Forecast")
        self.root.geometry("760x690")
        self.root.minsize(650, 620)
        self.root.configure(bg=self.BACKGROUND)
        self.service = WeatherService()
        self._build_interface()

    def _build_interface(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(14, 9))
        style.configure("TEntry", font=("Segoe UI", 12), padding=8)

        header = tk.Frame(self.root, bg=self.BACKGROUND)
        header.pack(fill="x", padx=34, pady=(26, 12))
        tk.Label(header, text="Weather Forecast", font=("Segoe UI", 25, "bold"),
                 bg=self.BACKGROUND, fg=self.TEXT).pack(anchor="w")
        tk.Label(header, text="Check current conditions and the 5-day outlook",
                 font=("Segoe UI", 10), bg=self.BACKGROUND, fg=self.MUTED).pack(anchor="w", pady=(4, 0))

        search = tk.Frame(self.root, bg=self.BACKGROUND)
        search.pack(fill="x", padx=34, pady=12)
        self.city_entry = ttk.Entry(search)
        self.city_entry.pack(side="left", fill="x", expand=True)
        self.city_entry.insert(0, "Hyderabad")
        self.city_entry.bind("<Return>", lambda _event: self.search_weather())
        self.search_button = ttk.Button(search, text="Get Weather", command=self.search_weather)
        self.search_button.pack(side="left", padx=(10, 0))

        self.status_label = tk.Label(self.root, text="Enter a city to get started.",
                                     font=("Segoe UI", 9), bg=self.BACKGROUND, fg=self.MUTED)
        self.status_label.pack(anchor="w", padx=36, pady=(0, 8))

        self.current_card = tk.Frame(self.root, bg=self.CARD, highlightthickness=1,
                                     highlightbackground="#dce7ed")
        self.current_card.pack(fill="x", padx=34, pady=8)
        self.location_label = tk.Label(self.current_card, text="Current weather",
                                       font=("Segoe UI", 16, "bold"), bg=self.CARD, fg=self.TEXT)
        self.location_label.pack(anchor="w", padx=22, pady=(18, 2))
        self.updated_label = tk.Label(self.current_card, text="", font=("Segoe UI", 9),
                                      bg=self.CARD, fg=self.MUTED)
        self.updated_label.pack(anchor="w", padx=22)

        current_row = tk.Frame(self.current_card, bg=self.CARD)
        current_row.pack(fill="x", padx=22, pady=18)
        self.temperature_label = tk.Label(current_row, text="--°", font=("Segoe UI", 42, "bold"),
                                           bg=self.CARD, fg=self.PRIMARY)
        self.temperature_label.pack(side="left", padx=(0, 28))
        self.condition_label = tk.Label(current_row, text="Search for a city",
                                         font=("Segoe UI", 15), bg=self.CARD, fg=self.TEXT,
                                         justify="left")
        self.condition_label.pack(side="left", anchor="center")

        metrics = tk.Frame(self.current_card, bg=self.CARD)
        metrics.pack(fill="x", padx=22, pady=(0, 20))
        self.humidity_label = self._metric(metrics, "Humidity", "--%")
        self.wind_label = self._metric(metrics, "Wind speed", "-- km/h")
        self.feels_label = self._metric(metrics, "Feels like", "--°")

        forecast_header = tk.Label(self.root, text="5-Day Forecast", font=("Segoe UI", 16, "bold"),
                                   bg=self.BACKGROUND, fg=self.TEXT)
        forecast_header.pack(anchor="w", padx=36, pady=(20, 10))
        self.forecast_frame = tk.Frame(self.root, bg=self.BACKGROUND)
        self.forecast_frame.pack(fill="both", expand=True, padx=34, pady=(0, 20))
        self._show_empty_forecast()

        footer = tk.Label(self.root, text="Weather data provided by Open-Meteo",
                          font=("Segoe UI", 8), bg=self.BACKGROUND, fg=self.MUTED)
        footer.pack(pady=(0, 12))

    def _metric(self, parent: tk.Widget, title: str, value: str) -> tk.Label:
        block = tk.Frame(parent, bg="#f3f8fa", padx=14, pady=10)
        block.pack(side="left", fill="x", expand=True, padx=(0, 9))
        tk.Label(block, text=title, font=("Segoe UI", 9), bg="#f3f8fa", fg=self.MUTED).pack(anchor="w")
        label = tk.Label(block, text=value, font=("Segoe UI", 13, "bold"), bg="#f3f8fa", fg=self.TEXT)
        label.pack(anchor="w", pady=(4, 0))
        return label

    def _show_empty_forecast(self) -> None:
        for child in self.forecast_frame.winfo_children():
            child.destroy()
        tk.Label(self.forecast_frame, text="Your daily forecast will appear here.",
                 font=("Segoe UI", 10), bg=self.BACKGROUND, fg=self.MUTED).pack(anchor="w")

    def search_weather(self) -> None:
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("City required", "Please enter a city name.")
            self.city_entry.focus_set()
            return
        self.search_button.configure(state="disabled")
        self.status_label.configure(text=f"Fetching weather for {city}...")
        threading.Thread(target=self._fetch_weather, args=(city,), daemon=True).start()

    def _fetch_weather(self, city: str) -> None:
        try:
            data = self.service.get_weather(city)
            self.root.after(0, lambda: self._display_weather(data))
        except WeatherServiceError as error:
            self.root.after(0, lambda: self._show_error(str(error)))
        except requests.RequestException:
            self.root.after(0, lambda: self._show_error("Could not connect to the weather service. Check your internet connection."))
        except Exception as error:  # Keep unexpected failures from freezing the interface.
            self.root.after(0, lambda: self._show_error(f"Something went wrong: {error}"))

    def _display_weather(self, data: dict) -> None:
        current = data["current"]
        place = data["location"]
        description, symbol = weather_description(current["weather_code"])
        self.location_label.configure(text=f"{place['name']}, {place.get('admin1') or place['country']}")
        self.updated_label.configure(text=f"Local time: {current['time'].replace('T', ' ')}")
        self.temperature_label.configure(text=f"{round(current['temperature_2m'])}°C")
        self.condition_label.configure(text=f"{symbol}  {description}\nFeels like {round(current['apparent_temperature'])}°C")
        self.humidity_label.configure(text=f"{current['relative_humidity_2m']}%")
        self.wind_label.configure(text=f"{current['wind_speed_10m']} km/h")
        self.feels_label.configure(text=f"{round(current['apparent_temperature'])}°C")
        self.status_label.configure(text="Weather updated successfully.")
        self._display_forecast(data["daily"])
        self.search_button.configure(state="normal")

    def _display_forecast(self, daily: dict) -> None:
        for child in self.forecast_frame.winfo_children():
            child.destroy()
        for index, date in enumerate(daily["time"]):
            description, symbol = weather_description(daily["weather_code"][index])
            day_card = tk.Frame(self.forecast_frame, bg=self.CARD, highlightthickness=1,
                                highlightbackground="#dce7ed", padx=10, pady=13)
            day_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
            day_name = date
            try:
                from datetime import date as date_type
                day_name = date_type.fromisoformat(date).strftime("%a")
            except ValueError:
                pass
            tk.Label(day_card, text=day_name, font=("Segoe UI", 10, "bold"),
                     bg=self.CARD, fg=self.TEXT).pack(pady=(0, 9))
            tk.Label(day_card, text=symbol, font=("Segoe UI", 20), bg=self.CARD).pack()
            tk.Label(day_card, text=description, font=("Segoe UI", 8), bg=self.CARD,
                     fg=self.MUTED, wraplength=90, justify="center").pack(pady=7)
            tk.Label(day_card, text=f"{round(daily['temperature_2m_max'][index])}° / "
                                    f"{round(daily['temperature_2m_min'][index])}°",
                     font=("Segoe UI", 10, "bold"), bg=self.CARD, fg=self.PRIMARY).pack()

    def _show_error(self, message: str) -> None:
        self.status_label.configure(text="Weather could not be loaded.")
        self.search_button.configure(state="normal")
        messagebox.showerror("Weather lookup failed", message)


def main() -> None:
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
