# Home Assistant Custom Components

## CometBlue
HomeAssistant Custom Component for CometBlue/Xavax/Sygonix Bluetooth Thermostats.
Based on work of mirko located on [Github](https://github.com/mirko/home-assistant/blob/cometblue/homeassistant/components/climate/cometblue.py)

## Requirements
- [HomeAssistant](https://www.home-assistant.io)
- RaspberryPi v3
- cometblue Python library from [Github](https://github.com/xrucka/cometblue)

## Installation

1. Installation of cometblue Python library
Please follow original installation procedure at: https://github.com/xrucka/cometblue#installation

2. If you are using venv in you HA installation you have to allow `homeassistant` user to use bluetooth dbus
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

3. Download and extract latest release of cometblue.py to your HA config path
if you followed HA recomendations it could be done by this command:
   ```console
   $ wget -c https://github.com/Hy3n4/ha-cc-cometblue/releases/download/v0.0.1-alpha/cometblue.tar.gz -O - | tar -xz -C /home/homeassistant/.homeassistant/
   ```

4. Create HA config file

   ```yaml
   platform: cometblue
   devices:
     living_room_cb:
       mac: 00:00:00:00:00:00
   ```

5. Check config witthin Home Assistant and restart HA

## Links
https://github.com/xrucka/cometblue


## TODO
This readme file ;)
Posibly make it a supported part of HA??

## Troubleshooting
if you 

## Notes
Special thanks to mirko for his work