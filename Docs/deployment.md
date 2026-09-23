# Deployment

## Overview

This document describes the deployment process of the Azure Sentinel SOC laboratory.

The environment was built to simulate a Linux endpoint generating SSH authentication events and to centralize, detect, enrich, and visualize those events using Microsoft Sentinel.

---

## 1. Azure Environment

The laboratory was deployed using an Azure for Students subscription.

### Main Azure resources

--------------------------------------------------------
| Resource                  |           Name           |
|---------------------------|--------------------------|
| Resource Group            |        `JM-SOC-LAB`      |
| Linux VM                  |        `Agency-JM`       |
| Operating System          |         Debian 11        |
| VM Region                 |       Mexico Central     |
| Log Analytics Workspace   |       `workspace-soc`    |
| Microsoft Sentinel        |          Enabled         |
| Data Collection Rule      |       `DCR-.SOC-LAB`     |
| GeoIP Watchlist           |         `GeoIP_List`     |
--------------------------------------------------------

The Linux virtual machine acts as the monitored endpoint, while Microsoft Sentinel provides the SIEM capabilities used for detection and investigation.

---

## 2. Linux Endpoint Deployment

A Debian 11 virtual machine was deployed in Azure to serve as the monitored Linux endpoint.

The endpoint uses OpenSSH to generate authentication events that can be collected and analyzed by the SOC platform.

### Network configuration

The virtual machine was deployed inside an Azure virtual network and associated with a Network Security Group.

Because the endpoint is intentionally used to generate security events, network exposure must be carefully controlled.

For a real environment, SSH access should be restricted to trusted source IP addresses or a VPN instead of allowing unrestricted Internet access.

---

## 3. Syslog Configuration

The Linux endpoint uses `rsyslog` to process system logs.

The SSH authentication events are written to:

```text
/var/log/auth.log

```

The service was verified with:

```bash
sudo systemctl status rsyslog

```

Authentication events can be inspected locally with:

```bash
sudo tail -n 20 /var/log/auth.log

```

Failed SSH authentication attempts can be identified with:

```bash
sudo grep "Failed password" /var/log/auth.log

```

This confirms that the Linux endpoint is generating the events required for the detection pipeline.

---

## 4. Azure Monitor Agent

The Azure Monitor Agent (AMA) was installed on the Debian virtual machine.

AMA acts as the collection agent responsible for forwarding supported Linux logs to Azure Monitor.

The agent runs alongside the Linux logging infrastructure and forwards the collected Syslog events according to the configured Data Collection Rule.

The agent can be verified on the endpoint by checking its running processes and services.

---

## 5. Log Analytics Workspace

A Log Analytics workspace named:

```text
workspace-soc

```

was created to store and query the collected telemetry.

Microsoft Sentinel was subsequently enabled on this workspace.

The workspace provides the central location where the Linux Syslog events become available for investigation using Kusto Query Language (KQL).

---

## 6. Data Collection Rule

A Data Collection Rule (DCR) named:

```text
DCR-.SOC-LAB

```

was configured to collect Linux Syslog events.

The rule was configured to collect the following facilities:

```text
auth
authpriv

```

The following log levels were included:

```text
Info
Notice
Warning
Error
Critical
Alert
Emergency

```

The collected events are sent to the `workspace-soc` Log Analytics workspace through the `Microsoft-Syslog` data stream.

The repository contains sanitized copies of the DCR configuration under:

```text
Azure/DCR/

```

---

## 7. DCR Association

The Data Collection Rule was associated with the `Agency-JM` virtual machine.

The resulting data flow is:

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
DCR-.SOC-LAB
      |
      v
Log Analytics
      |
      v
Microsoft Sentinel

```

This association allows the Azure Monitor Agent running on the Linux endpoint to use the configured collection rule.

---

## 8. Verifying Syslog Ingestion

After configuring AMA and the DCR, a controlled failed SSH authentication attempt was generated against the Linux endpoint.

The local endpoint was first checked to confirm that the event was generated:

```bash
sudo grep "Failed password" /var/log/auth.log | tail -20

```

The same event was then searched for in Microsoft Sentinel using KQL:

```kusto
Syslog
| where TimeGenerated > ago(30m)
| where ProcessName == "sshd"
| where SyslogMessage has "Failed password"
| project TimeGenerated, Computer, SyslogMessage
| order by TimeGenerated desc
```

A successful result confirms that the complete telemetry pipeline is operational.

---

## 9. SSH Detection

The first detection objective was identifying failed SSH authentication attempts.

The relevant SSH event contains information such as:

- Timestamp
- Username
- Source IP address
- Authentication method
- SSH process
- Target system

The source IP address can be extracted from the raw Syslog message using KQL.

Example:

```kusto
Syslog
| where TimeGenerated > ago(30m)
| where ProcessName == "sshd"
| where SyslogMessage has "Failed password"
| extend AttackerIP = extract(@"from\s+((?:\d{1,3}\.){3}\d{1,3})", 1, SyslogMessage)
| where isnotempty(AttackerIP)
```

This transforms the raw SSH event into structured information that can be used for further investigation.

---

## 10. GeoIP Enrichment

After extracting the source IP address, the IP was enriched with geographic information using a Microsoft Sentinel Watchlist.

The watchlist is named:

```text
GeoIP_List

```

It contains CIDR network ranges and associated geographic information.

The main fields are:

```text
network
country
region
city
latitude
longitude

```

The IP address extracted from the SSH event is matched against the CIDR ranges using:

```kusto
evaluate ipv4_lookup()

```

This allows the detection pipeline to associate an observed source IP with geographic information without manually adding individual attacker IP addresses.

The GeoIP database itself is not included in the repository due to its size. The repository contains the conversion script and documentation used to prepare the data.

---

## 11. Geographic Visualization

The enriched SSH events were used to create a Microsoft Sentinel Workbook displaying the geographic distribution of observed source IP addresses.

The visualization uses:

- Latitude
- Longitude
- Failure count
- Friendly geographic location

The resulting map provides a visual representation of the source locations associated with the observed SSH authentication failures.

The Workbook configuration is stored in:

```text
Sentinel/WorkBooks/

```

---

## 12. Validation

The laboratory was validated through the following workflow:

1. Generate a controlled failed SSH authentication attempt.
2. Confirm the event in `/var/log/auth.log`.
3. Confirm the event reaches Microsoft Sentinel.
4. Filter the event using the `sshd` process.
5. Extract the source IP address.
6. Enrich the IP using the `GeoIP_List` Watchlist.
7. Display the resulting geographic information in a Sentinel Workbook.

This validates the complete pipeline from endpoint telemetry to SIEM investigation and visualization.

---

## 13. Security Considerations

This laboratory uses an intentionally monitored Linux endpoint and should not be treated as a production architecture.

The following practices are recommended:

- Restrict SSH access to trusted source IP addresses.
- Avoid exposing administrative services unnecessarily.
- Do not store credentials or secrets in the repository.
- Do not publish SSH private keys.
- Review Azure resource identifiers before publishing the repository.
- Avoid committing subscription credentials, API keys, tokens, or passwords.
- Deallocate or remove unused Azure resources when the laboratory is not being used.

The purpose of the environment is controlled security experimentation and SOC analysis.