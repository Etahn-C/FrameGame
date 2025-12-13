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
    def __init__(self):
        super().__init__()
        self.title("FrameGame!")
        self.geometry("680x580")
        self.config(background="#808080")
        self.width = 680
        self.bg = "#808080"
        self.button_color = "#A0A0A0"
        self.y=1/29
        self.x=1/34
        self.game_dir = ""
                
        if os.path.exists("./defaults.json"):
            try:
                with open("./defaults.json", 'r', encoding='utf-8')as file:
                    data = json.load(file)
                    self.game_dir = data["path"]
                    print(self.game_dir)
            except:
                self.game_dir =""
        
        container = tk.Frame(self)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        container.pack(fill="both", expand=True)
        self.pages = {}
        
        for Page in (main_screen, settings_screen):
            page = Page(container, self)
            self.pages[Page] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page(main_screen)


    def show_page(self, page_class):
        """Bring a page to the front."""
        page = self.pages[page_class]
        page.tkraise()
        
        if hasattr(page, "on_show"):
            page.on_show()


    def resize_image(self, event=None):
        canvas_w = self.image_canvas.winfo_width()
        self.width = canvas_w
        canvas_h = self.image_canvas.winfo_height()
        if canvas_w < 5 or canvas_h < 5:
            return
        # resize keeping aspect ratio
        resized = self.img.copy()
        resized.thumbnail((canvas_w, canvas_h))
        # convert to PhotoImage
        tk_img = ImageTk.PhotoImage(resized)
        # save reference so it doesn't get garbage-collected
        self.image_canvas.img = tk_img
        # clear old image
        self.image_canvas.delete("all")
        # center the image
        self.image_canvas.create_image(canvas_w/2, canvas_h/2, anchor="center", image=tk_img)


