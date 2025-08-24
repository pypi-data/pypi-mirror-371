from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QDialog, QListWidget, QHBoxLayout

import sys
import os
import json
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCSuite - Professional PC Cleaning Suite")
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()
        # Live stats/analytics
    self.stats_label = QLabel()
    self.stats_label.setToolTip("Live system statistics and cleaning summary.")
    layout.addWidget(self.stats_label)
    self.update_stats()
    # Cleaning controls placeholder
    self.clean_btn = QPushButton("Run Cleanup")
    self.clean_btn.setToolTip("Run a full system clean now.")
    self.clean_btn.clicked.connect(self.run_cleanup)
    layout.addWidget(self.clean_btn)
    # Scheduling controls placeholder
    self.schedule_btn = QPushButton("Manage Schedules")
    self.schedule_btn.setToolTip("Set up automatic cleaning using Windows Task Scheduler.")
    self.schedule_btn.clicked.connect(self.manage_schedules)
    layout.addWidget(self.schedule_btn)
    # Quarantine management placeholder
    self.quarantine_btn = QPushButton("Manage Quarantine")
    self.quarantine_btn.setToolTip("View, restore, or permanently delete quarantined files.")
    self.quarantine_btn.clicked.connect(self.manage_quarantine)
    layout.addWidget(self.quarantine_btn)
    # Notifications placeholder
    self.notif_label = QLabel("")
    layout.addWidget(self.notif_label)
    container = QWidget()
    container.setLayout(layout)
    self.setCentralWidget(container)

    def update_stats(self):
        # Load stats from latest report(s)
        reports_dir = Path.cwd() / "reports"
        total_bytes = 0
        total_files = 0
        if reports_dir.exists():
            for f in reports_dir.glob("*.json"):
                try:
                    with open(f, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                    stats = data.get("stats", {})
                    total_bytes += int(stats.get("bytes_reclaimed", 0))
                    total_files += int(stats.get("examined", 0))
                except Exception:
                    continue
        self.stats_label.setText(f"<b>Total bytes reclaimed:</b> {total_bytes:,}<br><b>Total files cleaned:</b> {total_files:,}")

    def run_cleanup(self):
        import subprocess
        try:
            result = subprocess.run([
                sys.executable, "-m", "pcsuite.cli.main", "clean", "run", "--mode", "quarantine", "--yes"
            ], capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0:
                self.show_info("Cleanup completed successfully.")
            else:
                self.show_error("Cleanup failed.", f"{result.stdout}\n{result.stderr}")
        except Exception as e:
            self.show_error("Cleanup Error", str(e))
        self.update_stats()

    def show_error(self, message, details=None):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        if details:
            msg.setDetailedText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_info(self, message, details=None):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Info")
        msg.setText(message)
        if details:
            msg.setDetailedText(details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def manage_schedules(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Schedules")
        layout = QVBoxLayout()
        # Placeholder: list of scheduled tasks
        list_widget = QListWidget()
        list_widget.addItem("[Scheduled tasks will appear here]")
        layout.addWidget(list_widget)
        # Placeholder: add/remove buttons (not yet functional)
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Schedule")
        remove_btn = QPushButton("Remove Schedule")
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        dialog.exec_()

    def manage_quarantine(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Quarantine")
        layout = QVBoxLayout()
        list_widget = QListWidget()
        # List real quarantined files
        quar_dir = Path.cwd() / "Quarantine"
        files = []
        if quar_dir.exists():
            for f in quar_dir.iterdir():
                if f.is_file() and not f.name.endswith(".meta.json"):
                    files.append(f.name)
                    list_widget.addItem(f.name)
        if not files:
            list_widget.addItem("[No quarantined files found]")
        layout.addWidget(list_widget)
        btn_layout = QHBoxLayout()
        restore_btn = QPushButton("Restore File")
        restore_btn.setToolTip("Restore the selected quarantined file to its original location.")
        purge_btn = QPushButton("Purge Old Files")
        purge_btn.setToolTip("Permanently delete all old quarantined files.")
        btn_layout.addWidget(restore_btn)
        btn_layout.addWidget(purge_btn)
        layout.addLayout(btn_layout)
        def show_error(message, details=None):
            msg = QMessageBox(dialog)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText(message)
            if details:
                msg.setDetailedText(details)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        def show_info(message, details=None):
            msg = QMessageBox(dialog)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Info")
            msg.setText(message)
            if details:
                msg.setDetailedText(details)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        def restore_selected():
            selected = list_widget.currentItem()
            if selected and selected.text() not in ("[No quarantined files found]", "[Quarantined files will appear here]"):
                fname = selected.text()
                import subprocess
                try:
                    result = subprocess.run([
                        sys.executable, "-m", "pcsuite.cli.main", "quarantine", "restore", fname, "--yes"
                    ], capture_output=True, text=True, cwd=os.getcwd())
                    if result.returncode == 0:
                        show_info(f"Restored {fname} successfully.")
                        list_widget.takeItem(list_widget.currentRow())
                    else:
                        show_error("Restore failed.", f"{result.stdout}\n{result.stderr}")
                except Exception as e:
                    show_error("Restore Error", str(e))
        def purge_files():
            confirm = QMessageBox.question(dialog, "Confirm Purge", "Permanently delete old quarantined files?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                import subprocess
                try:
                    result = subprocess.run([
                        sys.executable, "-m", "pcsuite.cli.main", "quarantine", "purge", "--yes"
                    ], capture_output=True, text=True, cwd=os.getcwd())
                    if result.returncode == 0:
                        show_info("Purge completed successfully.")
                        # Refresh list
                        list_widget.clear()
                        files2 = []
                        if quar_dir.exists():
                            for f in quar_dir.iterdir():
                                if f.is_file() and not f.name.endswith(".meta.json"):
                                    files2.append(f.name)
                                    list_widget.addItem(f.name)
                        if not files2:
                            list_widget.addItem("[No quarantined files found]")
                    else:
                        show_error("Purge failed.", f"{result.stdout}\n{result.stderr}")
                except Exception as e:
                    show_error("Purge Error", str(e))
        restore_btn.clicked.connect(restore_selected)
        purge_btn.clicked.connect(purge_files)
        dialog.setLayout(layout)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
