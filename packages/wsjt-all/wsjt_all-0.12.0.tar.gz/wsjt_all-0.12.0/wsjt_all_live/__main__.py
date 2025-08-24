import configparser
from wsjt_all.plotter import plot_live


config = configparser.ConfigParser()
config.read("wsjt_all.ini")
allA = config.get("inputs","allA")
allB = config.get("inputs","allB")
live_plot_window_seconds = int(config.get("settings","live_plot_window_seconds"))
plot_live(allA, allB, live_plot_window_seconds)



