<div align="center">
  <a href="https://electricitymaps.com/?utm_source=github&utm_medium=logo" target="_blank">
    <img src="https://raw.githubusercontent.com/electricitymaps/electricitymaps-contrib/refs/heads/master/web/public/images/electricitymap_social_image.png" alt="Electricity Maps Python SDK" height="200">
  </a>

  _Real-time and historical electricity data to help developers build a more sustainable future. If you want to join us in making electricity consumption more transparent and sustainable
  [<kbd>**Check out our careers page**</kbd>](https://electricitymaps.com/careers/)_.

  [![PyPi page link -- version](https://img.shields.io/pypi/v/electricitymaps.svg)](https://pypi.python.org/pypi/electricitymaps)
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
  [![Twitter Follow](https://img.shields.io/twitter/follow/electricitymaps?label=@electricitymaps&style=social)](https://twitter.com/intent/follow?screen_name=electricitymaps)

  <br/>

</div>

# Official Electricity Maps SDK for Python

Welcome to the official Python SDK for **[Electricity Maps](https://electricitymaps.com/)**.

**⚠️ Beta Notice:** This SDK is currently in beta. While functional, the API may change before the stable release. We welcome feedback and contributions!

## 📦 Getting Started

### Prerequisites

You need an Electricity Maps [API key](https://portal.electricitymaps.com/auth/signup). Sign up for free to get started.

### Installation

Getting the Electricity Maps SDK into your project is straightforward. Just run this command in your terminal:

```bash
pip install electricitymaps
```

### Basic Configuration

Here's a quick configuration example to get started:

```python
import os
from electricitymaps import create_client

# Create a client with your API key
client = create_client(api_key=os.environ["ELECTRICITY_MAPS_API_KEY"])
```

## ⚡ Supported Signals

The SDK provides access to the following electricity data signals:

| Signal | Latest | Forecast | History | Description |
|--------|--------|----------|---------|-------------|
| **Carbon Intensity** | ✅ | ✅ | ✅ | Real-time and forecasted carbon intensity (gCO2eq/kWh) |
| **Power Breakdown** | ✅ | ❌ | ✅ | Electricity generation by source (coal, gas, nuclear, solar, wind, etc.) |
| **Renewable Energy** | ✅ | ❌ | ❌ | Percentage of renewable energy in the electricity mix |
| **Carbon-Free Energy** | ✅ | ❌ | ❌ | Percentage of carbon-free energy sources |
| **Total Load** | ✅ | ❌ | ✅ | Total electricity demand/consumption |
| **Net Load** | ✅ | ❌ | ✅ | Load minus renewable generation |
| **Day-Ahead Prices** | ✅ | ❌ | ✅ | Next-day electricity market prices |

> **Note**: All signals support querying by both zone keys (e.g., "DK-DK1") and geographic coordinates (latitude/longitude).

> **Coverage**: This table shows the current SDK coverage. The full Electricity Maps API offers additional endpoints and functionality. For complete API documentation and all available endpoints, visit our [Developer Hub](https://portal.electricitymaps.com/developer-hub/api/getting-started).

## 🚀 Quick Usage Examples

### Carbon Intensity

```python
# Get latest carbon intensity for Denmark West
result = client.carbon_intensity.latest(zone_key="DK-DK1")
print(f"Carbon intensity: {result.carbon_intensity} gCO2eq/kWh")

# Get 24-hour carbon intensity forecast
forecast = client.carbon_intensity.forecast(zone_key="DK-DK1", horizon_hours=24)
print(f"Forecast: {forecast}")

# Get historical carbon intensity data
history = client.carbon_intensity.history(zone_key="DK-DK1")
print(f"Historical data: {history}")
```

### Power Breakdown

```python
# Get current power generation breakdown
breakdown = client.power_breakdown.latest(zone_key="DK-DK1")
print(f"Power sources: {breakdown}")

# Get historical power breakdown
history = client.power_breakdown.history(zone_key="DK-DK1")
print(f"Historical breakdown: {history}")
```

### Renewable and Carbon-Free Energy

```python
# Get current renewable energy share
renewable = client.renewable_energy.latest(zone_key="DK-DK1")
print(f"Renewable energy share: {renewable}")

# Get carbon-free energy share
carbon_free = client.carbon_free_energy.latest(zone_key="DK-DK1")
print(f"Carbon-free energy share: {carbon_free}")
```

### Load and Pricing Data

```python
# Get total electricity load
total_load = client.total_load.latest(zone_key="DK-DK1")
print(f"Total load: {total_load}")

# Get net load (load minus renewables)
net_load = client.net_load.latest(zone_key="DK-DK1")
print(f"Net load: {net_load}")

# Get day-ahead electricity prices
prices = client.price_day_ahead.latest(zone_key="DK-DK1")
print(f"Day-ahead prices: {prices}")
```

### Using Coordinates

Most endpoints support both zone keys and geographic coordinates:

```python
# Get data by coordinates (Copenhagen)
result = client.carbon_intensity.latest(lat=55.6761, lon=12.5683)
print(f"Carbon intensity: {result.carbon_intensity} gCO2eq/kWh")

# Forecast by coordinates
forecast = client.carbon_intensity.forecast(
    lat=55.6761, 
    lon=12.5683, 
    horizon_hours=48
)
print(f"48-hour forecast: {forecast}")
```

## 📚 Documentation

For more details on API endpoints, parameters, and response formats, check out our full documentation at [https://portal.electricitymaps.com/developer-hub/api/getting-started](https://portal.electricitymaps.com/developer-hub/api/getting-started).

## 🔑 Authentication

The SDK uses API key authentication. You can obtain your API key from the [Electricity Maps dashboard](https://portal.electricitymaps.com/auth).

Set your API key as an environment variable:
```bash
export ELECTRICITY_MAPS_API_KEY="your-api-key-here"
```

## 🛟 Need Help?

If you encounter issues or need help setting up the SDK, please:

- Check our [documentation](https://docs.electricitymaps.com)
- Open an issue on [GitHub](https://github.com/electricitymaps/electricitymaps-contrib)
- Contact us at [hello@electricitymaps.com](mailto:hello@electricitymaps.com)

## 🔗 Resources

- [API Documentation](https://docs.electricitymaps.com) - Complete API reference
- [Electricity Maps Website](https://electricitymaps.com) - Live electricity data visualization
- [GitHub](https://github.com/electricitymaps/electricitymaps-contrib) - Open source project
- [Twitter](https://twitter.com/electricitymaps) - Follow us for updates

## 📃 License

This SDK is open-source and available under the MIT license.

## 🌱 Contributing

We welcome contributions! This SDK is part of our mission to make electricity consumption more transparent and sustainable. Every contribution helps us build a better future.
