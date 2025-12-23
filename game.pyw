import tkinter as tk
from tkinter import filedialog as fd
from PIL import ImageTk, Image
import json
import os
import random
from fuzzywuzzy import process
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
            "default-image": "./game-images/default-image.jpg",
            "start-image": "./game-images/start-image.jpg",

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
            "all-frame-paths": [],
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
        self.img = Image.open(self.shared_data["default-image"])
        self.tk_img = ImageTk.PhotoImage(self.img)
        # Game vars
        self.current_s = "S01"
        self.current_e = "E01"
        self.current_f = "F001"
        self.current_ft = 0
        # ---
        self.draw_widgets()
        self.bindings()
        self.after(0, self.resize_widgets)

    def on_show(self):
        """Runs when the page is shown"""
        # Sets defaults for gameplay when returning from other screens
        self.next_button["text"] = "Start"
        self.search_bar.delete(0, tk.END)
        for i in range(len(self.menus)):
            self.menus[i]["text"] = ""
            self.menus[i]["value"] = ""
        # ---
        self.restart()
        self.update_widgets()
        self.resize_widgets()

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
            self, bg=self.shared_data["bg-color"], bd=1)
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
        self.scrollable_frame_width = self.scrollable_frame.winfo_width()*.95

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
                                wraplength=int(self.scrollable_frame_width))
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
        # self.leaderboard_button.place(relheight=self.shared_data["y-mod"],
        #                               relwidth=7*self.shared_data["x-mod"],
        #                               relx=26*self.shared_data["x-mod"],
        #                               rely=(20+7)*self.shared_data["y-mod"])

        # Image Box
        self.image_canvas = tk.Canvas(self, bg=self.shared_data["bg-color"])
        self.image_canvas.place(relheight=18*self.shared_data["y-mod"],
                                relwidth=32*self.shared_data["x-mod"],
                                relx=1*self.shared_data["x-mod"],
                                rely=1*self.shared_data["y-mod"])

    def bindings(self):
        """Sets tkinter bindings"""

        self.image_canvas.bind("<Configure>", self.resize_widgets)
        self.search_bar.bind("<KeyRelease>", self.on_search)
        self.search_bar.bind("<Return>", self.on_submit)
        for menu in self.menus:
            menu.bind("<Return>", self.on_submit)

    def next_skip(self):
        """Will start game, prepare for new frame, or skip frame"""

        # Start / Next Button
        if (self.next_button["text"] == "Start" or
                self.next_button["text"] == "Next"):
            self.next_button["text"] = "Skip"

            # Score label
            nq = self.shared_data["question-num"]
            score = self.shared_data["score"]
            if nq == 0:
                self.score_label["text"] = (f"Score: {score} / {nq} "
                                            f"({100.00:.2f}%)")
            else:
                self.score_label["text"] = (f"Score: {score} / "
                                            f"{nq} ({score/nq*100:.2f}%)")

            # Info Label and border reset
            self.image_info_label["text"] = "What episode is this frame from?"
            self.image_canvas.config(
                highlightbackground="white", highlightcolor="white")

            # Updates Question
            self.shared_data["question-num"] += 1
            self.new_frame()

        # Skip Button
        elif self.next_button["text"] == "Skip":
            self.next_button["text"] = "Next"
            ft = self.current_ft
            e = self.current_e
            s = self.current_s
            time = f"{ft//3600:02}:{(ft % 3600)//60:02}:{ft % 60:02}"
            title = self.shared_data["all-ep-info"][f"{s}{e}"]["title"]
            self.image_info_label["text"] = (f"{s}{e}: {title} - {time}")
            if not self.shared_data["answered"]:
                self.image_canvas.config(
                    highlightbackground="red", highlightcolor="red")
            self.shared_data["answered"] = False
        self.update_widgets()

    def new_frame(self):
        """Updates the current image with a new one"""

        # Season
        si = random.randrange(
            0, len(self.shared_data["allowed-frames"].keys()))
        s = list(self.shared_data["allowed-frames"].keys())[si]

        # Episode
        ei = random.randrange(
            0, len(self.shared_data["allowed-frames"][s].keys()))
        e = list(self.shared_data["allowed-frames"][s].keys())[ei]

        # Frame
        fi = random.randrange(
            0, len(self.shared_data["allowed-frames"][s][e].keys()))
        f = list(self.shared_data["allowed-frames"][s][e].keys())[fi]

        # Time
        t = self.shared_data["allowed-frames"][s][e][f]["time"]

        # Removes frame from pool
        del self.shared_data["allowed-frames"][s][e][f]

        # Removes ep or season from pool if empty
        if len(self.shared_data["allowed-frames"][s][e].keys()) == 0:
            del self.shared_data["allowed-frames"][s][e]
        if len(self.shared_data["allowed-frames"][s].keys()) == 0:
            del self.shared_data["allowed-frames"][s]

        # Updates class variables
        self.current_s = s
        self.current_e = e
        self.current_f = f
        self.current_ft = t

        # Updats img
        for frame in self.shared_data["all-frame-paths"]:
            if f"{s}{e} - {f}" in frame:
                self.img = Image.open(frame)
                self.resize_widgets()
        self.update_widgets()

    def settings_page(self):
        """Switches the page to the settings page"""
        self.controller.show_page(settings_screen)

    def restart(self):
        """Resets score and frame data"""
        self.next_button["text"] = "Start"
        self.shared_data["question-num"] = 0
        self.score_label["text"] = ""
        self.image_info_label["text"] = ""
        self.image_canvas.config(
                highlightbackground="#ffffff", highlightcolor="#ffffff")
        self.img = Image.open(self.shared_data["start-image"])
        self.resize_widgets()

    def report(self):
        """Reports the current frame"""
        if self.report_button["text"] == "Report Frame":
            self.report_button["text"] = "Click Again to Confirm"
            self.report_button["fg"] = "#AA0000"
            self.after(2000, self.report_reset)
        elif self.report_button["text"] == "Click Again to Confirm":
            # Removes question
            self.shared_data["question-num"] -= 1
            self.shared_data["answered"] = True
            # Updates data
            rep_t = self.shared_data["report-threshold"]
            if rep_t == -1:
                (self.shared_data["all-data"]["frames"][self.current_s]
                    [self.current_e][self.current_f]["reports"]) = 0
            else:
                (self.shared_data["all-data"]["frames"][self.current_s]
                    [self.current_e][self.current_f]["reports"]) += 1
            # Writes to file
            with open(self.shared_data["data-file"], "w") as file:
                json.dump(self.shared_data["all-data"], file,
                          ensure_ascii=False, indent=4)
            # Continues
            self.next_skip()
            self.report_reset()

    def report_reset(self):
        """Just used for a reset of report info"""
        self.report_button["text"] = "Report Frame"
        self.report_button["fg"] = "black"

    def leaderboard_page(self):
        """Switches the page to the leaderboard page"""
        # Just using for testing at the moment
        for x in self.shared_data.keys():
            if not isinstance(self.shared_data[x], dict):
                print(f"{x}: {self.shared_data[x]}")
            else:
                print("was a dict", x)

    def on_search(self, event=None):
        """Displays information based on text input"""

        query = self.search_bar.get()
        all_results = []
        if len(query) > 3:

            # Single ep search: s01e20
            regex_search = (
                re.search(r"([Ss]0?[1-9]\d*)([Ee]0?[1-9]\d*)", query))
            if regex_search:
                s_no = regex_search.group(1)
                e_no = regex_search.group(2)
                ep = f"S{int(s_no[1:]):02}E{int(e_no[1:]):02}"
                if ep in list(self.shared_data["all-ep-info"].keys()):
                    all_results.append([100, ep])

            # Fuzzy search
            for r in process.extract(query,
                                     self.shared_data["title-map"],
                                     limit=10):
                all_results.append([r[1], r[2]])
            if self.shared_data["synopsis-search"]:
                for r in process.extract(query,
                                         self.shared_data["synopsis-map"],
                                         limit=10):
                    all_results.append([r[1], r[2]])

            # Sorts List and remove dupes
            all_results.sort(reverse=True)
            results = []
            for r in all_results:
                results.append(r[1])
            results = list(dict.fromkeys(results))

            # Updating radio info
            self.selected_ep.set(results[0])
            for i in range(len(self.menus)):
                title = self.shared_data["all-ep-info"][results[i]]["title"]
                synopsis = (self.shared_data["all-ep-info"]
                            [results[i]]["synopsis"])
                if self.shared_data["synopsis-search"]:
                    display_text = (f"{results[i]}: {title}\n{synopsis}")
                else:
                    display_text = (f"{results[i]}: {title}")
                self.menus[i]["text"] = display_text
                self.menus[i]["value"] = results[i]
        else:
            self.selected_ep.set("")
            for i in range(len(self.menus)):
                self.menus[i]["text"] = ""
                self.menus[i]["value"] = ""
        self.update_widgets()

    def on_submit(self, event=None):
        """Submits current guess and proceeds"""
        self.search_bar.focus_set()
        # Checks if answer is correct
        if self.selected_ep.get() == f"{self.current_s}{self.current_e}":
            self.shared_data["score"] += 1
            nq = self.shared_data["question-num"]
            score = self.shared_data["score"]
            self.score_label["text"] = (f"Score: {score} / "
                                        f"{nq} ({score/nq*100:.2f}%)")
            self.image_canvas.config(
                highlightbackground="#00ff00", highlightcolor="#00ff00")
        else:
            self.image_canvas.config(
                highlightbackground="red", highlightcolor="red")
        self.shared_data["answered"] = True
        self.selected_ep.set("")
        for i in range(len(self.menus)):
            self.menus[i]["text"] = ""
            self.menus[i]["value"] = ""
        self.search_bar.delete(0, tk.END)
        self.next_skip()
        self.update_widgets()

    def resize_widgets(self, event=None):
        """Resizes the image as well as the radio buttons"""

        self.update_idletasks()
        # Full widths and heights
        self.shared_data["sc-width"] = self.controller.winfo_width()
        self.shared_data["sc-height"] = self.controller.winfo_height()

        # Image edits
        img_width = self.shared_data["sc-width"]*self.shared_data["x-mod"]*32
        img_height = self.shared_data["sc-height"]*self.shared_data["y-mod"]*18
        resized = self.img.copy()
        resized.thumbnail((img_width, img_height))
        self.tk_img = ImageTk.PhotoImage(resized)
        self.image_canvas.delete("all")
        self.image_canvas.create_image(img_width/2, img_height/2,
                                       anchor="center", image=self.tk_img)

        # Radio wraplength scale
        radio_width = (
            self.shared_data["sc-width"]*self.shared_data["x-mod"]*22*0.95)
        for menu in self.menus:
            menu.config(wraplength=radio_width)

        # Radio sizes?
        new_width = max(0, self.search_menu_canvas.winfo_width()-6)
        self.search_menu_canvas.itemconfig(
            self.inner_window_id,
            width=new_width)

    def update_widgets(self):
        """Updates widget configs"""

        if self.shared_data["game-dir"] == "":
            self.next_button.config(state=tk.DISABLED)
            self.report_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.DISABLED)
            self.leaderboard_button.config(state=tk.DISABLED)
            self.search_bar.config(state=tk.DISABLED)
        else:
            self.next_button.config(state=tk.NORMAL)
            if ("What episode is this frame from?"
                    in self.image_info_label['text']):
                self.report_button.config(state=tk.NORMAL)
            else:
                self.report_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.NORMAL)
            self.leaderboard_button.config(state=tk.NORMAL)
            self.search_bar.config(state=tk.NORMAL)

        if self.shared_data["game-title"] != "":
            self.title_bar["text"] = (
                f"FrameGame: {self.shared_data["game-title"]}")
        else:
            self.title_bar["text"] = "FrameGame"

        for menu in self.menus:
            if menu["text"] == "":
                menu.forget()
            else:
                menu.pack(fill="x")

        if self.shared_data["game-dir"] == "":
            self.img = Image.open(self.shared_data["default-image"])
        elif self.shared_data["question-num"] == 0:
            self.img = Image.open(self.shared_data["start-image"])

        self.resize_widgets()


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
        self.file_button = tk.Button(self, anchor="w",
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
                                          anchor="w")
        self.file_button_label.place(relheight=1*self.shared_data["y-mod"],
                                     relwidth=23*self.shared_data["x-mod"],
                                     relx=10*self.shared_data["x-mod"],
                                     rely=3*self.shared_data["y-mod"])

        # Season Entry
        self.season_entry = tk.Entry(self, relief="raised",
                                     bg=self.shared_data["bt-color"])
        self.season_entry.place(relheight=1*self.shared_data["y-mod"],
                                relwidth=23*self.shared_data["x-mod"],
                                relx=10*self.shared_data["x-mod"],
                                rely=5*self.shared_data["y-mod"])

        self.season_entry_label = tk.Label(self, anchor="w",
                                           bg=self.shared_data["bg-color"],
                                           text="Must be in \"1 2 5\" format")
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
        self.report_entry = tk.Entry(self, relief="raised",
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
                with open(self.shared_data["defaults-file"], "r") as file:
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
                self.shared_data["all-data"]["settings"]["synopsis"])

            self.shared_data["report-threshold"] = (
                self.shared_data["all-data"]["settings"]["report"])

            self.shared_data["allowed-seasons"] = (
                self.shared_data["all-data"]["settings"]["seasons"])

    def update_settings(self):
        """Updates the settings"""

        if self.shared_data["game-dir"] != "":
            # Main data file
            self.shared_data["data-file"] = os.path.join(
                self.shared_data["game-dir"],
                self.shared_data["data-file-name"])
            with open(self.shared_data["data-file"], "r") as file:
                self.shared_data["all-data"] = json.load(file)

            self.shared_data["synopsis-search"] = (
                self.shared_data["all-data"]["settings"]["synopsis"])

            self.shared_data["report-threshold"] = (
                self.shared_data["all-data"]["settings"]["report"])

            self.shared_data["allowed-seasons"] = (
                self.shared_data["all-data"]["settings"]["seasons"])

            # Title
            self.shared_data["game-title"] = (
                self.shared_data["all-data"]["settings"]["title"])

            # Synopsis data
            self.shared_data["ep-data-file"] = os.path.join(
                self.shared_data["game-dir"],
                self.shared_data["ep-data-file-name"])
            with open(self.shared_data["ep-data-file"], "r") as file:
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

            # All frame-paths
            self.shared_data["all-frame-paths"] = []
            for root, _, files in os.walk(self.shared_data["game-dir"]):
                for name in files:
                    (self.shared_data["all-frame-paths"]
                     .append(os.path.join(root, name)))

            # Frame data copy
            self.shared_data["allowed-frames"] = (
                copy.deepcopy(self.shared_data["all-data"]["frames"]))

            # Temp allowed-frames for smaller var len
            allowed_frames = self.shared_data["allowed-frames"]

            # Removes seasons from allowed frames
            for s in list(allowed_frames.keys()):
                if int(s[1:]) not in self.shared_data["allowed-seasons"]:
                    del allowed_frames[s]

            # Removes frames from allowed frames based on reports
            rep_t = self.shared_data["report-threshold"]
            for s in list(allowed_frames.keys()):
                for e in list(
                        allowed_frames[s].keys()):
                    for f in list(allowed_frames[s][e].keys()):
                        if rep_t == -1:
                            if (allowed_frames[s][e][f]["reports"] == 0):
                                del allowed_frames[s][e][f]
                        else:
                            if (allowed_frames[s][e][f]["reports"] >= rep_t):
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
        self.file_button["text"] = self.shared_data["game-dir"]
        self.season_entry.delete(0, tk.END)
        self.season_entry.insert(0, self.shared_data["allowed-seasons"])
        self.report_entry.delete(0, tk.END)
        self.report_entry.insert(0, self.shared_data["report-threshold"])
        self.syn.set(self.shared_data["synopsis-search"])

    def default_settings(self):
        """Generates default settings from data file"""

        # Game title
        self.shared_data["game-title"] = (
            self.shared_data["all-data"]["settings"]["title"])

        # Allowed seasons
        self.shared_data["allowed-seasons"].clear()
        for s in self.shared_data["all-data"]["frames"].keys():
            self.shared_data["allowed-seasons"].append(int(s[1:]))

        # Synopsis and Report settings
        self.shared_data["synopsis-search"] = True
        self.shared_data["report-threshold"] = 1

        self.update_widgets()

    def to_main_screen(self):
        """Switches screen to main screen"""
        self.reset_data()
        self.update_settings()
        self.controller.show_page(main_screen)

    def save_settings(self):
        """Saves new settings to file"""

        if self.shared_data["game-dir"] == "":
            return
        # Allowed season get
        results = []
        for s in self.season_entry.get().split(" "):
            try:
                results.append(int(s))
            except Exception:
                pass
        list(set(results)).sort()
        self.shared_data["allowed-seasons"].clear()
        for s in list(self.shared_data["all-data"]["frames"].keys()):
            if int(s[1:]) in results:
                self.shared_data["allowed-seasons"].append(int(s[1:]))
        if len(self.shared_data["allowed-seasons"]) == 0:
            self.shared_data["allowed-seasons"].clear()
            for s in self.shared_data["all-data"]["frames"].keys():
                self.shared_data["allowed-seasons"].append(int(s[1:]))

        # Synopsis get
        self.shared_data["synopsis-search"] = self.syn.get()

        # Report get
        try:
            if int(self.report_entry.get()) >= -1:
                self.shared_data["report-threshold"] = (
                    int(self.report_entry.get()))
        except Exception:
            self.shared_data["report-threshold"] = 1

        # Applies settings to game variables
        self.shared_data["all-data"]["settings"].update({
            "seasons": self.shared_data["allowed-seasons"],
            "synopsis": self.shared_data["synopsis-search"],
            "report": self.shared_data["report-threshold"]})

        # Writes the data
        with open(self.shared_data["data-file"], "w") as file:
            json.dump(self.shared_data["all-data"], file,
                      ensure_ascii=False, indent=4)

        # Updates default loadout file
        with open(self.shared_data["defaults-file"],
                  "w", encoding="utf-8") as file:
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
        if (os.path.exists(self.shared_data["data-file"]) and
                self.shared_data["game-dir"] != ""):
            with open(self.shared_data["data-file"], "r") as file:
                self.shared_data["all-data"] = json.load(file)
            self.shared_data["all-data"]["settings"].update({
                "seasons": [], "synopsis": True, "report": 1})
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
