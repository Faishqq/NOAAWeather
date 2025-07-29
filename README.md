# NOAA Weather Integration for Home Assistant
This integration provides weather forecast data from the [NOAA National Weather Service](https://www.weather.gov/) for the current location set in your Home Assistant installation. It fetches data directly from the NOAA API, providing you with up-to-date and reliable weather information.

## Features
- **Current Weather Conditions:** Get real-time weather data for your location, including temperature, humidity, wind speed, and more.
- **Daily and Hourly Forecasts:** Access detailed daily and hourly weather forecasts to plan your day.
- **Weather Sensors:** The integration creates various sensors in Home Assistant for different weather attributes, which can be used in your dashboards and automations.
- **Automations:** Create powerful automations based on weather conditions, such as turning on your lights when it gets cloudy or adjusting your thermostat based on the forecast.

## License
This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. This is a strong "copyleft" license, which means that any derivative works or modifications must also be licensed under the same GPL terms. This ensures that the code remains free and open-source for the entire community.

## Installation
### Using HACS (Recommended)
1. Ensure you have HACS installed in your Home Assistant instance. If not, follow the instructions on the [HACS documentation](https://hacs.xyz/).
2. In Home Assistant, go to **HACS > Integrations**.
3. Click on the three dots in the top right corner and select **Custom Repositories**.
4. Add the following URL: https://github.com/Faishqq/NOAAWeather.
5. Select the category **Integration**.
6. Search for "NOAA Weather" in HACS and download it.
7. **Restart Home Assistant** to ensure the integration is properly loaded.

### Manual Installation
1. Create a custom_components folder in your Home Assistant configuration directory if it doesn't already exist.
2. Download the contents of this repository and copy the noaa_weather folder into your custom_components directory.
3. **Restart Home Assistant.**

## Configuration
1. In Home Assistant, navigate to **Settings > Devices & Services.**
2. Click on **+ Add Integration.**
3. Search for "NOAA Weather" and select it.
4. The integration will automatically use the location configured in your Home Assistant instance. No further configuration is required.

## Usage
Once configured, you can add entities from the "NOAA Weather" integration to your Home Assistant dashboard and use them in automations and scripts.

## Disclaimer
This is an unofficial integration and is not affiliated with or endorsed by the National Oceanic and Atmospheric Administration (NOAA).