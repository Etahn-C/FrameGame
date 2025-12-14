import tkinter as tk
# from tkinter import filedialog as fd
# from PIL import ImageTk, Image
import json
import os
# import random
# from fuzzywuzzy import process
import re
# import copy


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
            "frame-data-file-name": "frame-data.json",
            "ep-data-file-name": "ep-data.json",
            "game-data-file-name": "game-data.json",
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
            "frame-data-file": "",
            "ep-data-file": "",
            "synopsis-map": {},
            "title-map": {},
            "game-data-file": "",
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

        self.update_widgets()

    def draw_widgets(self):
        """Draws all the widgets used for the main screen"""

        # Title bar
        self.title_bar = tk.Label(
            self, text="Frame Game", bg=self.shared_data["bg-color"])
        self.title_bar.place(relheight=self.shared_data["y-mod"]*1,
                             relwidth=self.shared_data["x-mod"]*28,
                             relx=self.shared_data["x-mod"]*3,
                             rely=self.shared_data["y-mod"]*0)

        # Image Info
        self.image_info_label = tk.Label(
            self, bg=self.shared_data["bg-color"])
        self.image_info_label.place(relheight=self.shared_data["y-mod"],
                                    relwidth=24*self.shared_data["x-mod"],
                                    relx=1*self.shared_data["x-mod"],
                                    rely=19*self.shared_data["y-mod"])

        # Score Info
        self.score_label = tk.Label(self, bg=self.shared_data["bg-color"])
        self.score_label.place(relheight=self.shared_data["y-mod"],
                               relwidth=7*self.shared_data["x-mod"],
                               relx=26*self.shared_data["x-mod"],
                               rely=19*self.shared_data["y-mod"])

        # Search Bar
        self.search_bar = tk.Entry(self, bg=self.shared_data["bt-color"])
        self.search_bar.place(relheight=self.shared_data["y-mod"],
                              relwidth=24*self.shared_data["x-mod"],
                              relx=self.shared_data["x-mod"],
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
                                relx=self.shared_data["x-mod"],
                                rely=self.shared_data["y-mod"])

    def next_skip(self):
        """Will start game, prepare for new frame, or skip frame"""
        pass

    def new_frame(self):
        """Updates the current image with a new one"""
        pass

    def settings_page(self):
        """Switches the page to the settings page"""
        self.controller.shared_data = self.shared_data
        self.controller.show_page(settings_screen)
        pass

    def restart(self):
        """Resets score and frame data"""
        pass

    def report(self):
        """Reports the current frame"""
        pass

    def leaderboard_page(self):
        """Switches the page to the leaderboard page"""
        pass

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


class settings_screen(tk.Frame):
    """Class for settings_screen of FrameGame"""

    def __init__(self, parent, controller):
        """Initializes the screen"""

        super().__init__(parent, bg=controller.shared_data["bg-color"])
        self.shared_data = controller.shared_data
        self.controller = controller
        self.draw_widgets()
        self.update_settings()

    def on_show(self):
        """Runs when the page is shown"""
        pass

    def draw_widgets(self):
        """Draws all the widgets used for the main screen"""
        pass

    def update_settings(self):
        """Updates the settings"""

        if self.shared_data["game-dir"] == "":
            if os.path.exists(self.shared_data["defaults-file"]):
                try:
                    with open(self.shared_data["defaults-file"], 'r') as file:
                        data = json.load(file)
                        self.shared_data["game-dir"] = data["path"]
                except Exception:
                    pass

        if self.shared_data["game-dir"] != "":

            # Main data file
            self.shared_data["frame-data-file"] = os.path.join(
                self.shared_data["game-dir"],
                self.shared_data["frame-data-file-name"])
            with open(self.shared_data["frame-data-file"], 'r') as file:
                self.shared_data["all-data"] = json.load(file)

            # Synopsis data
            self.shared_data["ep-data-file"] = os.path.join(
                self.shared_data["game-dir"],
                self.shared_data["ep-data-file-name"])
            with open(self.shared_data["ep-data-file"], 'r') as file:
                self.shared_data["all-ep-data"] = json.load(file)

            # Settings change
            self.shared_data["synopis-search"] = (
                self.shared_data["all-data"]["Settings"]["Synopsis"])

            self.shared_data["report-threshold"] = (
                self.shared_data["all-data"]["Settings"]["Report"])

            self.shared_data["allowed-seasons"] = (
                self.shared_data["all-data"]["Settings"]["Seasons"])

            # Ep data slicing
            regex = r"([Ss]0?[1-9]\d*)([Ee]0?[1-9]\d*)"
            for key in list(self.shared_data["all-ep-data"].keys()):
                if int(re.search(regex, key).group(1)[1:]) not in (
                           self.shared_data["allowed-seasons"]):
                    del self.shared_data["all-ep-data"][key]

            # Title map
            self.shared_data["title-map"] = {ep_id: info["title"]
                                             for ep_id, info
                                             in self.shared_data
                                             ["all-ep-data"].items()}

            # Syn map
            self.shared_data["synopsis-map"] = {ep_id: info["synopsis"]
                                                for ep_id, info
                                                in self.shared_data
                                                ["all-ep-data"].items()}


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
