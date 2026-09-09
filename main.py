import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import requests
import airportsdata
from airports import airport_data

# Загрузка базы аэропортов
ALL_AIRPORTS = airportsdata.load('icao')

# КОНСТАНТА ДЛЯ OPEN-METEO
OPEN_METEO_URL = "https://open-meteo.com"

def get_airport_by_icao(icao):
    """Поиск аэропорта по ICAO (все аэропорты мира)"""
    try:
        icao = icao.upper().strip()
        if icao in ALL_AIRPORTS:
            ap = ALL_AIRPORTS[icao]
            return ap['name'], ap['lat'], ap['lon']
        result = airport_data.get_airport_by_icao(icao)
        if isinstance(result, list) and len(result) > 0:
            airport = result[0]
            return airport.get('name'), airport.get('lat') or airport.get('latitude'), airport.get('lon') or airport.get('longitude')
        elif isinstance(result, dict):
            return result.get('name'), result.get('lat') or result.get('latitude'), result.get('lon') or result.get('longitude')
    except Exception:
        pass
    return None, None, None

def get_metar_by_icao(icao):
    """Запрашивает METAR через открытый источник NOAA (без avwx)"""
    try:
        clean_icao = icao.upper().replace("METAR", "").strip()
        if len(clean_icao) != 4:
            return None
        
        url = f"https://noaa.gov{clean_icao}.TXT"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            if len(lines) >= 2:
                return lines[1].strip()
            return response.text.strip()
        return None
    except Exception as e:
        print(f"Ошибка получения METAR: {e}")
        return None

def decode_full_metar(metar):
    """Полная расшифровка METAR по стандартам ICAO"""
    import re
    info = {}
    try:
        time_match = re.search(r'(\d{2})(\d{2})(\d{2})Z', metar)
        if time_match:
            day = time_match.group(1)
            hour = time_match.group(2)
            minute = time_match.group(3)
            info['Время (UTC)'] = f"{day}-е число, {hour}:{minute}"
        wind_match = re.search(r'(\d{3})(\d{2})KT', metar)
        if wind_match:
            direction = wind_match.group(1)
            speed = wind_match.group(2)
            info['Ветер'] = f"{direction}°, {speed} узлов"
        vis_match = re.search(r'\s(\d{4})\s', metar)
        if vis_match:
            vis_val = vis_match.group(1)
            if vis_val == "9999":
                info['Видимость'] = "10 км и более"
            else:
                info['Видимость'] = f"{int(vis_val)} м"
        cloud_match = re.search(r'(FEW|SCT|BKN|OVC)(\d{3})', metar)
        if cloud_match:
            cloud_type = cloud_match.group(1)
            height = cloud_match.group(2)
            cloud_codes = {"FEW": "Малооблачно", "SCT": "Рассеянные", "BKN": "Значительная", "OVC": "Сплошная"}
            info['Облачность'] = f"{cloud_codes[cloud_type]} на {int(height)*100} фт"
        temp_match = re.search(r'(\d{2})/(\d{2})', metar)
        if temp_match:
            temp = temp_match.group(1)
            dew = temp_match.group(2)
            info['Температура'] = f"{temp}°C"
            info['Точка росы'] = f"{dew}°C"
        pressure_match = re.search(r'Q(\d{4})', metar)
        if pressure_match:
            pressure = pressure_match.group(1)
            info['QNH'] = f"{pressure} гПа"
        wx_match = re.search(r'-?\+?(RA|SN|DZ|BR|FG|TS|SH)', metar)
        if wx_match:
            wx_codes = {"RA": "Дождь", "SN": "Снег", "DZ": "Морось", "BR": "Дымка", "FG": "Туман", "TS": "Гроза", "SH": "Ливень"}
            info['Погодные явления'] = wx_codes.get(wx_match.group(1), wx_match.group(1))
    except:
        pass
    return info

