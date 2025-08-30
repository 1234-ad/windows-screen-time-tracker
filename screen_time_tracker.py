"""
Windows Screen Time Tracker
A comprehensive screen time monitoring application for Windows

Features:
- Real-time active window tracking
- Daily and all-time usage statistics
- Visual charts and analytics
- Data persistence
- User-friendly GUI interface
"""

import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import win32gui
import win32process
import time
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ScreenTimeTracker:
    def __init__(self):
        self.data_file = "screen_time_data.json"
        self.app_usage = defaultdict(int)  # app_name: seconds
        self.daily_usage = defaultdict(lambda: defaultdict(int))  # date: {app: seconds}
        self.is_tracking = False
        self.current_window = None
        self.last_check_time = time.time()
        self.load_data()
        
    def get_active_window_info(self):
        """Get information about the currently active window"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                window_title = win32gui.GetWindowText(hwnd)
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                app_name = process.name()
                return app_name, window_title
        except:
            pass
        return None, None
    
    def start_tracking(self):
        """Start tracking screen time"""
        self.is_tracking = True
        self.last_check_time = time.time()
        
    def stop_tracking(self):
        """Stop tracking screen time"""
        self.is_tracking = False
        self.save_data()
        
    def update_usage(self):
        """Update usage statistics"""
        if not self.is_tracking:
            return
            
        current_time = time.time()
        time_diff = current_time - self.last_check_time
        
        app_name, window_title = self.get_active_window_info()
        
        if app_name and time_diff < 5:  # Only count if less than 5 seconds (user is active)
            self.app_usage[app_name] += time_diff
            today = datetime.now().strftime("%Y-%m-%d")
            self.daily_usage[today][app_name] += time_diff
            
        self.last_check_time = current_time
        
    def get_top_apps(self, limit=10):
        """Get top apps by usage time"""
        sorted_apps = sorted(self.app_usage.items(), key=lambda x: x[1], reverse=True)
        return sorted_apps[:limit]
    
    def get_daily_total(self, date=None):
        """Get total screen time for a specific date"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return sum(self.daily_usage[date].values())
    
    def format_time(self, seconds):
        """Format seconds to human readable time"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def save_data(self):
        """Save tracking data to file"""
        data = {
            'app_usage': dict(self.app_usage),
            'daily_usage': dict(self.daily_usage)
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        """Load tracking data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.app_usage = defaultdict(int, data.get('app_usage', {}))
                    self.daily_usage = defaultdict(lambda: defaultdict(int))
                    for date, apps in data.get('daily_usage', {}).items():
                        self.daily_usage[date] = defaultdict(int, apps)
            except:
                pass

