# Sentinel Watchlists

## Overview

This directory documents the Watchlists used by the Microsoft Sentinel laboratory.

The project uses the `GeoIP_List` Watchlist to enrich source IP addresses extracted from failed SSH authentication events with geographic information.

---

## GeoIP_List

`GeoIP_List` contains IPv4 network ranges and their associated geographic information.

The data originates from the IP2Location LITE DB11 dataset and is processed before being uploaded to Microsoft Sentinel.

The Watchlist uses the following fields:

| Field | Description |
|---|---|
| `network` | IPv4 network used for IP matching |
| `country` | Country associated with the network |
| `region` | Region associated with the network |
| `city` | City associated with the network |
| `latitude` | Geographic latitude |
| `longitude` | Geographic longitude |

---

## Usage

The Watchlist is queried from KQL using:

```kusto
_GetWatchlist("GeoIP_List")