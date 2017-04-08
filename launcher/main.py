#!/usr/bin/python3

import sys
from pathlib import Path

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QTextCursor
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from bireus.client.repository import ClientRepository

from launcher.download_service import QDownloadService, BireusDownloadService
from launcher.patch import PatchingThread


class MainWindow(QMainWindow):
    # Maintain the list of browser windows so that they do not get garbage collected.
    _window_list = []

    def __init__(self, repo_path: Path):
        QMainWindow.__init__(self)

        self.repo_path = repo_path
        self.setWindowTitle("BiReUS Launcher")

        MainWindow._window_list.append(self)
        self.downloader = QDownloadService(QNetworkAccessManager())
        # self.downloader.downloadProgress.connect(self.show_progress)

        self.bireus_repo = ClientRepository(repo_path, BireusDownloadService(self.downloader))

        widget = loadUi("resources/main.ui")
        widget.buttonCancel.clicked.connect(lambda: sys.exit())

        self.download_service = QDownloadService(QNetworkAccessManager())

        self.setCentralWidget(widget)

        self.show()

    def start(self):
        thread = PatchingThread(self.repo_path)
        thread.patching_finished.connect(self._on_finished)
        thread.progressUpdate.connect(self.show_progress)
        thread.notify.connect(self._on_notify)
        thread.run()

    @pyqtSlot(str)
    def _on_notify(self, message: str) -> None:
        widget = self.centralWidget()
        widget.progressText.moveCursor(QTextCursor.End)
        widget.progressText.insertPlainText(message)
        app.processEvents()

    @pyqtSlot(bool)
    def _on_finished(self, success: bool) -> None:
        if success:
            self.centralWidget().buttonLaunch.setEnabled(True)
            app.processEvents()

    @pyqtSlot(float)
    def show_progress(self, progress) -> None:
        self.centralWidget().progressBar.setValue(progress*100)
        app.processEvents()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = MainWindow(Path("C:\\repos\\mission"))
    w.start()

    sys.exit(app.exec_())
