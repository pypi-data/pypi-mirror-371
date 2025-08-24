import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCSuite Dashboard (Preview)")
        layout = QVBoxLayout()
        self.label = QLabel("Welcome to PCSuite! (GUI preview)")
        layout.addWidget(self.label)
        self.btn_clean = QPushButton("Run Clean")
        layout.addWidget(self.btn_clean)
        self.btn_quarantine = QPushButton("View Quarantine")
        layout.addWidget(self.btn_quarantine)
        self.btn_reports = QPushButton("Open Reports Folder")
        layout.addWidget(self.btn_reports)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.btn_reports.clicked.connect(self.open_reports)
    def open_reports(self):
        folder = str(Path.cwd() / "reports")
        QFileDialog.getOpenFileName(self, "Open Report", folder)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
