import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import requests
import avwx
import airportsdata
from airports import airport_data

ALL_AIRPORTS = airportsdata.load('icao')
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def get_airport_by_icao(icao):
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
    try:
        clean_icao = icao.upper().replace("METAR", "").strip()
        if len(clean_icao) != 4:
            return None
        metar = avwx.Metar(clean_icao)
        metar.update()
        raw_text = metar.raw
        if raw_text and raw_text.startswith("METAR"):
            raw_text = raw_text[5:].strip()
        return raw_text
    except Exception as e:
        print(f"Ошибка получения METAR через avwx: {e}")
        return None

def decode_full_metar(metar):
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
        wx_match = re.search(r'(-|\+)?(RA|SN|DZ|BR|FG|TS|SH)', metar)
        if wx_match:
            wx_codes = {"RA": "Дождь", "SN": "Снег", "DZ": "Морось", "BR": "Дымка", "FG": "Туман", "TS": "Гроза", "SH": "Ливень"}
            info['Погодные явления'] = wx_codes.get(wx_match.group(2), wx_match.group(2))
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
    if code in [0, 1]:
        return "sunny"
    elif code in [2, 3]:
        return "cloudy"
    elif code in [45, 48]:
        return "fog"
    elif code in [51, 53, 55, 61, 63, 65, 80]:
        return "rain"
    elif code in [71, 73, 75]:
        return "snow"
    elif code in [95, 96, 99]:
        return "storm"
    return "sunny"

class WeatherApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.weather_label = toga.Label("Введите ICAO-код для получения погоды")
        self.icao_input = toga.TextInput(placeholder="Введите ICAO (например, UUWW)")
        self.search_button = toga.Button("Поиск", on_press=self.search_airport)
        
        self.metar_label = toga.Label("", style=Pack(padding=5))
        self.details_label = toga.Label("", style=Pack(padding=5))
        
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        main_box.add(self.icao_input)
        main_box.add(self.search_button)
        main_box.add(self.weather_label)
        main_box.add(self.metar_label)
        main_box.add(self.details_label)
        
        self.main_window.content = main_box
        self.main_window.show()

    def search_airport(self, widget):
        icao = self.icao_input.value
        if len(icao) < 4:
            return
        
        name, lat, lon = get_airport_by_icao(icao)
        if name:
            self.weather_label.text = f"Погода: {name}"
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

def main():
    return WeatherApp()
