from algoliasearch.search_client import SearchClient

from app import config
from .models import VideoIndex, PlaylistIndex

settings = config.get_settings()

ALGOLIA_APP_ID = settings.algolia_app_id
ALGOLIA_API_KEY = settings.algolia_api_key
ALGOLIA_INDEX_NAME = settings.algolia_index_name


def get_index(name=ALGOLIA_INDEX_NAME):
    client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
    index = client.init_index(name)
    return index


def get_dataset(db):
    videos = [VideoIndex(**video).dict() for video in db.videos.find()]
    playlists = [PlaylistIndex(**playlist).dict() for playlist in db.playlists.find()]
    dataset = videos + playlists
    return dataset


def update_index(db):
    index = get_index()
    dataset = get_dataset(db)
    response = index.save_objects(dataset)
    try:
        count = len((response.raw_responses[0]['objectIDs']))
    except:
        count = 0
    return count


def search_index(query):
    index = get_index()
    return index.search(query)
