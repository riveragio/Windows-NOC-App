# Windows-NOC-App
## ***Note:*** *this is still under development*
# Network Visibility Monitor (Agentless Smart NOC System)

A lightweight, Windows-based **agentless network visibility monitoring system** designed for small offices, schools, home labs, and basic IT environments.

It provides real-time awareness of devices connected to a local network without requiring:
- SNMP configuration
- Agents on devices
- Credentials or login access
- Modifications on target machines

Instead, it uses **smart active probing and state tracking** to detect network activity.

---

# Project Concept

This system was designed as a **simplified Network Operations Center (NOC) tool** focused on:

> “Instant network visibility without setup complexity.”

Traditional monitoring tools require:
- SNMP setup
- Enterprise routers
- Endpoint agents
- Complex configuration

This project removes all of that and focuses only on:

- What devices are connected?
- Are they online or offline?
- When did they join or leave?
- Is the network stable?

---

# How the System Works (Architecture)

## 1. Network Discovery Phase
When the app starts:

- User inputs a network range (example: `192.168.1.0/24`)
- System scans available IPs in the subnet
- Uses lightweight TCP probing (no CMD or external tools)

---

## 2. Smart Scanning Engine

Instead of constantly scanning everything:

### First Scan:
- Full network scan

### Next Scans:
- Only previously detected devices
- Gateway monitoring
- Newly detected IPs

This reduces CPU usage and improves performance.

---

## 3. Device State Tracking

The system stores previous scan results and compares them:

| Event Type | Description |
|------------|-------------|
| NEW DEVICE | Device appears for first time |
| OFFLINE | Device stops responding |
| ONLINE | Device reconnects |

This creates a **network activity timeline**.

---

## 4. Visualization Layer

The system displays:

- Live device table
- Online / Offline status
- Device type classification
- Pie chart (network health overview)
- Timeline of network events

---

## 5. Reporting Layer

The system exports:

- CSV reports (raw data logs)
- PDF reports (formatted network summary)

---

# Features

## Core Features
- Real-time network scanning
- Smart scan (incremental updates)
- No SNMP required
- No agents required
- Fully Windows-compatible

---

## Monitoring Features
- Online / Offline detection
- Device join detection
- Device leave detection
- Network state tracking
- Gateway monitoring

---

## Visualization Features
- Live pie chart (Online vs Offline)
- Device status table
- Color-coded indicators
- Event timeline dashboard

---

## Device Classification
- Windows PC detection (heuristic)
- Linux device detection
- Router detection
- Mobile device detection
- Unknown device fallback

---

## Export Features
- Export to CSV
- Export to PDF report
- Timestamped logs

---

# Technology Stack

- Python 3.x
- PySide6 (GUI + Charts)
- ReportLab (PDF generation)
- socket (network probing)
- threading / QThread (background scanning)
- ipaddress (network parsing)

---

# Project Structure

```text
network-visibility-monitor/
│
├── app.py               # Main application source code
├── config.json          # Stores saved network range
├── README.md            # Documentation
├── dist/                # Compiled EXE output
└── assets/              # Icons, screenshots (optional)
