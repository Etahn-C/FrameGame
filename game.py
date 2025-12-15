import tkinter as tk
from tkinter import filedialog as fd
# from PIL import ImageTk, Image
import json
import os
# import random
# from fuzzywuzzy import process
import re
import copy


class FrameGame(tk.Tk):
    """Class for Framegame"""

    def __init__(self):
        super().__init__()

        # All the data so it can be shared between all pages.
        self.shared_data = {
            # Static display variables
            "bg-color": "#808080",
            "bt-color": "#A0A0A0",
            "y-mod": 1/29,
            "x-mod": 1/34,

            # Static file variables
            "data-file-name": "data.json",
            "ep-data-file-name": "ep-data.json",
            "defaults-file": "defaults.json",

            # Display variables
            "sc-width": 680,
            "sc-height": 580,

            # Gameplay variables
            "score": 0,
            "question-num": 0,
            "answered": False,

            # Data Variables
            "all-data": {},
            "all-ep-info": {},
            "allowed-frames": {},

            # Settings Variables
            "game-dir": "",
            "data-file": "",
            "ep-data-file": "",

            "synopsis-map": {},
            "title-map": {},

            "game-title": "",

            "allowed-seasons": [],
            "synopsis-search": True,
            "report-threshold": 1,

            "leaderboard": {}
        }

        # Sets up the screen.
        self.title("FrameGame!")
        self.geometry(
            f"{self.shared_data["sc-width"]}x{self.shared_data["sc-height"]}")
        self.configure(background=self.shared_data["bg-color"])

        # Creates container to hold all the frames on the screen.
        container = tk.Frame(self)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.pack(fill="both", expand=True)

        self.pages = {}
        for Page in (main_screen, settings_screen, leaderboard_screen):
            page = Page(container, self)
            self.pages[Page] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page(main_screen)

    def show_page(self, page_class):
        """Bring a page to the front."""
        page = self.pages[page_class]
        page.tkraise()
        # Will run on_show() if it exists for the page
        if hasattr(page, "on_show"):
            page.on_show()


