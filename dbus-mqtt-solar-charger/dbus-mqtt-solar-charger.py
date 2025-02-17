#!/usr/bin/env python

from gi.repository import GLib  # pyright: ignore[reportMissingImports]
import platform
import logging
import sys
import os
from time import sleep, time
import json
import configparser  # for config/ini file
import _thread

# import external packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "ext"))
import paho.mqtt.client as mqtt

# import Victron Energy packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "ext", "velib_python"))
from vedbus import VeDbusService  # noqa: E402
from ve_utils import get_vrm_portal_id  # noqa: E402


# get values from config.ini file
try:
    config_file = (os.path.dirname(os.path.realpath(__file__))) + "/config.ini"
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        if config["MQTT"]["broker_address"] == "IP_ADDR_OR_FQDN":
            print('ERROR:The "config.ini" is using invalid default values like IP_ADDR_OR_FQDN. The driver restarts in 60 seconds.')
            sleep(60)
            sys.exit()
    else:
        print('ERROR:The "' + config_file + '" is not found. Did you copy or rename the "config.sample.ini" to "config.ini"? The driver restarts in 60 seconds.')
        sleep(60)
        sys.exit()

except Exception:
    exception_type, exception_object, exception_traceback = sys.exc_info()
    file = exception_traceback.tb_frame.f_code.co_filename
    line = exception_traceback.tb_lineno
    print(f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}")
    print("ERROR:The driver restarts in 60 seconds.")
    sleep(60)
    sys.exit()


# Get logging level from config.ini
# ERROR = shows errors only
# WARNING = shows ERROR and warnings
# INFO = shows WARNING and running functions
# DEBUG = shows INFO and data/values
if "DEFAULT" in config and "logging" in config["DEFAULT"]:
    if config["DEFAULT"]["logging"] == "DEBUG":
        logging.basicConfig(level=logging.DEBUG)
    elif config["DEFAULT"]["logging"] == "INFO":
        logging.basicConfig(level=logging.INFO)
    elif config["DEFAULT"]["logging"] == "ERROR":
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.WARNING)


# get timeout
if "DEFAULT" in config and "timeout" in config["DEFAULT"]:
    timeout = int(config["DEFAULT"]["timeout"])
else:
    timeout = 60


# get history days
if "DEFAULT" in config and "history_days" in config["DEFAULT"]:
    history_days = int(config["DEFAULT"]["history_days"])
else:
    history_days = 0


# set variables
connected = 0
last_changed = 0
last_updated = 0


# formatting
def _a(p, v):
    return str("%.1f" % v) + "A"


def _n(p, v):
    return str("%i" % v)


def _s(p, v):
    return str("%s" % v)


def _v(p, v):
    return str("%.2f" % v) + "V"


def _w(p, v):
    return str("%i" % v) + "W"


def _kwh(p, v):
    return str("%i" % v) + "kWh"


