import sys
import ipaddress
import json
import os
import socket
import time

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QMessageBox, QHBoxLayout, QFileDialog
)

from PySide6.QtCharts import QChart, QChartView, QPieSeries
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPainter

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"network": "192.168.1.0/24"}


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)


# FAST NON-CMD CHECK (no subprocess, no popup)
def ping(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.25)

        # lightweight probe (port 80)
        result = sock.connect_ex((str(ip), 80))
        sock.close()

        return result == 0
    except:
        return False


def detect_device_type(ip):
    try:
        host = socket.getfqdn(str(ip)).lower()

        if ip.endswith(".1"):
            return "Router"
        elif "windows" in host:
            return "Windows PC"
        elif "linux" in host:
            return "Linux Device"
        elif "android" in host or "phone" in host:
            return "Mobile"
        return "Unknown"
    except:
        return "Unknown"


# ---------------- WORKER THREAD ----------------
class ScanWorker(QThread):
    result = Signal(list, int, int, dict)

    def __init__(self, targets, previous_state):
        super().__init__()
        self.targets = targets
        self.previous_state = previous_state

    def run(self):
        online = 0
        offline = 0
        results = []
        current_state = {}

        with ThreadPoolExecutor(max_workers=30) as executor:
            statuses = list(executor.map(ping, self.targets))

        for ip, status in zip(self.targets, statuses):
            ip_str = str(ip)
            current_state[ip_str] = status

            if status:
                online += 1
                results.append((ip_str, "Online"))
            else:
                offline += 1
                results.append((ip_str, "Offline"))

        self.result.emit(results, online, offline, current_state)


# ---------------- MAIN APP ----------------
class ScannerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Network Visibility Monitor")
        self.setGeometry(200, 200, 1150, 750)

        self.config = load_config()
        self.base_network = self.config["network"]

        # STATE
        self.previous_state = {}
        self.known_hosts = set()
        self.events = []
        self.results_cache = []

        self.init_ui()
        self.apply_theme()

        # AUTO SCAN
        self.timer = QTimer()
        self.timer.timeout.connect(self.smart_scan)
        self.timer.start(10000)

    # ---------------- UI ----------------
    def init_ui(self):

        self.status = QLabel("Status: Smart Monitoring Active")

        self.network_input = QLineEdit()
        self.network_input.setText(self.base_network)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_network)

        self.scan_button = QPushButton("Manual Scan")
        self.scan_button.clicked.connect(self.smart_scan)

        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)

        self.export_pdf_btn = QPushButton("Export PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)

        top = QHBoxLayout()
        top.addWidget(QLabel("Network:"))
        top.addWidget(self.network_input)
        top.addWidget(self.save_button)
        top.addWidget(self.scan_button)
        top.addWidget(self.export_csv_btn)
        top.addWidget(self.export_pdf_btn)

        # TABLE
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["IP", "Status", "Type"])

        # CHART
        self.series = QPieSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("Network Status")

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        # LAYOUT
        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.status)
        layout.addWidget(self.chart_view)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # ---------------- THEME ----------------
    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QLabel { color: #e5e7eb; }
            QLineEdit {
                background: #111c33;
                color: white;
                border: 1px solid #334155;
                padding: 5px;
                border-radius: 6px;
            }
            QTableWidget {
                background: #111c33;
                color: white;
            }
            QHeaderView::section {
                background: #1e293b;
                color: white;
            }
            QPushButton {
                background: #3b82f6;
                color: white;
                padding: 6px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #60a5fa;
            }
        """)

    # ---------------- SAVE ----------------
    def save_network(self):
        self.base_network = self.network_input.text()
        save_config({"network": self.base_network})
        QMessageBox.information(self, "Saved", "Network updated")

    # ---------------- SMART SCAN ----------------
    def smart_scan(self):
        try:
            network = ipaddress.ip_network(self.base_network, strict=False)
        except:
            self.status.setText("Invalid network")
            return

        # SMART LOGIC:
        # 1st scan = full
        # next scans = only known + last seen + gateway
        if not self.known_hosts:
            targets = list(network.hosts())
        else:
            targets = list(self.known_hosts)

            # always include gateway
            targets.append(network.network_address + 1)

        self.worker = ScanWorker(targets, self.previous_state)
        self.worker.result.connect(self.on_scan_done)
        self.worker.start()

    # ---------------- RESULT HANDLER ----------------
    def on_scan_done(self, results, online, offline, current_state):

        now = datetime.now().strftime("%H:%M:%S")

        # EVENT ENGINE
        for ip, status in current_state.items():

            if ip not in self.previous_state and status:
                self.events.append((now, "NEW DEVICE", ip))

            if ip in self.previous_state:
                if self.previous_state[ip] and not status:
                    self.events.append((now, "OFFLINE", ip))
                if not self.previous_state[ip] and status:
                    self.events.append((now, "ONLINE", ip))

        self.previous_state = current_state
        self.known_hosts = set(current_state.keys())
        self.results_cache = []

        # ENRICH DATA
        enriched = []
        for ip, status in results:
            enriched.append((ip, status, detect_device_type(ip)))
            self.results_cache.append((ip, status, detect_device_type(ip), now))

        self.update_table(enriched)
        self.update_chart(online, offline)

        self.status.setText(
            f"{now} | Online: {online} | Offline: {offline}"
        )

    # ---------------- TABLE ----------------
    def update_table(self, data):
        self.table.setRowCount(len(data))

        for r, (ip, status, dtype) in enumerate(data):
            self.table.setItem(r, 0, QTableWidgetItem(ip))
            self.table.setItem(r, 1, QTableWidgetItem(status))
            self.table.setItem(r, 2, QTableWidgetItem(dtype))

    # ---------------- CHART ----------------
    def update_chart(self, online, offline):
        self.series.clear()
        self.series.append("Online", online)
        self.series.append("Offline", offline)

    # ---------------- EXPORT CSV ----------------
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "CSV", "", "CSV (*.csv)")
        if not path:
            return

        with open(path, "w") as f:
            f.write("IP,Status,Type,Time\n")
            for r in self.results_cache:
                f.write(",".join(r) + "\n")

    # ---------------- EXPORT PDF ----------------
    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "PDF", "", "PDF (*.pdf)")
        if not path:
            return

        pdf = canvas.Canvas(path, pagesize=letter)
        pdf.drawString(50, 750, "Network Visibility Report")

        y = 720
        for r in self.results_cache:
            pdf.drawString(50, y, str(r))
            y -= 15
            if y < 50:
                pdf.showPage()
                y = 750

        pdf.save()


# ---------------- RUN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScannerApp()
    window.show()
    sys.exit(app.exec())