from random import randrange
import ffmpeg
import os
from shutil import copytree
import json
import re
from dotenv import load_dotenv
from apicaller import get_all_synopses
import argparse
from fractions import Fraction


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
                extract_frames(file, save_path, times)
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
        if season not in data["frames"]:
            data["frames"].update({season: {}})
        if episode not in data["frames"][season]:
            data["frames"][season].update({episode: {}})
        for frame in range(len(times)):
            data["frames"][season][episode].update(
                {f"F{frame+1:03}": {"time": times[frame], "reports": 0}})
        json.dump(data, file, ensure_ascii=False, indent=4)
    file.close()


def dir_path(string):
    if os.path.isdir(string):
        return os.path.abspath(string)
    else:
        raise NotADirectoryError(string)


def main():

    # Arugment processing
    parser = argparse.ArgumentParser(description=(
        "frame-scaper, uses video files and grabs frames from it."))
    parser.add_argument("-i", "--input",
                        help="Input folder path",
                        required=True,
                        type=dir_path)
    parser.add_argument("-o", "--output",
                        help="Output folder path",
                        required=True,
                        type=dir_path)
    parser.add_argument("-t", "--title",
                        help="Title of videos",
                        required=True,
                        type=str)
    parser.add_argument("-fr", "--framerate",
                        help="Number of fps, defaults to 1/60",
                        default=1/60,
                        type=Fraction)
    parser.add_argument("-rt", "--random-timing",
                        help="Random Timing, defaults to False",
                        action=argparse.BooleanOptionalAction)
    parser.add_argument("-ov", "--overwrite",
                        help="Overwrite current data, defaults to False",
                        action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    # Variable setting
    input_dir = args.input
    output_dir = args.output
    title = args.title
    framerate = args.framerate
    if args.random_timing:
        random_timing = args.random_timing
    else:
        random_timing = False

    if args.overwrite:
        overwrite = args.overwrite
    else:
        overwrite = False

    print(f"{input_dir=}\n{output_dir=}\n"
          f"{title=}\nframerate={framerate}\n{random_timing=}"
          f"{overwrite=}")

    # Checking for API key
    load_dotenv()
    API_KEY = os.getenv("OMDB_API_KEY")
    if API_KEY is None:
        print("No Api Key found, make and .env file with OMDB_API_KEY=\"\" "
              "or add OMDB_API_KEY to your enviroment variables")
        return

    # Will create the data file if not already made.
    if (not os.path.isfile(
            os.path.join(output_dir, "data.json"))) or (overwrite):
        print("\nCreating Data File")
        with open(os.path.join(output_dir, "data.json"), "w",
                  encoding='utf-8') as file:
            data = {"settings": {"random_timing": random_timing,
                                 "framerate": f"{framerate}",
                                 "title": title}, "frames": {}}
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("Data File Created")
        file.close()

    # Will create the ep data file and use api if not already present
    if (not os.path.isfile(
            os.path.join(output_dir, "ep-data.json"))) or (overwrite):
        print("\nFetching Episode Data")
        with open(os.path.join(output_dir, "ep-data.json"),
                  "w", encoding='utf-8') as file:
            json.dump(get_all_synopses(title, API_KEY),
                      file, ensure_ascii=False, indent=4)
        print("Episode Data Fetched - Recommended to check for missing data")

    # Will copy the file structure from the input dir to the output dir
    copytree(input_dir, os.path.join(output_dir, "frames"),
             dirs_exist_ok=True, ignore=ignore_files)

    # Double checks if you want to extract the frames
    run_files(input_dir, os.path.join(output_dir, "frames"), random_timing,
              framerate, os.path.join(output_dir, "data.json"))


if __name__ == "__main__":
    main()
