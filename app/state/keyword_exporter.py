import os
from datetime import datetime
from pathlib import Path


def format_duration(seconds: int) -> str:
    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if minutes > 0:
        return f"{minutes} min {remaining_seconds} sec"

    return f"{remaining_seconds} sec"


def export_keywords_to_file(session_state) -> str:
    session_dir = Path("data/sessions")
    session_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = session_dir / f"study_session_{timestamp}.txt"

    lines = []

    lines.append("STUDY SESSION SUMMARY")
    lines.append("=" * 50)
    lines.append("")

    lines.append(
        f"Total Unique Keywords: {len(session_state.unique_keywords)}"
    )
    lines.append(
        f"Window Switches: {session_state.metrics.tab_switch_count}"
    )
    lines.append("")

    lines.append("TOPICS")
    lines.append("=" * 50)
    lines.append("")

    sorted_topics = sorted(
        session_state.topic_durations.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    for topic, duration in sorted_topics:
        lines.append(f"Topic: {topic}")
        lines.append(f"Time Spent: {format_duration(duration)}")

        keywords = sorted(session_state.topic_keywords.get(topic, []))

        if keywords:
            lines.append("Keywords:")
            for keyword in keywords:
                lines.append(f"- {keyword}")

        lines.append("")
        lines.append("-" * 50)
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")

    return str(output_path)


def open_file_in_default_app(file_path: str) -> None:
    os.startfile(file_path)