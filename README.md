# AI Study Copilot

## Overview

This project is a two-part hackathon project focused on improving study habits, productivity, and the study environment.

The system is split into two connected subsystems:

1. Subsystem 1 focuses on physical study conditions using hardware such as an Arduino Uno and Rubik Pi.
2. Subsystem 2 focuses on software-based monitoring of the user's study behavior and screen activity.

The goal is for both subsystems to eventually work together as one product.

Subsystem 1 monitors environmental factors such as room temperature and light levels. Using sensors connected to an Arduino, the system can detect## Features

### Subsystem 1 - Hardware Environment Monitor

* Uses an Arduino Uno and Rubik Pi
* Monitors room temperature
* Monitors room light levels
* Uses LEDs to indicate environmental conditions
* Sends sensor data to a connected device
* Can be expanded to provide environmental recommendations

### Subsystem 2 - AI Study Assistant

* Tracks active window titles and processes
* Detects topic keywords from current activity
* Monitors window switching behavior
* Detects excessive tab switching
* Detects inactivity and displays reminders
* Generates a study session summary file
* Exports unique keywords gathered during a session
* GUI dashboard for starting and stopping monitoring

## Project Structure.

## Features

* Tracks active window titles and processes
* Detects topic keywords from current activity
* Monitors window switching behavior
* Detects excessive tab switching
* Detects inactivity and displays reminders
* Generates a study session summary file
* Exports unique keywords gathered during a session
* GUI dashboard for starting and stopping monitoring

## Project Structure

```text
app/
├── main.py
├── ui/
├── monitoring/
├── analysis/
├── popups/
├── exports/
└── utils/
```

The software portion of the repository currently contains the code for Subsystem 2. Hardware files, Arduino code, and Rubik Pi setup for Subsystem 1 may be added later.

## Requirements

* Python 3.10 or newer
* Windows operating system
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

### Windows

```bash
.venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Program

From the project root folder, run:

```bash
python app/main.py
```

## Notes

* The program is currently designed for Windows.
* Some features may require administrator permissions depending on how window monitoring is implemented.
* Generated files such as keyword exports or study summaries are not included in the repository.
* The `.venv` folder should not be uploaded to GitHub.

## Future Improvements

* Fully connect both subsystems together
* Allow Subsystem 2 to trigger environmental recommendations through Subsystem 1
* Add on

## Authors

Ophir Maor, Darren Rauvola, Dmitri Singer
