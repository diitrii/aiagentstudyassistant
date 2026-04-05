from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class MonitoringSnapshot:
    timestamp: datetime
    active_window_title: str
    process_name: str
    process_id: Optional[int]
    screenshot_path: Optional[Path]
    clipboard_text: str
    ocr_text: str = ""
    extracted_topic: str = ""
    extracted_keywords: list[str] = field(default_factory=list)
    idle_seconds: float = 0.0


@dataclass
class ProductivityMetrics:
    focus_score: float = 100.0
    distraction_score: float = 0.0
    productivity_score: float = 100.0
    tab_switch_count: int = 0
    repeated_topic_count: int = 0
    break_recommended: bool = False
    rapid_switching_detected: bool = False
    recent_switch_count: int = 0


@dataclass
class StudySessionState:
    current_topic: str = ""
    current_subtopic: str = ""

    topics_to_review: list[str] = field(default_factory=list)
    cheat_sheet_items: list[str] = field(default_factory=list)
    study_guide_items: list[str] = field(default_factory=list)
    weak_topics: list[str] = field(default_factory=list)

    unique_keywords: list[str] = field(default_factory=list)
    monitoring_history: list[MonitoringSnapshot] = field(default_factory=list)
    metrics: ProductivityMetrics = field(default_factory=ProductivityMetrics)

    topic_keywords: dict[str, set[str]] = field(
        default_factory=lambda: defaultdict(set)
    )
    topic_durations: dict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    last_topic: str | None = None