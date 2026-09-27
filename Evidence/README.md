# Evidence

## Overview

This directory contains screenshots collected during the implementation and validation of the Microsoft Sentinel SOC laboratory.

The evidence documents the main stages of the telemetry pipeline, from the Linux virtual machine and Azure Monitor Agent configuration to SSH attack detection, GeoIP enrichment, and geographic visualization.

---

## Evidence Files

| File | Description |
|---|---|
| `01.azure-vm.png` | Shows the Linux virtual machine used as the monitored endpoint in Azure. |
| `02.ama-running.png` | Shows the Azure Monitor Agent running on the Linux endpoint. |
| `03.dcr.png` | Shows the Data Collection Rule configured for Syslog collection. |
| `03.dcr-data-source.png` | Shows the data source configuration of the Data Collection Rule. |
| `03.dcr-resources.png` | Shows the resources associated with the Data Collection Rule. |
| `04.syslog-ingestion.png` | Shows Linux Syslog events successfully ingested into Microsoft Sentinel. |
| `05.failed-ssh.png` | Shows detected failed SSH authentication attempts. |
| `06.geoip-enrichment.png` | Shows failed SSH events enriched with geographic information. |
| `07.attack-map.png` | Shows the geographic visualization of the detected SSH activity. |

---

## Validation Flow

The evidence follows the main validation sequence of the laboratory:

```text
Azure Linux VM
      |
      v
Azure Monitor Agent
      |
      v
Data Collection Rule
      |
      +--------------------+
      |                    |
      v                    v
Data Sources          Resources
      |
      v
Syslog Ingestion
      |
      v
Failed SSH Detection
      |
      v
GeoIP Enrichment
      |
      v
Attack Map
```

---

## Purpose

The evidence is included to document the practical implementation of the laboratory and provide visual verification of the main components and results.

The screenshots complement the technical documentation, KQL queries, configuration files, and architecture documentation contained in the repository.
