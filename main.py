from tkinter import filedialog
from random import randrange
import ffmpeg


def get_response(question, options, outputs):
    while True:
        user_input = input(question)
        if user_input.lower() in options:
            return outputs[options.index(user_input)]
        else:
            print("Not a valid input, try again")


def get_settings(vid_dir="", frame_dir="", frame_timing=None):
    while True:

        if vid_dir == "":
            print("A file choice dialogue will appear, choose location where video files are")
            input("press enter to continue")
            while vid_dir == "":
                vid_dir = filedialog.askdirectory(title="Choose location where videos are", mustexist=True)
        elif get_response("change video directory? (Y/n): ", ['y','n'], [True, False]):
            vid_dir = ""
            while vid_dir == "":
                vid_dir = filedialog.askdirectory(title="Choose location where videos are", mustexist=True)

        if frame_dir == "":
            print("A file choice dialogue will appear, choose location where you want frames and data to be saved")
            input("press enter to continue")
            while frame_dir == "": 
                frame_dir = filedialog.askdirectory(title="Choose frame/data saving location", mustexist=True)
        elif get_response("change frame/data directory? (Y/n): ", ['y','n'], [True, False]):
            frame_dir = ""
            while frame_dir == "": 
                frame_dir = filedialog.askdirectory(title="Choose frame/data saving location", mustexist=True)

        if frame_timing is None:
            frame_timing = get_response("Do you want random frame timings? (Y/n): ", ['y','n'], [True, False])
        elif get_response("change frame timing setting? (Y/n): ", ['y','n'], [True, False]):
            frame_timing = get_response("Do you want random frame timings? (Y/n): ", ['y','n'], [True, False])

        if not get_response(f"Here are your current settings:\n\tVideo Directory ------- {vid_dir}\n\tFrame/Data Directory -- {frame_dir}\n\tRandom Frame Times ---- {frame_timing}\nwould you like to change them? (Y/n): ", ['y','n'], [True, False]):
            return vid_dir, frame_dir, frame_timing


def frame_times(frame_timing, length, fps=1/60):
    r_fps = int(1/fps)
    frames = []

    if not frame_timing:
        for min in range(1, int((length+r_fps-1)//r_fps)):
            frames.append(('t', min*r_fps, min*r_fps+1))

    else:
        prev_frame = 0
        for min in range(1, int((length+r_fps-1)//r_fps)):
            frame = randrange(max(0,int(prev_frame-3/4*r_fps)), r_fps)
            frames.append(('t', int(min*r_fps-r_fps/2+frame), int(min*r_fps-r_fps/2+frame+1)))

    return frames

def extract_frames(file=0, output_loc=0, frames=0):
    (
        ffmpeg
        .input(r"C:\Users\Couto\Personal\Coding\FrameGame\test-folder\video\My Little Pony Friendship Is Magic S01E01.mkv")
        .output(r"C:\Users\Couto\Personal\Coding\FrameGame\test-folder\frame-data\out%d.jpg", vf="select='between(t,60,61)+between(t,120,121)+between(t,180,181)+between(t,240,241)+between(t,300,301)+between(t,360,361)+between(t,420,421)+between(t,480,481)+between(t,540,541)+between(t,600,601)+between(t,660,661)+between(t,720,721)+between(t,780,781)+between(t,840,841)+between(t,900,901)+between(t,960,961)+between(t,1020,1021)+between(t,1080,1081)+between(t,1140,1141)+between(t,1200,1201)+between(t,1260,1261)+between(t,1320,1321)+between(t,1380,1381)',fps=1/61")
        .run()
    )
    
    


def main():
    print("--Welcome to FrameExtractor for FrameGame!--")
    input("press enter to continue")
    #vid_dir, frame_dir, frame_timing = get_settings()
    #print (f"Here are your current settings:\n\tVideo Directory ------- {vid_dir}\n\tFrame/Data Directory -- {frame_dir}\n\tRandom Frame Times ---- {frame_timing}")

    #print(frame_times(False, 300, 1/60))
    print(frame_times(True, 300, 1/60))
    extract_frames()
    input("hit enter to exit")


if __name__ == "__main__":
    main()
