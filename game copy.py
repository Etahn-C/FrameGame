import tkinter as tk
from PIL import ImageTk, Image


class FrameGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FrameGame!")
        self.geometry("680x580")
        self.config(background="#808080")
        self.bg = "#808080"
        self.y=1/29
        self.x=1/34
        self.main_screen()
        

    def settings_screen(self):
        next_button = tk.Button(self, text="Next / Skip", bg=self.bg, command=self.main_screen)
        next_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=22*self.y)

        pass

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
        super().__init__(parent)
        # Title bar:
        title_bar = tk.Label(self, text="Frame Game: My Little Pony Edition", bg=self.bg)
        title_bar.place(relheight=self.y, relwidth=28*self.x, relx=3*self.x, rely=self.y*0)
        
        # Image Info: 
        image_info_label = tk.Label(self, bg=self.bg, text="From SXXEXX at XX:XX ---- Score: 27/79")
        image_info_label.place(relheight=self.y, relwidth=16*self.x, relx=9*self.x, rely=19*self.y)
        
        # Search Bar:
        search_bar = tk.Entry(self, bg=self.bg)
        search_bar.place(relheight=self.y, relwidth=24*self.x, relx=self.x, rely=20*self.y)
        seach_menu_canvas = tk.Canvas(self, bg=self.bg)
        seach_menu_canvas.place(relheight=7*self.y, relwidth=24*self.x, relx=1*self.x, rely=21*self.y)
        search_menu = tk.Listbox(seach_menu_canvas, bg=self.bg)
        search_menu.insert(tk.END, "S01E01 : Friendship Is Magic - Part 1 (Mare in the Moon) : After being warned of a ","horrible prophecy, Princess Celestia sends her overly studious student Twilight Sparkle to ", "Ponyville to supervise the preparations for the Summer Sun Celebration and to \"make ", "some friends\".", "2", "3", "1", "2", "3", "1", "2", "3")
        search_menu.place(relheight=1, relwidth=1, relx=0, rely=0)
        
        # Game Buttons
        next_button = tk.Button(self, text="Next / Skip", bg=self.bg, command="") #TODO
        report_button = tk.Button(self, text="Report Frame", bg=self.bg)
        restart_button = tk.Button(self, text="Restart", bg=self.bg)
        settings_button = tk.Button(self, text="Settings", bg=self.bg)
        next_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=20*self.y)
        report_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=22*self.y)
        restart_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=24*self.y)
        settings_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=26*self.y)
        
        # Image Box:
        self.image_canvas = tk.Canvas(self, bg=self.bg)
        self.image_canvas.place(relheight=18*self.y, relwidth=32*self.x, relx=self.x, rely=self.y)
        self.img = Image.open(r"C:\Users\Couto\Personal\Coding\FrameGame\test-folder\frame-data\Season 01\My Little Pony Friendship Is Magic S01E01 - F001.jpg")
        
class settinfs_screen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        next_button = tk.Button(self, text="Next / Skip", bg=self.bg, command=self.main_screen)
        next_button.place(relheight=self.y, relwidth=7*self.x, relx=26*self.x, rely=22*self.y)

def main():
    
    window = FrameGame()
    # Bind canvas resizing
    window.image_canvas.bind("<Configure>", window.resize_image)
    window.mainloop()

if __name__ == "__main__":
    main()
