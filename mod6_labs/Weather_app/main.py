"""Weather Application using Flet v0.28.3 with Search History and Temperature Unit Toggle"""

import flet as ft
from weather_service import WeatherService
from config import Config
import json
from pathlib import Path
from weather_service import WeatherServiceError
import asyncio
from datetime import datetime


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.history_file = Path("search_history.json")
        self.preferences_file = Path("user_preferences.json")
        self.favorites_file = Path("favorite_cities.json")
        self.search_history = self.load_history()
        self.preferences = self.load_preferences()
        self.favorite_cities = self.load_favorites()
        self.use_fahrenheit = self.preferences.get('use_fahrenheit', False)
        self.current_weather_data = None
        self.current_city_name = None
        self.setup_page()
        self.build_ui()

    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
        
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO
        
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()


    def get_weather_background_color(self, weather_id: int, icon_code: str) -> str:
        """Determine background color based on weather condition."""
        is_night = icon_code.endswith('n')
        
        if is_night:
            return ft.Colors.INDIGO_900
        
        if 200 <= weather_id < 300:
            return ft.Colors.GREY_800
        elif 300 <= weather_id < 600:
            return ft.Colors.BLUE_700
        elif 600 <= weather_id < 700:
            return ft.Colors.LIGHT_BLUE_100
        elif 700 <= weather_id < 800:
            return ft.Colors.GREY_400
        elif weather_id == 800:
            return ft.Colors.AMBER_400
        elif weather_id == 801:
            return ft.Colors.LIGHT_BLUE_300
        elif 802 <= weather_id <= 804:
            return ft.Colors.BLUE_GREY_300
        
        return ft.Colors.BLUE_400


    def get_text_color_for_background(self, bg_color: str) -> str:
        """Return appropriate text color based on background brightness."""
        dark_backgrounds = [
            ft.Colors.INDIGO_900,
            ft.Colors.GREY_800,
            ft.Colors.BLUE_700,
        ]
        
        if bg_color in dark_backgrounds:
            return ft.Colors.WHITE
        
        return ft.Colors.BLACK


    def load_preferences(self):
        """Load user preferences from file."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    
    def save_preferences(self):
        """Save user preferences to file."""
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    
    def load_favorites(self):
        """Load favorite cities from file."""
        if self.favorites_file.exists():
            try:
                with open(self.favorites_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    
    def save_favorites(self):
        """Save favorite cities to file."""
        try:
            with open(self.favorites_file, 'w') as f:
                json.dump(self.favorite_cities, f, indent=2)
        except Exception as e:
            print(f"Error saving favorites: {e}")
    
    
    def is_favorite(self, city: str) -> bool:
        """Check if a city is in favorites."""
        return any(fav.lower() == city.lower() for fav in self.favorite_cities)
    
    
    def toggle_favorite(self, e):
        """Toggle current city as favorite."""
        if not self.current_city_name:
            return
        
        city = self.current_city_name
        
        if self.is_favorite(city):
            # Remove from favorites
            self.favorite_cities = [f for f in self.favorite_cities if f.lower() != city.lower()]
            self.favorite_button.icon = ft.Icons.STAR_BORDER
            self.favorite_button.tooltip = "Add to favorites"
        else:
            # Add to favorites
            self.favorite_cities.append(city)
            self.favorite_button.icon = ft.Icons.STAR
            self.favorite_button.tooltip = "Remove from favorites"
        
        self.save_favorites()
        self.update_favorites_display()
        self.page.update()
    
    
    def get_weather_tip(self, weather_data: dict) -> str:
        """Get a helpful tip based on weather conditions."""
        weather_id = weather_data.get("weather", [{}])[0].get("id", 800)
        temp = weather_data.get("main", {}).get("temp", 0)
        humidity = weather_data.get("main", {}).get("humidity", 0)
        
        # Rain conditions
        if 300 <= weather_id < 600:
            return "Don't forget your umbrella today! ☔"
        
        # Thunderstorm
        elif 200 <= weather_id < 300:
            return "Stay indoors if possible. Thunderstorm warning! ⚡"
        
        # Snow
        elif 600 <= weather_id < 700:
            return "Bundle up warm! Snow expected ❄️"
        
        # Hot weather
        elif temp > 30:
            return "Stay hydrated! It's hot out there! 💧"
        
        # Cold weather
        elif temp < 5:
            return "Dress warmly! It's quite cold today 🧥"
        
        # High humidity
        elif humidity > 80:
            return "High humidity today. Stay cool! 😌"
        
        # Clear/nice weather
        elif weather_id == 800:
            return "Perfect weather for outdoor activities! ☀️"
        
        # Cloudy
        elif 801 <= weather_id <= 804:
            return "Cloudy skies today. Bring a light jacket! ☁️"
        
        # Foggy/Misty
        elif 700 <= weather_id < 800:
            return "Visibility might be low. Drive safely! 🌫️"
        
        # Default
        return "Have a great day! Stay weather-aware! 🌤️"


    def celsius_to_fahrenheit(self, celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9/5) + 32
    
    
    def get_temp_display(self, celsius: float) -> str:
        """Get temperature display based on current unit preference."""
        if self.use_fahrenheit:
            return f"{self.celsius_to_fahrenheit(celsius):.1f}°F"
        return f"{celsius:.1f}°C"
    
    
    def get_temp_unit_symbol(self) -> str:
        """Get current temperature unit symbol."""
        return "°F" if self.use_fahrenheit else "°C"


    def toggle_temperature_unit(self, e):
        """Toggle between Celsius and Fahrenheit."""
        self.use_fahrenheit = not self.use_fahrenheit
        
        self.preferences['use_fahrenheit'] = self.use_fahrenheit
        self.save_preferences()
        
        if self.use_fahrenheit:
            self.temp_toggle.content.controls[0].value = "°F"
            self.temp_toggle.content.controls[0].color = ft.Colors.ORANGE_700
            self.temp_toggle.bgcolor = ft.Colors.ORANGE_100
        else:
            self.temp_toggle.content.controls[0].value = "°C"
            self.temp_toggle.content.controls[0].color = ft.Colors.BLUE_700
            self.temp_toggle.bgcolor = ft.Colors.BLUE_100
        
        if self.current_weather_data and self.weather_container.visible:
            # Schedule the async refresh
            async def refresh():
                await self.refresh_weather_display()
            
            self.page.run_task(refresh)
        
        self.page.update()


    def build_ui(self):
        """Build the user interface."""
        self.title = ft.Row(
            [
                ft.Icon(ft.Icons.CLOUD, size=40, color=ft.Colors.BLUE_700),
                ft.Text(
                    "Weather App",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_700,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
            icon_size=24,
        )
        
        self.temp_toggle = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "°F" if self.use_fahrenheit else "°C",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ORANGE_700 if self.use_fahrenheit else ft.Colors.BLUE_700,
                    ),
                    ft.Icon(
                        ft.Icons.THERMOSTAT,
                        size=20,
                        color=ft.Colors.ORANGE_700 if self.use_fahrenheit else ft.Colors.BLUE_700,
                    ),
                ],
                spacing=5,
            ),
            bgcolor=ft.Colors.ORANGE_100 if self.use_fahrenheit else ft.Colors.BLUE_100,
            border_radius=20,
            padding=10,
            tooltip="Toggle °C/°F",
            on_click=self.toggle_temperature_unit,
            ink=True,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
            expand=True,
        )
        
        self.search_button = ft.ElevatedButton(
            "Search",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
                padding=15,
            ),
            height=56,
        )
        
        # Refresh button (initially hidden)
        self.refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh weather data",
            icon_size=28,
            on_click=self.on_refresh,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_600,
            ),
            visible=False,
        )
        
        # Favorite button (initially hidden)
        self.favorite_button = ft.IconButton(
            icon=ft.Icons.STAR_BORDER,
            tooltip="Add to favorites",
            icon_size=28,
            on_click=self.toggle_favorite,
            style=ft.ButtonStyle(
                color=ft.Colors.AMBER_700,
            ),
            visible=False,
        )
        
        search_row = ft.Row(
            [
                self.city_input,
                self.search_button,
                self.refresh_button,
                self.favorite_button,
            ],
            spacing=10,
        )
        
        self.history_expanded = False
        self.expand_icon = ft.IconButton(
            icon=ft.Icons.EXPAND_MORE,
            tooltip="Show history",
            icon_size=20,
            on_click=self.toggle_history,
        )
        
        # Favorites Section
        self.favorites_expanded = False
        self.favorites_expand_icon = ft.IconButton(
            icon=ft.Icons.EXPAND_MORE,
            tooltip="Show favorites",
            icon_size=20,
            on_click=self.toggle_favorites,
        )
        
        self.favorites_header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.STAR, size=20, color=ft.Colors.AMBER_700),
                            ft.Text(
                                "Favorite Cities",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.AMBER_700,
                            ),
                        ],
                        spacing=8,
                    ),
                    self.favorites_expand_icon,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.AMBER),
            border_radius=10,
            padding=15,
            on_click=self.toggle_favorites,
            ink=True,
            visible=False,
        )
        
        self.favorites_list = ft.Column(spacing=8)
        
        self.favorites_dropdown = ft.Container(
            content=ft.Container(
                content=ft.Column(
                    [self.favorites_list],
                    scroll=ft.ScrollMode.AUTO,
                ),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.AMBER),
                border_radius=10,
                padding=15,
            ),
            visible=False,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            animate_opacity=300,
            opacity=0,
        )
        
        # Search History Section
        self.history_header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.HISTORY, size=20, color=ft.Colors.BLUE_700),
                            ft.Text(
                                "Recent Searches",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Clear history",
                                icon_size=20,
                                on_click=self.clear_history,
                            ),
                            self.expand_icon,
                        ],
                        spacing=0,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
            border_radius=10,
            padding=15,
            on_click=self.toggle_history,
            ink=True,
            visible=False,
        )
        
        self.history_list = ft.Column(spacing=8)
        
        self.history_dropdown = ft.Container(
            content=ft.Container(
                content=ft.Column(
                    [self.history_list],
                    scroll=ft.ScrollMode.AUTO,
                ),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
                border_radius=10,
                padding=15,
            ),
            visible=False,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            animate_opacity=300,
            opacity=0,
        )
        
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
            border_radius=15,
            padding=30,
            animate=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
        )
        
        # Weather tip container
        self.weather_tip = ft.Container(
            visible=False,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREEN),
            border_radius=10,
            padding=15,
            margin=ft.margin.only(top=10),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
            size=16,
        )
        
        self.loading = ft.ProgressRing(visible=False, width=40, height=40)
        
        self.info_message = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.INFO_OUTLINED, size=20, color=ft.Colors.BLUE_700),
                    ft.Text(
                        "Enter a city name and click Search to get weather information",
                        size=14,
                        color=ft.Colors.BLUE_700,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
            border_radius=10,
            padding=15,
            margin=ft.margin.only(top=20),
        )
        
        title_row = ft.Row(
            [
                self.title,
                ft.Row(
                    [
                        self.temp_toggle,
                        self.theme_button,
                    ],
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    search_row,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    self.favorites_header,
                    self.favorites_dropdown,
                    self.history_header,
                    self.history_dropdown,
                    self.loading,
                    self.error_message,
                    self.weather_container,
                    self.weather_tip,
                    self.info_message,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=10,
            )
        )
        
        self.update_history_display()
        self.update_favorites_display()


    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()


    def load_history(self):
        """Load search history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    
    def save_history(self):
        """Save search history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.search_history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    
    def add_to_history(self, city: str):
        """Add city to history."""
        self.search_history = [item for item in self.search_history 
                               if item.get('city', '').lower() != city.lower()]
        
        self.search_history.insert(0, {
            'city': city,
            'timestamp': datetime.now().isoformat()
        })
        
        self.search_history = self.search_history[:10]
        
        self.save_history()
        
        self.update_history_display()
    
    
    def toggle_history(self, e):
        """Toggle history dropdown visibility."""
        self.history_expanded = not self.history_expanded
        
        if self.history_expanded:
            self.expand_icon.icon = ft.Icons.EXPAND_LESS
            self.history_dropdown.visible = True
            self.history_dropdown.opacity = 1
        else:
            self.expand_icon.icon = ft.Icons.EXPAND_MORE
            self.history_dropdown.opacity = 0
            self.history_dropdown.visible = False
            
        self.page.update()
    
    
    def toggle_favorites(self, e):
        """Toggle favorites dropdown visibility."""
        self.favorites_expanded = not self.favorites_expanded
        
        if self.favorites_expanded:
            self.favorites_expand_icon.icon = ft.Icons.EXPAND_LESS
            self.favorites_dropdown.visible = True
            self.favorites_dropdown.opacity = 1
        else:
            self.favorites_expand_icon.icon = ft.Icons.EXPAND_MORE
            self.favorites_dropdown.opacity = 0
            self.favorites_dropdown.visible = False
            
        self.page.update()
    
    
    def update_history_display(self):
        """Update the history display with current history."""
        self.history_list.controls.clear()
        
        if not self.search_history:
            self.history_header.visible = False
            self.history_dropdown.visible = False
            self.page.update()
            return
        
        self.history_header.visible = True
        
        for item in self.search_history:
            city = item.get('city', '')
            timestamp = item.get('timestamp', '')
            
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%b %d, %I:%M %p")
            except:
                time_str = ""
            
            history_item = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.LOCATION_ON,
                            size=18,
                            color=ft.Colors.BLUE_600,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    city,
                                    size=15,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.Colors.BLUE_900,
                                ),
                                ft.Text(
                                    time_str,
                                    size=12,
                                    color=ft.Colors.GREY_600,
                                ) if time_str else ft.Container(),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=18,
                            tooltip="Remove from history",
                            on_click=lambda e, c=city: self.remove_from_history(c),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                padding=12,
                on_click=lambda e, c=city: self.search_from_history(c),
                ink=True,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            )
            
            self.history_list.controls.append(history_item)
        
        self.page.update()
    
    
    def update_favorites_display(self):
        """Update the favorites display with current favorites."""
        self.favorites_list.controls.clear()
        
        if not self.favorite_cities:
            self.favorites_header.visible = False
            self.favorites_dropdown.visible = False
            self.page.update()
            return
        
        self.favorites_header.visible = True
        
        for city in self.favorite_cities:
            favorite_item = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.STAR,
                            size=18,
                            color=ft.Colors.AMBER_600,
                        ),
                        ft.Text(
                            city,
                            size=15,
                            weight=ft.FontWeight.W_500,
                            color=ft.Colors.AMBER_900,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=18,
                            tooltip="Remove from favorites",
                            on_click=lambda e, c=city: self.remove_from_favorites(c),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=ft.Colors.AMBER_50,
                border_radius=10,
                padding=12,
                on_click=lambda e, c=city: self.search_from_history(c),
                ink=True,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            )
            
            self.favorites_list.controls.append(favorite_item)
        
        self.page.update()
    
    
    def remove_from_favorites(self, city: str):
        """Remove a city from favorites."""
        self.favorite_cities = [f for f in self.favorite_cities if f.lower() != city.lower()]
        self.save_favorites()
        self.update_favorites_display()
        
        # Update favorite button if this is the current city
        if self.current_city_name and self.current_city_name.lower() == city.lower():
            self.favorite_button.icon = ft.Icons.STAR_BORDER
            self.favorite_button.tooltip = "Add to favorites"
            self.page.update()
    
    
    def search_from_history(self, city: str):
        """Search weather for a city from history."""
        self.city_input.value = city
        self.page.update()
        
        # Schedule the async task
        async def search():
            await self.get_weather()
        
        self.page.run_task(search)
    
    
    def remove_from_history(self, city: str):
        """Remove a city from search history."""
        self.search_history = [item for item in self.search_history 
                               if item.get('city', '').lower() != city.lower()]
        self.save_history()
        self.update_history_display()
    
    
    def clear_history(self, e):
        """Clear all search history."""
        self.search_history = []
        self.save_history()
        self.update_history_display()
    
    
    def on_search(self, e):
        """Handle search button click."""
        # Wrap the async call in a proper coroutine
        async def search():
            await self.get_weather()
        
        self.page.run_task(search)
    
    
    def on_refresh(self, e):
        """Handle refresh button click."""
        # Re-fetch weather for the last searched city
        if self.current_weather_data:
            last_city = self.current_weather_data.get("name", "")
            if last_city:
                self.city_input.value = last_city
                self.page.update()
                
                # Show refreshing indicator
                self.refresh_button.icon = ft.Icons.HOURGLASS_BOTTOM
                self.refresh_button.disabled = True
                self.page.update()
                
                async def refresh():
                    await self.get_weather()
                    # Reset refresh button
                    self.refresh_button.icon = ft.Icons.REFRESH
                    self.refresh_button.disabled = False
                    self.page.update()
                
                self.page.run_task(refresh)


    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        if not city:
            self.show_error("Please enter a city name")
            return
        
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            weather_data = await self.weather_service.get_weather(city)
            
            self.current_weather_data = weather_data
            
            actual_city_name = weather_data.get("name", city)
            self.add_to_history(actual_city_name)
            
            # Show refresh button after successful search
            self.refresh_button.visible = True
            
            # Show and update favorite button
            self.favorite_button.visible = True
            self.current_city_name = actual_city_name
            if self.is_favorite(actual_city_name):
                self.favorite_button.icon = ft.Icons.STAR
                self.favorite_button.tooltip = "Remove from favorites"
            else:
                self.favorite_button.icon = ft.Icons.STAR_BORDER
                self.favorite_button.tooltip = "Add to favorites"
            
            await self.display_weather(weather_data)
        
        except WeatherServiceError as e:
            self.show_error(str(e))

        except Exception as e:
            self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    
    async def refresh_weather_display(self):
        """Refresh weather display with current temperature unit."""
        if self.current_weather_data:
            await self.display_weather(self.current_weather_data)
    
    
    async def display_weather(self, data: dict):
        """Display weather information."""
        self.info_message.visible = False
        
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp = data.get("main", {}).get("temp", 0)
        temp_max = data.get("main", {}).get("temp_max", 0)
        temp_min = data.get("main", {}).get("temp_min", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        pressure = data.get("main", {}).get("pressure", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        cloudiness = data.get("clouds", {}).get("all", 0)
        weather_id = data.get("weather", [{}])[0].get("id", 800)
        
        bg_color = self.get_weather_background_color(weather_id, icon_code)
        text_color = self.get_text_color_for_background(bg_color)
        
        self.weather_container.bgcolor = bg_color
        self.weather_container.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.LOCATION_ON, size=24, color=text_color),
                        ft.Text(
                            f"{city_name}, {country}",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=text_color,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                
                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                ft.Text(
                    description,
                    size=20,
                    italic=True,
                    color=text_color,
                ),
                
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                
                ft.Text(
                    self.get_temp_display(temp),
                    size=56,
                    weight=ft.FontWeight.BOLD,
                    color=text_color,
                ),
                
                ft.Column(
                    [
                        ft.Text(
                            f"Feels like {self.get_temp_display(feels_like)}",
                            size=16,
                            color=text_color,
                        ),
                        ft.Row(
                            [
                                ft.Text(
                                    f"↑ {self.get_temp_display(temp_max)}",
                                    size=14,
                                    color=ft.Colors.RED_300 if bg_color in [ft.Colors.INDIGO_900, ft.Colors.GREY_800, ft.Colors.BLUE_700] else ft.Colors.RED_600,
                                ),
                                ft.Text(
                                    f"↓ {self.get_temp_display(temp_min)}",
                                    size=14,
                                    color=ft.Colors.LIGHT_BLUE_200 if bg_color in [ft.Colors.INDIGO_900, ft.Colors.GREY_800, ft.Colors.BLUE_700] else ft.Colors.BLUE_600,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                
                ft.Divider(
                    height=20,
                    color=ft.Colors.with_opacity(0.3, text_color),
                    thickness=1
                ),
                
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%",
                            text_color
                        ),
                        self.create_info_card(
                            ft.Icons.AIR,
                            "Wind Speed",
                            f"{wind_speed} m/s",
                            text_color
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15,
                ),
                
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.COMPRESS,
                            "Pressure",
                            f"{pressure} hPa",
                            text_color
                        ),
                        self.create_info_card(
                            ft.Icons.CLOUD,
                            "Cloudiness",
                            f"{cloudiness}%",
                            text_color
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )
        
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.page.update()

        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.page.update()

        self.error_message.visible = False
        
        # Show weather tip
        tip_text = self.get_weather_tip(data)
        self.weather_tip.content = ft.Row(
            [
                ft.Icon(ft.Icons.TIPS_AND_UPDATES, size=20, color=ft.Colors.GREEN_700),
                ft.Text(
                    tip_text,
                    size=14,
                    color=ft.Colors.GREEN_900,
                    weight=ft.FontWeight.W_500,
                ),
            ],
            spacing=10,
        )
        self.weather_tip.visible = True
        self.page.update()
    
    
    def create_info_card(self, icon, label, value, text_color=ft.Colors.BLUE_900):
        """Create an info card for weather details."""
        card_bg = ft.Colors.with_opacity(0.2, ft.Colors.WHITE) if text_color == ft.Colors.WHITE else ft.Colors.WHITE
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=32, color=text_color),
                    ft.Text(label, size=13, color=text_color),
                    ft.Text(
                        value,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=text_color,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=card_bg,
            border_radius=12,
            padding=20,
            width=160,
            height=120,
        )
    
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.info_message.visible = False
        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)