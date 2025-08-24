﻿# PCSuite


# PCSuite - Professional PC Cleaning Suite

PCSuite is a robust, modular, and user-friendly PC cleaning suite for Windows, featuring advanced analytics, automation, and a modern GUI. It is designed for both power users and everyday users who want to keep their systems clean, fast, and safe.

## Features

- **Advanced CLI**: Clean, quarantine, inspect, and manage your system from the command line with rich options and automation.
- **Analytics**: View cleaning stats, trends, recommendations, and export reports to CSV.
- **Automation**: Schedule cleanups using real Windows Task Scheduler integration.
- **GUI**: Modern PyQt5 interface with live stats, one-click cleaning, scheduling, and quarantine management.
- **Quarantine**: Safely isolate and restore files, with full management from CLI and GUI.
- **Power-user tools**: Inspect reports, filter cleaning, and more.

## Installation

1. Clone the repository:
	```sh
	git clone https://github.com/LogunLACC/PCSuite.git
	cd PCSuite
	```
2. Create and activate a virtual environment (recommended):
	```sh
	python -m venv .venv
	.venv\Scripts\activate  # On Windows
	```
3. Install dependencies:
	```sh
	pip install -e .
	```

## Usage

### Command Line Interface (CLI)

Run the main CLI:
```sh
python -m pcsuite.cli.main [COMMAND] [OPTIONS]
```

#### Cleaning
```sh
python -m pcsuite.cli.main clean run --mode quarantine --yes
```

#### Analytics
```sh
python -m pcsuite.cli.main analytics stats
python -m pcsuite.cli.main analytics trends
python -m pcsuite.cli.main analytics recommend
python -m pcsuite.cli.main analytics export analytics_export.csv
```

#### Scheduling (Automation)
```sh
python -m pcsuite.cli.main schedule create --name "WeeklyClean" --when weekly --time 03:00
python -m pcsuite.cli.main schedule list
python -m pcsuite.cli.main schedule delete --name "WeeklyClean"
```

#### Quarantine Management
```sh
python -m pcsuite.cli.main quarantine list
python -m pcsuite.cli.main quarantine restore <filename> --yes
python -m pcsuite.cli.main quarantine purge --yes
```

### Graphical User Interface (GUI)

Launch the GUI:
```sh
python -m pcsuite.gui.main
```

Features:
- Live stats and analytics
- One-click cleaning
- Schedule management
- Quarantine management (restore/purge)

## Reports & Quarantine

- Cleaning reports are saved in the `reports/` directory as JSON files.
- Quarantined files are stored in the `Quarantine/` directory, with metadata in `.meta.json` files.

## Requirements

- Python 3.11+
- Windows 10/11
- [PyQt5](https://pypi.org/project/PyQt5/), [Typer](https://typer.tiangolo.com/), [Rich](https://rich.readthedocs.io/), [psutil](https://pypi.org/project/psutil/), [pywin32](https://pypi.org/project/pywin32/), [pyyaml](https://pypi.org/project/PyYAML/), [send2trash](https://pypi.org/project/Send2Trash/)

## Contributing

Pull requests and feedback are welcome!

## License

MIT License
