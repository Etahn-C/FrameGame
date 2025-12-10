import tkinter as tk
from tkinter import filedialog as fd
from PIL import ImageTk, Image
import json
import os
import random


class FrameGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FrameGame!")
        self.geometry("680x580")
        self.config(background="#808080")
        
        self.bg = "#808080"
        self.button_color = "#A0A0A0"
        self.y=1/29
        self.x=1/34
        self.game_dir = ""
                
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
        self.dir_path = controller.game_dir
        self.all_frames = []
        
        super().__init__(parent, bg=self.bg)
        # Title bar:
        self.title_bar = tk.Label(self, text="Frame Game", bg=self.bg)
        self.title_bar.place(relheight=self.y, relwidth=28*self.x, relx=3*self.x, rely=self.y*0)
        
        # Image Info: 
        self.image_info_label = tk.Label(self, bg=self.bg, text="")
        self.image_info_label.place(relheight=self.y, relwidth=16*self.x, relx=9*self.x, rely=19*self.y)
        
        # Search Bar:
        self.search_bar = tk.Entry(self, bg=self.button_color)
        self.search_bar.place(relheight=self.y, relwidth=24*self.x, relx=self.x, rely=20*self.y)
        self.search_menu_canvas = tk.Canvas(self, bg=self.bg)
        self.search_menu_canvas.place(relheight=7*self.y, relwidth=24*self.x, relx=1*self.x, rely=21*self.y)
        self.search_menu = tk.Listbox(self.search_menu_canvas, bg=self.bg)
        #self.search_menu.insert(tk.END, "S01E01 : Friendship Is Magic - Part 1 (Mare in the Moon) : After being warned of a ","horrible prophecy, Princess Celestia sends her overly studious student Twilight Sparkle to ", "Ponyville to supervise the preparations for the Summer Sun Celebration and to \"make ", "some friends\".", "2", "3", "1", "2", "3", "1", "2", "3")
        self.search_menu.place(relheight=1, relwidth=1, relx=0, rely=0)
        
        # Game Buttons
        self.next_button = tk.Button(self, text="Next / Skip", bg=self.button_color, command=lambda: self.new_frame())
        self.report_button = tk.Button(self, text="Report Frame", bg=self.button_color)
        self.restart_button = tk.Button(self, text="Restart", bg=self.button_color)
        self.settings_button = tk.Button(self, text="Settings", bg=self.button_color, command=lambda: (controller.show_page(settings_screen)))
        self.next_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=20*self.y)
        self.report_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=22*self.y)
        self.restart_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=24*self.y)
        self.settings_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=26*self.y)
        
        # Image Box:
        self.image_canvas = tk.Canvas(self, bg=self.bg)
        self.image_canvas.place(relheight=18*self.y, relwidth=32*self.x, relx=self.x, rely=self.y)
        self.img = Image.open(r"./start_image.jpg")
        self.controller.image_canvas = self.image_canvas
        self.controller.img = self.img
    
    def update_disabled_widgets(self):
        if self.dir_path == "":
            self.next_button.config(state=tk.DISABLED)
            self.report_button.config(state=tk.DISABLED)
            self.restart_button.config(state=tk.DISABLED)
            self.search_bar.config(state=tk.DISABLED)
            self.search_menu.config(state=tk.DISABLED)
        else:
            self.next_button.config(state=tk.NORMAL)
            self.report_button.config(state=tk.NORMAL)
            self.restart_button.config(state=tk.NORMAL)
            self.search_bar.config(state=tk.NORMAL)
    
    def on_show(self):
        self.dir_path = self.controller.game_dir
        self.update_disabled_widgets()
        if self.dir_path != "":
            game_data_file_path = os.path.join(self.dir_path, 'game-data.json')
            frame_data_file_path = os.path.join(self.dir_path, 'data.json')
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
                
                self.img = Image.open(r"./start_image.jpg")
            except:
                pass
        else:
            self.img = Image.open(r"./default_image.jpg")
            self.title_bar['text'] = "FrameGame"
            self.image_info_label['text'] = ""
        
        self.controller.img = self.img
        self.controller.resize_image()
            
    def update_game_dir(self):
        self.controller.game_dir = self.dir_path
    
    def new_frame(self):
        with open(os.path.join(self.dir_path, "data.json"), 'r', encoding='utf-8') as file:
            frame_data = json.load(file)
        
        rand_season_index = random.randrange(0, len(self.season_select))
        rand_season = f"S{self.season_select[rand_season_index]:02}"
        rand_episode_index = random.randrange(0, len(frame_data["Frames"][rand_season].keys()))
        rand_episode = list(frame_data["Frames"][rand_season].keys())[rand_episode_index]
        rand_frame_index = random.randrange(0, len(frame_data["Frames"][rand_season][rand_episode].keys()))
        rand_frame = list(frame_data["Frames"][rand_season][rand_episode].keys())[rand_frame_index]
        if len(self.all_frames) == 0:
            for root, _, files in os.walk(self.dir_path):
                for name in files:
                    self.all_frames.append(os.path.join(root, name))
        for frame in self.all_frames:
            if f"{rand_season}{rand_episode} - {rand_frame}" in frame:
                self.img = Image.open(frame)
                exit
        self.controller.img = self.img
        self.controller.resize_image()
        self.current_season = rand_season
        self.current_episode = rand_episode
        self.current_frame = rand_frame
        self.current_frame_time = frame_data["Frames"][rand_season][rand_episode][rand_frame]["time"]
        time = f"{self.current_frame_time//3600:02}:{(self.current_frame_time%3600)//60:02}:{self.current_frame_time%60:02}"
        # TODO not gonna leave this, just for testing
        self.image_info_label['text'] = f"{rand_season}{rand_episode} - {time}"
        pass

class settings_screen(tk.Frame):
    def __init__(self, parent, controller):
        self.bg = controller.bg
        self.button_color = controller.button_color
        self.y = controller.y
        self.x = controller.x
        self.controller = controller
        self.data_dir = ""
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

    window.image_canvas.bind("<Configure>", window.resize_image)
    window.mainloop()

if __name__ == "__main__":
    main()
