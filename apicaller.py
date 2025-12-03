import requests


def get_imdb_id(title, api_key):
    url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
    r = requests.get(url).json()
    return r.get("imdbID")


def get_total_seasons_by_id(imdb_id, api_key):
    url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}"
    r = requests.get(url).json()
    return int(r.get("totalSeasons", 0))


def get_episode_synopsis_by_id(imdb_id, season, episode, api_key):
    url = (
        f"http://www.omdbapi.com/?i={imdb_id}"
        f"&Season={season}&Episode={episode}"
        f"&plot=full&apikey={api_key}"
    )
    return requests.get(url).json()


def get_all_synopses(title, api_key):
    imdb_id = get_imdb_id(title, api_key)
    total_seasons = get_total_seasons_by_id(imdb_id, api_key)
    all_eps = {}

    for season in range(1, total_seasons + 1):
        season_url = (
            f"http://www.omdbapi.com/?i={imdb_id}"
            f"&Season={season}&apikey={api_key}"
        )
        season_data = requests.get(season_url).json()

        for ep in season_data.get("Episodes", []):
            ep_num = int(ep["Episode"])
            ep_data = get_episode_synopsis_by_id(imdb_id, season, ep_num, api_key)

            all_eps[f"S{season:02}E{ep_num:02}"] = {
                "title": ep_data.get("Title"),
                "synopsis": ep_data.get("Plot")
            }

    return all_eps
