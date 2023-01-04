
[![GitHub Release](https://img.shields.io/github/release/bkbilly/oralb_hacs.svg?style=flat-square)](https://github.com/bkbilly/oralb_hacs/releases)
[![License](https://img.shields.io/github/license/bkbilly/oralb_hacs.svg?style=flat-square)](LICENSE)
[![hacs](https://img.shields.io/badge/HACS-default-orange.svg?style=flat-square)](https://hacs.xyz)


# OralB_hacs
Integrates [OralB](https://oralb.com/en-us/products/shop-all/) Bluetooth Toothbrushes into Home Assistant.

It is using an active connection to communicate with the tootbrush in contrary with the [official](https://www.home-assistant.io/integrations/oralb/) which is using a passive connection. This means that it can get more information, but it uses the [limited connections](https://esphome.io/components/bluetooth_proxy.html) that exist on ESPHome.

Support for Bluetooth toothbrush by OralB which exposes the following sensors:
 - Brush Time in seconds
 - Battery Percentage
 - Selected Mode
 - Operation status

## Installation

Easiest install is via [HACS](https://hacs.xyz/):

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bkbilly&repository=oralb_hacs&category=integration)

`HACS -> Explore & Add Repositories -> OralB_hacs`

HACS does not "configure" the integration for you. You must go to `Configuration > Integrations` and add OralB_hacs after installing via HACS.
