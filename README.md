# dbus-mqtt-solar-charger - Emulates a physical Solar Charger from MQTT data

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
    "Pv": {
        "0": {
            "V": 60.0,                           --> Float - Voltage of 1. MPPT tracker
            "P": 10.0                            --> Float - Power of 1. MPPT tracker
        },
        "1": {
            "V": 60.0,                           --> Float - Voltage of 2. MPPT tracker
            "P": 20.0                            --> Float - Power of 2. MPPT tracker
        },
        "2": {
            "V": 60.0,                           --> Float - Voltage of 3. MPPT tracker
            "P": 30.0                            --> Float - Power of 3. MPPT tracker
        },
        "3": {
            "V": 60.0,                           --> Float - Voltage of 4. MPPT tracker
            "P": 40.0                            --> Float - Power of 4. MPPT tracker
        }
    },
    "Yield": {
        "Power": 180,                            --> Float - Power of single MTTP tracker or sum of all trackers. Calculated in multiple MTTP tracker mode, if not set
        "User": 30,                              --> Int - kWh produced until reset
        "System": 30                             --> Int - kWh produced until now (lifetime)
    },
    "Dc": {
        "0": {
            "Current": 15,                       --> Float - Battery current
            "Voltage": 12                        --> Float - Battery voltage
        }
    },
    "Link": {
        "NetworkMode": "0x1",                    --> See dbus documentation
        "BatteryCurrent": 0.0,                   --> See dbus documentation
        "ChargeCurrent": 0.0,                    --> See dbus documentation
        "ChargeVoltage": 0.0,                    --> See dbus documentation
        "NetworkStatus": "0x04",                 --> See dbus documentation
        "TemperatureSense": 20.0,                --> See dbus documentation
        "TemperatureSenseActive": 0,             --> See dbus documentation
        "VoltageSense": 80.0,                    --> See dbus documentation
        "VoltageSenseActive": 0                  --> See dbus documentation
    },
    "Settings": {
        "BmsPresent": 0,                         --> See dbus documentation
        "ChargeCurrentLimit": 120.0              --> Float - Maximum charge current
    },
    "Load": {
        "State": 0,                              --> Int - Whether the load is on or of
        "I": 0.0                                 --> Float - Current from the load output
    },
    "ErrorCode": 0,                              --> See dbus documentation
    "State": 3,                                  --> See dbus documentation
    "Mode": 4,                                   --> 0 = On; 4 = Off
    "MppOperationMode": 2,                       --> 0 = Off; 1 = Voltage or Current limited; 2 = MPPT Tracker active
    "DeviceOffReason": "",                       --> See dbus documentation
    "Relay": {
        "0": {
            "State": 0                           --> See dbus documentation
        }
    },
    "History": {
        "Daily": {                               --> Daily history
            "0": {                               --> String - Today
                "Yield": 11,                     --> Float - kWh of today
                "Consumption": 22,               --> Int - kWh of today
                "MaxPower": 33,                  --> Float - Watt peak of today
                "MaxPvVoltage": 44,              --> Float - Volt peak of today
                "MinBatteryVoltage": 55,         --> Float - Min battery voltage of today
                "MaxBatteryVoltage": 66,         --> Float - Max battery voltage of today
                "MaxBatteryCurrent": 77,         --> Float - Max battery current of today
                "TimeInBulk": 3600,              --> Int - Seconds in bulk mode of today
                "TimeInAbsorption": 1800,        --> Int - Seconds in absorption mode of today
                "TimeInFloat": 900,              --> Int - Seconds in float mode of today
                "LastError1": 1,                 --> Int - Last error of today - See dbus documentation /ErrorCode
                "LastError2": 2,                 --> Int - Second last error of today - See dbus documentation /ErrorCode
                "LastError3": 3,                 --> Int - Thrid last error of today - See dbus documentation /ErrorCode
                "LastError4": 4,                 --> Int - Fourth last error of today - See dbus documentation /ErrorCode
                "Pv": {
                    "0": {                       --> MPPT tracker number 1
                        "Yield": 1,              --> Float - kWh of today for MPPT tracker 1
                        "MaxPower": 11,          --> Float - Watt peak of today for MPPT tracker 1
                        "MaxVoltage": 111        --> Float - Volt peak of today for MPPT tracker 1
                    },
                    "1": {                       --> MPPT tracker number 2
                        "Yield": 2,              --> Float - kWh of today for MPPT tracker 2
                        "MaxPower": 22,          --> Float - Watt peak of today for MPPT tracker 2
                        "MaxVoltage": 222        --> Float - Volt peak of today for MPPT tracker 2
                    },
                    "2": {                       --> MPPT tracker number 3
                        "Yield": 3,              --> Float - kWh of today for MPPT tracker 3
                        "MaxPower": 33,          --> Float - Watt peak of today for MPPT tracker 3
                        "MaxVoltage": 333        --> Float - Volt peak of today for MPPT tracker 3
                    },
                    "3": {                       --> MPPT tracker number 4
                        "Yield": 4,              --> Float - kWh of today for MPPT tracker 4
                        "MaxPower": 44,          --> Float - Watt peak of today for MPPT tracker 4
                        "MaxVoltage": 444        --> Float - Volt peak of today for MPPT tracker 4
                    }
                }
            },
            "1": {                               --> String - Yesterday
                "Yield": 11,                     --> Float - kWh of yesterday
                "Consumption": 22,               --> Int - kWh of yesterday
                "MaxPower": 33,                  --> Float - Watt peak of yesterday
                "MaxPvVoltage": 44,              --> Float - Volt peak of yesterday
                "MinBatteryVoltage": 55,         --> Float - Min battery voltage of yesterday
                "MaxBatteryVoltage": 66,         --> Float - Max battery voltage of yesterday
                "MaxBatteryCurrent": 77,         --> Float - Max battery current of yesterday
                "TimeInBulk": 3600,              --> Int - Seconds in bulk mode of yesterday
                "TimeInAbsorption": 1800,        --> Int - Seconds in absorption mode of yesterday
                "TimeInFloat": 900,              --> Int - Seconds in float mode of yesterday
                "LastError1": 1,                 --> Int - Last error of yesterday - See dbus documentation /ErrorCode
                "LastError2": 2,                 --> Int - Second last error of yesterday - See dbus documentation /ErrorCode
                "LastError3": 3,                 --> Int - Thrid last error of yesterday - See dbus documentation /ErrorCode
                "LastError4": 4,                 --> Int - Fourth last error of yesterday - See dbus documentation /ErrorCode
                "Pv": {
                    "0": {                       --> MPPT tracker number 1
                        "Yield": 1,              --> Float - kWh of yesterday for MPPT tracker 1
                        "MaxPower": 11,          --> Float - Watt peak of yesterday for MPPT tracker 1
                        "MaxVoltage": 111        --> Float - Volt peak of yesterday for MPPT tracker 1
                    },
                    "1": {                       --> MPPT tracker number 2
                        "Yield": 2,              --> Float - kWh of yesterday for MPPT tracker 2
                        "MaxPower": 22,          --> Float - Watt peak of yesterday for MPPT tracker 2
                        "MaxVoltage": 222        --> Float - Volt peak of yesterday for MPPT tracker 2
                    },
                    "2": {                       --> MPPT tracker number 3
                        "Yield": 3,              --> Float - kWh of yesterday for MPPT tracker 3
                        "MaxPower": 33,          --> Float - Watt peak of yesterday for MPPT tracker 3
                        "MaxVoltage": 333        --> Float - Volt peak of yesterday for MPPT tracker 3
                    },
                    "3": {                       --> MPPT tracker number 4
                        "Yield": 4,              --> Float - kWh of yesterday for MPPT tracker 4
                        "MaxPower": 44,          --> Float - Watt peak of yesterday for MPPT tracker 4
                        "MaxVoltage": 444        --> Float - Volt peak of yesterday for MPPT tracker 4
                    }
                }
            },
            "2": {                               --> String - 2 days ago (I do not recommend more than 30 days)
                "Yield": 11,                     --> Float - kWh of 2 days ago
                "Consumption": 22,               --> Int - kWh of 2 days ago
                "MaxPower": 33,                  --> Float - Watt peak of 2 days ago
                "MaxPvVoltage": 44,              --> Float - Volt peak of 2 days ago
                "MinBatteryVoltage": 55,         --> Float - Min battery voltage of 2 days ago
                "MaxBatteryVoltage": 66,         --> Float - Max battery voltage of 2 days ago
                "MaxBatteryCurrent": 77,         --> Float - Max battery current of 2 days ago
                "TimeInBulk": 3600,              --> Int - Seconds in bulk mode of 2 days ago
                "TimeInAbsorption": 1800,        --> Int - Seconds in absorption mode of 2 days ago
                "TimeInFloat": 900,              --> Int - Seconds in float mode of 2 days ago
                "LastError1": 1,                 --> Int - Last error of 2 days ago - See dbus documentation /ErrorCode
                "LastError2": 2,                 --> Int - Second last error of 2 days ago - See dbus documentation /ErrorCode
                "LastError3": 3,                 --> Int - Thrid last error of 2 days ago - See dbus documentation /ErrorCode
                "LastError4": 4,                 --> Int - Fourth last error of 2 days ago - See dbus documentation /ErrorCode
                "Pv": {
                    "0": {                       --> MPPT tracker number 1
                        "Yield": 1,              --> Float - kWh of 2 days ago for MPPT tracker 1
                        "MaxPower": 11,          --> Float - Watt peak of 2 days ago for MPPT tracker 1
                        "MaxVoltage": 111        --> Float - Volt peak of 2 days ago for MPPT tracker 1
                    },
                    "1": {                       --> MPPT tracker number 2
                        "Yield": 2,              --> Float - kWh of 2 days ago for MPPT tracker 2
                        "MaxPower": 22,          --> Float - Watt peak of 2 days ago for MPPT tracker 2
                        "MaxVoltage": 222        --> Float - Volt peak of 2 days ago for MPPT tracker 2
                    },
                    "2": {                       --> MPPT tracker number 3
                        "Yield": 3,              --> Float - kWh of 2 days ago for MPPT tracker 3
                        "MaxPower": 33,          --> Float - Watt peak of 2 days ago for MPPT tracker 3
                        "MaxVoltage": 333        --> Float - Volt peak of 2 days ago for MPPT tracker 3
                    },
                    "3": {                       --> MPPT tracker number 4
                        "Yield": 4,              --> Float - kWh of 2 days ago for MPPT tracker 4
                        "MaxPower": 44,          --> Float - Watt peak of 2 days ago for MPPT tracker 4
                        "MaxVoltage": 444        --> Float - Volt peak of 2 days ago for MPPT tracker 4
                    }
                }
            }
        },
        "Overall": {                             --> Lifetime history
            "DaysAvailable": 3,                  --> Fetched from config.ini from "history_days"
            "MaxPvVoltage": 44,                  --> Float - Max PV voltage in lifetime
            "MaxBatteryVoltage": 14,             --> Float - Max PV voltage in lifetime
            "MinBatteryVoltage": 11,             --> Float - Max PV voltage in lifetime
            "LastError1": 1,                     --> Int - Last error - See dbus documentation /ErrorCode
            "LastError2": 2,                     --> Int - Second last error - See dbus documentation /ErrorCode
            "LastError3": 3,                     --> Int - Thrid last error - See dbus documentation /ErrorCode
            "LastError4": 4                      --> Int - Fourth last error - See dbus documentation /ErrorCode
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


### Screenshots

<details><summary>MQTT Solar Charger</summary>

![MQTT Solar Charger - pages](/screenshots/solar-charger_pages.png)
![MQTT Solar Charger - device list](/screenshots/solar-charger_device_list.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_1.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_2.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_3.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_4.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_5.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_6.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_7.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_8.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_9.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_10.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_11.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_12.png)
![MQTT Solar Charger - device list - mqtt solar-charger](/screenshots/solar-charger_device_list_mqtt-solar-charger_13.png)

</details>


## Supporting/Sponsoring this project

You like the project and you want to support me?

[<img src="https://github.md0.eu/uploads/donate-button.svg" height="50">](https://www.paypal.com/donate/?hosted_button_id=3NEVZBDM5KABW)
