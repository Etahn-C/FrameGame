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
        for minute in range(1, int((length+r_fps-2)//r_fps)):
            frames.append(f"t,{minute*r_fps},{minute*r_fps+1}")

    else:
        prev_frame = 0
        for minute in range(1, int((length+r_fps-2)//r_fps)):
            frame = randrange(max(0,int(prev_frame-3/4*r_fps)), min(r_fps, length-r_fps*minute))
            frames.append(f"t,{int(minute*r_fps-r_fps/2+frame)},{int(minute*r_fps-r_fps/2+frame+1)}")

    return frames

#TODO Make this work with frames instead of seconds!
def frame_times(frame_timing, length, fps=1/60, framerate=24):
    r_fps = int(1/fps)
    frames = []

    if not frame_timing:
        for minute in range(1, int((length+r_fps-2)//r_fps)):
            time = minute*r_fps * framerate
            frames.append(f"n,{time},{time+1}")

    else:
        prev_frame = 0
        for minute in range(1, int((length+r_fps-2)//r_fps)):
            frame = randrange(max(0,int(prev_frame-3/4*r_fps)), min(r_fps, length-r_fps*minute))
            time = int(minute*r_fps-r_fps/2+frame)*framerate
            frames.append(f"n,{time},{time+1}")

    return frames

def extract_frames(file, output_loc=0):
    length = int(float(ffmpeg.probe(file)['format']['duration']))
    print(ffmpeg.probe(file)['streams'][0]['r_frame_rate'])
    frames = f"select='"
    for times in frame_times(True, length, 1, int(eval(ffmpeg.probe(file)['streams'][0]['r_frame_rate']))):
        frames += f"between({times})+"
    frames = frames[0:-1]
    frames += f"',fps=1/60"

    print(frames)
    (
        ffmpeg
        .input(file)
        .output(r"C:\Users\Couto\Personal\Coding\FrameGame\test-folder\frame-data\out%d.jpg", vf=frames, fps_mode='vfr')
        .run()
    )
    
    


def main():
    print("--Welcome to FrameExtractor for FrameGame!--")
    input("press enter to continue")
    #vid_dir, frame_dir, frame_timing = get_settings()
    #print (f"Here are your current settings:\n\tVideo Directory ------- {vid_dir}\n\tFrame/Data Directory -- {frame_dir}\n\tRandom Frame Times ---- {frame_timing}")

    #print(frame_times(False, 300, 1/60))
    print(frame_times(True, 300, 1/60))
 
    extract_frames(r"C:\Users\Couto\Personal\Coding\FrameGame\test-folder\video\My Little Pony Friendship Is Magic S01E01.mkv")
    input("hit enter to exit")


if __name__ == "__main__":
    main()
