from tkinter import filedialog
from random import randrange
import ffmpeg
import os
from  shutil import copytree
import json
import re
from dotenv import load_dotenv
from apicaller import get_all_synopses


def get_response(question: str, options: list[str], outputs: list[str]):
    """
    Gets a text response based on input
    
    :param question: question string
    :param options: list with all valid options
    :param outputs: list with responses coordinated with options
    """
    while True:
        user_input = input(question)
        if user_input.lower() in options:
            return outputs[options.index(user_input)]
        else:
            print("Not a valid input, try again")


def get_settings(vid_dir: str="", frame_dir: str="", frame_timing: bool=None):
    """
    Gets responses from user and returns them
    
    :param vid_dir: None
    :param frame_dir: None
    :param frame_timing: None
    """
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


def frame_times(frame_timing:bool, length:int, fps:float=1/60):
    """
    Generates a list of frame times
    
    :param rand_frame_timing: Bool
    :param length: length in seconds
    :param fps: how many frames per second
    """
    r_fps = int(1/fps)
    frames = []

    if not frame_timing:
        for minute in range(1, int((length+r_fps-2)//r_fps)):
            frames.append(minute*r_fps)

    else:
        prev_frame = 0
        for minute in range(1, int((length+r_fps-2)//r_fps)):
            frame = randrange(
                max(0,min(int(prev_frame-3/4*r_fps), length-r_fps*minute)-1), 
                min(r_fps, length-r_fps*minute))
            prev_frame = frame
            time = int(minute*r_fps-r_fps/2+frame)
            frames.append(time)

    return frames


def extract_frames(file:str, output_loc:str, times:list[int]):
    """
    Uses ffmpeg to extract frames
    
    :param file: input file path
    :param output_loc: output fiel path
    """
    frames = f"fps=1, select='"
    for time in times:
        frames += f"eq(t,{time})+"
    frames = frames[0:-1]
    frames += f"'"

    file_name = os.path.splitext(os.path.basename(file))[0]
    print(f"\nProcessing: {file_name}")
    (
        ffmpeg
        .input(file)
        .output(os.path.join(output_loc, file_name + r" - F%03d.jpg"), vf=frames, fps_mode='vfr')
        .global_args("-hide_banner")
        .global_args("-loglevel", "error")
        .global_args("-stats")
        .run()
    )


def ignore_files(dir, files):
    return [f for f in files if os.path.isfile(os.path.join(dir, f))]


def folder_structure(file_path:str, save_path:str):
    copytree(file_path, save_path, dirs_exist_ok=True, ignore=ignore_files)


def run_files(file_path:str, save_path:str, frame_timing:bool=False, fps:float=1/60, data_file_path:str=None):
    for item in os.listdir(file_path):
        file = os.path.join(file_path, item)
        if os.path.isdir(file):
            run_files(file, os.path.join(save_path, item), frame_timing, fps, data_file_path)
        else:
            length = int(float(ffmpeg.probe(file)['format']['duration']))
            times = frame_times(frame_timing, length, fps)
            try:
                extract_frames(file, save_path, times)
                write_data(data_file_path, item, times)
            except Exception:
                print("Failed, moving to next file.")


def write_data(data_file_path:str, item, times):
    season = re.search(r"([S]\d\d)[E]\d\d", item).group(1)
    episode = re.search(r"[S]\d\d([E]\d\d)", item).group(1)
    with open(data_file_path, "r", encoding='utf-8') as file:
        data = json.load(file)
    file.close()
    with open(data_file_path, "w", encoding='utf-8') as file:
        if season not in data["Frames"]:
            data["Frames"].update({season:{}})
        if episode not in data["Frames"][season]:
            data["Frames"][season].update({episode:{}})
        for frame in range(len(times)):
            data["Frames"][season][episode].update({f"F{frame+1:03}":{"time":times[frame], "reports":0}})
        json.dump(data, file, ensure_ascii=False, indent=4)
    file.close()    


def main():
    print("--Welcome to FrameExtractor for FrameGame!--")
    input("press enter to continue")
    input_dir, output_dir, frame_timing = get_settings()
    
    framerate = "1/60"
    fps = 1/60
    title = "My Little Pony Friendship Is Magic"
    data_override = False
    ep_override = False
    
    load_dotenv()
    API_KEY = os.getenv("OMDB_API_KEY")
    
    if (not os.path.isfile(os.path.join(output_dir, "data.json"))) or (data_override):
        print("\nCreating Data File")
        with open(os.path.join(output_dir, "data.json"), "w", encoding='utf-8') as file:
            data = {"Settings":{"RandomTiming": frame_timing, "Framerate": f"{framerate}", "Title": title}, "Frames":{}}
            json.dump(data, file, ensure_ascii=False, indent=4)  
        print("Data File Created")
        file.close()
    
    if (not os.path.isfile(os.path.join(output_dir, "ep-data.json"))) or (ep_override):
        print("\nFetching Episode Data")
        with open(os.path.join(output_dir, "ep-data.json"), "w", encoding='utf-8') as file:
            json.dump(get_all_synopses(title, API_KEY), file, ensure_ascii=False, indent=4) 
        print("Episode Data Saved")
        file.close()
        
    folder_structure(input_dir, output_dir)
    
    if get_response("\nDo you to run the files (yes/no): ", ["yes","no"], [True, False]):
        run_files(input_dir, output_dir, frame_timing, fps, os.path.join(output_dir, "data.json"))
    
    input("\nPress enter to exit")


if __name__ == "__main__":
    main()