solar_charger_dict = {
    # general data
    "/NrOfTrackers": {"value": None, "textformat": _n},
    "/Pv/V": {"value": None, "textformat": _v},
    "/Pv/0/V": {"value": None, "textformat": _v},
    "/Pv/1/V": {"value": None, "textformat": _v},
    "/Pv/2/V": {"value": None, "textformat": _v},
    "/Pv/3/V": {"value": None, "textformat": _v},
    "/Pv/0/P": {"value": None, "textformat": _w},
    "/Pv/1/P": {"value": None, "textformat": _w},
    "/Pv/2/P": {"value": None, "textformat": _w},
    "/Pv/3/P": {"value": None, "textformat": _w},
    "/Yield/Power": {"value": None, "textformat": _w},
    # external control
    "/Link/NetworkMode": {"value": None, "textformat": _s},
    "/Link/BatteryCurrent": {"value": None, "textformat": _a},
    "/Link/ChargeCurrent": {"value": None, "textformat": _a},
    "/Link/ChargeVoltage": {"value": None, "textformat": _v},
    "/Link/NetworkStatus": {"value": None, "textformat": _s},
    "/Link/TemperatureSense": {"value": None, "textformat": _n},
    "/Link/TemperatureSenseActive": {"value": None, "textformat": _n},
    "/Link/VoltageSense": {"value": None, "textformat": _n},
    "/Link/VoltageSenseActive": {"value": None, "textformat": _n},
    # settings
    "/Settings/BmsPresent": {"value": None, "textformat": _n},
    "/Settings/ChargeCurrentLimit": {"value": None, "textformat": _n},
    # other paths
    "/Dc/0/Voltage": {"value": None, "textformat": _v},
    "/Dc/0/Current": {"value": None, "textformat": _a},
    "/Yield/User": {"value": None, "textformat": _kwh},
    "/Yield/System": {"value": None, "textformat": _kwh},
    "/Load/State": {"value": None, "textformat": _n},
    "/Load/I": {"value": None, "textformat": _a},
    "/ErrorCode": {"value": 0, "textformat": _n},
    "/State": {"value": 0, "textformat": _n},
    "/Mode": {"value": None, "textformat": _n},
    "/MppOperationMode": {"value": None, "textformat": _n},
    "/DeviceOffReason": {"value": None, "textformat": _s},
    "/Relay/0/State": {"value": None, "textformat": _n},
    # alarms
    "/Alarms/LowVoltage": {"value": None, "textformat": _n},
    "/Alarms/HighVoltage": {"value": None, "textformat": _n},
    # history
    "/History/Overall/DaysAvailable": {"value": history_days, "textformat": _n},
    "/History/Overall/MaxPvVoltage": {"value": None, "textformat": _n},
    "/History/Overall/MaxBatteryVoltage": {"value": None, "textformat": _n},
    "/History/Overall/MinBatteryVoltage": {"value": None, "textformat": _n},
    "/History/Overall/LastError1": {"value": None, "textformat": _n},
    "/History/Overall/LastError2": {"value": None, "textformat": _n},
    "/History/Overall/LastError3": {"value": None, "textformat": _n},
    "/History/Overall/LastError4": {"value": None, "textformat": _n},
}


# create history keys
if history_days > 0:
    for day in range(history_days):
        solar_charger_dict.update(
            {
                # history daily
                "/History/Daily/" + str(day) + "/Yield": {"value": None, "textformat": _w},
                "/History/Daily/" + str(day) + "/Consumption": {"value": None, "textformat": _kwh},
                "/History/Daily/" + str(day) + "/MaxPower": {"value": None, "textformat": _w},
                "/History/Daily/" + str(day) + "/MaxPvVoltage": {"value": None, "textformat": _v},
                "/History/Daily/" + str(day) + "/MinBatteryVoltage": {"value": None, "textformat": _v},
                "/History/Daily/" + str(day) + "/MaxBatteryVoltage": {"value": None, "textformat": _v},
                "/History/Daily/" + str(day) + "/MaxBatteryCurrent": {"value": None, "textformat": _a},
                "/History/Daily/" + str(day) + "/TimeInBulk": {"value": None, "textformat": _n},
                "/History/Daily/" + str(day) + "/TimeInAbsorption": {"value": None, "textformat": _n},
                "/History/Daily/" + str(day) + "/TimeInFloat": {"value": None, "textformat": _n},
                "/History/Daily/" + str(day) + "/LastError1": {"value": None, "textformat": _n},
                "/History/Daily/" + str(day) + "/LastError2": {"value": None, "textformat": _n},
                "/History/Daily/" + str(day) + "/LastError3": {"value": None, "textformat": _n},
                "/History/Daily/" + str(day) + "/LastError4": {"value": None, "textformat": _n},
                "/History/Daily/" + str(day) + "/Pv/0/Yield": {"value": None, "textformat": _kwh},
                "/History/Daily/" + str(day) + "/Pv/0/MaxPower": {"value": None, "textformat": _w},
                "/History/Daily/" + str(day) + "/Pv/0/MaxVoltage": {"value": None, "textformat": _v},
                "/History/Daily/" + str(day) + "/Pv/1/Yield": {"value": None, "textformat": _kwh},
                "/History/Daily/" + str(day) + "/Pv/1/MaxPower": {"value": None, "textformat": _w},
                "/History/Daily/" + str(day) + "/Pv/1/MaxVoltage": {"value": None, "textformat": _v},
                "/History/Daily/" + str(day) + "/Pv/2/Yield": {"value": None, "textformat": _kwh},
                "/History/Daily/" + str(day) + "/Pv/2/MaxPower": {"value": None, "textformat": _w},
                "/History/Daily/" + str(day) + "/Pv/2/MaxVoltage": {"value": None, "textformat": _v},
                "/History/Daily/" + str(day) + "/Pv/3/Yield": {"value": None, "textformat": _kwh},
                "/History/Daily/" + str(day) + "/Pv/3/MaxPower": {"value": None, "textformat": _w},
                "/History/Daily/" + str(day) + "/Pv/3/MaxVoltage": {"value": None, "textformat": _v},
            }
        )