class main_screen(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        self.bg = controller.bg
        self.button_color = controller.button_color
        self.y = controller.y
        self.x = controller.x
        self.score = -1
        self.dir_path = ""
        self.all_frames = []
        self.all_ep_data = {}
        self.title_map = {}
        self.synopsis_map = {}
        self.frame_data = {}
        self.allowed_frames = {}
        self.answered = False
        self.score = 0
        self.num_questions = 0
        self.prev_frames = []
        
        super().__init__(parent, bg=self.bg)
        # Title bar:
        self.title_bar = tk.Label(self, text="Frame Game", bg=self.bg)
        self.title_bar.place(relheight=self.y, relwidth=28*self.x, relx=3*self.x, rely=self.y*0)
        
        # Image Info: 
        self.image_info_label = tk.Label(self, bg=self.bg, text="")
        self.image_info_label.place(relheight=self.y, relwidth=24*self.x, relx=1*self.x, rely=19*self.y)
        
        # Score Info
        self.score_label = tk.Label(self, bg=self.bg, text="")
        self.score_label.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=19*self.y)
        
        # Search Bar:
        self.search_bar = tk.Entry(self, bg=self.button_color)
        self.search_bar.place(relheight=self.y, relwidth=24*self.x, relx=self.x, rely=20*self.y)
        # Search menu container
        self.search_menu_canvas = tk.Canvas(self, bg=self.bg)
        self.search_menu_canvas.place(relheight=7*self.y, relwidth=23*self.x, relx=1*self.x, rely=21*self.y)

        self.search_menu_canvas.bind("<Enter>", lambda e: self.search_menu_canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.search_menu_canvas.bind("<Leave>", lambda e: self.search_menu_canvas.unbind_all("<MouseWheel>"))

        
        # Scrollbar
        scroll_bar = tk.Scrollbar(self, orient="vertical", command=self.search_menu_canvas.yview)
        scroll_bar.place(relheight=7*self.y, relwidth=1*self.x, relx=24*self.x, rely=21*self.y)

        self.search_menu_canvas.configure(yscrollcommand=scroll_bar.set)

        # Frame inside the canvas
        self.scrollable_frame = tk.Frame(self.search_menu_canvas, bg=self.bg)
        self.scrollabe_frame_width = self.scrollable_frame.winfo_width()

        # Expand scrollregion when contents change
        self.scrollable_frame.bind("<Configure>",lambda e: self.search_menu_canvas.configure(scrollregion=self.search_menu_canvas.bbox("all")))

        # Add the frame into the canvas and store window ID
        self.inner_window_id = self.search_menu_canvas.create_window((0, 0),window=self.scrollable_frame,anchor="nw")

        # Make inner frame always stretch full width
        self.search_menu_canvas.bind("<Configure>",lambda e: self.search_menu_canvas.itemconfig(self.inner_window_id,width=e.width))

        # Add the radiobuttons
        self.selected_ep = tk.StringVar()   
        self.default_ep = ""     
        self.menu1 = tk.Radiobutton(self.scrollable_frame, text="", value="", variable=self.selected_ep, indicatoron=False, bg=self.button_color, wraplength=int(self.scrollabe_frame_width))
        self.menu2 = tk.Radiobutton(self.scrollable_frame, text="", value="", variable=self.selected_ep, indicatoron=False, bg=self.button_color, wraplength=int(self.scrollabe_frame_width))
        self.menu3 = tk.Radiobutton(self.scrollable_frame, text="", value="", variable=self.selected_ep, indicatoron=False, bg=self.button_color, wraplength=int(self.scrollabe_frame_width))
        self.menu4 = tk.Radiobutton(self.scrollable_frame, text="", value="", variable=self.selected_ep, indicatoron=False, bg=self.button_color, wraplength=int(self.scrollabe_frame_width))
        self.menu5 = tk.Radiobutton(self.scrollable_frame, text="", value="", variable=self.selected_ep, indicatoron=False, bg=self.button_color, wraplength=int(self.scrollabe_frame_width))
        self.menus = {"menu_1": self.menu1,"menu_2": self.menu2,"menu_3": self.menu3,"menu_4": self.menu4,"menu_5": self.menu5}
        
        # Game Buttons
        self.next_button = tk.Button(self, text="Start", bg=self.button_color, command=self.new_frame)
        self.report_button = tk.Button(self, text="Report Frame", bg=self.button_color, command=self.report)
        self.restart_button = tk.Button(self, text="Restart", bg=self.button_color, command=self.restart)
        self.settings_button = tk.Button(self, text="Settings", bg=self.button_color, command=self.settings_page)
        self.Leaderboard_button = tk.Button(self, text="Leaderboard", bg=self.button_color)
        self.next_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=(20+7/4*0)*self.y)
        self.report_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=(20+7/4*1)*self.y)
        self.restart_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=(20+7/4*2)*self.y)
        self.settings_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=(20+7/4*3)*self.y)
        # TODO Leaderboard stuffs
        #self.Leaderboard_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=(20+7/4*4)*self.y)
        
        # Image Box:
        self.image_canvas = tk.Canvas(self, bg=self.bg)
        self.image_canvas.place(relheight=18*self.y, relwidth=32*self.x, relx=self.x, rely=self.y)
        self.img = Image.open(r"./game_images/default_image.jpg")
        
    def _on_mousewheel(self, event):
        self.search_menu_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


    def settings_page(self):
        self.controller.show_page(settings_screen)
        self.search_bar.delete(0,tk.END)
        self.search_bar.config(state=tk.DISABLED)
        self.restart()
    

    def update_disabled_widgets(self):
        if self.dir_path == "":
            self.next_button.config(state=tk.DISABLED)
            self.report_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.DISABLED)
            self.search_bar.config(state=tk.DISABLED)            
        else:
            self.next_button.config(state=tk.NORMAL)
            self.report_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)
            self.search_bar.config(state=tk.NORMAL)


    def on_show(self):
        if self.dir_path != self.controller.game_dir and self.controller.game_dir != "":
            self.dir_path = self.controller.game_dir
            ep_data_file_path = os.path.join(self.dir_path, 'ep-data.json')
            game_data_file_path = os.path.join(self.dir_path, 'game-data.json')
            frame_data_file_path = os.path.join(self.dir_path, 'data.json')
            self.img = Image.open(r"./game_images/start_image.jpg")
            
            # Settings load
            try:
                with open(game_data_file_path, "r", encoding='utf-8') as file:
                    data = json.load(file)
                with open(frame_data_file_path, "r", encoding='utf-8') as file:
                    frame_data = json.load(file)
                    
                self.title = frame_data["Settings"]["Title"]
                self.syn = data["Settings"]["Synopsis"]
                self.reports = data["Settings"]["Report"]
                
                self.season_select = []
                for x in data["Settings"]["Seasons"].split(','):
                    self.season_select.append(int(x))
                self.title_bar['text'] = f"FrameGame: {self.title}"
            except:
                pass
            
            # Search Maps
            with open(ep_data_file_path, "r", encoding='utf-8') as file:
                data = json.load(file)
                self.all_ep_data = data
                for key in list(self.all_ep_data.keys()):
                    if int(re.search(r"([Ss]0?[1-9]\d*)([Ee]0?[1-9]\d*)", key).group(1)[1:]) not in self.season_select:
                        del self.all_ep_data[key]
                self.title_map = { ep_id: info["title"] for ep_id, info in self.all_ep_data.items() }
                self.synopsis_map = { ep_id: info["synopsis"] for ep_id, info in self.all_ep_data.items() }
 
        elif self.controller.game_dir == "":
            self.dir_path = self.controller.game_dir
            self.img = Image.open(r"./game_images/default_image.jpg")
            self.title_bar['text'] = "FrameGame"
            self.image_info_label['text'] = ""
        self.controller.image_canvas = self.image_canvas
        self.controller.img = self.img
        self.controller.after(75, self.controller.resize_image)
        self.resize_radios()
        self.update_disabled_widgets()


    def report(self):
        if self.report_button['text'] == "Report Frame":
            self.report_button['text'] = "Click Again to Confirm"
            
        else:
            self.report_button['text'] = "Report Frame"
            self.frame_data["Frames"][self.current_season][self.current_episode][self.current_frame]["reports"] += 1
            with open(os.path.join(self.dir_path, "data.json"), 'w', encoding='utf-8') as file:
                json.dump(self.frame_data, file, ensure_ascii=False, indent=4)
            self.num_questions -= 1
            self.answered = True
            self.new_frame()

   
    def update_game_dir(self):
        self.controller.game_dir = self.dir_path


    def restart(self):
        self.answered = False
        self.score = 0
        self.num_questions = 0
        self.img = Image.open(r"./game_images/start_image.jpg")
        self.controller.img = self.img
        self.controller.resize_image()
        self.image_info_label['text'] = f""
        self.score_label['text'] = f""
        self.next_button['text'] = "Start"
        self.allowed_frames = {}
        self.frame_data = {}
        
    def get_random_frame(self):
        rand_season_index = random.randrange(0, len(self.allowed_frames["Frames"].keys()))
        rand_season = list(self.allowed_frames["Frames"].keys())[rand_season_index]
        rand_episode_index = random.randrange(0, len(self.allowed_frames["Frames"][rand_season].keys()))
        rand_episode = list(self.allowed_frames["Frames"][rand_season].keys())[rand_episode_index]
        rand_frame_index = random.randrange(0, len(self.allowed_frames["Frames"][rand_season][rand_episode].keys()))
        rand_frame = list(self.allowed_frames["Frames"][rand_season][rand_episode].keys())[rand_frame_index] 
        if self.allowed_frames["Frames"][rand_season][rand_episode][rand_frame]["reports"] >= self.reports or f"{rand_season}{rand_episode} - {rand_frame}" in self.prev_frames:
            del self.allowed_frames["Frames"][rand_season][rand_episode][rand_frame]
            if len(self.allowed_frames["Frames"][rand_season][rand_episode]) == 0:
                del self.allowed_frames["Frames"][rand_season][rand_episode]
            return self.get_random_frame()
        return rand_season, rand_episode, rand_frame


    def new_frame(self):
        self.report_button['text'] = "Report Frame"
        # Removes disallowed frames from pool
        if len(self.frame_data) == 0:
            with open(os.path.join(self.dir_path, "data.json"), 'r', encoding='utf-8') as file:
                self.frame_data = json.load(file)
                self.allowed_frames = copy.deepcopy(self.frame_data)
                for s in list(self.allowed_frames["Frames"].keys()):
                    if int(s[1:]) not in self.season_select:
                        del self.allowed_frames["Frames"][s]
                for s in list(self.allowed_frames["Frames"].keys()):
                    for e in list(self.allowed_frames["Frames"][s].keys()):
                        for f in list(self.allowed_frames["Frames"][s][e].keys()):
                            if self.allowed_frames["Frames"][s][e][f]['reports'] >= self.reports:
                                del self.allowed_frames["Frames"][s][e][f]
                        if len(self.allowed_frames["Frames"][s][e].keys()) == 0:
                            del self.allowed_frames["Frames"][s][e]
                            
                    if len(self.allowed_frames["Frames"][s].keys()) == 0:
                        del self.allowed_frames["Frames"][s]
        
        if not self.answered and self.num_questions != 0: 
            self.answered = True      
            self.image_canvas.config(highlightbackground="red", highlightcolor="red")     
            time = f"{self.current_frame_time//3600:02}:{(self.current_frame_time%3600)//60:02}:{self.current_frame_time%60:02}"
            self.next_button['text'] = "Next"
            self.score_label['text'] = f"Score: {self.score} / {self.num_questions} ({self.score/self.num_questions*100:.2f}%)"
            self.image_info_label['text'] = f"{self.current_season}{self.current_episode}: {self.all_ep_data[f"{self.current_season}{self.current_episode}"]["title"]} - {time}"
            self.search_bar.delete(0, tk.END)
            for menu in self.menus.keys():
                self.menus[menu].pack_forget()
                self.selected_ep.set("")
        else:
            self.image_canvas.config(highlightbackground="white", highlightcolor="white")
            self.next_button['text'] = "Skip"
            if self.num_questions == 0:
                self.score_label['text'] = f"Score: {self.score} / {self.num_questions} ({100.00:.2f}%)"
            else:
                self.score_label['text'] = f"Score: {self.score} / {self.num_questions} ({self.score/self.num_questions*100:.2f}%)"
            self.num_questions += 1
            self.answered = False
            
            self.current_season, self.current_episode, self.current_frame = self.get_random_frame()
            self.prev_frames.append(f"{self.current_season}{self.current_episode} - {self.current_frame}")
            if len(self.all_frames) == 0:
                for root, _, files in os.walk(self.dir_path):
                    for name in files:
                        self.all_frames.append(os.path.join(root, name))
            for frame in self.all_frames:
                if f"{self.current_season}{self.current_episode} - {self.current_frame}" in frame:
                    self.img = Image.open(frame)
                    exit
            self.controller.img = self.img
            self.controller.resize_image()
            self.current_frame_time = self.frame_data["Frames"][self.current_season][self.current_episode][self.current_frame]["time"]
            self.image_info_label['text'] = f"What episode is this frame from?"


    def on_search(self, event):
        query = self.search_bar.get()
        result = [] 
        if len(query) > 3:
            regex_search = re.search(r"([Ss]0?[1-9]\d*)([Ee]0?[1-9]\d*)", query)
            if regex_search:
                season_no = regex_search.group(1)
                episode_no = regex_search.group(2)
                episode = f"S{int(season_no[1:]):02}E{int(episode_no[1:]):02}"
                if episode in list(self.all_ep_data.keys()):
                    result.append([episode, 100])

            # Fuzzy Time??
            for r in process.extract(query, self.title_map):
                result.append([r[2], r[1]])
            if self.syn == 1:
                for r in process.extract(query, self.synopsis_map, limit=10):
                    result.append([r[2], r[1]])
            # Displaying
            result.sort(key=lambda x: x[1], reverse=True)
            results = []
            for x in result:
                results.append(x[0])
            results = list(dict.fromkeys(results))
            self.default_ep = results
            menus_list = list(self.menus.keys())
            for i in range(len(menus_list)):
                self.menus[menus_list[i]].pack(fill='x')
                if self.syn == 1:
                    menu_text = f"{results[i]} : {self.all_ep_data[results[i]]['title']}\n{self.all_ep_data[results[i]]['synopsis']}"
                else:
                    menu_text = f"{results[i]} : {self.all_ep_data[results[i]]['title']}"
                self.menus[menus_list[i]].config(text=menu_text, value=results[i])
                
        else:
            for menu in self.menus.keys():
                self.menus[menu].pack_forget()
                self.selected_ep.set("")
            

    def resize_radios(self, event=None):
        self.scrollabe_frame_width = self.scrollable_frame.winfo_width()
        for menu in self.menus.keys():
            self.menus[menu].config(wraplength=self.scrollabe_frame_width-10)


    def on_submit(self, event=None):
        if self.answered:
            self.new_frame()
        
        elif len(self.search_bar.get()) > 3:
            self.answered = True
            correct_ep = f"{self.current_season}{self.current_episode}"
            if self.default_ep[0] == correct_ep or self.selected_ep.get() == correct_ep:
                self.score += 1
                self.image_canvas.config(highlightbackground="#00FF00", highlightcolor="#00FF00")
            else:
                self.image_canvas.config(highlightbackground="red", highlightcolor="red")

            
            time = f"{self.current_frame_time//3600:02}:{(self.current_frame_time%3600)//60:02}:{self.current_frame_time%60:02}"
            self.next_button['text'] = "Next"
            self.score_label['text'] = f"Score: {self.score} / {self.num_questions} ({self.score/self.num_questions*100:.2f}%)"
            self.image_info_label['text'] = f"{self.current_season}{self.current_episode}: {self.all_ep_data[f"{self.current_season}{self.current_episode}"]["title"]} - {time}"
            self.search_bar.delete(0, tk.END)
            for menu in self.menus.keys():
                self.menus[menu].pack_forget()
                self.selected_ep.set("")


