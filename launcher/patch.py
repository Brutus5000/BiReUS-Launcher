from pathlib import Path

import time
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtNetwork import QNetworkAccessManager
from bireus.client.repository import ClientRepository

from launcher.download_service import QDownloadService, BireusDownloadService
from launcher.notification_service import QNotificationService, BireusNotificationService


class PatchingThread(QThread):
    download_service = QDownloadService(QNetworkAccessManager())

    progressUpdate = pyqtSignal(float)
    patching_finished = pyqtSignal(bool)
    notify = pyqtSignal(str)

    def __init__(self, repository_path: Path):
        QThread.__init__(self)
        self.repository_path = repository_path
        self.notification_service = QNotificationService()
        self.notification_service.notify.connect(self._on_notify)
        self.notification_service.patching_finished.connect(self._on_patching_finished)

        PatchingThread.download_service.downloadProgress.connect(lambda progress: self.progressUpdate.emit(progress))
        PatchingThread.download_service.finished.connect(lambda: self.finished.emit())

        self.repo = ClientRepository(self.repository_path, BireusDownloadService(PatchingThread.download_service))
        self.repo.notification_service = BireusNotificationService(self.repo, self.notification_service)

    def run(self):
        self.repo.checkout_latest()

    @pyqtSlot(str)
    def _on_notify(self, message):
        self.notify.emit(message)

    @pyqtSlot(bool)
    def _on_patching_finished(self, success: bool):
        self.patching_finished.emit(success)