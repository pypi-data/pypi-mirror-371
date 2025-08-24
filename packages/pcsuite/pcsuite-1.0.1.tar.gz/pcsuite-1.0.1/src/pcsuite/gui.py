import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget


from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QTextEdit, QProgressBar

class WorkerThread(QThread):
    output = pyqtSignal(str)
    finished = pyqtSignal(int)
    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd
    def run(self):
        import subprocess
        proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=str(Path.cwd()))
        for line in proc.stdout:
            self.output.emit(line.rstrip())
        proc.wait()
        self.finished.emit(proc.returncode)

class MainWindow(QMainWindow):
    def log_debug(self, msg):
        print(msg)
    def set_status(self, text, busy=False):
        self.status_label.setText(text)
        if busy:
            self.status_label.setStyleSheet("color: orange;")
        else:
            self.status_label.setStyleSheet("")
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCSuite Dashboard")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCSuite Dashboard")
        layout = QVBoxLayout()
        self.label = QLabel("Welcome to PCSuite!")
        layout.addWidget(self.label)

        # Main action buttons
        self.btn_quarantine = QPushButton("Open Quarantine")
        self.btn_reports = QPushButton("Open Reports")
        self.btn_clean = QPushButton("Clean")
        layout.addWidget(self.btn_quarantine)
        layout.addWidget(self.btn_reports)
        layout.addWidget(self.btn_clean)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self._main_layout = layout  # Store reference for later use

        # Connect buttons to actions
        self.btn_quarantine.clicked.connect(self.show_quarantine)
        self.btn_reports.clicked.connect(self.open_reports)
        self.btn_clean.clicked.connect(self.clean_action)

    def clean_action(self):
        # Show progress bar and simulate cleaning
        from PyQt5.QtCore import QTimer
        if not hasattr(self, 'clean_progress'):
            self.clean_progress = QProgressBar()
            self._main_layout.addWidget(self.clean_progress)
        self.clean_progress.setValue(0)
        self.clean_progress.setVisible(True)
        self.set_status("Cleaning in progress...", busy=True)

        def update_progress():
            val = self.clean_progress.value()
            if val < 100:
                self.clean_progress.setValue(val + 10)
            else:
                self.clean_progress.setVisible(False)
                self.set_status("Cleaning complete!", busy=False)
                self.clean_timer.stop()

        self.clean_timer = QTimer()
        self.clean_timer.timeout.connect(update_progress)
        self.clean_timer.start(150)

    def show_quarantine(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QHBoxLayout, QPushButton, QMessageBox
        dialog = QDialog(self)
        dialog.setWindowTitle("Quarantine Management")
        layout = QVBoxLayout()
        list_widget = QListWidget()
        self.set_status("Loading quarantine...", busy=True)
        self.log_debug("[QUARANTINE] Fetching quarantine list...")
        cmd = [sys.executable, "-m", "pcsuite.cli.main", "quarantine", "list"]
        if not hasattr(dialog, '_worker_refs'):
            dialog._worker_refs = []
        def handle_quarantine_list(line):
            if line.strip() and not line.startswith("┏") and not line.startswith("┃") and not line.startswith("┡") and not line.startswith("└"):
                parts = line.split()
                if parts:
                    list_widget.addItem(parts[0])
        def on_list_finish(code):
            self.set_status("Idle", busy=False)
            if list_widget.count() == 0:
                list_widget.addItem("[No quarantined files found]")
            dialog.setEnabled(True)
            dialog._worker_refs.remove(list_worker)
        dialog.setEnabled(False)
        list_worker = WorkerThread(cmd)
        dialog._worker_refs.append(list_worker)
        list_worker.output.connect(handle_quarantine_list)
        list_worker.output.connect(lambda line: self.log_debug(f"[QUARANTINE] {line}"))
        list_worker.finished.connect(on_list_finish)
        list_worker.start()
        layout.addWidget(list_widget)
        btn_layout = QHBoxLayout()
        restore_btn = QPushButton("Restore Selected")
        # ...existing code...
        layout.addWidget(list_widget)
        btn_layout = QHBoxLayout()
        restore_btn = QPushButton("Restore Selected")
        inspect_btn = QPushButton("Inspect Selected")
        purge_btn = QPushButton("Purge All")
        btn_layout.addWidget(restore_btn)
        btn_layout.addWidget(inspect_btn)
        btn_layout.addWidget(purge_btn)
        layout.addLayout(btn_layout)

        def restore_selected():
            selected = list_widget.currentItem()
            if selected and selected.text() and not selected.text().startswith("["):
                fname = selected.text()
                self.set_status(f"Restoring {fname}...", busy=True)
                self.log_debug(f"[QUARANTINE] Restoring {fname}...")
                cmd_restore = [sys.executable, "-m", "pcsuite.cli.main", "quarantine", "restore", fname]
                dialog.setEnabled(False)
                if not hasattr(dialog, '_worker_refs'):
                    dialog._worker_refs = []
                worker = WorkerThread(cmd_restore)
                dialog._worker_refs.append(worker)
                worker.output.connect(lambda line: self.log_debug(f"[QUARANTINE] {line}"))
                def on_finish(code):
                    self.set_status("Idle", busy=False)
                    dialog.setEnabled(True)
                    if code == 0:
                        QMessageBox.information(dialog, "Restore", f"Restored {fname} successfully.")
                        list_widget.takeItem(list_widget.currentRow())
                    else:
                        QMessageBox.warning(dialog, "Restore Failed", f"Restore failed. See debug log.")
                    dialog._worker_refs.remove(worker)
                worker.finished.connect(on_finish)
                worker.start()

        def inspect_selected():
            selected = list_widget.currentItem()
            if selected and selected.text() and not selected.text().startswith("["):
                fname = selected.text()
                self.set_status(f"Inspecting {fname}...", busy=True)
                self.log_debug(f"[QUARANTINE] Inspecting {fname}...")
                cmd_inspect = [sys.executable, "-m", "pcsuite.cli.main", "quarantine", "inspect", fname]
                dialog.setEnabled(False)
                if not hasattr(dialog, '_worker_refs'):
                    dialog._worker_refs = []
                worker = WorkerThread(cmd_inspect)
                dialog._worker_refs.append(worker)
                output_lines = []
                def collect_output(line):
                    output_lines.append(line)
                    self.log_debug(f"[QUARANTINE] {line}")
                worker.output.connect(collect_output)
                def on_finish(code):
                    self.set_status("Idle", busy=False)
                    dialog.setEnabled(True)
                    if code == 0 and output_lines:
                        QMessageBox.information(dialog, f"Inspect: {fname}", "\n".join(output_lines))
                    else:
                        QMessageBox.warning(dialog, f"Inspect Failed", f"Could not inspect {fname}. See debug log.")
                    dialog._worker_refs.remove(worker)
                worker.finished.connect(on_finish)
                worker.start()

        def restore_selected():
            selected = list_widget.currentItem()
            if selected and selected.text() and not selected.text().startswith("["):
                fname = selected.text()
                self.set_status(f"Restoring {fname}...", busy=True)
                self.log_debug(f"[QUARANTINE] Restoring {fname}...")
                cmd_restore = [sys.executable, "-m", "pcsuite.cli.main", "quarantine", "restore", fname]
                dialog.setEnabled(False)
                if not hasattr(dialog, '_worker_refs'):
                    dialog._worker_refs = []
                worker = WorkerThread(cmd_restore)
                dialog._worker_refs.append(worker)
                worker.output.connect(lambda line: self.log_debug(f"[QUARANTINE] {line}"))
                def on_finish(code):
                    self.set_status("Idle", busy=False)
                    dialog.setEnabled(True)
                    if code == 0:
                        QMessageBox.information(dialog, "Restore", f"Restored {fname} successfully.")
                        list_widget.takeItem(list_widget.currentRow())
                    else:
                        QMessageBox.warning(dialog, "Restore Failed", f"Restore failed. See debug log.")
                    dialog._worker_refs.remove(worker)
                worker.finished.connect(on_finish)
                worker.start()

        def inspect_selected():
            selected = list_widget.currentItem()
            if selected and selected.text() and not selected.text().startswith("["):
                fname = selected.text()
                self.set_status(f"Inspecting {fname}...", busy=True)
                self.log_debug(f"[QUARANTINE] Inspecting {fname}...")
                cmd_inspect = [sys.executable, "-m", "pcsuite.cli.main", "quarantine", "inspect", fname]
                dialog.setEnabled(False)
                if not hasattr(dialog, '_worker_refs'):
                    dialog._worker_refs = []
                worker = WorkerThread(cmd_inspect)
                dialog._worker_refs.append(worker)
                output_lines = []
                def collect_output(line):
                    output_lines.append(line)
                    self.log_debug(f"[QUARANTINE] {line}")
                worker.output.connect(collect_output)
                def on_finish(code):
                    self.set_status("Idle", busy=False)
                    dialog.setEnabled(True)
                    if code == 0 and output_lines:
                        QMessageBox.information(dialog, f"Inspect: {fname}", "\n".join(output_lines))
                    else:
                        QMessageBox.warning(dialog, f"Inspect Failed", f"Could not inspect {fname}. See debug log.")
                    dialog._worker_refs.remove(worker)
                worker.finished.connect(on_finish)
                worker.start()

        def purge_all():
            confirm = QMessageBox.question(dialog, "Confirm Purge", "Permanently delete all quarantined files?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.set_status("Purging quarantine...", busy=True)
                self.log_debug("[QUARANTINE] Purging all quarantined files...")
                cmd_purge = [sys.executable, "-m", "pcsuite.cli.main", "quarantine", "purge", "--days", "0", "--yes"]
                dialog.setEnabled(False)
                if not hasattr(dialog, '_worker_refs'):
                    dialog._worker_refs = []
                worker = WorkerThread(cmd_purge)
                dialog._worker_refs.append(worker)
                worker.output.connect(lambda line: self.log_debug(f"[QUARANTINE] {line}"))
                def on_finish(code):
                    self.set_status("Idle", busy=False)
                    dialog.setEnabled(True)
                    if code == 0:
                        QMessageBox.information(dialog, "Purge", "Purge completed successfully.")
                        list_widget.clear()
                        list_widget.addItem("[No quarantined files found]")
                    else:
                        QMessageBox.warning(dialog, "Purge Failed", f"Purge failed. See debug log.")
                    dialog._worker_refs.remove(worker)
                worker.finished.connect(on_finish)
                worker.start()

        restore_btn.clicked.connect(restore_selected)
        inspect_btn.clicked.connect(inspect_selected)
        purge_btn.clicked.connect(purge_all)
        def restore_selected():
            selected = list_widget.currentItem()
            if selected and selected.text() and not selected.text().startswith("["):
                fname = selected.text()
                self.set_status(f"Restoring {fname}...", busy=True)
                self.log_debug(f"[QUARANTINE] Restoring {fname}...")
                cmd_restore = [sys.executable, "-m", "pcsuite.cli.main", "quarantine", "restore", fname]
                dialog.setEnabled(False)
                if not hasattr(dialog, '_worker_refs'):
                    dialog._worker_refs = []
                worker = WorkerThread(cmd_restore)
                dialog._worker_refs.append(worker)
                worker.output.connect(lambda line: self.log_debug(f"[QUARANTINE] {line}"))
                def on_finish(code):
                    self.set_status("Idle", busy=False)
                    dialog.setEnabled(True)
                    if code == 0:
                        QMessageBox.information(dialog, "Restore", f"Restored {fname} successfully.")
                        list_widget.takeItem(list_widget.currentRow())
                    else:
                        QMessageBox.warning(dialog, "Restore Failed", f"Restore failed. See debug log.")
                    dialog._worker_refs.remove(worker)
                worker.finished.connect(on_finish)
                worker.start()

        def inspect_selected():
            selected = list_widget.currentItem()
            if selected and selected.text() and not selected.text().startswith("["):
                fname = selected.text()
                self.set_status(f"Inspecting {fname}...", busy=True)
                self.log_debug(f"[QUARANTINE] Inspecting {fname}...")
                cmd_inspect = [sys.executable, "-m", "pcsuite.cli.main", "quarantine", "inspect", fname]
                dialog.setEnabled(False)
                if not hasattr(dialog, '_worker_refs'):
                    dialog._worker_refs = []
                worker = WorkerThread(cmd_inspect)
                dialog._worker_refs.append(worker)
                output_lines = []
                def collect_output(line):
                    output_lines.append(line)
                    self.log_debug(f"[QUARANTINE] {line}")
                worker.output.connect(collect_output)
                def on_finish(code):
                    self.set_status("Idle", busy=False)
                    dialog.setEnabled(True)
                    from PyQt5.QtWidgets import QMessageBox
                    if code == 0 and output_lines:
                        QMessageBox.information(dialog, f"Inspect: {fname}", "\n".join(output_lines))
                    else:
                        QMessageBox.warning(dialog, f"Inspect Failed", f"Could not inspect {fname}. See debug log.")
                    dialog._worker_refs.remove(worker)
                worker.finished.connect(on_finish)
                worker.start()
        def purge_all():
            confirm = QMessageBox.question(dialog, "Confirm Purge", "Permanently delete all quarantined files?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.set_status("Purging quarantine...", busy=True)
                self.log_debug("[QUARANTINE] Purging all quarantined files...")
                cmd_purge = [sys.executable, "-m", "pcsuite.cli.main", "quarantine", "purge"]
                dialog.setEnabled(False)
                if not hasattr(dialog, '_worker_refs'):
                    dialog._worker_refs = []
                worker = WorkerThread(cmd_purge)
                dialog._worker_refs.append(worker)
                worker.output.connect(lambda line: self.log_debug(f"[QUARANTINE] {line}"))
                def on_finish(code):
                    self.set_status("Idle", busy=False)
                    dialog.setEnabled(True)
                    if code == 0:
                        QMessageBox.information(dialog, "Purge", "Purge completed successfully.")
                        list_widget.clear()
                        list_widget.addItem("[No quarantined files found]")
                    else:
                        QMessageBox.warning(dialog, "Purge Failed", f"Purge failed. See debug log.")
                    dialog._worker_refs.remove(worker)
                worker.finished.connect(on_finish)
                worker.start()
    # ...existing code...

    def open_reports(self):
        import subprocess
        from PyQt5.QtWidgets import QMessageBox
        folder = str(Path.cwd() / "reports")
        try:
            if sys.platform.startswith("win"):
                subprocess.Popen(["explorer", folder])
            elif sys.platform.startswith("darwin"):
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            QMessageBox.critical(self, "Open Reports Error", str(e))

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
