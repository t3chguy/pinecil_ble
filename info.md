# OralB-BLE
Integrates [OralB](https://oralb.com/en-us/products/shop-all/) Bluetooth Toothbrushes into Home Assistant.

It is using an active connection to communicate with the tootbrush in contrary with the [official](https://www.home-assistant.io/integrations/oralb/) which is using a passive connection. This means that it can get more information, but it uses the [limited connections](https://esphome.io/components/bluetooth_proxy.html) that exist on ESPHome.

Support for Bluetooth toothbrush by OralB which exposes the following sensors:
 - Brush Time in seconds
 - Battery Percentage
 - Selected Mode
 - Operation status