def elaborateData(items, key_root, level=0):
    global solar_charger_dict

    for key_1, data_1 in items.items():
        key = key_root + "/" + key_1
        if type(data_1) is dict:
            elaborateData(data_1, key, level=level + 1)

        else:
            if key in solar_charger_dict and (type(data_1) is str or type(data_1) is int or type(data_1) is float):
                solar_charger_dict[key]["value"] = data_1
            else:
                logging.warning('Received key "' + str(key) + '" with value "' + str(data_1) + '" is not valid')


# MQTT requests
def on_disconnect(client, userdata, flags, reason_code, properties):
    global connected
    logging.warning("MQTT client: Got disconnected")
    if reason_code != 0:
        logging.warning("MQTT client: Unexpected MQTT disconnection. Will auto-reconnect")
    else:
        logging.warning("MQTT client: reason_code value:" + str(reason_code))

    while connected == 0:
        try:
            logging.warning(f"MQTT client: Trying to reconnect to broker {config['MQTT']['broker_address']} on port {config['MQTT']['broker_port']}")
            client.connect(host=config["MQTT"]["broker_address"], port=int(config["MQTT"]["broker_port"]))
            connected = 1
        except Exception as err:
            logging.error(f"MQTT client: Error in retrying to connect with broker ({config['MQTT']['broker_address']}:{config['MQTT']['broker_port']}): {err}")
            logging.error("MQTT client: Retrying in 15 seconds")
            connected = 0
            sleep(15)


def on_connect(client, userdata, flags, reason_code, properties):
    global connected
    if reason_code == 0:
        logging.info("MQTT client: Connected to MQTT broker!")
        connected = 1
        client.subscribe(config["MQTT"]["topic"])
    else:
        logging.error("MQTT client: Failed to connect, return code %d\n", reason_code)


