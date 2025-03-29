import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os

class F1Dashboard:
    def __init__(self, year, event_name, dark_mode=True):
        os.makedirs('./f1_cache', exist_ok=True)
        fastf1.Cache.enable_cache('./f1_cache')
        
        # Dark mode setup
        plt.style.use('dark_background' if dark_mode else 'default')
        
        self.year = year
        self.event_name = event_name
        self.session = fastf1.get_session(year, event_name, 'Race')
        
        # Explicitly load session
        try:
            self.session.load() #live=True
        except Exception as e:
            print(f"Error loading session: {e}")
            return
        
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(
            2, 2, figsize=(16, 10), 
            gridspec_kw={'width_ratios': [2, 1]}
        )
        
        # Color adjustments for dark mode
        fig_color = 'black' if dark_mode else 'white'
        text_color = 'white' if dark_mode else 'black'
        
        self.fig.patch.set_facecolor(fig_color)
        self.fig.suptitle(f'F1 Live Dashboard - {year} {event_name}', color=text_color)
        
        try:
            self.track_plot = self.session.get_circuit().plot_track(ax=self.ax1)
            self.ax1.set_title('Track Layout', color=text_color)
        except:
            self.ax1.text(0.5, 0.5, 'N/A', 
                          horizontalalignment='center', 
                          verticalalignment='center',
                          color=text_color)
            self.ax1.set_title('Track Layout', color=text_color)
        
        for ax in [self.ax2, self.ax3, self.ax4]:
            ax.set_title(ax.get_title(), color=text_color)
        
        self.animation = animation.FuncAnimation(
            self.fig, 
            self.update_dashboard, 
            interval=5000,
            cache_frame_data=False
        )
    
    def plot_driver_positions(self):
        plt.figure(figsize=(10, 8))

        # Get all laps and all drivers
        laps = self.session.laps
        drivers = self.session.drivers  # List of driver numbers



        # Plot track layout if available
        try:
            track_data = self.session.get_circuit()
            plt.plot(track_data['X'], track_data['Y'], 'k-', linewidth=2, alpha=0.5)  # Track outline
        except:
            print("No track layout available.")

        # Plot driver positions
        for driver in drivers:
            driver_laps = laps.pick_driver(driver)
            if not driver_laps.empty:
                driver_lap = driver_laps.iloc[-1]  # Latest lap
                pos_data = driver_lap.get_car_data().add_distance()
        
                if not pos_data.empty:
                    plt.scatter(pos_data['X'], pos_data['Y'], label=driver)

        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.title(f"Driver Positions - {self.event_name} {self.year}")
        plt.legend()
        plt.show()


    def fetch_live_positions(self):
        while True:
            self.session.load(live=True)  # Reload latest telemetry

            plt.clf()  # Clear old plot

            for driver in self.session.drivers:
                try:
                    driver_lap = self.session.laps.pick_driver(driver).pick_fastest()
                    pos_data = driver_lap.get_pos_data()
                    plt.scatter(pos_data['X'], pos_data['Y'], label=driver)
                except:
                    print(f"No data for {driver}")

            plt.legend()
            plt.pause(2)  # Refresh every 2 seconds

    def update_dashboard(self, frame):
        self.ax1.clear()  # Clear old positions
        self.ax1.set_title("Live Driver Positions", color="white")

        try:
            laps = self.session.laps
            drivers = self.session.drivers

            for driver in drivers:
                driver_lap = laps.pick_driver(driver).pick_fastest()
                pos_data = driver_lap.get_pos_data()
            
                self.ax1.scatter(pos_data['X'], pos_data['Y'], label=driver)

            self.ax1.legend()
        except Exception as e:
            self.ax1.text(0.5, 0.5, f"Error: {e}", ha="center", va="center", color="white")



        for ax in [self.ax2, self.ax3, self.ax4]:
            ax.clear()
        
        try:
            laps = self.session.laps
            
            # Tyre Strategies
            tyre_strategies = laps.tire_strategies()
            for driver, strategy in tyre_strategies.items():
                self.ax2.text(0.1, 0.9 - (0.1 * driver), 
                              f"{driver}: {' → '.join(strategy)}", 
                              transform=self.ax2.transAxes,
                              color='white')
            self.ax2.set_title('Tyre Strategies', color='white')
        except:
            self.ax2.text(0.5, 0.5, 'N/A', 
                          horizontalalignment='center', 
                          verticalalignment='center',
                          color='white')
            self.ax2.set_title('Tyre Strategies', color='white')
        
        try:
            # Lap Times
            current_lap_times = laps.pick_fastest()
            times = current_lap_times['LapTime'].dt.total_seconds()
            drivers = current_lap_times['Driver']
            self.ax3.bar(drivers, times, color='red')
            self.ax3.set_xticklabels(drivers, rotation=45, color='white')
            self.ax3.set_ylabel('Lap Time (seconds)', color='white')
            self.ax3.set_title('Current Lap Times', color='white')
        except:
            self.ax3.text(0.5, 0.5, 'N/A', 
                          horizontalalignment='center', 
                          verticalalignment='center',
                          color='white')
            self.ax3.set_title('Current Lap Times', color='white')
        
        try:
            # Driver Positions
            positions = laps.pick_fastest()['Position']
            self.ax4.pie(positions, labels=drivers, autopct='%1.1f%%', 
                         colors=plt.cm.Spectral(np.linspace(0, 1, len(positions))))
            self.ax4.set_title('Driver Positions', color='white')
        except:
            self.ax4.text(0.5, 0.5, 'N/A', 
                          horizontalalignment='center', 
                          verticalalignment='center',
                          color='white')
            self.ax4.set_title('Driver Positions', color='white')
        
        plt.tight_layout()
    
    def show(self):
        plt.show()

# Example usage
dashboard = F1Dashboard(2024, 'Japan', dark_mode=True)
dashboard.plot_driver_positions()