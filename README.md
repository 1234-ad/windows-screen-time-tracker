# Windows Screen Time Tracker

A comprehensive screen time monitoring application for Windows that tracks application usage and provides detailed analytics.

## Features

- **Real-time Tracking**: Monitor active window usage in real-time
- **Daily Statistics**: View today's application usage breakdown
- **All-time Analytics**: Track cumulative usage across all sessions
- **Visual Charts**: Pie charts and bar graphs for usage visualization
- **Data Persistence**: Automatic saving and loading of usage data
- **User-friendly GUI**: Clean, intuitive interface with tabbed navigation

## Installation

### Prerequisites
- Windows 10/11
- Python 3.7 or higher

### Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/1234-ad/windows-screen-time-tracker.git
   cd windows-screen-time-tracker
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python screen_time_tracker.py
   ```

## Usage

1. **Start Tracking**: Click "Start Tracking" to begin monitoring
2. **View Statistics**: Switch between tabs to view different analytics
3. **Stop Tracking**: Click "Stop Tracking" to pause monitoring
4. **Refresh Data**: Click "Refresh Data" to update displays

## How It Works

The application uses Windows APIs to:
- Detect the currently active window
- Identify the application process
- Track time spent in each application
- Store data persistently in JSON format

## Data Storage

Usage data is stored locally in `screen_time_data.json` with the following structure:
- `app_usage`: Total time per application (all-time)
- `daily_usage`: Daily breakdown by date and application

## Privacy

- All data is stored locally on your machine
- No data is transmitted to external servers
- You have full control over your usage data

## Requirements

- `psutil`: Process and system monitoring
- `pywin32`: Windows API access
- `matplotlib`: Chart generation
- `numpy`: Numerical computations
- `tkinter`: GUI framework (included with Python)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Troubleshooting

### Common Issues

1. **Import Error**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission Error**: Run as administrator if needed

3. **Chart Display Issues**: Ensure matplotlib is properly installed

### System Requirements

- Windows 10/11
- Python 3.7+
- 50MB free disk space
- Administrative privileges (for some system monitoring features)