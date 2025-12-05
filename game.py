import tkinter as tk
from PIL import ImageTk, Image


def main():
    root = tk.Tk()
    root.title("FrameGame!")
    root.geometry("680x580")
    root.config(background="#808080")
    bg = "#808080"
    y=1/29
    x=1/34

    # Title bar:
    title_bar = tk.Label(root, text="Frame Game: My Little Pony Edition", bg=bg)
    title_bar.place(relheight=y, relwidth=28*x, relx=3*x, rely=y*0)
    
    # Image Info: 
    image_info_label = tk.Label(root, bg=bg, text="From SXXEXX at XX:XX ---- Score: 27/79")
    image_info_label.place(relheight=y, relwidth=16*x, relx=9*x, rely=19*y)
    
    # Search Bar:
    search_bar = tk.Entry(root, bg=bg)
    search_bar.place(relheight=y, relwidth=24*x, relx=x, rely=20*y)
    seach_menu_canvas = tk.Canvas(root, bg=bg)
    seach_menu_canvas.place(relheight=7*y, relwidth=24*x, relx=1*x, rely=21*y)
    search_menu = tk.Listbox(seach_menu_canvas, bg=bg)
    search_menu.insert(tk.END, "S01E01 : Friendship Is Magic - Part 1 (Mare in the Moon) : After being warned of a ","horrible prophecy, Princess Celestia sends her overly studious student Twilight Sparkle to ", "Ponyville to supervise the preparations for the Summer Sun Celebration and to \"make ", "some friends\".", "2", "3", "1", "2", "3", "1", "2", "3")
    search_menu.place(relheight=1, relwidth=1, relx=0, rely=0)
    
    # Game Buttons
    next_button = tk.Button(root, text="Next / Skip", bg=bg)
    report_button = tk.Button(root, text="Report Frame", bg=bg)
    restart_button = tk.Button(root, text="Restart", bg=bg)
    settings_button = tk.Button(root, text="Settings", bg=bg)
    next_button.place(relheight=y, relwidth=7*x, relx=26*x, rely=20*y)
    report_button.place(relheight=y, relwidth=7*x, relx=26*x, rely=22*y)
    restart_button.place(relheight=y, relwidth=7*x, relx=26*x, rely=24*y)
    settings_button.place(relheight=y, relwidth=7*x, relx=26*x, rely=26*y)
    
    # Image Box:
    image_canvas = tk.Canvas(root, bg=bg)
    image_canvas.place(relheight=18*y, relwidth=32*x, relx=x, rely=y)
    img = Image.open(r"C:\Users\Couto\Personal\Coding\FrameGame\test-folder\frame-data\Season 01\My Little Pony Friendship Is Magic S01E01 - F001.jpg")

    # Function to resize + draw image
    def resize_image(event=None):
        canvas_w = image_canvas.winfo_width()
        canvas_h = image_canvas.winfo_height()

        if canvas_w < 5 or canvas_h < 5:
            return

        # resize keeping aspect ratio
        resized = img.copy()
        resized.thumbnail((canvas_w, canvas_h))

        # convert to PhotoImage
        tk_img = ImageTk.PhotoImage(resized)

        # save reference so it doesn't get garbage-collected
        image_canvas.img = tk_img

        # clear old image
        image_canvas.delete("all")

        # center the image
        image_canvas.create_image(canvas_w/2, canvas_h/2, anchor="center", image=tk_img)

    # Bind canvas resizing
    image_canvas.bind("<Configure>", resize_image)

    root.mainloop()

if __name__ == "__main__":
    main()
