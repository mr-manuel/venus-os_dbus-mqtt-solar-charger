# dbus-mqtt-solar-charger - Emulates a physical PV Inverter from MQTT data

<small>GitHub repository: [mr-manuel/venus-os_dbus-mqtt-solar-charger](https://github.com/mr-manuel/venus-os_dbus-mqtt-solar-charger)</small>

### Disclaimer

I wrote this script for myself. I'm not responsible, if you damage something using my script.


### Purpose

The script emulates a Solar Charger in Venus OS. It gets the MQTT data from a subscribed topic and publishes the information on the dbus as the service `com.victronenergy.solarcharger.mqtt_solar_charger` with the VRM instance `51`.


### Config

Copy or rename the `config.sample.ini` to `config.ini` in the `dbus-mqtt-solar-charger` folder and change it as you need it.


### JSON structure

<details><summary>Minimum required</summary>

Single MTTP tracker
```json
{
    "Pv": {
        "V": 60.0
    },
    "Yield": {
        "Power": 120.0
    },
    "Dc": {
        "0": {
            "Current": 10.0,
            "Voltage": 12.0
        }
    }
}
```

OR

Multiple MPPT tracker (min 2, max 4)
```json
{
  "Pv": {
    "0": {
      "V": 60.0,
      "P": 10.0
    },
    "1": {
      "V": 60.0,
      "P": 20.0
    },
    "2": {
      "V": 60.0,
      "P": 30.0
    },
    "3": {
      "V": 60.0,
      "P": 40.0
    }
  },
  "Dc": {
    "0": {
      "Voltage": 12.0,
      "Current": 8.33
    }
  }
}
```
</details>

<details><summary>Full</summary>

See [dbus](https://github.com/victronenergy/venus/wiki/dbus#solar-chargers) documentation for value description.

```json
{
    "NrOfTrackers": 4,                <!-- calculated if not set
    "Pv": {
        "0": {
        "V": 60.0,
        "P": 10.0
        },
        "1": {
        "V": 60.0,
        "P": 20.0
        },
        "2": {
        "V": 60.0,
        "P": 30.0
        },
        "3": {
        "V": 60.0,
        "P": 40.0
        }
    },
    "Yield": {
        "Power": 180,                 <!-- calculated in multiple MTTP tracker mode, if not set
        "User": 30,
        "System": 30
    },
    "Dc": {
        "0": {
            "Current": 15,
            "Voltage": 12
        }
    },
    "Link": {
        "NetworkMode": "0x1",
        "BatteryCurrent": 0.0,
        "ChargeCurrent": 0.0,
        "ChargeVoltage": 0.0,
        "NetworkStatus": "0x04",
        "TemperatureSense": 20.0,
        "TemperatureSenseActive": 0,
        "VoltageSense": 80.0,
        "VoltageSenseActive": 0,
    },
    "Settings": {
        "BmsPresent": 0,
        "ChargeCurrentLimit": 120.0
    },
    "Load": {
        "State": 0,
        "I": 0.0
    },
    "ErrorCode": 0,
    "State": 3,
    "Mode": 4,
    "MppOperationMode": 2,
    "DeviceOffReason": "",
    "Relay": {
        "0": {
            "State": 0
        }
    },
    "History": {
        "Daily": {
            "0": {
                "Yield": 11,
                "Consumption": 22,
                "MaxPower": 33,
                "MaxPvVoltage": 44,
                "MinBatteryVoltage": 55,
                "MaxBatteryVoltage": 66,
                "MaxBatteryCurrent": 77,
                "TimeInBulk": 3600,
                "TimeInAbsorption": 1800,
                "TimeInFloat": 900,
                "LastError1": 1,
                "LastError2": 2,
                "LastError3": 3,
                "LastError4": 4
            },
            "1": {
                "Yield": 11,
                "Consumption": 22,
                "MaxPower": 33,
                "MaxPvVoltage": 44,
                "MinBatteryVoltage": 55,
                "MaxBatteryVoltage": 66,
                "MaxBatteryCurrent": 77,
                "TimeInBulk": 3600,
                "TimeInAbsorption": 1800,
                "TimeInFloat": 900,
                "LastError1": 1,
                "LastError2": 2,
                "LastError3": 3,
                "LastError4": 4
            },
            "2": {
                "Yield": 11,
                "Consumption": 22,
                "MaxPower": 33,
                "MaxPvVoltage": 44,
                "MinBatteryVoltage": 55,
                "MaxBatteryVoltage": 66,
                "MaxBatteryCurrent": 77,
                "TimeInBulk": 3600,
                "TimeInAbsorption": 1800,
                "TimeInFloat": 900,
                "LastError1": 1,
                "LastError2": 2,
                "LastError3": 3,
                "LastError4": 4
            }
        },
        "Overall": {
            "DaysAvailable": 3,
            "MaxPvVoltage": 44,
            "MaxBatteryVoltage": 14,
            "MinBatteryVoltage": 11,
            "LastError1": 1,
            "LastError2": 2,
            "LastError3": 3,
            "LastError4": 4
        }
    }
}
```
</details>


### Install

1. Copy the `dbus-mqtt-solar-charger` folder to `/data/etc` on your Venus OS device

2. Run `bash /data/etc/dbus-mqtt-solar-charger/install.sh` as root

   The daemon-tools should start this service automatically within seconds.

### Uninstall

Run `/data/etc/dbus-mqtt-solar-charger/uninstall.sh`

### Restart

Run `/data/etc/dbus-mqtt-solar-charger/restart.sh`

### Debugging

The logs can be checked with `tail -n 100 -F /data/log/dbus-mqtt-solar-charger/current | tai64nlocal`

The service status can be checked with svstat `svstat /service/dbus-mqtt-solar-charger`

This will output somethink like `/service/dbus-mqtt-solar-charger: up (pid 5845) 185 seconds`

If the seconds are under 5 then the service crashes and gets restarted all the time. If you do not see anything in the logs you can increase the log level in `/data/etc/dbus-mqtt-solar-charger/dbus-mqtt-solar-charger.py` by changing `level=logging.WARNING` to `level=logging.INFO` or `level=logging.DEBUG`

If the script stops with the message `dbus.exceptions.NameExistsException: Bus name already exists: com.victronenergy.solarcharger.mqtt_solar_charger"` it means that the service is still running or another service is using that bus name.

### Multiple instances

It's possible to have multiple instances, but it's not automated. Follow these steps to achieve this:

1. Save the new name to a variable `driverclone=dbus-mqtt-solar-charger-2`

2. Copy current folder `cp -r /data/etc/dbus-mqtt-solar-charger/ /data/etc/$driverclone/`

3. Rename the main script `mv /data/etc/$driverclone/dbus-mqtt-solar-charger.py /data/etc/$driverclone/$driverclone.py`

4. Fix the script references for service and log
    ```
    sed -i 's:dbus-mqtt-solar-charger:'$driverclone':g' /data/etc/$driverclone/service/run
    sed -i 's:dbus-mqtt-solar-charger:'$driverclone':g' /data/etc/$driverclone/service/log/run
    ```

5. Change the `device_name` and increase the `device_instance` in the `config.ini`

Now you can install and run the cloned driver. Should you need another instance just increase the number in step 1 and repeat all steps.

### Compatibility

It was tested on Venus OS Large `v2.92` on the following devices:

* RaspberryPi 4b
* MultiPlus II (GX Version)


## Supporting/Sponsoring this project

You like the project and you want to support me?

[<img src="https://github.md0.eu/uploads/donate-button.svg" height="50">](https://www.paypal.com/donate/?hosted_button_id=3NEVZBDM5KABW)
