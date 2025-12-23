from tkinter import filedialog
from random import randrange
import ffmpeg
import os
from shutil import copytree
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
    # Runs until the user submits a acceptable response
    while True:
        user_input = input(question)
        if user_input.lower() in options:
            return outputs[options.index(user_input)]
        else:
            print("Not a valid input, try again")


def get_settings():
    """
    Gets responses from user and returns them
    """

    vid_dir = ""
    frame_dir = ""
    frame_timing = None

    while True:

        # Getting the video directory
        if vid_dir == "":
            print(
                "A file choice dialogue will appear, choose location where \
video files are")
            input("press enter to continue")
            while vid_dir == "":
                vid_dir = filedialog.askdirectory(
                    title="Choose location where videos are", mustexist=True)
        elif get_response("change video directory? (Y/n): ",
                          ['y', 'n'], [True, False]):
            vid_dir = ""
            while vid_dir == "":
                vid_dir = filedialog.askdirectory(
                    title="Choose location where videos are", mustexist=True)

        # Getting the frame/data directory
        if frame_dir == "":
            print(
                "A file choice dialogue will appear, choose location where \
you want frames and data to be saved")
            input("press enter to continue")
            while frame_dir == "":
                frame_dir = filedialog.askdirectory(
                    title="Choose frame/data saving location", mustexist=True)
        elif get_response("change frame/data directory? (Y/n): ",
                          ['y', 'n'], [True, False]):
            frame_dir = ""
            while frame_dir == "":
                frame_dir = filedialog.askdirectory(
                    title="Choose frame/data saving location", mustexist=True)

        # Gets the frame timing boolean
        if frame_timing is None:
            frame_timing = get_response(
                "Do you want random frame timings? (Y/n): ",
                ['y', 'n'], [True, False])
        elif get_response("change frame timing setting? (Y/n): ",
                          ['y', 'n'], [True, False]):
            frame_timing = get_response(
                "Do you want random frame timings? (Y/n): ",
                ['y', 'n'], [True, False])

        # Will allow you to start again if you want
        if not get_response(f"Here are your current settings:\n\tVideo \
Directory ------- {vid_dir}\n\tFrame/Data Directory -- \
{frame_dir}\n\tRandom Frame Times ---- {frame_timing}\nwould you like to \
change them? (Y/n): ", ['y', 'n'], [True, False]):
            return vid_dir, frame_dir, frame_timing