def get_weather_from_open_meteo(lat, lon):
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,wind_speed_10m,wind_direction_10m,weather_code,surface_pressure",
            "timezone": "auto"
        }
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        if "current" not in data:
            return None
        current = data["current"]
        return {
            "temperature": current.get("temperature_2m", "N/A"),
            "wind_speed": current.get("wind_speed_10m", "N/A"),
            "wind_direction": current.get("wind_direction_10m", "N/A"),
            "weather_code": current.get("weather_code", 0),
            "pressure": current.get("surface_pressure", "N/A"),
            "visibility": "N/A",
            "clouds": "N/A"
        }
    except Exception as e:
        print(f"Ошибка Open-Meteo: {e}")
        return None

def translate_weather_code(code):
    codes = {
        0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность", 3: "Пасмурно",
        45: "Туман", 48: "Иней", 51: "Мелкая морось", 53: "Морось", 55: "Сильная морось",
        61: "Небольшой дождь", 63: "Дождь", 65: "Сильный дождь",
        71: "Небольшой снег", 73: "Снег", 75: "Сильный снег", 80: "Ливневые дожди",
        95: "Гроза", 96: "Гроза с градом", 99: "Сильная гроза с градом"
    }
    return codes.get(code, "Неизвестно")

def translate_weather_to_icon_type(code):
    if code in:
        return "sunny"
    elif code in:
        return "cloudy"
    elif code in:
        return "fog"
    elif code in:
        return "rain"
    elif code in:
        return "snow"
    elif code in:
        return "storm"
    return "sunny"

class WeatherApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        
        self.title_label = Label(text="Погода у аэропорта", font_size=24, size_hint_y=None, height=50)
        self.layout.add_widget(self.title_label)
        
        self.input_box = BoxLayout(size_hint_y=None, height=50)
        self.icao_input = TextInput(multiline=False, hint_text="Введите ICAO (например, UUWW)", font_size=18)
        self.search_button = Button(text="Поиск", font_size=18, size_hint_x=None, width=100)
        self.search_button.bind(on_press=self.search_airport)
        self.input_box.add_widget(self.icao_input)
        self.input_box.add_widget(self.search_button)
        self.layout.add_widget(self.input_box)
        
        self.tabs = TabbedPanel(do_default_tab=False)
        self.weather_tab = BoxLayout(orientation='vertical')
        self.metar_tab = BoxLayout(orientation='vertical')
        self.details_tab = BoxLayout(orientation='vertical')
        
        self.weather_label = Label(text="Введите ICAO-код для получения погоды", font_size=18, halign="center", valign="middle")
        self.weather_tab.add_widget(self.weather_label)
        
        self.metar_label = Label(text="", font_size=16, halign="left", valign="top")
        self.metar_tab.add_widget(self.metar_label)
        
        self.details_label = Label(text="", font_size=16, halign="left", valign="top")
        self.details_tab.add_widget(self.details_label)
        
        self.tabs.add_widget(self.weather_tab)
        self.tabs.add_widget(self.metar_tab)
        self.tabs.add_widget(self.details_tab)
        self.layout.add_widget(self.tabs)
        
        return self.layout

    def search_airport(self, instance):
        icao = self.icao_input.text
        if len(icao) < 4:
            return
        
        name, lat, lon = get_airport_by_icao(icao)
        if name:
            self.title_label.text = f"Погода: {name}"
            weather = get_weather_from_open_meteo(lat, lon)
            if weather:
                weather_code = weather.get("weather_code", 0)
                weather["weather"] = translate_weather_code(weather_code)
                weather["weather_type"] = translate_weather_to_icon_type(weather_code)
                self.weather_label.text = f"Температура: {weather['temperature']}°C\nВетер: {weather['wind_speed']} км/ч, {weather['wind_direction']}°\nПогодные условия: {weather['weather']}\nQNH: {weather['pressure']} гПа"
            else:
                self.weather_label.text = "Не удалось получить погоду"
        
        metar = get_metar_by_icao(icao)
        if metar:
            self.metar_label.text = f"METAR {icao.upper()}\n{metar}"
            details = decode_full_metar(metar)
            details_text = ""
            for key, value in details.items():
                details_text += f"{key}: {value}\n"
            self.details_label.text = details_text
        else:
            self.metar_label.text = "Ошибка получения METAR"
        
        return

if __name__ == "__main__":
    WeatherApp().run()
