# GeoIP Data Processing

## Overview

This directory contains the scripts and data processing workflow used to prepare IPv4 geolocation data for Microsoft Sentinel.

The process is based on the **IP2Location LITE DB11** dataset and converts the original IP range information into CIDR-based network data that can be used by the Sentinel `ipv4_lookup()` operator.

The GeoIP processing workflow consists of three main stages:

```text
IP2Location LITE DB11
        |
        v
convertir_geoip.py
        |
        v
geoip.csv
        |
        v
optimizar_geoip.py
        |
        v
geoip_optimizado.csv
        |
        v
Sentinel Watchlist
```

An additional script is available when only a specific list of attacker IP addresses needs to be processed:

```text
attackerip_list.txt
        |
        v
crear_geoip_watchlist.py
        |
        v
geoip.csv
```

---

## Source Dataset

The original data source is:

```text
IP2LOCATION-LITE-DB11.CSV
```

This dataset contains IPv4 ranges and associated geographic information.

The relevant fields used by the laboratory are:

| Field       | Description                                  |
| ----------- | -------------------------------------------- |
| `ip_from`   | First IPv4 address represented as an integer |
| `ip_to`     | Last IPv4 address represented as an integer  |
| `country`   | Country associated with the IP range         |
| `region`    | Region associated with the IP range          |
| `city`      | City associated with the IP range            |
| `latitude`  | Geographic latitude                          |
| `longitude` | Geographic longitude                         |

The original dataset uses numeric values to represent the beginning and end of each IPv4 range.

The scripts convert these values into standard IPv4/CIDR notation.

---

## `convertir_geoip.py`

This script converts the complete IP2Location dataset into CIDR-based network records.

### Input

```text
IP2LOCATION-LITE-DB11.CSV
```

### Output

```text
geoip.csv
```

The generated file contains:

```text
network,country,region,city,latitude,longitude
```

For each IP range, the script:

1. Reads the `ip_from` and `ip_to` values.
2. Converts them into IPv4 addresses.
3. Summarizes the address range into CIDR networks.
4. Preserves the associated geographic information.
5. Writes the resulting networks to `geoip.csv`.

The conversion is performed using Python's `ipaddress` module.

The key operation is:

```python
networks = ipaddress.summarize_address_range(start, end)
```

This allows an arbitrary IPv4 range to be represented as one or more CIDR networks.

---

## `crear_geoip_watchlist.py`

This script provides a more targeted processing method.

Instead of processing the entire IP2Location dataset into the output, it receives a list of specific IPv4 addresses and searches for their corresponding geographic information.

### Input

```text
IP2LOCATION-LITE-DB11.CSV
attackerip_list.txt
```

### Output

```text
geoip.csv
```

The IP list contains one IPv4 address per line.

For example:

```text
192.168.1.10
8.8.8.8
181.59.3.218
```

The script validates each address using Python's `ipaddress` module and stores the addresses as integers.

It then searches the IP2Location ranges to determine which range contains each requested IP.

When a match is found, the IP is written as a `/32` network:

```text
181.59.3.218/32
```

The generated record contains:

```text
network,country,region,city,latitude,longitude
```

This approach is useful when the laboratory only needs geographic information for a known set of attacker IP addresses.

---

## `optimizar_geoip.py`

The optimization script reduces the number of records in the generated GeoIP dataset.

### Input

```text
geoip.csv
```

### Output

```text
geoip_optimizado.csv
```

The script compares consecutive network records and checks whether they contain the same geographic information.

Two records can be merged when they have identical:

* Country
* Region
* City
* Latitude
* Longitude

The network ranges are then passed to:

```python
ipaddress.collapse_addresses()
```

If the networks can be represented as a single CIDR network, they are merged into one record.

This reduces the number of entries that need to be stored and processed by the Sentinel Watchlist.

---

## Processing Strategies

The repository therefore supports two different GeoIP preparation strategies.

### Complete Dataset

Used when the complete IP2Location database needs to be converted:

```text
IP2LOCATION-LITE-DB11.CSV
        |
        v
convertir_geoip.py
        |
        v
geoip.csv
        |
        v
optimizar_geoip.py
        |
        v
geoip_optimizado.csv
```

### Targeted IP Processing

Used when only known attacker IP addresses need to be enriched:

```text
attackerip_list.txt
        |
        v
crear_geoip_watchlist.py
        |
        v
geoip.csv
```

The targeted approach avoids processing the entire database when only a limited number of IP addresses are relevant to the investigation.

---

## Sentinel Integration

The resulting CIDR-based data can be uploaded to the `GeoIP_List` Watchlist in Microsoft Sentinel.

The Watchlist uses the following structure:

| Field       | Description                  |
| ----------- | ---------------------------- |
| `network`   | IPv4 network used for lookup |
| `country`   | Country                      |
| `region`    | Region                       |
| `city`      | City                         |
| `latitude`  | Latitude                     |
| `longitude` | Longitude                    |

The KQL queries use the `network` field as the lookup column:

```kusto
| evaluate ipv4_lookup(_GetWatchlist("GeoIP_List"), AttackerIP, network)
```

This allows an attacker IP extracted from an SSH event to be matched against the prepared network data.

---

## Data Flow

The complete GeoIP workflow is:

```text
IP2Location LITE DB11
        |
        v
IP Range Conversion
        |
        v
CIDR Network Generation
        |
        +-----------------------------+
        |                             |
        v                             v
Complete Dataset              Targeted IP List
        |                             |
        v                             v
convertir_geoip.py        crear_geoip_watchlist.py
        |                             |
        +-------------+---------------+
                      |
                      v
                  geoip.csv
                      |
                      v
             optimizar_geoip.py
                      |
                      v
            geoip_optimizado.csv
                      |
                      v
              GeoIP_List
                      |
                      v
              Microsoft Sentinel
```

---

## Limitations

The GeoIP data provides contextual information about an IP address but does not establish the physical location or identity of an attacker.

The resulting geographic information may be affected by:

* VPN infrastructure
* Proxies
* NAT
* Cloud providers
* Hosting providers
* ISP address allocation
* Limitations of the underlying geolocation database

Therefore, GeoIP information is treated as **contextual enrichment for security investigations**, not as definitive attribution.

---

## Directory Structure

```text
GeoIP/
├── IP2LOCATION-LITE-DB11.CSV
├── attackerip_list.txt
├── convertir_geoip.py
├── crear_geoip_watchlist.py
├── optimizar_geoip.py
└── README.md
```

Large source datasets may be excluded from version control depending on their size and licensing requirements.
