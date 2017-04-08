from PyQt5.QtCore import QObject, pyqtSignal
from bireus.client.notification_service import NotificationService
from bireus.client.repository import ClientRepository


class QNotificationService(QObject):
    notify = pyqtSignal(str)
    patching_finished = pyqtSignal(bool)

    def __init__(self):
        QObject.__init__(self)

    def on_notify(self, message: str) -> None:
        self.notify.emit(message)

    def on_finished(self, success: bool) -> None:
        self.patching_finished.emit(success)


class BireusNotificationService(NotificationService):
    def __init__(self, repo: ClientRepository, parent: 'QNotificationService'):
        super().__init__(repo)
        self._parent = parent

    def notify(self, message: str, line_break: bool = True, indent: bool = True) -> None:
        """
        Show a message to the user
        Overwrite this message to adapt to your needs
        :param message: str
        :param line_break: bool
        :param indent: bool
        :return: None
        """
        if indent:
            indent_chars = ' ' * self._indent
        else:
            indent_chars = ''

        if line_break:
            message = indent_chars + message + "\n"
        else:
            message = indent_chars + message

        self._parent.on_notify(message)

    def checked_out_already(self) -> None:
        super().checked_out_already()
        self._parent.on_finished(True)

    def finish_checkout_version(self, version: str) -> None:
        super().finish_checkout_version(version)
        self._parent.on_finished(True)

    def error(self, message: str) -> None:
        super().error(message)
        self._parent.on_finished(False)