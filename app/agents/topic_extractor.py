import re
from collections import Counter
from typing import List


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "for", "to", "of", "in", "on", "at",
    "by", "with", "from", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "as", "if", "then", "than", "into",
    "about", "over", "under", "between", "through", "during", "without",
    "within", "also", "can", "could", "should", "would", "you", "your", "we",
    "they", "he", "she", "i", "me", "my", "our", "their", "not", "no", "yes",
    "do", "does", "did", "done", "have", "has", "had", "will", "just", "so",
    "what", "when", "where", "why", "how", "all", "any", "each", "few", "more",
    "most", "other", "some", "such", "only", "own", "same", "too", "very",
    "s", "t", "ll", "re", "ve", "d", "m",
}

NOISE_WORDS = {
    "google", "chrome", "mozilla", "firefox", "visual", "studio", "code",
    "discord", "powershell", "command", "prompt", "announcements",
    "general", "chat", "welcome", "server", "feedback", "window",
    "topic", "keywords", "snapshot", "enabled", "disabled", "status",
    "worker", "layout", "popup", "none", "self", "true", "false",
    "python", "main", "app", "monitor", "monitoring", "assistant",
    "copilot", "label", "button", "click", "stop", "start",
    "process", "clipboard", "current", "last", "switches",
    "bookmarks", "bookmark", "translate", "details", "extractor",
    "import", "from", "default", "factory", "dataclass", "field",
    "list", "str", "int", "float", "bool", "path", "optional",
}

FILE_EXTENSION_WORDS = {
    "py", "cpp", "c", "h", "hpp", "java", "js", "ts", "tsx", "jsx",
    "html", "css", "json", "md", "txt", "pdf", "pptx", "docx",
}

COMMON_UI_WORDS = {
    "home", "settings", "search", "results", "page", "tab", "new",
    "open", "close", "back", "next", "previous", "save", "edit",
    "view", "tools", "help", "file", "folder", "untitled",
    "dashboard", "panel", "control", "session", "study",
    "time", "seconds", "keyword", "enable", "enabled",
    "disable", "disabled", "inactivity",
}

GENERIC_ACTION_WORDS = {
    "using", "trying", "making", "running", "clicked", "opened",
    "closed", "started", "stopped", "updated", "selected",
    "loading", "saving", "editing", "viewing",
}


ACADEMIC_BOOST_WORDS = {
    "assignment", "homework", "midterm", "final", "quiz", "exam",
    "lecture", "notes", "chapter", "proof", "theorem", "lemma",
    "algorithm", "runtime", "complexity", "derivative", "integral",
    "matrix", "probability", "distribution", "physics", "chemistry",
    "biology", "calculus", "history", "literature", "graph",
    "search", "tree", "trees", "hash", "weighted", "shortest",
    "path", "traversal", "dijkstra", "breadth", "depth",
}

BAD_TITLE_SEGMENTS = {
    "google chrome",
    "visual studio code",
    "mozilla firefox",
    "microsoft edge",
    "new tab",
    "home",
    "dashboard",
    "canvas",
    "discord",
}

BAD_CLIPBOARD_PATTERNS = {
    "python app/main.py",
    "python",
    ".py",
    "powershell",
    "ctrl",
}