def on_message(client, userdata, msg):
    try:
        global solar_charger_dict, last_changed

        # get JSON from topic
        if msg.topic == config["MQTT"]["topic"]:
            if msg.payload != "" and msg.payload != b"":
                jsonpayload = json.loads(msg.payload)

                last_changed = int(time())

                if (
                    ("Pv" in jsonpayload and "V" in jsonpayload["Pv"] and "Yield" in jsonpayload and "Power" in jsonpayload["Yield"])
                    or (
                        "Pv" in jsonpayload
                        and "0" in jsonpayload["Pv"]
                        and "V" in jsonpayload["Pv"]["0"]
                        and "P" in jsonpayload["Pv"]["0"]
                        and "1" in jsonpayload["Pv"]
                        and "V" in jsonpayload["Pv"]["1"]
                        and "P" in jsonpayload["Pv"]["1"]
                    )
                    and "Dc" in jsonpayload
                    and "0" in jsonpayload["Dc"]
                    and "Current" in jsonpayload["Dc"]["0"]
                    and "Voltage" in jsonpayload["Dc"]["0"]
                ):
                    # save JSON data into solar_charger_dict
                    elaborateData(jsonpayload, "")

                    # ------ calculate possible values if missing -----
                    nr_of_trackers = 0
                    yield_power = 0
                    if "Pv" in jsonpayload and "0" in jsonpayload["Pv"] and "P" in jsonpayload["Pv"]["0"]:
                        nr_of_trackers += 1
                        yield_power += jsonpayload["Pv"]["0"]["P"]
                    if "Pv" in jsonpayload and "1" in jsonpayload["Pv"] and "P" in jsonpayload["Pv"]["1"]:
                        nr_of_trackers += 1
                        yield_power += jsonpayload["Pv"]["1"]["P"]
                    if "Pv" in jsonpayload and "2" in jsonpayload["Pv"] and "P" in jsonpayload["Pv"]["2"]:
                        nr_of_trackers += 1
                        yield_power += jsonpayload["Pv"]["2"]["P"]
                    if "Pv" in jsonpayload and "3" in jsonpayload["Pv"] and "P" in jsonpayload["Pv"]["3"]:
                        nr_of_trackers += 1
                        yield_power += jsonpayload["Pv"]["3"]["P"]

                    # calculate number of mppt trackers, if not set
                    if "NrOfTrackers" not in jsonpayload and nr_of_trackers > 0:
                        solar_charger_dict["/NrOfTrackers"]["value"] = nr_of_trackers
                    else:
                        solar_charger_dict["/NrOfTrackers"]["value"] = 1

                    # calculate total power, if multiple trackers set, but total yield power not
                    if "Yield" not in jsonpayload or ("Yield" in jsonpayload and "Power" not in jsonpayload["Yield"]):
                        solar_charger_dict["/Yield/Power"]["value"] = yield_power

                    # set state, if not set
                    if "State" not in jsonpayload:
                        if solar_charger_dict["/Yield/Power"]["value"] > 0:
                            solar_charger_dict["/State"]["value"] = 3
                        else:
                            solar_charger_dict["/State"]["value"] = 0

                else:
                    logging.warning("Received JSON doesn't contain minimum required values")
                    logging.warning('Example: {"Pv": { "V": 0.0 }, "Yield": {"Power": 0.0 }, "Dc": { "0": { "Voltage": 0.0, "Current": 0.0 } } }')
                    logging.warning("OR")
                    logging.warning('Example: { "Pv": { "0": { "V": 0.0, "P": 0.0 }, "1": { "V": 0.0, "P": 0.0 } }, "Yield": { "Power": 142.4 }, "Dc": { "0": { "Voltage": 0.0, "Current": 0.0 } } }')
                    logging.debug("MQTT payload: " + str(msg.payload)[1:])

            else:
                logging.warning("Received message was empty and therefore it was ignored")
                logging.debug("MQTT payload: " + str(msg.payload)[1:])

    except TypeError as e:
        logging.error("Received message is not valid. Check the README and sample payload. %s" % e)
        logging.debug("MQTT payload: " + str(msg.payload)[1:])

    except ValueError as e:
        logging.error("Received message is not a valid JSON. Check the README and sample payload. %s" % e)
        logging.debug("MQTT payload: " + str(msg.payload)[1:])

    except Exception:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        file = exception_traceback.tb_frame.f_code.co_filename
        line = exception_traceback.tb_lineno
        logging.error(f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}")
        logging.debug("MQTT payload: " + str(msg.payload)[1:])


class DbusMqttSolarChargerService:
    def __init__(
        self,
        servicename,
        deviceinstance,
        paths,
        productname="MQTT Solar Charger",
        customname="MQTT Solar Charger",
        connection="MQTT Solar Charger service",
    ):
        self._dbusservice = VeDbusService(servicename, register=False)
        self._paths = paths

        logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path("/Mgmt/ProcessName", __file__)
        self._dbusservice.add_path(
            "/Mgmt/ProcessVersion",
            "Unkown version, and running on Python " + platform.python_version(),
        )
        self._dbusservice.add_path("/Mgmt/Connection", connection)

        # Create the mandatory objects
        self._dbusservice.add_path("/DeviceInstance", deviceinstance)
        self._dbusservice.add_path("/ProductId", 0xFFFF)
        self._dbusservice.add_path("/ProductName", productname)
        self._dbusservice.add_path("/CustomName", customname)
        self._dbusservice.add_path("/FirmwareVersion", 399)
        self._dbusservice.add_path("/HardwareVersion", "1.0.4 (20250217)")
        self._dbusservice.add_path("/Connected", 1)

        self._dbusservice.add_path("/Latency", None)

        for path, settings in self._paths.items():
            self._dbusservice.add_path(
                path,
                settings["value"],
                gettextcallback=settings["textformat"],
                writeable=True,
                onchangecallback=self._handlechangedvalue,
            )

        # register VeDbusService after all paths where added
        self._dbusservice.register()

        GLib.timeout_add(1000, self._update)  # pause 1000ms before the next request

    def _update(self):
        global solar_charger_dict, last_changed, last_updated

        now = int(time())

        if last_changed != last_updated:
            for setting, data in solar_charger_dict.items():
                try:
                    self._dbusservice[setting] = data["value"]

                except TypeError as e:
                    logging.error('Received key "' + setting + '" with value "' + str(data["value"]) + '" is not valid: ' + str(e))
                    sys.exit()

                except Exception:
                    (
                        exception_type,
                        exception_object,
                        exception_traceback,
                    ) = sys.exc_info()
                    file = exception_traceback.tb_frame.f_code.co_filename
                    line = exception_traceback.tb_lineno
                    logging.error(f"Exception occurred: {repr(exception_object)} of type {exception_type} in {file} line #{line}")

            logging.info(
                "Solar Charger: {:.2f} W".format(
                    solar_charger_dict["/Yield/Power"]["value"],
                )
            )

            last_updated = last_changed

        # quit driver if timeout is exceeded
        if timeout != 0 and (now - last_changed) > timeout:
            logging.error("Driver stopped. Timeout of %i seconds exceeded, since no new MQTT message was received in this time." % timeout)
            sys.exit()

        # increment UpdateIndex - to show that new data is available
        index = self._dbusservice["/UpdateIndex"] + 1  # increment index
        if index > 255:  # maximum value of the index
            index = 0  # overflow from 255 to 0
        self._dbusservice["/UpdateIndex"] = index
        return True

    def _handlechangedvalue(self, path, value):
        logging.debug("someone else updated %s to %s" % (path, value))
        return True  # accept the change


