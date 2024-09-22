# SmartEVSE-2 Home Assistant Integration

## Overview

The SmartEVSE-2 integration for Home Assistant allows you to monitor and control your SmartEVSE electric vehicle charging station. This integration provides real-time data about charging status, power consumption, and allows you to control the charging process.

## Features

- Monitor charging status
- View real-time charging current
- Control access to the charging station
- View error states and diagnostics
- Integration with Home Assistant energy management

## Requirements

- Home Assistant
- SmartEVSE charging station with firmware version 2.30
- RS485 to Ethernet converter (see note below)

**Note on Connectivity:** The author of this integration used a [Waveshare RS485 to ETH](https://www.waveshare.com/rs485-to-eth.htm) converter to connect the SmartEVSE (which uses RS485) to the local network via Ethernet. This allows for Modbus TCP communication.

## Installation

### HACS (Recommended)

1. Ensure that [HACS](https://hacs.xyz/) is installed.
2. In the HACS panel, go to "Integrations".
3. Click on the three dots in the top right corner and select "Custom repositories".
4. Add the URL of this repository: `https://github.com/kasperiio/smartevse-2-custom-component.git`
5. Select "Integration" as the category.
6. Click "ADD".
7. Close the custom repositories window.
8. Click the "+ EXPLORE & DOWNLOAD REPOSITORIES" button.
9. Search for "SmartEVSE 2" and select it.
10. Click "Download" in the bottom right corner.
11. Restart Home Assistant.

### Manual Installation

1. Download the `smartevse2` folder from this repository.
2. Copy the folder to your `config/custom_components` directory.
3. Restart Home Assistant.

## Configuration

1. In Home Assistant, go to Configuration > Integrations.
2. Click the "+ ADD INTEGRATION" button.
3. Search for "SmartEVSE" and select it.
4. Follow the configuration steps:
   - Enter the IP address of your SmartEVSE (or the RS485 to Ethernet converter).
   - Enter the Modbus port (default is 26).
   - Configure the polling interval (optional).

## Entities

After setting up the integration, you'll have access to the following entities:

### Sensors

- SmartEVSE State
- Charging Current
- Max Charging Current
- Error State
- Temperature
- Used Phases
- Mode (Normal/Smart/Solar)
- Solar Timer
- Serial Number

### Switches

- SmartEVSE Access (Enable/Disable charging)

## Usage

### Controlling Charging

You can control the charging process using the "SmartEVSE Access" switch. Turn it on to allow charging, and off to stop charging.

## Troubleshooting

If you encounter any issues:

1. Ensure your SmartEVSE is on the v2.30 firmware.
2. Check that the IP address and port are correct in the configuration.
3. Verify that your Home Assistant instance can reach the RS485 to Ethernet converter on your network.
4. Check the Home Assistant logs for any error messages related to the SmartEVSE integration.

## Contributing

Contributions to improve the SmartEVSE integration are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This integration is released under the MIT License.

## Disclaimer

This integration is not officially associated with or endorsed by SmartEVSE. Use at your own risk.