class TopicExtractor:
    def clean_window_title(self, title: str) -> str:
        if not title:
            return ""

        cleaned = title.strip()
        cleaned = re.sub(r"\(\d+\)", "", cleaned).strip()

        suffixes_to_remove = [
            " - Google Chrome",
            " - Visual Studio Code",
            " - Mozilla Firefox",
            " - Microsoft Edge",
            " - Notepad",
        ]

        for suffix in suffixes_to_remove:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()

        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def split_title_segments(self, title: str) -> List[str]:
        if not title:
            return []

        parts = re.split(r"\s*[|\-:]\s*", title)
        segments = []

        for part in parts:
            cleaned = part.strip()
            lower = cleaned.lower()

            if not cleaned:
                continue
            if lower in BAD_TITLE_SEGMENTS:
                continue
            if lower in NOISE_WORDS:
                continue
            if lower in COMMON_UI_WORDS:
                continue
            if lower.startswith("#"):
                continue

            segments.append(cleaned)

        return segments

    def clean_code_or_file_title(self, title: str) -> str:
        if not title:
            return ""

        cleaned = title.strip()

        if " - " in cleaned:
            cleaned = cleaned.split(" - ")[0].strip()

        cleaned = cleaned.replace("_", " ")
        cleaned = cleaned.replace("-", " ")

        cleaned = re.sub(
            r"\.([A-Za-z0-9]+)$",
            lambda match: ""
            if match.group(1).lower() in FILE_EXTENSION_WORDS
            else match.group(0),
            cleaned,
        )

        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        if not cleaned:
            return ""

        words = cleaned.split()
        normalized_words = []

        for word in words:
            if word.lower() in FILE_EXTENSION_WORDS:
                continue

            if len(word) <= 4 and word.isupper():
                normalized_words.append(word)
            else:
                normalized_words.append(word.capitalize())

        return " ".join(normalized_words)

    def is_code_or_file_context(self, window_title: str, process_name: str) -> bool:
        title = (window_title or "").lower()
        process = (process_name or "").lower()

        code_processes = {
            "code.exe",
            "devenv.exe",
            "pycharm64.exe",
            "idea64.exe",
            "notepad++.exe",
        }

        if process in code_processes:
            return True

        file_extensions = [
            ".py", ".cpp", ".c", ".h", ".hpp", ".java", ".js",
            ".ts", ".tsx", ".jsx", ".html", ".css", ".json",
            ".md", ".txt", ".pdf", ".pptx", ".docx",
        ]

        for extension in file_extensions:
            if extension in title:
                return True

        return False

    def looks_like_garbage_token(self, word: str) -> bool:
        if not word:
            return True

        if len(word) < 3:
            return True

        if len(word) > 20:
            return True

        if re.search(r"\d", word):
            return True

        if re.fullmatch(r"[a-z]{1,2}", word):
            return True

        if re.fullmatch(r"[a-z]+com[a-z]*", word):
            return True

        if re.fullmatch(r"[a-f0-9\-]{8,}", word):
            return True

        consonants_only = re.fullmatch(r"[bcdfghjklmnpqrstvwxyz]{6,}", word)
        if consonants_only:
            return True

        return False

    def is_meaningful_keyword(self, word: str) -> bool:
        if not word:
            return False

        if word in STOPWORDS:
            return False

        if word in NOISE_WORDS:
            return False

        if word in COMMON_UI_WORDS:
            return False

        if word in FILE_EXTENSION_WORDS:
            return False

        if word in GENERIC_ACTION_WORDS:
            return False

        if self.looks_like_garbage_token(word):
            return False

        if word.isdigit():
            return False

        if re.fullmatch(r"\d+[a-z]+", word):
            return False

        if re.fullmatch(r"[a-z]+\d+", word):
            return False

        if re.fullmatch(r"[_\-\W]+", word):
            return False

        if len(set(word)) == 1:
            return False

        if word.endswith("ing") and len(word) <= 7:
            return False

        if word.endswith("ed") and len(word) <= 6:
            return False

        return True

    def tokenize(self, text: str) -> List[str]:
        if not text:
            return []

        raw_words = re.findall(r"[A-Za-z][A-Za-z'\-]*", text.lower())
        tokens = []

        for word in raw_words:
            word = word.strip("'").strip("-")
            if not self.is_meaningful_keyword(word):
                continue
            tokens.append(word)

        return tokens

    def score_keyword(self, word: str, source: str, segment_score: int = 0) -> int:
        score = 0

        if source == "title":
            score += 3
        elif source == "file":
            score += 4
        elif source == "ocr":
            score += 6
        elif source == "clipboard":
            score += 2
        else:
            score += 1

        score += segment_score

        if len(word) >= 5:
            score += 1

        if len(word) >= 8:
            score += 1

        if word in ACADEMIC_BOOST_WORDS:
            score += 4

        return score

    def score_title_segment(self, segment: str) -> int:
        tokens = self.tokenize(segment)

        if not tokens:
            return -100

        score = 0
        score += min(len(tokens), 4)

        for token in tokens:
            if token in ACADEMIC_BOOST_WORDS:
                score += 3
            if len(token) >= 7:
                score += 1

        if len(segment.split()) <= 1:
            score -= 1

        if len(segment) > 60:
            score -= 2

        return score

    def extract_keywords_from_text(
        self,
        text: str,
        source: str,
        top_n: int,
        segment_score: int = 0,
    ) -> List[str]:
        tokens = self.tokenize(text)
        if not tokens:
            return []

        counts = Counter(tokens)

        ranked = sorted(
            counts.items(),
            key=lambda item: (
                -(item[1] * 10 + self.score_keyword(item[0], source, segment_score)),
                item[0],
            ),
        )

        return [word for word, _ in ranked[:top_n]]

    def extract_keywords_from_title_segments(
        self,
        title: str,
        top_n: int = 5,
    ) -> List[str]:
        segments = self.split_title_segments(title)
        if not segments:
            return []

        scored_segments = sorted(
            segments,
            key=lambda segment: self.score_title_segment(segment),
            reverse=True,
        )

        merged = []
        seen = set()

        for segment in scored_segments[:2]:
            segment_score = self.score_title_segment(segment)
            keywords = self.extract_keywords_from_text(
                text=segment,
                source="title",
                top_n=top_n,
                segment_score=segment_score,
            )

            for keyword in keywords:
                normalized = keyword.lower()
                if normalized in seen:
                    continue

                seen.add(normalized)
                merged.append(keyword)

                if len(merged) >= top_n:
                    return merged

        return merged

    def is_useful_clipboard_text(self, clipboard_text: str) -> bool:
        if not clipboard_text:
            return False

        text = clipboard_text.strip().lower()

        if len(text) < 18:
            return False

        if text in BAD_CLIPBOARD_PATTERNS:
            return False

        if re.fullmatch(r"[\W_]+", text):
            return False

        if len(text.split()) <= 2:
            return False

        return True

    def merge_keywords(
        self,
        primary_keywords: List[str],
        secondary_keywords: List[str],
        top_n: int,
    ) -> List[str]:
        merged = []
        seen = set()

        for keyword in primary_keywords + secondary_keywords:
            normalized = keyword.lower()
            if normalized in seen:
                continue

            seen.add(normalized)
            merged.append(keyword)

            if len(merged) >= top_n:
                break

        return merged

    def pick_best_topic_segment(self, cleaned_title: str) -> str:
        segments = self.split_title_segments(cleaned_title)
        if not segments:
            return cleaned_title

        best_segment = max(segments, key=self.score_title_segment)

        if self.score_title_segment(best_segment) < 0:
            return cleaned_title

        return best_segment

    def extract_snapshot_keywords(
        self,
        window_title: str,
        clipboard_text: str,
        process_name: str = "",
    ) -> List[str]:
        cleaned_title = self.clean_window_title(window_title)

        if self.is_code_or_file_context(window_title, process_name):
            cleaned_file_title = self.clean_code_or_file_title(cleaned_title)
            title_keywords = self.extract_keywords_from_text(
                text=cleaned_file_title,
                source="file",
                top_n=3,
                segment_score=2,
            )
        else:
            title_keywords = self.extract_keywords_from_title_segments(
                cleaned_title,
                top_n=2,
            )

        text_keywords = []
        if self.is_useful_clipboard_text(clipboard_text):
            text_keywords = self.extract_keywords_from_text(
                text=clipboard_text,
                source="ocr",
                top_n=6,
            )

        return self.merge_keywords(
            primary_keywords=text_keywords,
            secondary_keywords=title_keywords,
            top_n=6,
        )

    def extract_topic(
        self,
        window_title: str,
        clipboard_text: str,
        process_name: str = "",
    ) -> str:
        cleaned_title = self.clean_window_title(window_title)

        if self.is_code_or_file_context(window_title, process_name):
            topic = self.clean_code_or_file_title(cleaned_title)
        else:
            topic = self.pick_best_topic_segment(cleaned_title)

        text_keywords = []
        if self.is_useful_clipboard_text(clipboard_text):
            text_keywords = self.extract_keywords_from_text(
                text=clipboard_text,
                source="ocr",
                top_n=3,
            )

        if len(text_keywords) >= 2:
            return ", ".join(text_keywords)

        if topic:
            return topic

        if text_keywords:
            return ", ".join(text_keywords)

        return "Unknown Topic"