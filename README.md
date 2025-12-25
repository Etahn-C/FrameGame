# FrameGame

FrameGame is a frame scaping script and game.

## Frame Scraper

The frame-scraper-cli.py and frame-scraper.py allow for the scraping of video files for images. It saves random or set frames from the video file and saves them neatly into an output file. It also creates a data file with all the frame times and other formatting data.

frame-scraper-cli.py is a fully functional cli tool, it just takes flags and can run the files specified. It it the recomended version.

To actually scrape the files, FFMPEG and FFPROBE are required to be added to the path. The script crashes if it is not installed.

FrameScraper.py is the semi-command line version, it asks for user input throughout and has file dialoogue boxes for file choice. (Slightly Unfinished)

Both of the FrameScaper files acces apicaller.py file which uses OMDB to collect data about the show you are scraping.

## Game

game.pyw is the actual game. It uses a simple ui but allows for different games to be played, it should work with any show that was run using the previous files.

It has settings that allow you to report frames if they are in the opening or ending or just blank. Decide what seasons you want to play with, and if you want to be able to use the sysnopsis to search.

It uses fuzzy search and allows searching by title, synopsis or just episode number. Keeps score per attempt, leaderboard could be added.

## Extra

Feel free to mess with this, it was just a hobby project that I was recommended to try and make. The code is probably very inefficient.
