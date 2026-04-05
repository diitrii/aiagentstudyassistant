from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import AI_ASSISTANT_ENABLED, ENABLE_INACTIVITY_POPUP
from monitoring.session_monitor import SessionMonitor
from state.keyword_exporter import export_keywords_to_file, open_file_in_default_app
from state.models import MonitoringSnapshot, StudySessionState
from ui.inactivity_popup import (
    show_break_popup,
    show_inactivity_popup,
    show_rapid_switch_popup,
)


class MonitorWorker(QObject):
    snapshot_signal = Signal(dict)
    finished = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.monitor = SessionMonitor(
            poll_interval_seconds=1.0,
            on_snapshot=self.handle_snapshot,
        )

    def handle_snapshot(
        self,
        snapshot: MonitoringSnapshot,
        session_state: StudySessionState,
    ) -> None:
        topic = snapshot.extracted_topic.strip()

        if topic:
            session_state.current_topic = topic

            for keyword in snapshot.extracted_keywords:
                clean_keyword = keyword.strip().lower()

                if clean_keyword:
                    if clean_keyword not in session_state.unique_keywords:
                        session_state.unique_keywords.append(clean_keyword)

                    session_state.topic_keywords[topic].add(clean_keyword)

            session_state.topic_durations[topic] += max(
                1, int(round(self.monitor.poll_interval_seconds))
            )

            session_state.last_topic = topic

        payload = {
            "timestamp": snapshot.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "window": snapshot.active_window_title,
            "process": snapshot.process_name,
            "topic": snapshot.extracted_topic,
            "idle_seconds_text": f"{snapshot.idle_seconds:.1f}",
            "idle_seconds_raw": snapshot.idle_seconds,
            "tab_switches": session_state.metrics.tab_switch_count,
            "recent_switch_count": session_state.metrics.recent_switch_count,
            "rapid_switching": session_state.metrics.rapid_switching_detected,
            "rapid_switch_window_seconds": int(
                self.monitor.rapid_switch_window_seconds
            ),
            "ai_enabled": self.monitor.ai_assistant_enabled,
            "popup_enabled": self.monitor.enable_inactivity_popup,
            "keyword_count": len(session_state.unique_keywords),
            "active_study_minutes": int(self.monitor.active_study_seconds // 60),
            "show_popup": self.monitor.consume_inactivity_popup_request(),
            "show_rapid_switch_popup": (
                self.monitor.consume_rapid_switch_popup_request()
            ),
            "show_break_popup": self.monitor.consume_break_popup_request(),
        }
        self.snapshot_signal.emit(payload)

    @Slot()
    def run(self) -> None:
        self.monitor.run()
        self.finished.emit()

    def stop(self) -> None:
        self.monitor.stop()

    def set_ai_enabled(self, enabled: bool) -> None:
        self.monitor.set_ai_assistant_enabled(enabled)

    def set_popup_enabled(self, enabled: bool) -> None:
        self.monitor.set_inactivity_popup_enabled(enabled)

    def export_keywords_and_open(self) -> None:
        output_path = export_keywords_to_file(self.monitor.session_state)
        open_file_in_default_app(output_path)


class DashboardWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("AI Study Copilot Control Panel")
        self.resize(700, 380)

        self.worker: MonitorWorker | None = None
        self.thread: QThread | None = None

        self.status_label = QLabel("Status: Stopped")
        self.topic_label = QLabel("Current Topic: -")
        self.window_label = QLabel("Last Window: -")
        self.idle_label = QLabel("Idle Time: 0.0 seconds")
        self.active_study_label = QLabel("Active Study Time: 0 minute(s)")
        self.switches_label = QLabel("Tab/Window Switches: 0")
        self.recent_switches_label = QLabel("Recent Switches (10s): 0")
        self.rapid_switching_label = QLabel("Rapid Switching: No")
        self.keyword_count_label = QLabel("Unique Keywords: 0")
        self.ai_status_label = QLabel("AI Assistant: Enabled")
        self.popup_status_label = QLabel("Inactivity Popup: Enabled")

        self.start_button = QPushButton("Start Assistant")
        self.stop_button = QPushButton("Stop Assistant")
        self.stop_button.setEnabled(False)

        self.ai_checkbox = QCheckBox("Enable AI Assistant")
        self.ai_checkbox.setChecked(AI_ASSISTANT_ENABLED)

        self.popup_checkbox = QCheckBox("Enable Inactivity Popup")
        self.popup_checkbox.setChecked(ENABLE_INACTIVITY_POPUP)

        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.ai_checkbox.toggled.connect(self.on_ai_toggled)
        self.popup_checkbox.toggled.connect(self.on_popup_toggled)

        info_layout = QGridLayout()
        info_layout.addWidget(self.status_label, 0, 0)
        info_layout.addWidget(self.ai_status_label, 0, 1)
        info_layout.addWidget(self.popup_status_label, 1, 0)
        info_layout.addWidget(self.switches_label, 1, 1)
        info_layout.addWidget(self.keyword_count_label, 2, 0)
        info_layout.addWidget(self.recent_switches_label, 2, 1)
        info_layout.addWidget(self.rapid_switching_label, 3, 0, 1, 2)
        info_layout.addWidget(self.active_study_label, 4, 0, 1, 2)
        info_layout.addWidget(self.topic_label, 5, 0, 1, 2)
        info_layout.addWidget(self.window_label, 6, 0, 1, 2)
        info_layout.addWidget(self.idle_label, 7, 0, 1, 2)

        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.ai_checkbox)
        controls_layout.addWidget(self.popup_checkbox)
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.stop_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(info_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(controls_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    @Slot()
    def start_monitoring(self) -> None:
        if self.thread is not None and self.thread.isRunning():
            return

        self.worker = MonitorWorker()
        self.thread = QThread()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.snapshot_signal.connect(self.update_ui_from_snapshot)

        self.worker.set_ai_enabled(self.ai_checkbox.isChecked())
        self.worker.set_popup_enabled(self.popup_checkbox.isChecked())

        self.thread.start()

        self.status_label.setText("Status: Running")
        self.ai_status_label.setText(
            f"AI Assistant: {'Enabled' if self.ai_checkbox.isChecked() else 'Disabled'}"
        )
        self.popup_status_label.setText(
            f"Inactivity Popup: {'Enabled' if self.popup_checkbox.isChecked() else 'Disabled'}"
        )

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def _stop_monitoring_internal(self, export_session: bool) -> None:
        if self.worker is not None:
            self.worker.stop()

        if self.thread is not None:
            self.thread.quit()
            self.thread.wait()

        if export_session and self.worker is not None:
            self.worker.export_keywords_and_open()

        self.worker = None
        self.thread = None

        self.status_label.setText("Status: Stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    @Slot()
    def stop_monitoring(self) -> None:
        self._stop_monitoring_internal(export_session=True)

    @Slot(bool)
    def on_ai_toggled(self, checked: bool) -> None:
        self.ai_status_label.setText(
            f"AI Assistant: {'Enabled' if checked else 'Disabled'}"
        )
        if self.worker is not None:
            self.worker.set_ai_enabled(checked)

    @Slot(bool)
    def on_popup_toggled(self, checked: bool) -> None:
        self.popup_status_label.setText(
            f"Inactivity Popup: {'Enabled' if checked else 'Disabled'}"
        )
        if self.worker is not None:
            self.worker.set_popup_enabled(checked)

    @Slot(dict)
    def update_ui_from_snapshot(self, payload: dict) -> None:
        self.status_label.setText("Status: Running")
        self.topic_label.setText(f"Current Topic: {payload['topic']}")
        self.window_label.setText(f"Last Window: {payload['window']}")
        self.idle_label.setText(
            f"Idle Time: {payload['idle_seconds_text']} seconds"
        )
        self.active_study_label.setText(
            f"Active Study Time: {payload['active_study_minutes']} minute(s)"
        )
        self.switches_label.setText(
            f"Tab/Window Switches: {payload['tab_switches']}"
        )
        self.recent_switches_label.setText(
            f"Recent Switches (10s): {payload['recent_switch_count']}"
        )
        self.rapid_switching_label.setText(
            f"Rapid Switching: {'Yes' if payload['rapid_switching'] else 'No'}"
        )
        self.keyword_count_label.setText(
            f"Unique Keywords: {payload['keyword_count']}"
        )
        self.ai_status_label.setText(
            f"AI Assistant: {'Enabled' if payload['ai_enabled'] else 'Disabled'}"
        )
        self.popup_status_label.setText(
            f"Inactivity Popup: {'Enabled' if payload['popup_enabled'] else 'Disabled'}"
        )

        if payload["show_popup"]:
            show_inactivity_popup(self, float(payload["idle_seconds_raw"]))

        if payload["show_rapid_switch_popup"]:
            show_rapid_switch_popup(
                self,
                int(payload["recent_switch_count"]),
                int(payload["rapid_switch_window_seconds"]),
            )

        if payload["show_break_popup"]:
            show_break_popup(
                self,
                int(payload["active_study_minutes"]),
            )

    def closeEvent(self, event) -> None:
        self._stop_monitoring_internal(export_session=True)
        event.accept()


def run_dashboard() -> None:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    window = DashboardWindow()
    window.show()
    app.exec()