class settings_screen(tk.Frame):
    def __init__(self, parent, controller):
        self.bg = controller.bg
        self.button_color = controller.button_color
        self.y = controller.y
        self.x = controller.x
        self.controller = controller
        self.data_dir = controller.game_dir
        super().__init__(parent, bg=self.bg)

        # Title bar:
        title_bar = tk.Label(self, text="Frame Game: Settings", bg=self.bg)
        title_bar.place(relheight=self.y, relwidth=28*self.x, relx=3*self.x, rely=self.y*0)
        
        # Settings Labels:
        file_label = tk.Label(self, text="Change File", bg=self.bg, relief="sunken")
        season_label = tk.Label(self, text="Season Select", bg=self.bg, relief="sunken")
        synopsis_label = tk.Label(self, text="Synopsis Search", bg=self.bg, relief="sunken")
        report_label = tk.Label(self, text="Report Threshold", bg=self.bg, relief="sunken")
        file_label.place(relheight=self.y, relwidth=8*self.x, relx=1*self.x, rely=self.y*2)
        season_label.place(relheight=self.y, relwidth=8*self.x, relx=1*self.x, rely=self.y*5)
        synopsis_label.place(relheight=self.y, relwidth=8*self.x, relx=1*self.x, rely=self.y*8)
        report_label.place(relheight=self.y, relwidth=8*self.x, relx=1*self.x, rely=self.y*11)
        
        # Settings options:
        self.file_button = tk.Button(self, text="No Current Directory", bg=self.button_color, anchor='w', command=lambda: self.change_file())
        self.file_button_label = tk.Label(self, text="Click ^ To Choose Directory", bg=self.bg, anchor='w')
        self.file_button.place(relheight=self.y, relwidth=23*self.x, relx=10*self.x, rely=self.y*2)
        self.file_button_label.place(relheight=self.y, relwidth=23*self.x, relx=10*self.x, rely=self.y*3)
        
        self.season_entry = tk.Entry(self, bg=self.button_color, relief='raised') 
        self.season_entry_label = tk.Label(self, bg=self.bg, text="Must be in '1, 2, 5' format", anchor='w')
        self.season_entry.place(relheight=self.y, relwidth=23*self.x, relx=10*self.x, rely=self.y*5)
        self.season_entry_label.place(relheight=self.y, relwidth=23*self.x, relx=10*self.x, rely=self.y*6)
        
        self.syn = tk.IntVar(self, value=1)
        self.synopsis_radio_yes = tk.Radiobutton(self, text="Yes", bg=self.button_color, variable=self.syn, value=1, indicatoron=False)
        self.synopsis_radio_no = tk.Radiobutton(self, text="No", bg=self.button_color, variable=self.syn, value=0, indicatoron=False)
        self.synopsis_radio_yes.place(relheight=self.y, relwidth=3*self.x, relx=10*self.x, rely=self.y*8)
        self.synopsis_radio_no.place(relheight=self.y, relwidth=3*self.x, relx=13*self.x, rely=self.y*8)
        
        self.report_entry = tk.Entry(self, bg=self.button_color, relief='raised')
        self.report_entry.place(relheight=self.y, relwidth=4*self.x, relx=10*self.x, rely=self.y*11)
        
        self.save_button = tk.Button(self, text="Save Settings", bg=self.button_color, command=lambda: self.save_settings())
        self.save_button.place(relheight=self.y, relwidth=14*self.x, relx=10*self.x, rely=14*self.y)
        
        self.return_button = tk.Button(self, text="Return to Main Menu", bg=self.button_color, command=lambda: (self.update_game_dir(), controller.show_page(main_screen)))
        self.return_button.place(relheight=self.y, relwidth=14*self.x, relx=10*self.x, rely=17*self.y)
        
        self.default_button = tk.Button(self, text="Default Settings", fg="#AA0000", bg=self.button_color, command=lambda: self.default_settings(self.data_dir))
        self.default_button.place(relheight=self.y, relwidth=10*self.x, relx=12*self.x, rely=27*self.y)

        self.update_disabled_widgets()

    
    def update_game_dir(self):
        self.controller.game_dir = self.data_dir


    def on_show(self):
        self.data_dir = self.controller.game_dir
        self.file_button["text"] = self.data_dir
        self.update_disabled_widgets()
        if os.path.exists(os.path.join(self.data_dir, "game-data.json")):
            self.import_settings(os.path.join(self.data_dir, "game-data.json"))
        else:
            self.default_settings(os.path.join(self.data_dir))
        
        
    def change_file(self):
        self.data_dir = fd.askdirectory(title="Choose Game Data Directory", mustexist=True)
        if not os.path.exists(os.path.join(self.data_dir, "data.json")):
            self.data_dir = ""
            self.file_button["text"] = "No Current Directory"
            self.syn.set(1)
            self.season_entry.delete(0, tk.END)
            self.season_entry.insert(0, "")
            self.report_entry.delete(0, tk.END)
            self.report_entry.insert(0, "")
            self.update_disabled_widgets()
            return
        self.file_button["text"] = self.data_dir
        self.update_disabled_widgets()
        if os.path.exists(os.path.join(self.data_dir, "game-data.json")):
            self.import_settings(os.path.join(self.data_dir, "game-data.json"))
        else:
            self.default_settings(os.path.join(self.data_dir))
        with open("./defaults.json", 'w', encoding='utf-8') as file:
            data = {"path":self.data_dir}
            json.dump(data, file, ensure_ascii=False, indent=4)


    def update_disabled_widgets(self):
        if self.data_dir == "":
            self.default_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            self.report_entry.config(state=tk.DISABLED)
            self.season_entry.config(state=tk.DISABLED)
            self.synopsis_radio_no.config(state=tk.DISABLED)
            self.synopsis_radio_yes.config(state=tk.DISABLED)
        else:
            self.default_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
            self.report_entry.config(state=tk.NORMAL)
            self.season_entry.config(state=tk.NORMAL)
            self.synopsis_radio_no.config(state=tk.NORMAL)
            self.synopsis_radio_yes.config(state=tk.NORMAL)


    def import_settings(self, path):
        try:
            with open(path, "r", encoding='utf-8') as file:
                data = json.load(file)
                self.season_entry.delete(0, tk.END)
                self.season_entry.insert(0, data["Settings"]["Seasons"])
                self.report_entry.delete(0, tk.END)
                self.report_entry.insert(0, data["Settings"]["Report"])
                self.syn.set(data["Settings"]["Synopsis"])
        except:
            self.default_settings(path)


    def default_settings(self, path):
        data_file_path = os.path.join(path, 'data.json')
        game_data_file_path = os.path.join(path, 'game-data.json')
        
        try:
            with open(data_file_path, "r", encoding='utf-8') as file:
                data = json.load(file)
            seasons = ""
            for s in data["Frames"].keys():
                seasons += str(int(s[1:])) + ', '
            seasons = seasons[:-2]
            
            self.season_entry.delete(0, tk.END)
            self.season_entry.insert(0, seasons)
            self.report_entry.delete(0, tk.END)
            self.report_entry.insert(0, 1)
            self.syn.set(1)

            with open(game_data_file_path,"w", encoding='utf-8') as file:
                game_data = {
                    "Settings":{"Seasons":seasons,"Synopsis": 1,"Report": 1,}
                }
                json.dump(game_data, file, ensure_ascii=False, indent=4)
        except:
            pass


    def save_settings(self):
        new_seasons = self.season_entry.get().split(',')
        remove_list = []
        for i in range(len(new_seasons)):
            try:
                new_seasons[i] = int(new_seasons[i])
            except:
                remove_list.append(i)
        for i in remove_list[::-1]:
            del new_seasons[i]

        data_file_path = os.path.join(self.data_dir, 'data.json')
        game_data_file_path = os.path.join(self.data_dir, 'game-data.json')

        with open(data_file_path, "r", encoding='utf-8') as file:
                data = json.load(file)
        all_seasons = []
        for s in data["Frames"].keys():
            all_seasons.append((int(s[1:])))

        seasons = list(set(new_seasons).intersection(all_seasons))
        if len(seasons) == 0:
            seasons = all_seasons
        s_entry = ""
        for s in seasons:
            s_entry += str(s) + ', '
        self.season_entry.delete(0, tk.END)
        self.season_entry.insert(0, s_entry[:-2])
        
        try: 
            reports = int(self.report_entry.get())
        except:
            reports = 1

        self.report_entry.delete(0, tk.END)
        self.report_entry.insert(0, reports)

        with open(game_data_file_path,"w", encoding='utf-8') as file:
                game_data = {
                    "Settings":{"Seasons":s_entry[:-2],"Synopsis": self.syn.get(),"Report": reports}
                }
                json.dump(game_data, file, ensure_ascii=False, indent=4)
    

def main():
    
    window = FrameGame()

    # get the main page instance
    main_page = window.pages[main_screen]

    # connect resize binding to the main page's canvas
    main_page.search_bar.bind("<KeyRelease>", main_page.on_search)
    main_page.search_bar.bind("<Return>", main_page.on_submit)
    for key in list(main_page.menus.keys()):
        main_page.menus[key].bind("<Return>", main_page.on_submit)
    window.image_canvas.bind("<Configure>", window.resize_image)
    main_page.controller.image_canvas.bind("<Configure>", main_page.resize_radios)
    window.mainloop()

if __name__ == "__main__":
    main()
