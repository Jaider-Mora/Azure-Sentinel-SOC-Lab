The SSH Attack Intelligence Dashboard in Microsoft Sentinel collects failed ‘sshd’ attempts on an endpoint, extracts the IP addresses of each attacker, and then processes this data alongside Syslog events to generate a heat map.  

## 1. Porpuse 
---

The Microsoft Sentinel guide allows you to save and interact with the data from the monitoring list so that you can later generate a geographic heat map, with a higher volume representing the IP addresses most frequently used by attackers and a lower volume representing the IP addresses used less frequently.

It processes failed SSH authentication events, extracts attacker IP addresses, enriches them with geographic information, and displays the resulting locations on a map.

The dashboard is intended for:

    Security monitoring.

    Incident investigation.

    Attack source visualization.

    Geographic enrichment of IP addresses.

    SOC laboratory demonstrations.

## 2. Data flow
---

```text
Linux Endpoint
      |
      v
rsyslog
      |
      v
Azure Monitor Agent
      |
      v
DCR-.SOC-LAB    --> Data Collection Rule
      |
      v
Log Analytics
      |
      v
Microsoft Sentinel
Syslog
      │
      ▼
Failed SSH Authentication
      │
      ▼
Attacker IP Extraction
      │
      ▼
    GeoIP Lookup
      │
      ▼
Geographic Enrichment
      │
      ▼
SSH Attack Intelligence Dashboard

```    

## 3. Data Sources
---

The dashboard uses the following Sentinel resources:

| Resource | Purpose |
|---|---|
| `workspace-soc` | Stores the collected Syslog events |
| `GeoIP_List` | Provides geographic information for IPv4 networks |
| `Syslog` | Contains Linux authentication events |
| `sshd` | Identifies SSH authentication events |


## 4. Detection Logic
---

The dashboard searches for failed SSH authentication attempts within the previous 30 days.

The relevant events are identified using:

```kusto
Syslog
| where TimeGenerated > ago(30d)
| where ProcessName == "sshd"
| where SyslogMessage has "Failed password"

```

The attacker IP address is extracted from the Syslog message:

```kusto

| extend AttackerIP = extract(@"from\s+((?:\d{1,3}\.){3}\d{1,3})", 1, SyslogMessage)

```

Only events containing a successfully extracted IP address are processed.

## 5. GeoIP Enrichment
---

The extracted IP addresses are matched against the GeoIP_List Watchlist using the ipv4_lookup() operator.

```kusto

| evaluate ipv4_lookup(_GetWatchlist("GeoIP_List"), AttackerIP, network)

```

The geographic information returned by the lookup includes:

    Country.

    Region.

    City.

    Latitude.

    Longitude.

The coordinates are converted to numeric values before being used by the map:

```kusto

| extend Lat = todouble(latitude)
| extend Lon = todouble(longitude)

```

## 6. Attack Aggregation
---

The dashboard groups failed authentication attempts by attacker IP and geographic location.

```kusto 

| summarize FailureCount = count() by AttackerIP, Lat, Lon, city, country

```

This allows the visualization to represent the relative number of failed authentication attempts associated with each IP address.

The location label is generated using:

```kusto

| extend friendly_location = strcat(city, " (", country, ")")

```

## 7. Complete KQL Query
---

The following query is used by the dashboard:

```kusto
Syslog
| where TimeGenerated > ago(30d)
| where ProcessName == "sshd"
| where SyslogMessage has "Failed password"
| extend AttackerIP = extract(@"from\s+((?:\d{1,3}\.){3}\d{1,3})", 1, SyslogMessage)
| where isnotempty(AttackerIP)
| evaluate ipv4_lookup(_GetWatchlist("GeoIP_List"), AttackerIP, network)
| extend Lat = todouble(latitude)
| extend Lon = todouble(longitude)
| where isnotnull(Lat) and isnotnull(Lon)
| summarize FailureCount = count() by AttackerIP, Lat, Lon, city, country
| extend friendly_location = strcat(city, " (", country, ")")
| project FailureCount, AttackerIP, Lat, Lon, city, country, friendly_location
| order by FailureCount desc
| render scatterchart with (kind = map)

```

## 8. Map Configuration
---

The Workbook uses a geographic map visualization based on latitude and longitude.

| Map Setting         | Value                    |
|---------------------|--------------------------|
| Setting Information | Latitude and Longitude   |
| Latitude            | `Lat`                    |
| Longitude           | `Lon`                    |
| Size                | `FailureCount`           |
| Size Aggregation    | `Sum`                    |
| Label               | `friendly_location`      |

The map marker size is based on the number of failed SSH authentication attempts associated with each attacker IP.

## 9. Workbook JSON
---

The Workbook configuration is exported and stored in the repository:

```
Sentinel/
└── WorkBooks/
    ├── README.md
    └── ssh-attack-map.json
```

The JSON file allows the visualization configuration to be version-controlled and reused as part of the laboratory deployment.

## 10. Interpretation
---

The map provides a geographic representation of the IP addresses associated with failed SSH authentication attempts.

A larger marker indicates a higher number of observed failed authentication attempts for that IP within the selected time window.

The geographic information should be considered an approximation. IP geolocation databases do not necessarily represent the physical location of the individual or system responsible for an attack.

Therefore, geographic information should be treated as contextual enrichment rather than definitive attribution.

## 11. Limitations
---

The dashboard has several limitations:

IP geolocation is approximate.

VPNs, proxies, NAT and cloud infrastructure can affect geographic accuracy.

The dashboard only processes events available in the Log Analytics Workspace.

The current query analyzes a 30-day time window.

Private IP addresses cannot be reliably geolocated through public IP geolocation databases.

Geographic location alone does not establish attacker identity.

## 12. Security Monitoring Value
---

The dashboard demonstrates how raw authentication telemetry can be transformed into contextual security information.

The implemented workflow combines:


Event Detection
      +
IP Extraction
      +
GeoIP Enrichment
      +
Geographic Enrichment
      +
Visualization