class main_screen(tk.Frame):
    """Class for main_screen of FrameGame"""

    def __init__(self, parent, controller):
        """Initializes the screen"""

        super().__init__(parent, bg=controller.shared_data["bg-color"])
        self.shared_data = controller.shared_data
        self.controller = controller
        self.draw_widgets()

    def on_show(self):
        """Runs when the page is shown"""
        # Sets defaults for gameplay when returning from other screens
        self.next_button['text'] = "Start"
        self.search_bar.delete(0, tk.END)
        # ---
        self.update_widgets()

    def draw_widgets(self):
        """Draws all the widgets used for the main screen"""

        # Title bar
        self.title_bar = tk.Label(
            self, text="Frame Game", bg=self.shared_data["bg-color"])
        self.title_bar.place(relheight=1*self.shared_data["y-mod"],
                             relwidth=28*self.shared_data["x-mod"],
                             relx=3*self.shared_data["x-mod"],
                             rely=0*self.shared_data["y-mod"])

        # Image Info
        self.image_info_label = tk.Label(
            self, bg=self.shared_data["bg-color"])
        self.image_info_label.place(relheight=1*self.shared_data["y-mod"],
                                    relwidth=24*self.shared_data["x-mod"],
                                    relx=1*self.shared_data["x-mod"],
                                    rely=19*self.shared_data["y-mod"])

        # Score Info
        self.score_label = tk.Label(self, bg=self.shared_data["bg-color"])
        self.score_label.place(relheight=1*self.shared_data["y-mod"],
                               relwidth=7*self.shared_data["x-mod"],
                               relx=26*self.shared_data["x-mod"],
                               rely=19*self.shared_data["y-mod"])

        # Search Bar
        self.search_bar = tk.Entry(self, bg=self.shared_data["bt-color"])
        self.search_bar.place(relheight=1*self.shared_data["y-mod"],
                              relwidth=24*self.shared_data["x-mod"],
                              relx=1*self.shared_data["x-mod"],
                              rely=20*self.shared_data["y-mod"])
        # Search Menu Canvas
        self.search_menu_canvas = tk.Canvas(
            self, bg=self.shared_data["bg-color"])
        self.search_menu_canvas.place(relheight=7*self.shared_data["y-mod"],
                                      relwidth=23*self.shared_data["x-mod"],
                                      relx=1*self.shared_data["x-mod"],
                                      rely=21*self.shared_data["y-mod"])

        # Scrollbar
        self.scroll_bar = tk.Scrollbar(
            self, orient="vertical", command=self.search_menu_canvas.yview)
        self.scroll_bar.place(relheight=7*self.shared_data["y-mod"],
                              relwidth=1*self.shared_data["x-mod"],
                              relx=24*self.shared_data["x-mod"],
                              rely=21*self.shared_data["y-mod"])
        self.search_menu_canvas.configure(yscrollcommand=self.scroll_bar.set)

        # Frame In Search Menu Canvas
        self.scrollable_frame = tk.Frame(
            self.search_menu_canvas, bg=self.shared_data["bg-color"])
        self.scrollabe_frame_width = self.scrollable_frame.winfo_width()*.95

        # TODO No clue How the next 7 line do stuffs
        self.scrollable_frame.bind(
            "<Configure>", lambda _: self.search_menu_canvas.configure(
                scrollregion=self.search_menu_canvas.bbox("all")))
        self.inner_window_id = self.search_menu_canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")
        self.search_menu_canvas.bind(
            "<Configure>", lambda e: self.search_menu_canvas.itemconfig(
                self.inner_window_id, width=e.width))

        # Radio Buttons
        self.selected_ep = tk.StringVar()
        self.menus = []
        for _ in range(5):
            rb = tk.Radiobutton(self.scrollable_frame,
                                variable=self.selected_ep,
                                indicatoron=False,
                                bg=self.shared_data["bt-color"],
                                wraplength=int(self.scrollabe_frame_width))
            self.menus.append(rb)

        # Start Button
        self.next_button = tk.Button(self, text="Start",
                                     bg=self.shared_data["bt-color"],
                                     command=self.next_skip)
        self.next_button.place(relheight=self.shared_data["y-mod"],
                               relwidth=7*self.shared_data["x-mod"],
                               relx=26*self.shared_data["x-mod"],
                               rely=(20+7/4*0)*self.shared_data["y-mod"])

        # Report Button
        self.report_button = tk.Button(self, text="Report Frame",
                                       bg=self.shared_data["bt-color"],
                                       command=self.report)
        self.report_button.place(relheight=self.shared_data["y-mod"],
                                 relwidth=7*self.shared_data["x-mod"],
                                 relx=26*self.shared_data["x-mod"],
                                 rely=(20+7/4*1)*self.shared_data["y-mod"])

        # Restart Button
        self.restart_button = tk.Button(self, text="Restart",
                                        bg=self.shared_data["bt-color"],
                                        command=self.restart)
        self.restart_button.place(relheight=self.shared_data["y-mod"],
                                  relwidth=7*self.shared_data["x-mod"],
                                  relx=26*self.shared_data["x-mod"],
                                  rely=(20+7/4*2)*self.shared_data["y-mod"])

        # Settings Button
        self.settings_button = tk.Button(self, text="Settings",
                                         bg=self.shared_data["bt-color"],
                                         command=self.settings_page)
        self.settings_button.place(relheight=self.shared_data["y-mod"],
                                   relwidth=7*self.shared_data["x-mod"],
                                   relx=26*self.shared_data["x-mod"],
                                   rely=(20+7/4*3)*self.shared_data["y-mod"])

        # Leaderboard Button
        self.leaderboard_button = tk.Button(self, text="Leaderboard",
                                            bg=self.shared_data["bt-color"],
                                            command=self.leaderboard_page)
        self.leaderboard_button.place(relheight=self.shared_data["y-mod"],
                                      relwidth=7*self.shared_data["x-mod"],
                                      relx=26*self.shared_data["x-mod"],
                                      rely=(20+7)*self.shared_data["y-mod"])

        # Image Box
        self.image_canvas = tk.Canvas(self, bg=self.shared_data["bg-color"])
        self.image_canvas.place(relheight=18*self.shared_data["y-mod"],
                                relwidth=32*self.shared_data["x-mod"],
                                relx=1*self.shared_data["x-mod"],
                                rely=1*self.shared_data["y-mod"])

    def next_skip(self):
        """Will start game, prepare for new frame, or skip frame"""
        if self.next_button["text"] == "Start":
            self.next_button["text"] = "Skip"
            # TODO Loads frame and stuff
        elif self.next_button["text"] == "Next":
            self.next_button["text"] = "Skip"
        elif self.next_button["text"] == "Skip":
            self.next_button["text"] = "Next"
        else:
            print("idk how you got here...")

    def new_frame(self):
        """Updates the current image with a new one"""
        pass

    def settings_page(self):
        """Switches the page to the settings page"""
        self.controller.show_page(settings_screen)

    def restart(self):
        """Resets score and frame data"""
        pass

    def report(self):
        """Reports the current frame"""
        pass

    def leaderboard_page(self):
        """Switches the page to the leaderboard page"""
        # Just using for testing at the moment
        for x in self.shared_data.keys():
            if not isinstance(self.shared_data[x], dict):
                print(f"{x}: {self.shared_data[x]}")
            else:
                print("was a dict", x)

    def on_search(self):
        """Displays information based on text input"""
        pass

    def on_submit(self):
        """Submits current guess and proceeds"""
        pass

    def resize_widgets(self):
        """Resizes the image as well as the radio buttons"""
        pass

    def update_widgets(self):
        """
        Enables or Disables Widgets
        """
        if self.shared_data["game-dir"] == "":
            self.next_button.config(state=tk.DISABLED)
            self.report_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.DISABLED)
            self.leaderboard_button.config(state=tk.DISABLED)
            self.search_bar.config(state=tk.DISABLED)
        else:
            self.next_button.config(state=tk.NORMAL)
            self.report_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)
            self.leaderboard_button.config(state=tk.NORMAL)
            self.search_bar.config(state=tk.NORMAL)

        if self.shared_data["game-title"] != "":
            self.title_bar["text"] = (
                f"FrameGame: {self.shared_data["game-title"]}")
        else:
            self.title_bar["text"] = "FrameGame"


