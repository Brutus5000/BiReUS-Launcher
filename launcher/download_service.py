from pathlib import Path

import asyncio
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QUrl, QByteArray, QEventLoop
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from bireus.client.download_service import AbstractDownloadService


class QDownloadService(QObject):
    downloadProgress = pyqtSignal(float)
    finished = pyqtSignal()

    def __init__(self, nam: QNetworkAccessManager):
        super().__init__()
        self._nam = nam

    def _download_update(self, received, total) -> None:
        self.downloadProgress.emit(received / total)

    def download(self, url: str, path: Path):
        url = QUrl(url)
        req = QNetworkRequest(url)

        worker_loop = QEventLoop(self)
        reply = self._nam.get(req)
        reply.finished.connect(worker_loop.quit)
        reply.downloadProgress.connect(self._download_update)
        worker_loop.exec()

        qbytes = reply.readAll()  # type: QByteArray
        with path.open("wb") as file:
            file.write(qbytes.data())

        self.finished.emit()

    def read(self, url: str) -> bytes:
        url = QUrl(url)
        req = QNetworkRequest(url)

        worker_loop = QEventLoop(self)
        reply = self._nam.get(req)
        reply.readyRead.connect(worker_loop.quit)
        reply.downloadProgress.connect(self._download_update)
        worker_loop.exec_()

        return reply.readAll().data()


class BireusDownloadService(AbstractDownloadService):
    def __init__(self, parent: 'QDownloadService'):
        self.parent = parent

    def download(self, url: str, path: Path) -> None:
        return self.parent.download(url, path)

    def read(self, url: str) -> bytes:
        return self.parent.read(url)