def main():
    _thread.daemon = True  # allow the program to quit

    from dbus.mainloop.glib import (
        DBusGMainLoop,
    )  # pyright: ignore[reportMissingImports]

    # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
    DBusGMainLoop(set_as_default=True)

    # MQTT setup
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="MqttSolarCharger_" + get_vrm_portal_id() + "_" + str(config["DEFAULT"]["device_instance"]))
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect
    client.on_message = on_message

    # check tls and use settings, if provided
    if "tls_enabled" in config["MQTT"] and config["MQTT"]["tls_enabled"] == "1":
        logging.info("MQTT client: TLS is enabled")

        if "tls_path_to_ca" in config["MQTT"] and config["MQTT"]["tls_path_to_ca"] != "":
            logging.info('MQTT client: TLS: custom ca "%s" used' % config["MQTT"]["tls_path_to_ca"])
            client.tls_set(config["MQTT"]["tls_path_to_ca"], tls_version=2)
        else:
            client.tls_set(tls_version=2)

        if "tls_insecure" in config["MQTT"] and config["MQTT"]["tls_insecure"] != "":
            logging.info("MQTT client: TLS certificate server hostname verification disabled")
            client.tls_insecure_set(True)

    # check if username and password are set
    if "username" in config["MQTT"] and "password" in config["MQTT"] and config["MQTT"]["username"] != "" and config["MQTT"]["password"] != "":
        logging.info('MQTT client: Using username "%s" and password to connect' % config["MQTT"]["username"])
        client.username_pw_set(username=config["MQTT"]["username"], password=config["MQTT"]["password"])

    # connect to broker
    logging.info(f"MQTT client: Connecting to broker {config['MQTT']['broker_address']} on port {config['MQTT']['broker_port']}")
    client.connect(host=config["MQTT"]["broker_address"], port=int(config["MQTT"]["broker_port"]))
    client.loop_start()

    # wait to receive first data, else the JSON is empty and phase setup won't work
    i = 0
    while solar_charger_dict["/Yield/Power"]["value"] is None:
        if i % 12 != 0 or i == 0:
            logging.info("Waiting 5 seconds for receiving first data...")
        else:
            logging.warning("Waiting since %s seconds for receiving first data..." % str(i * 5))

        # check if timeout was exceeded
        if timeout != 0 and timeout <= (i * 5):
            logging.error("Driver stopped. Timeout of %i seconds exceeded, since no new MQTT message was received in this time." % timeout)
            sys.exit()

        sleep(5)
        i += 1

    paths_dbus = {
        "/UpdateIndex": {"value": 0, "textformat": _n},
    }
    paths_dbus.update(solar_charger_dict)

    DbusMqttSolarChargerService(
        servicename="com.victronenergy.solarcharger.mqtt_solarcharger_" + str(config["DEFAULT"]["device_instance"]),
        deviceinstance=int(config["DEFAULT"]["device_instance"]),
        customname=config["DEFAULT"]["device_name"],
        paths=paths_dbus,
    )

    logging.info("Connected to dbus and switching over to GLib.MainLoop() (= event based)")
    mainloop = GLib.MainLoop()
    mainloop.run()


if __name__ == "__main__":
    main()
