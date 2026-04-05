# AI Study Copilot - Subsystem 2

This project is the second subsystem of a larger hackathon project focused on improving study habits and productivity.

Subsystem 2 monitors the user's active windows, extracts keywords/topics from what they are working on, tracks inactivity, detects excessive tab switching, and provides study-related reminders or popups.

## Features

* Active window tracking
* Process name tracking
* Topic extraction from window titles
* Keyword extraction
* Inactivity detection
* Tab/window switching detection
* Popups for inactivity or distraction
* Export of study session keywords and summaries
* GUI dashboard to start and stop monitoring

## Requirements

* Python 3.10+
* Windows
* VS Code recommended

## Installation

1. Clone the repository:

```bash
git clone <repo-url>
cd <repo-folder>
```

2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the virtual environment:

Windows:

```bash
.venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Program

Run the main file:

```bash
python app/main.py
```

The GUI should appear and allow you to start and stop the assistant.

## Project Structure

```text
app/
├── main.py
├── ui/
├── monitoring/
├── popup/
├── exporters/
├── utils/
```

## Notes

* Do not upload the `.venv` folder to GitHub.
* The `.gitignore` file is already configured to ignore virtual environments and cache files.
* Some functionality may require administrator permissions depending on the monitoring libraries being used.
* The project is currently designed for Windows.

## Future Improvements

* Smarter topic detection
* Better keyword grouping
* Online search assistance
* Study recommendations based on active content
* Arduino / Rubik Pi integration with subsystem 1
* Improved popup design and customization

## Authors

Ophir Maor, Darren Rauvola, Dmitri Singer
