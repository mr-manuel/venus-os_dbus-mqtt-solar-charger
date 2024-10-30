# Changelog

## v1.0.4-dev
* Changed: Broker port missing on reconnect
* Changed: Default device instance is now `100`
* Changed: Fixed service not starting sometimes

## v1.0.3
* Changed: Add VRM ID to MQTT client name
* Changed: Fix registration to dbus https://github.com/victronenergy/velib_python/commit/494f9aef38f46d6cfcddd8b1242336a0a3a79563

## v1.0.2
* Changed: Fixed problems when timeout was set to `0`.

## v1.0.1
* Added: Timeout on driver startup. Prevents problems, if the MQTT broker is not reachable on driver startup

## v1.0.0
Initial release