def frame_times(frame_timing: bool, length: int, fps: float = 1/60):
    """
    Takes in some variables and return a list of numbers.

    :param frame_timing: True for random frame timings
    :type frame_timing: bool
    :param length: length of item in seconds
    :type length: int
    :param fps: how many cuts per second default 1/60
    :type fps: float
    """
    r_fps = int(1/fps)
    frames = []

    # Runs once per time variable and return the list of times
    if not frame_timing:
        for minute in range(1, int((length+r_fps-2)//r_fps)):
            frames.append(minute*r_fps)

    else:
        prev_frame = 0
        # Runs once per time variable
        for minute in range(1, int((length+r_fps-2)//r_fps)):
            # Gets a random int between 0 and time variable seconds
            # Ensures range is at least 1/4 time variable after previous frame
            # Ensures range does not exceed length
            # Ensures range exists, ie not (5,4)
            frame = randrange(
                max(0,
                    min(int(prev_frame-3/4*r_fps),
                        length-r_fps*minute)-1),
                min(r_fps, length-r_fps*minute))
            prev_frame = frame
            # Will append the time based on the random int.
            time = int(minute*r_fps-r_fps/2+frame)
            frames.append(time)

    return frames


def extract_frames(file: str, output_loc: str, times: list[int]):
    """
    Uses FFMPEG to extract frames based on a list of times.

    :param file: Input file path
    :type file: str
    :param output_loc: Output file path
    :type output_loc: str
    :param times: List of times to extract
    :type times: list[int]
    """
    # Creates the string for the FFMPEG command
    frames = "fps=1, select='"
    for time in times:
        frames += f"eq(t,{time})+"
    frames = frames[0:-1]
    frames += "'"

    file_name = os.path.splitext(os.path.basename(file))[0]
    print(f"\nProcessing: {file_name}")

    # Runs the FFMPEG command
    (
        ffmpeg
        .input(file)
        .output(os.path.join(output_loc, file_name + r" - F%03d.jpg"),
                vf=frames, fps_mode='vfr')
        .global_args("-hide_banner")
        .global_args("-loglevel", "error")
        .global_args("-stats")
        .run()
    )


def ignore_files(dir, files):
    # Just used by copytree to ingnore files and only copy directories.
    return [f for f in files if os.path.isfile(os.path.join(dir, f))]


def run_files(file_path: str, save_path: str, frame_timing: bool = False,
              fps: float = 1/60, data_file_path: str = None):
    """
    Goes through all files in directory and subdirectories
    and runs the extract frames and write data function.

    :param file_path: Input file path
    :type file_path: str
    :param save_path: output file path
    :type save_path: str
    :param frame_timing: True for random timing
    :type frame_timing: bool
    :param fps: frames per second 1/60 is def
    :type fps: float
    :param data_file_path: file path to data file
    :type data_file_path: str
    """
    # Runs once per item in the main directory
    for item in os.listdir(file_path):
        file = os.path.join(file_path, item)
        # If the item is directory, then it runs again in new directory
        if os.path.isdir(file):
            run_files(file, os.path.join(save_path, item),
                      frame_timing, fps, data_file_path)
        else:
            # Gets file length and times
            length = int(float(ffmpeg.probe(file)['format']['duration']))
            times = frame_times(frame_timing, length, fps)
            try:
                # Extracts frames and then writes data to data file.
                extract_frames(file, os.path.join(save_path, "frames"), times)
                write_data(data_file_path, item, times)
            except Exception:
                print("Failed, moving to next file.")


def write_data(data_file_path: str, item, times):
    """
    Will write data to the data file

    :param data_file_path: file path for data file
    :type data_file_path: str
    :param item: Name of the item being added
    :param times: List of times
    """
    # Gets season and episode data from file name
    season = re.search(r"([S]\d\d)[E]\d\d", item).group(1)
    episode = re.search(r"[S]\d\d([E]\d\d)", item).group(1)

    # Gets the current data from the data file
    with open(data_file_path, "r", encoding='utf-8') as file:
        data = json.load(file)
    file.close()

    # Updates the data in the data file based on the times
    with open(data_file_path, "w", encoding='utf-8') as file:
        if season not in data["Frames"]:
            data["Frames"].update({season: {}})
        if episode not in data["Frames"][season]:
            data["Frames"][season].update({episode: {}})
        for frame in range(len(times)):
            data["Frames"][season][episode].update(
                {f"F{frame+1:03}": {"time": times[frame], "reports": 0}})
        json.dump(data, file, ensure_ascii=False, indent=4)
    file.close()


def main():
    print("--Welcome to FrameExtractor for FrameGame!--")
    input("press enter to continue")
    input_dir, output_dir, frame_timing = get_settings()

    # Default Variables that could be changed to be user inputs
    framerate = "1/60"
    fps = 1/60
    title = "My Little Pony Friendship Is Magic"
    data_override = False
    ep_override = False

    # Gets enviroment variable for the OMDB api key
    load_dotenv()
    API_KEY = os.getenv("OMDB_API_KEY")

    # Will create the data file if not already made.
    if (not os.path.isfile(
            os.path.join(output_dir, "frame-data.json"))) or (data_override):
        print("\nCreating Data File")
        with open(os.path.join(output_dir, "frame-data.json"), "w",
                  encoding='utf-8') as file:
            data = {"Settings": {"RandomTiming": frame_timing,
                                 "Framerate": f"{framerate}",
                                 "Title": title}, "Frames": {}}
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("Data File Created")
        file.close()

    # Will create the ep data file and use api if not already present
    if (not os.path.isfile(
            os.path.join(output_dir, "ep-data.json"))) or (ep_override):
        if (get_response("Do you want to run api? (y/n): ",
                         ["y", "n"], [True, False])):
            print("\nFetching Episode Data")
            with open(os.path.join(output_dir, "ep-data.json"),
                      "w", encoding='utf-8') as file:
                json.dump(get_all_synopses(title, API_KEY),
                          file, ensure_ascii=False, indent=4)
            print("Episode Data Saved - Recommended to check for missing data")

    # Will copy the file structure from the input dir to the output dir
    copytree(input_dir, os.path.join(output_dir, "frames"),
             dirs_exist_ok=True, ignore=ignore_files)

    # Double checks if you want to extract the frames
    if get_response(
        "\nDo you want to run the files, can take a long time! (yes/no): ",
            ["yes", "no"], [True, False]):
        run_files(input_dir, output_dir, frame_timing, fps,
                  os.path.join(output_dir, "frame-data.json"))

    input("\nPress enter to exit")


if __name__ == "__main__":
    main()
