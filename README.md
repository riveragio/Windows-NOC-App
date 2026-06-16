# Windows-NOC-App
# Network Visibility Monitor (Agentless Smart NOC System)

A lightweight, Windows-based **agentless network visibility monitoring system** designed for small offices, schools, home labs, and basic IT environments.

It provides real-time awareness of devices connected to a local network without requiring:
- SNMP configuration
- Agent installation on endpoints
- Credentials or authentication
- Enterprise network hardware

Instead, it uses **smart active probing and state tracking** to monitor network activity in real time.

---

# Project Concept

This system is a simplified **Network Operations Center (NOC) dashboard** focused on:

- Device visibility
- Network status awareness
- Event tracking (join / leave)
- Real-time monitoring

It is designed for environments where simplicity and immediate setup are more important than enterprise-level depth.

---

# How It Works (System Overview)

## 1. Network Input
User provides a subnet range:

---

## 2. Smart Scanning Engine
- First scan: full subnet discovery
- Next scans: incremental updates only
- Uses lightweight TCP socket probing (no CMD tools)

---

## 3. State Tracking System
The system compares previous and current scans:

- New device detected
- Device went offline
- Device came back online

---

## 4. Visualization Layer
- Live device table
- Online / Offline indicators
- Pie chart (network health)
- Event timeline (join/leave history)

---

## 5. Reporting Layer
- CSV export
- PDF report generation

---

# Features

## Core Features
- Real-time LAN scanning
- Smart incremental scanning
- No SNMP required
- No agents required
- No device-side installation

---

## Monitoring Features
- Online / Offline detection
- Device join detection
- Device leave detection
- Network state history tracking
- Gateway detection

---

## Visualization Features
- Live pie chart (Online vs Offline)
- Color-coded device table
- Event timeline dashboard
- Real-time refresh system

---

## Device Classification
- Windows device detection (heuristic)
- Linux device detection
- Router detection
- Mobile device detection
- Unknown fallback type

---

## Export Features
- Export results to CSV
- Export reports to PDF
- Timestamped logs

---

# Technology Stack

- Python 3.x
- PySide6 (GUI + Qt Charts)
- ReportLab (PDF generation)
- socket (network probing)
- threading / QThread (background scanning)
- ipaddress (network handling)

---

# Installation Guide (FULL SETUP)

## Step 1: Install Python

### Download Python
Download Python 3.x from:

https://www.python.org/downloads/

### Important during installation:
- Check ✔ "Add Python to PATH"
- Click Install

---

## Step 2: Verify Python Installation

Open Command Prompt:

```bash id="checkpy"
python --version
