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

> Warning: If you are using venv for running hass as I do, You will probably want to shoot your brain out of your head during installation steps :wink: . Just like I did when I was creating this installation procedure.

There are several steps that you will have to execute as pi/root user on the other hand some steps are better executed as homeassistant user in venv (if you are using venv, of course). Such commands will be preceeded by string `(homeassistant)$`. Otherwise execute commands as pi/root.

1. Installation of cometblue Python library
You should install git if you didn't already.
    ```sh
    $ apt install git -y
    (homeassistant)$ cd /tmp
    (homeassistant)$ git clone https://github.com/xrucka/cometblue.git
    (homeassistant)$ cd cometblue
    ```
2. Follow original installation procedure at: https://github.com/xrucka/cometblue#installation

3. Install Dbus and some depencies for PyGObject if you didn't already

    ```sh
    $ apt install python3-dbus libglib2.0-dev libgirepository1.0-dev libcairo2-dev
    ```
    Dbus will be installed globally but in case you are running hass in venv you will need to copy dbus folder and some other files to venv site-packages location
    ```sh
    $ locate dbus
    ...
    /usr/lib/python3/dist-packages/_dbus_bindings.cpython-35m-arm-linux-gnueabihf.so
    /usr/lib/python3/dist-packages/_dbus_glib_bindings.cpython-35m-arm-linux-gnueabihf.so
    /usr/lib/python3/dist-packages/dbus
    ...
    ```
    Copy at least theese two files and one folder to 
    `/srv/homeassistant/lib/python3.5/site-packages/` and change ownership to homeassistant user
    
    ```sh
    cp -r /usr/lib/python3/dist-packages/{dbus,_dbus_bindings.cpython-35m-arm-linux-gnueabihf.so,_dbus_glib_bindings.cpython-35m-arm-linux-gnueabihf.so} /srv/homeassistant/lib/python3.5/site-packages/
    ```
4. Install PyGObject
   ```sh
   (homeassistant)$ pip3 install pygobject
   ```

5. If you are using venv in you HA installation you have to allow `homeassistant` user to use bluetooth dbus
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

6. Download and extract latest release of cometblue.py to your HA config path.
If you followed HA recomendations it could be done by this command:
   ```console
   (homeassistant)$ wget -c https://github.com/Hy3n4/ha-cc-cometblue/releases/download/v0.0.1-alpha/cometblue.tar.gz -O - | tar -xz -C /home/homeassistant/.homeassistant/
   (homeassistant)$ chown -R homeassistant:homeassistant /home/homeassistant/.homeassistant/custom_components/
   ```
   > At this moment you have to change ownership of downloaded files!

7. Copy dbus folder from it's original location (this issue is discussed [here](https://github.com/getsenic/gatt-python/issues/31))

8. Create HA config file

   ```yaml
   platform: cometblue
   devices:
     living_room_cb:
       mac: 00:00:00:00:00:00
   ```

9. Check config within Home Assistant and restart HA

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