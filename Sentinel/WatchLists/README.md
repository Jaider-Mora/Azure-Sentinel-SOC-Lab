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
```

The network field is used with the ipv4_lookup() operator to match an observed IP address against the corresponding IPv4 network.

```kusto
| evaluate ipv4_lookup(_GetWatchlist("GeoIP_List"), AttackerIP, network)
```

The lookup adds the geographic information associated with the matching network to the SSH authentication event.

## Data Flow

The Watchlist is part of the following enrichment process:

```text
Failed SSH Authentication
        |
        v
Source IP Extraction
        |
        v
AttackerIP
        |
        v
GeoIP_List
        |
        v
IPv4 Network Lookup
        |
        v
Geographic Information
        |
        v
SSH Attack Visualization
```

## Data Preparation

The data uploaded to GeoIP_List is generated from the IP2Location LITE DB11 dataset.

The preparation process is documented in:

```text
GeoIP/
├── convertir_geoip.py
├── crear_geoip_watchlist.py
└── optimizar_geoip.py
```

These scripts convert the original IP ranges into CIDR-based network records suitable for the ipv4_lookup() operation.

The resulting structure is:

```text
network,country,region,city,latitude,longitude
```

## Watchlist Role

GeoIP_List is used as reference data.

It does not contain confirmed attacker information and does not determine the identity or physical location of an attacker.

Its purpose is to provide geographic context to IP addresses observed in the security telemetry.