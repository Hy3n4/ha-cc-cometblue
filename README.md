# Home Assistant Custom Components

## CometBlue
HomeAssistant Custom Component for CometBlue/Xavax/Sygonix Bluetooth Thermostats.
Based on work of mirko located on [Github](https://github.com/mirko/home-assistant/blob/cometblue/homeassistant/components/climate/cometblue.py)

## Requirements
- [HomeAssistant](https://www.home-assistant.io)
- RaspberryPi v3
- cometblue Python library from [Github](https://github.com/xrucka/cometblue)

## What works

Feature | Get | Set
------- | ------- | ------
Mode | :heavy_check_mark: | :heavy_check_mark:
Childlock | :heavy_check_mark: | :heavy_check_mark:
Target Temperature | :heavy_check_mark: | :heavy_check_mark:
Current Temperature | :heavy_check_mark: | :heavy_check_mark:
Open Window Detection | :heavy_multiplication_x: | :heavy_multiplication_x:
Holiday | :heavy_multiplication_x: | :heavy_multiplication_x:
Battery Level | :heavy_check_mark: | :heavy_minus_sign:
Low Battery | :heavy_check_mark: | :heavy_minus_sign:
Model | :heavy_check_mark: | :heavy_minus_sign:
Manufacturer Name | :heavy_check_mark: | :heavy_minus_sign:
Firmware Rev. | :heavy_check_mark: | :heavy_minus_sign:
Software Rev. | :heavy_check_mark: | :heavy_minus_sign:

## Installation

1. Installation of cometblue Python library
You should install git if you didn't already.
```sh
$ apt install git -y
$ cd /tmp
$ git clone https://github.com/xrucka/cometblue.git
$ cd /cometblue
```
and then please follow original installation procedure at: https://github.com/xrucka/cometblue#installation

1. If you are using venv in you HA installation you have to allow `homeassistant` user to use bluetooth dbus
so add this:
   ```xml
   <policy user="homeassistant">
       <allow send_destination="org.bluez"/>
   </policy>
   ```
   to config file `/etc/dbus-1/system.d/bluetooth.conf`

   But you should add it before default `deny` section.
   ```xml
     <policy context="default">
       <deny send_destination="org.bluez"/>
     </policy>
   ```

   Restart bluetooth.service

   ```sh
   $ systemctl restart bluetooth.service
   ```

2. Download and extract latest release of cometblue.py to your HA config path.
If you followed HA recomendations it could be done by this command:
   ```console
   $ wget -c https://github.com/Hy3n4/ha-cc-cometblue/releases/download/v0.0.1-alpha/cometblue.tar.gz -O - | tar -xz -C /home/homeassistant/.homeassistant/
   $ chown -R homeassistant:homeassistant /home/homeassistant/.homeassistant/custom_components/
   ```
   > At this moment you have to change ownership of downloaded files!

3. Create HA config file

   ```yaml
   platform: cometblue
   devices:
     living_room_cb:
       mac: 00:00:00:00:00:00
   ```

4. Check config witthin Home Assistant and restart HA

## Links
https://github.com/xrucka/cometblue


## TODO
This readme file ;)
Posibly make it a supported part of HA??

## Troubleshooting
If you encounter any problem you should look into hass logfile located in config dir.
If there is no useful information turn on debugging in hass config.

```yaml
logger:
  default: warning
  logs:
    homeassistant.components.climate: debug
    custom_components.climate.cometblue: debug
    cometblue.device: debug
```

## Notes
Special thanks to mirko for his work on [Github]()