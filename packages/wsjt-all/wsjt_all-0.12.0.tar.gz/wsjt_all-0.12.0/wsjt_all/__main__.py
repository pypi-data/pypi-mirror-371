import configparser
from wsjt_all.plotter import plot_all_historic, plot_live


if(__name__ == "__main__"):
    config = configparser.ConfigParser()
    config.read("wsjt_all.ini")
    allA = config.get("inputs","allA")
    allB = config.get("inputs","allB")
    session_guard_seconds = int(config.get("settings","session_guard_seconds"))
    plot_all_historic(allA, allB, session_guard_seconds)


