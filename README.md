
[![GitHub Release](https://img.shields.io/github/release/t3chguy/pinecil_ble.svg?style=flat-square)](https://github.com/t3chguy/pinecil_ble/releases)
[![License](https://img.shields.io/github/license/t3chguy/pinecil_ble.svg?style=flat-square)](LICENSE)
[![hacs](https://img.shields.io/badge/HACS-default-orange.svg?style=flat-square)](https://hacs.xyz)


# Pinecil_BLE
Integrates [Pinecil V2](https://pine64.com/product/pinecil-smart-mini-portable-soldering-iron/) Soldering Irons into Home Assistant.

Support for Pinecil v2 soldering iron by Pine64 which exposes the following sensors:
  - Tip temperature
  - Set temperature
  - DC voltage
  - Handle temperature
  - Power (PWM)
  - Tip resistance
  - Uptime
  - Max temperature
  - Raw tip voltage
  - Hall effect strength
  - Estimated watts
  - Power source
  - Operating mode

## Installation

Easiest install is via [HACS](https://hacs.xyz/):

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=t3chguy&repository=pinecil_ble&category=integration)

`HACS -> Explore & Add Repositories -> Pinecil_BLE`

HACS does not "configure" the integration for you. You must go to `Configuration > Integrations` and add Pinecil_BLE after installing via HACS.

When adding the integration, enter the Pinecil's BLE MAC in the prompt dialogue.