class ScreenTimeGUI:
    def __init__(self):
        self.tracker = ScreenTimeTracker()
        self.root = tk.Tk()
        self.root.title("Windows Screen Time Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Create GUI elements
        self.create_widgets()
        
        # Start background tracking
        self.tracking_thread = None
        self.start_background_tracking()
        
    def create_widgets(self):
        """Create GUI widgets"""
        # Title
        title_label = tk.Label(self.root, text="Windows Screen Time Tracker", 
                              font=("Arial", 16, "bold"), bg='#f0f0f0')
        title_label.pack(pady=10)
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(pady=10)
        
        self.start_btn = tk.Button(control_frame, text="Start Tracking", 
                                  command=self.start_tracking, bg='#4CAF50', fg='white')
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(control_frame, text="Stop Tracking", 
                                 command=self.stop_tracking, bg='#f44336', fg='white')
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = tk.Button(control_frame, text="Refresh Data", 
                                    command=self.refresh_display, bg='#2196F3', fg='white')
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Status: Stopped", 
                                    font=("Arial", 10), bg='#f0f0f0')
        self.status_label.pack(pady=5)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Today's usage tab
        self.today_frame = tk.Frame(self.notebook)
        self.notebook.add(self.today_frame, text="Today's Usage")
        self.create_today_tab()
        
        # All time usage tab
        self.alltime_frame = tk.Frame(self.notebook)
        self.notebook.add(self.alltime_frame, text="All Time Usage")
        self.create_alltime_tab()
        
        # Statistics tab
        self.stats_frame = tk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        self.create_stats_tab()
        
    def create_today_tab(self):
        """Create today's usage tab"""
        # Today's total time
        self.today_total_label = tk.Label(self.today_frame, text="Today's Total: 00:00:00", 
                                         font=("Arial", 12, "bold"))
        self.today_total_label.pack(pady=10)
        
        # Today's app list
        self.today_tree = ttk.Treeview(self.today_frame, columns=('Time',), show='tree headings')
        self.today_tree.heading('#0', text='Application')
        self.today_tree.heading('Time', text='Time Used')
        self.today_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def create_alltime_tab(self):
        """Create all time usage tab"""
        # All time total
        self.alltime_total_label = tk.Label(self.alltime_frame, text="Total Time: 00:00:00", 
                                           font=("Arial", 12, "bold"))
        self.alltime_total_label.pack(pady=10)
        
        # All time app list
        self.alltime_tree = ttk.Treeview(self.alltime_frame, columns=('Time',), show='tree headings')
        self.alltime_tree.heading('#0', text='Application')
        self.alltime_tree.heading('Time', text='Time Used')
        self.alltime_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def create_stats_tab(self):
        """Create statistics tab with charts"""
        # Chart frame
        self.chart_frame = tk.Frame(self.stats_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def start_tracking(self):
        """Start tracking"""
        self.tracker.start_tracking()
        self.status_label.config(text="Status: Tracking...")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
    def stop_tracking(self):
        """Stop tracking"""
        self.tracker.stop_tracking()
        self.status_label.config(text="Status: Stopped")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.refresh_display()
        
    def start_background_tracking(self):
        """Start background tracking thread"""
        def track():
            while True:
                if self.tracker.is_tracking:
                    self.tracker.update_usage()
                time.sleep(1)
                
        self.tracking_thread = threading.Thread(target=track, daemon=True)
        self.tracking_thread.start()
        
        # Auto refresh display every 10 seconds
        self.root.after(10000, self.auto_refresh)
        
    def auto_refresh(self):
        """Auto refresh display"""
        if self.tracker.is_tracking:
            self.refresh_display()
        self.root.after(10000, self.auto_refresh)
        
    def refresh_display(self):
        """Refresh all display data"""
        self.update_today_display()
        self.update_alltime_display()
        self.update_stats_display()
        
    def update_today_display(self):
        """Update today's usage display"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_data = self.tracker.daily_usage[today]
        total_time = sum(today_data.values())
        
        self.today_total_label.config(text=f"Today's Total: {self.tracker.format_time(total_time)}")
        
        # Clear existing items
        for item in self.today_tree.get_children():
            self.today_tree.delete(item)
            
        # Add today's apps
        sorted_apps = sorted(today_data.items(), key=lambda x: x[1], reverse=True)
        for app, time_used in sorted_apps:
            self.today_tree.insert('', tk.END, text=app, values=(self.tracker.format_time(time_used),))
            
    def update_alltime_display(self):
        """Update all time usage display"""
        total_time = sum(self.tracker.app_usage.values())
        self.alltime_total_label.config(text=f"Total Time: {self.tracker.format_time(total_time)}")
        
        # Clear existing items
        for item in self.alltime_tree.get_children():
            self.alltime_tree.delete(item)
            
        # Add all time apps
        top_apps = self.tracker.get_top_apps(20)
        for app, time_used in top_apps:
            self.alltime_tree.insert('', tk.END, text=app, values=(self.tracker.format_time(time_used),))
            
    def update_stats_display(self):
        """Update statistics display with charts"""
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        # Create pie chart of top apps
        top_apps = self.tracker.get_top_apps(8)
        if top_apps:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Pie chart
            apps, times = zip(*top_apps)
            ax1.pie(times, labels=apps, autopct='%1.1f%%', startangle=90)
            ax1.set_title('App Usage Distribution')
            
            # Bar chart
            ax2.bar(range(len(apps)), [t/3600 for t in times])  # Convert to hours
            ax2.set_xlabel('Applications')
            ax2.set_ylabel('Hours')
            ax2.set_title('Usage Time (Hours)')
            ax2.set_xticks(range(len(apps)))
            ax2.set_xticklabels(apps, rotation=45, ha='right')
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
    def run(self):
        """Run the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle window closing"""
        self.tracker.stop_tracking()
        self.root.destroy()

if __name__ == "__main__":
    app = ScreenTimeGUI()
    app.run()