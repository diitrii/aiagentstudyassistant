import time
from collections import deque
from datetime import datetime
from typing import Callable, Optional

from agents.topic_extractor import TopicExtractor
from config import (
    ENABLE_CLIPBOARD,
    ENABLE_INACTIVITY_POPUP,
    ENABLE_SCREENSHOTS,
    INACTIVITY_THRESHOLD_SECONDS,
    SCREENSHOT_DIR,
)
from monitoring.active_window import ActiveWindowInfo, get_active_window_info
from monitoring.clipboard_reader import get_clipboard_text
from monitoring.idle_detector import get_idle_time_seconds
from monitoring.ocr_reader import extract_text_from_image
from monitoring.screenshot import capture_full_screen
from state.models import MonitoringSnapshot, StudySessionState


class SessionMonitor:
    def __init__(
        self,
        poll_interval_seconds: float = 1.0,
        on_snapshot: Optional[
            Callable[[MonitoringSnapshot, StudySessionState], None]
        ] = None,
    ):
        self.poll_interval_seconds = poll_interval_seconds
        self.session_state = StudySessionState()
        self.last_window_title: Optional[str] = None
        self.current_window_start_time: Optional[datetime] = None
        self.topic_extractor = TopicExtractor()
        self.inactivity_popup_shown = False
        self.inactivity_threshold_seconds = INACTIVITY_THRESHOLD_SECONDS
        self.enable_inactivity_popup = ENABLE_INACTIVITY_POPUP
        self.ai_assistant_enabled = True
        self.running = False
        self.on_snapshot = on_snapshot
        self.last_ocr_time: Optional[datetime] = None
        self.ocr_interval_seconds = 3.0
        self._pending_inactivity_popup = False

        self.window_switch_timestamps = deque()
        self.rapid_switch_window_seconds = 10.0
        self.rapid_switch_threshold = 3
        self._pending_rapid_switch_popup = False
        self.rapid_switch_popup_shown = False

        self.active_study_seconds = 0.0
        self.last_activity_check_time = time.time()
        self.break_reminder_minutes = 1
        self.last_break_popup_minutes = 0
        self._pending_break_popup = False

    def set_ai_assistant_enabled(self, enabled: bool) -> None:
        self.ai_assistant_enabled = enabled

    def set_inactivity_popup_enabled(self, enabled: bool) -> None:
        self.enable_inactivity_popup = enabled

    def stop(self) -> None:
        self.running = False

    def consume_inactivity_popup_request(self) -> bool:
        if self._pending_inactivity_popup:
            self._pending_inactivity_popup = False
            return True
        return False

    def consume_rapid_switch_popup_request(self) -> bool:
        if self._pending_rapid_switch_popup:
            self._pending_rapid_switch_popup = False
            return True
        return False

    def consume_break_popup_request(self) -> bool:
        if self._pending_break_popup:
            self._pending_break_popup = False
            return True
        return False

    def _add_unique_keywords(self, keywords: list[str]) -> None:
        existing_normalized = {
            keyword.lower() for keyword in self.session_state.unique_keywords
        }

        for keyword in keywords:
            normalized = keyword.lower()
            if normalized not in existing_normalized:
                self.session_state.unique_keywords.append(keyword)
                existing_normalized.add(normalized)

    def _record_window_switch(self) -> None:
        now = time.time()
        self.window_switch_timestamps.append(now)

        while self.window_switch_timestamps:
            if now - self.window_switch_timestamps[0] > self.rapid_switch_window_seconds:
                self.window_switch_timestamps.popleft()
            else:
                break

        recent_count = len(self.window_switch_timestamps)
        self.session_state.metrics.recent_switch_count = recent_count
        self.session_state.metrics.rapid_switching_detected = (
            recent_count >= self.rapid_switch_threshold
        )

        if self.session_state.metrics.rapid_switching_detected:
            if not self.rapid_switch_popup_shown:
                self._pending_rapid_switch_popup = True
                self.rapid_switch_popup_shown = True
        else:
            self.rapid_switch_popup_shown = False

    def create_snapshot(
        self,
        active_window: ActiveWindowInfo,
        idle_seconds: float,
        take_screenshot: bool,
    ) -> MonitoringSnapshot:
        clipboard_text = ""
        if ENABLE_CLIPBOARD:
            clipboard_text = get_clipboard_text()

        should_run_ocr = False
        if ENABLE_SCREENSHOTS:
            if self.last_ocr_time is None:
                should_run_ocr = True
            else:
                elapsed_since_ocr = (
                    datetime.now() - self.last_ocr_time
                ).total_seconds()
                if elapsed_since_ocr >= self.ocr_interval_seconds:
                    should_run_ocr = True

        ocr_text = ""

        if ENABLE_SCREENSHOTS and (take_screenshot or should_run_ocr):
            screenshot_path = capture_full_screen(SCREENSHOT_DIR)

            if screenshot_path is not None:
                ocr_text = extract_text_from_image(screenshot_path)
                self.last_ocr_time = datetime.now()

                try:
                    screenshot_path.unlink(missing_ok=True)
                except Exception:
                    pass

        text_for_extraction = ocr_text if ocr_text else clipboard_text

        extracted_topic = self.topic_extractor.extract_topic(
            window_title=active_window.title,
            clipboard_text=text_for_extraction,
            process_name=active_window.process_name or "",
        )

        extracted_keywords = self.topic_extractor.extract_snapshot_keywords(
            window_title=active_window.title,
            clipboard_text=text_for_extraction,
            process_name=active_window.process_name or "",
        )

        snapshot = MonitoringSnapshot(
            timestamp=datetime.now(),
            active_window_title=active_window.title,
            process_name=active_window.process_name or "",
            process_id=active_window.process_id,
            screenshot_path=None,
            clipboard_text=clipboard_text,
            ocr_text=ocr_text,
            extracted_topic=extracted_topic,
            extracted_keywords=extracted_keywords,
            idle_seconds=idle_seconds,
        )

        return snapshot

    def run(self) -> None:
        self.running = True

        print("AI Study Copilot Monitoring Started")
        print(f"Polling every {self.poll_interval_seconds} seconds")
        print(f"Inactivity popup enabled: {self.enable_inactivity_popup}")
        print(f"Inactivity threshold: {self.inactivity_threshold_seconds} seconds")
        print(f"Break reminder every: {self.break_reminder_minutes} active minutes")
        print("Press Ctrl + C to stop")
        print()

        try:
            while self.running:
                loop_start = time.time()
                idle_seconds = get_idle_time_seconds()

                current_time = time.time()
                elapsed_since_last_check = current_time - self.last_activity_check_time
                self.last_activity_check_time = current_time

                if idle_seconds < 60:
                    self.active_study_seconds += elapsed_since_last_check

                active_study_minutes = int(self.active_study_seconds // 60)

                if (
                    active_study_minutes >= self.break_reminder_minutes
                    and active_study_minutes - self.last_break_popup_minutes
                    >= self.break_reminder_minutes
                ):
                    self._pending_break_popup = True
                    self.last_break_popup_minutes = active_study_minutes

                if idle_seconds >= self.inactivity_threshold_seconds:
                    if not self.inactivity_popup_shown:
                        print("=" * 60)
                        print(f"Inactivity detected: {idle_seconds:.1f} seconds")

                        if self.enable_inactivity_popup:
                            print("Requesting inactivity popup from UI thread...")
                            self._pending_inactivity_popup = True
                        else:
                            print("Popup disabled. No popup requested.")

                        print()
                        self.inactivity_popup_shown = True
                else:
                    self.inactivity_popup_shown = False

                active_window = get_active_window_info()

                if self.current_window_start_time is None:
                    self.current_window_start_time = datetime.now()

                window_changed = False
                if self.last_window_title is not None:
                    window_changed = active_window.title != self.last_window_title

                if window_changed:
                    time_on_previous_window = (
                        datetime.now() - self.current_window_start_time
                    ).total_seconds()

                    self.current_window_start_time = datetime.now()
                    self.session_state.metrics.tab_switch_count += 1
                    self._record_window_switch()

                    print("=" * 60)
                    print("Window change detected")
                    print(f"Previous window: {self.last_window_title}")
                    print(
                        f"Time spent there: {time_on_previous_window:.1f} seconds"
                    )
                    print(f"New window: {active_window.title}")
                    print(
                        f"Recent switches in "
                        f"{int(self.rapid_switch_window_seconds)}s: "
                        f"{self.session_state.metrics.recent_switch_count}"
                    )

                    if self.session_state.metrics.rapid_switching_detected:
                        print("Rapid switching detected")

                    print()
                else:
                    now = time.time()
                    while self.window_switch_timestamps:
                        if now - self.window_switch_timestamps[0] > self.rapid_switch_window_seconds:
                            self.window_switch_timestamps.popleft()
                        else:
                            break

                    self.session_state.metrics.recent_switch_count = len(
                        self.window_switch_timestamps
                    )
                    self.session_state.metrics.rapid_switching_detected = (
                        self.session_state.metrics.recent_switch_count
                        >= self.rapid_switch_threshold
                    )

                    if not self.session_state.metrics.rapid_switching_detected:
                        self.rapid_switch_popup_shown = False

                snapshot = self.create_snapshot(
                    active_window=active_window,
                    idle_seconds=idle_seconds,
                    take_screenshot=window_changed,
                )

                self.session_state.monitoring_history.append(snapshot)
                self.session_state.current_topic = snapshot.extracted_topic
                self._add_unique_keywords(snapshot.extracted_keywords)

                if self.on_snapshot is not None:
                    self.on_snapshot(snapshot, self.session_state)

                time_on_current_window = (
                    datetime.now() - self.current_window_start_time
                ).total_seconds()

                print("=" * 60)
                print(f"Snapshot #{len(self.session_state.monitoring_history)}")
                print(f"Time: {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Window: {snapshot.active_window_title}")
                print(f"Process: {snapshot.process_name}")
                print(f"Detected Topic: {snapshot.extracted_topic}")
                print(f"Keywords: {', '.join(snapshot.extracted_keywords)}")
                print(f"AI Assistant Enabled: {self.ai_assistant_enabled}")
                print(f"Active study time: {active_study_minutes} minute(s)")
                print(
                    f"Tab/Window switches: "
                    f"{self.session_state.metrics.tab_switch_count}"
                )
                print(
                    f"Recent switches in "
                    f"{int(self.rapid_switch_window_seconds)}s: "
                    f"{self.session_state.metrics.recent_switch_count}"
                )
                print(
                    f"Rapid switching detected: "
                    f"{self.session_state.metrics.rapid_switching_detected}"
                )
                print(f"Time on current window: {time_on_current_window:.1f} seconds")
                print(f"System idle time: {idle_seconds:.1f} seconds")

                if snapshot.clipboard_text:
                    print(f"Clipboard: {snapshot.clipboard_text[:100]}")
                else:
                    print("Clipboard: [empty or non-text]")

                if snapshot.ocr_text:
                    print("OCR: [captured this cycle]")
                else:
                    print("OCR: [not run this cycle]")

                print()

                self.last_window_title = active_window.title

                while self.running and (time.time() - loop_start) < self.poll_interval_seconds:
                    time.sleep(0.05)

        except KeyboardInterrupt:
            print()
            print("Monitoring stopped by keyboard interrupt.")
        finally:
            self.running = False
            print(
                f"Total snapshots collected: "
                f"{len(self.session_state.monitoring_history)}"
            )
            print(
                f"Total window switches: "
                f"{self.session_state.metrics.tab_switch_count}"
            )
            print(f"Last detected topic: {self.session_state.current_topic}")