# ha-cc-cometblue
HomeAssistant Custom Component for CometBlue/Xavax/Sygonix Bluetooth Thermostats.
Based on work of mirko https://github.com/mirko/home-assistant/blob/cometblue/homeassistant/components/climate/cometblue.py

## Requirements
- HomeAssistant
- RaspberryPi v3
- cometblue Python library
  - https://github.com/xrucka/cometblue

## Installation

Installation of cometblue Python library:

Please follow installation origianl notes: https://github.com/xrucka/cometblue#installation

If you are using venv you have to enable homeassistant user to use bluettoth dbus
so add this:
 ``` xml
<policy user="homeassistant">
    <allow send_destination="org.bluez"/>
</policy>
```
to config file `/etc/dbus-1/system.d/bluetooth.conf`

But you should add it before default `deny` section.
``` xml
  <policy context="default">
    <deny send_destination="org.bluez"/>
  </policy>
```

copy cometblue.py to your HA config path
if you followed HA recomendations it should be here:
``` bash
wget https://raw.githubusercontent.com/Hy3n4/ha-cc-cometblue/master/cometblue.py -O /home/homeassistant/.homeassistant/custom_components/climate/
```

make HA config file

``` yaml
platform: cometblue
name: Living Room Test
devices:
  living_room_cb:
    mac: !secret thermo_living_room_mac
```

## Links
https://github.com/xrucka/cometblue


## TODO
This readme file ;)
Posibly make it a supported part of HA??

## Notes
Special thanks to mirko for his work