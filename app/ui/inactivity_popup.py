from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QWidget


BREAK_REMINDER_MINUTES = 75


def show_inactivity_popup(parent: QWidget | None, idle_seconds: float) -> None:
    minutes = int(idle_seconds // 60)
    if minutes <= 0:
        minutes = 1

    msg = QMessageBox(parent)
    msg.setWindowTitle("Study Copilot")
    msg.setText("You seem inactive.")
    msg.setInformativeText(
        f"You have been inactive for about {minutes} minute(s). "
        "Time to get back to studying?"
    )
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setWindowModality(Qt.WindowModality.ApplicationModal)
    msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
    msg.raise_()
    msg.activateWindow()
    msg.exec()


def show_rapid_switch_popup(
    parent: QWidget | None,
    recent_switch_count: int,
    window_seconds: int,
) -> None:
    msg = QMessageBox(parent)
    msg.setWindowTitle("Study Copilot")
    msg.setText("You are switching windows very quickly.")
    msg.setInformativeText(
        f"You switched windows {recent_switch_count} times in the last "
        f"{window_seconds} seconds. Try slowing down and focusing on one task."
    )
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setWindowModality(Qt.WindowModality.ApplicationModal)
    msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
    msg.raise_()
    msg.activateWindow()
    msg.exec()


def show_break_popup(
    parent: QWidget | None,
    active_study_minutes: int,
) -> None:
    msg = QMessageBox(parent)
    msg.setWindowTitle("Study Copilot")
    msg.setText("You have been studying for a while.")
    msg.setInformativeText(
        f"You have been actively working for about "
        f"{active_study_minutes} minute(s).\n\n"
        "Why don't you take a 10 minute break?"
    )
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.setWindowModality(Qt.WindowModality.ApplicationModal)
    msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
    msg.raise_()
    msg.activateWindow()
    msg.exec()