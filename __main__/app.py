from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

apikey = 'TyXHfOMpIAEQHPPybGT92kNPUqCV4Ac9'

baseurl = 'http://dataservice.accuweather.com'

def get_location_key_by_city(city_name):
    url = f"{baseurl}/locations/v1/cities/search"
    params = {"apikey": apikey, "q": city_name}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]["Key"]
        else:
            raise ValueError("Город не найден.")
    else:
        raise Exception(f"Ошибка API: {response.status_code}")

def get_location_key_by_coordinates(lat, lon):
    url = f"{baseurl}/locations/v1/cities/geoposition/search"
    params = {"apikey": apikey, "q": f"{lat},{lon}"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data["Key"]
        else:
            raise ValueError("Местоположение не найдено.")
    else:
        raise Exception(f"Ошибка API: {response.status_code}")

def get_weather_conditions(location_key):
    url = f"{baseurl}/currentconditions/v1/{location_key}"
    params = {"apikey": apikey, "details": "true"}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            weather = data[0]
            return {
                "temperature_celsius": weather["Temperature"]["Metric"]["Value"],
                "humidity": weather["RelativeHumidity"],
                "wind_speed_kph": weather["Wind"]["Speed"]["Metric"]["Value"],
                "precipitation_probability": weather.get("PrecipitationProbability", 0)
            }
        else:
            raise ValueError("Погодные данные отсутствуют.")
    else:
        raise Exception(f"Ошибка API: {response.status_code}")

def check_bad_weather(temperature, wind_speed, precipitation_probability):
    if temperature < 0 or temperature > 35:
        return True
    if wind_speed > 50:
        return True
    if precipitation_probability > 70:
        return True
    return False


@app.route("/", methods=["GET", "POST"])
def weather():
    if request.method == "POST":
        start_city = request.form.get("start_city")
        end_city = request.form.get("end_city")

        if not start_city or not end_city:
            return render_template("index.html", error="Пожалуйста, укажите оба города.")

        try:
            start_location_key = get_location_key_by_city(start_city)
            end_location_key = get_location_key_by_city(end_city)

            start_weather_data = get_weather_conditions(start_location_key)
            end_weather_data = get_weather_conditions(end_location_key)

            start_bad_weather = check_bad_weather(
                start_weather_data["temperature_celsius"],
                start_weather_data["wind_speed_kph"],
                start_weather_data["precipitation_probability"]
            )
            end_bad_weather = check_bad_weather(
                end_weather_data["temperature_celsius"],
                end_weather_data["wind_speed_kph"],
                end_weather_data["precipitation_probability"]
            )

            result = {
                "start_city": start_city,
                "end_city": end_city,
                "start_weather": start_weather_data,
                "end_weather": end_weather_data,
                "start_bad_weather": start_bad_weather,
                "end_bad_weather": end_bad_weather
            }

            return render_template("result.html", result=result)

        except Exception as e:
            return render_template("index.html", error=f"Ошибка: {str(e)}")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