class settings_screen(tk.Frame):
    """Class for settings_screen of FrameGame"""

    def __init__(self, parent, controller):
        """Initializes the screen"""

        super().__init__(parent, bg=controller.shared_data["bg-color"])
        self.shared_data = controller.shared_data
        self.controller = controller
        self.get_prev_session()
        self.draw_widgets()

    def on_show(self):
        """Runs when the page is shown"""
        self.update_widgets()

    def draw_widgets(self):
        """Draws all the widgets used for the main screen"""

        # Title bar
        title_bar = tk.Label(self, text="Frame Game: Settings",
                             bg=self.shared_data["bg-color"])
        title_bar.place(relheight=1*self.shared_data["y-mod"],
                        relwidth=28*self.shared_data["x-mod"],
                        relx=3*self.shared_data["x-mod"],
                        rely=0*self.shared_data["y-mod"])

        # Settings Labels
        file_label = tk.Label(self, text="Change File",
                              bg=self.shared_data["bg-color"],
                              relief="sunken")
        file_label.place(relheight=1*self.shared_data["y-mod"],
                         relwidth=8*self.shared_data["x-mod"],
                         relx=1*self.shared_data["x-mod"],
                         rely=2*self.shared_data["y-mod"])

        season_label = tk.Label(self, text="Season Select",
                                bg=self.shared_data["bg-color"],
                                relief="sunken")
        season_label.place(relheight=1*self.shared_data["y-mod"],
                           relwidth=8*self.shared_data["x-mod"],
                           relx=1*self.shared_data["x-mod"],
                           rely=5*self.shared_data["y-mod"])

        synopsis_label = tk.Label(self, text="Synopsis Search",
                                  bg=self.shared_data["bg-color"],
                                  relief="sunken")
        synopsis_label.place(relheight=1*self.shared_data["y-mod"],
                             relwidth=8*self.shared_data["x-mod"],
                             relx=1*self.shared_data["x-mod"],
                             rely=8*self.shared_data["y-mod"])

        report_label = tk.Label(self, text="Report Threshold",
                                bg=self.shared_data["bg-color"],
                                relief="sunken")
        report_label.place(relheight=1*self.shared_data["y-mod"],
                           relwidth=8*self.shared_data["x-mod"],
                           relx=1*self.shared_data["x-mod"],
                           rely=11*self.shared_data["y-mod"])

        # File Button
        self.file_button = tk.Button(self, anchor='w',
                                     text="",
                                     bg=self.shared_data["bt-color"],
                                     command=self.change_file)
        self.file_button.place(relheight=1*self.shared_data["y-mod"],
                               relwidth=23*self.shared_data["x-mod"],
                               relx=10*self.shared_data["x-mod"],
                               rely=2*self.shared_data["y-mod"])

        self.file_button_label = tk.Label(self,
                                          text="Click ^ To Choose Directory",
                                          bg=self.shared_data["bg-color"],
                                          anchor='w')
        self.file_button_label.place(relheight=1*self.shared_data["y-mod"],
                                     relwidth=23*self.shared_data["x-mod"],
                                     relx=10*self.shared_data["x-mod"],
                                     rely=3*self.shared_data["y-mod"])

        # Season Entry
        self.season_entry = tk.Entry(self, relief='raised',
                                     bg=self.shared_data["bt-color"])
        self.season_entry.place(relheight=1*self.shared_data["y-mod"],
                                relwidth=23*self.shared_data["x-mod"],
                                relx=10*self.shared_data["x-mod"],
                                rely=5*self.shared_data["y-mod"])

        self.season_entry_label = tk.Label(self, anchor='w',
                                           bg=self.shared_data["bg-color"],
                                           text="Must be in '1 2 5' format")
        self.season_entry_label.place(relheight=1*self.shared_data["y-mod"],
                                      relwidth=23*self.shared_data["x-mod"],
                                      relx=10*self.shared_data["x-mod"],
                                      rely=6*self.shared_data["y-mod"])

        # Synopsis Radios
        self.syn = tk.BooleanVar(self, value=True)
        self.synopsis_radio_yes = tk.Radiobutton(
            self, text="Yes", bg=self.shared_data["bt-color"],
            variable=self.syn, value=True, indicatoron=False)
        self.synopsis_radio_yes.place(relheight=1*self.shared_data["y-mod"],
                                      relwidth=3*self.shared_data["x-mod"],
                                      relx=10*self.shared_data["x-mod"],
                                      rely=8*self.shared_data["y-mod"])

        self.synopsis_radio_no = tk.Radiobutton(
            self, text="No", bg=self.shared_data["bt-color"],
            variable=self.syn, value=False, indicatoron=False)
        self.synopsis_radio_no.place(relheight=1*self.shared_data["y-mod"],
                                     relwidth=3*self.shared_data["x-mod"],
                                     relx=13*self.shared_data["x-mod"],
                                     rely=8*self.shared_data["y-mod"])

        # Report Entry
        self.report_entry = tk.Entry(self, relief='raised',
                                     bg=self.shared_data["bt-color"])
        self.report_entry.place(relheight=1*self.shared_data["y-mod"],
                                relwidth=4*self.shared_data["x-mod"],
                                relx=10*self.shared_data["x-mod"],
                                rely=11*self.shared_data["y-mod"])

        # Save Button
        self.save_button = tk.Button(self, text="Save Settings",
                                     bg=self.shared_data["bt-color"],
                                     command=self.save_settings)
        self.save_button.place(relheight=1*self.shared_data["y-mod"],
                               relwidth=14*self.shared_data["x-mod"],
                               relx=10*self.shared_data["x-mod"],
                               rely=14*self.shared_data["y-mod"])

        # Return Button
        self.return_button = tk.Button(self, text="Return to Main Menu",
                                       bg=self.shared_data["bt-color"],
                                       command=self.to_main_screen)
        self.return_button.place(relheight=1*self.shared_data["y-mod"],
                                 relwidth=14*self.shared_data["x-mod"],
                                 relx=10*self.shared_data["x-mod"],
                                 rely=17*self.shared_data["y-mod"])

        # Default Button
        self.default_button = tk.Button(self, text="Default Settings",
                                        fg="#AA0000",
                                        bg=self.shared_data["bt-color"],
                                        command=self.default_settings)
        self.default_button.place(relheight=1*self.shared_data["y-mod"],
                                  relwidth=10*self.shared_data["x-mod"],
                                  relx=12*self.shared_data["x-mod"],
                                  rely=27*self.shared_data["y-mod"])

    def get_prev_session(self):
        """Loads the most recent game in"""

        # Checks if file exists and reads it.
        if self.shared_data["game-dir"] == "":
            if os.path.exists(self.shared_data["defaults-file"]):
                with open(self.shared_data["defaults-file"], 'r') as file:
                    try:
                        data = json.load(file)
                        self.shared_data["game-dir"] = data["path"]
                    except Exception:
                        pass

        # Updates things
        self.update_settings()
        self.reset_data()

    def reset_data(self):
        """Resets the Settings Variables to the Data File Settings"""

        # Will reset settings with value in all-data
        if self.shared_data["game-dir"] != "":
            self.shared_data["synopsis-search"] = (
                self.shared_data["all-data"]["Settings"]["Synopsis"])

            self.shared_data["report-threshold"] = (
                self.shared_data["all-data"]["Settings"]["Report"])

            self.shared_data["allowed-seasons"] = (
                self.shared_data["all-data"]["Settings"]["Seasons"])

    def update_settings(self):
        """Updates the settings"""

        if self.shared_data["game-dir"] != "":
            # Main data file
            self.shared_data["data-file"] = os.path.join(
                self.shared_data["game-dir"],
                self.shared_data["data-file-name"])
            with open(self.shared_data["data-file"], 'r') as file:
                self.shared_data["all-data"] = json.load(file)

            # Title
            self.shared_data["game-title"] = (
                self.shared_data["all-data"]["Settings"]["Title"])

            # Synopsis data
            self.shared_data["ep-data-file"] = os.path.join(
                self.shared_data["game-dir"],
                self.shared_data["ep-data-file-name"])
            with open(self.shared_data["ep-data-file"], 'r') as file:
                self.shared_data["all-ep-info"] = json.load(file)

            # Ep data slicing
            regex = r"([Ss]0?[1-9]\d*)([Ee]0?[1-9]\d*)"
            for key in list(self.shared_data["all-ep-info"].keys()):
                if int(re.search(regex, key).group(1)[1:]) not in (
                        self.shared_data["allowed-seasons"]):
                    del self.shared_data["all-ep-info"][key]

            # Title map
            self.shared_data["title-map"] = {ep_id: info["title"]
                                             for ep_id, info
                                             in self.shared_data
                                             ["all-ep-info"].items()}

            # Syn map
            self.shared_data["synopsis-map"] = {ep_id: info["synopsis"]
                                                for ep_id, info
                                                in self.shared_data
                                                ["all-ep-info"].items()}

            # Frame data copy
            self.shared_data["allowed-frames"] = (
                copy.deepcopy(self.shared_data["all-data"]["Frames"]))

            # Temp allowed-frames for smaller var len
            allowed_frames = self.shared_data["allowed-frames"]

            # Removes seasons from allowed frames
            for s in list(allowed_frames.keys()):
                if int(s[1:]) not in self.shared_data["allowed-seasons"]:
                    del allowed_frames[s]

            # Removes frames from allowed frames based on reports
            for s in list(allowed_frames.keys()):
                for e in list(
                        allowed_frames[s].keys()):
                    for f in list(allowed_frames[s][e].keys()):
                        if (allowed_frames[s][e][f]['reports'] >=
                                self.shared_data["report-threshold"]):
                            del allowed_frames[s][e][f]
                    if (len(allowed_frames[s][e].keys()) == 0):
                        del allowed_frames[s][e]
                if len(allowed_frames[s].keys()) == 0:
                    del allowed_frames[s]

    def update_widgets(self):
        """Updates widget configs"""

        # Enables or disabled widgets
        if self.shared_data["game-dir"] == "":
            self.season_entry.config(state=tk.DISABLED)
            self.synopsis_radio_yes.config(state=tk.DISABLED)
            self.synopsis_radio_no.config(state=tk.DISABLED)
            self.report_entry.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            self.default_button.config(state=tk.DISABLED)
        else:
            self.season_entry.config(state=tk.NORMAL)
            self.synopsis_radio_yes.config(state=tk.NORMAL)
            self.synopsis_radio_no.config(state=tk.NORMAL)
            self.report_entry.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
            self.default_button.config(state=tk.NORMAL)

        # Updates the widgets to reflect settings
        self.file_button['text'] = self.shared_data["game-dir"]
        self.season_entry.delete(0, tk.END)
        self.season_entry.insert(0, self.shared_data["allowed-seasons"])
        self.report_entry.delete(0, tk.END)
        self.report_entry.insert(0, self.shared_data["report-threshold"])
        self.syn.set(self.shared_data["synopsis-search"])

    def default_settings(self):
        """Generates default settings from data file"""

        # Game title
        self.shared_data["game-title"] = (
            self.shared_data["all-data"]["Settings"]["Title"])

        # Allowed seasons
        self.shared_data["allowed-seasons"].clear()
        for s in self.shared_data["all-data"]["Frames"].keys():
            self.shared_data["allowed-seasons"].append(int(s[1:]))

        # Synopsis and Report settings
        self.shared_data["synopsis-search"] = True
        self.shared_data["report-threshold"] = 1

        self.update_widgets()

    def to_main_screen(self):
        """Switches screen to main screen"""
        self.reset_data()
        self.controller.show_page(main_screen)

    def save_settings(self):
        """Saves new settings to file"""

        # Allowed season get
        results = []
        for s in self.season_entry.get().split(" "):
            try:
                results.append(int(s))
            except Exception:
                pass
        list(set(results)).sort()
        self.shared_data["allowed-seasons"].clear()
        for s in list(self.shared_data["all-data"]["Frames"].keys()):
            if int(s[1:]) in results:
                self.shared_data["allowed-seasons"].append(int(s[1:]))
        if len(self.shared_data["allowed-seasons"]) == 0:
            self.shared_data["allowed-seasons"].clear()
            for s in self.shared_data["all-data"]["Frames"].keys():
                self.shared_data["allowed-seasons"].append(int(s[1:]))

        # Synopsis get
        self.shared_data["synopsis-search"] = self.syn.get()

        # Report get
        try:
            if int(self.report_entry.get()) >= 0:
                self.shared_data["report-threshold"] = (
                    int(self.report_entry.get()))
        except Exception:
            self.shared_data["report-threshold"] = 1

        # Applies settings to game variables
        self.shared_data["all-data"]["Settings"].update({
            "Seasons": self.shared_data["allowed-seasons"],
            "Synopsis": self.shared_data["synopsis-search"],
            "Report": self.shared_data["report-threshold"]})

        # Writes the data
        with open(self.shared_data["data-file"], 'w') as file:
            json.dump(self.shared_data["all-data"], file,
                      ensure_ascii=False, indent=4)

        # Updates default loadout file
        with open(self.shared_data["defaults-file"],
                  'w', encoding='utf-8') as file:
            data = {"path": self.shared_data["game-dir"]}
            json.dump(data, file, ensure_ascii=False, indent=4)

        # Gets all the data files prepared and updates widgets
        self.update_settings()
        self.update_widgets()

    def change_file(self):
        """Updates the current game file"""

        # Gets new directory
        self.shared_data["game-dir"] = fd.askdirectory(
            title="Choose Game Data Directory", mustexist=True)
        self.shared_data["data-file"] = os.path.join(
            self.shared_data["game-dir"],
            self.shared_data["data-file-name"])

        # Ensures dir has data file and correct values
        if os.path.exists(self.shared_data["data-file"]):
            with open(self.shared_data["data-file"], 'r') as file:
                self.shared_data["all-data"] = json.load(file)
            self.shared_data["all-data"]["Settings"].update({
                "Seasons": [], "Synopsis": True, "Report": 1})
            self.default_settings()
        else:
            self.shared_data["game-dir"] = ""

        # Runs updates
        self.save_settings()
        self.update_widgets()


class leaderboard_screen(tk.Frame):
    """Class for settings_screen of FrameGame"""

    def __init__(self, parent, controller):
        """Initializes the screen"""

        super().__init__(parent, bg=controller.shared_data["bg-color"])
        self.shared_data = controller.shared_data
        self.controller = controller
        self.draw_widgets()

    def on_show(self):
        """Runs when the page is shown"""
        pass

    def draw_widgets(self):
        """Draws all the widgets used for the main screen"""
        pass


def main():
    """Runs the FrameGame Game Code"""

    window = FrameGame()
    window.mainloop()


if __name__ == "__main__":
    main()
