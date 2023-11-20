from trenitalia.stations.models import Station
from trenitalia.utils import api

FIND_STATIONS_API_URL = (
    "https://www.lefrecce.it/Channels.Website.BFF.WEB/website/locations/search"
)


def find_stations(*, name: str) -> list[Station]:
    return [
        Station.from_api_response(station)
        for station in api.get(FIND_STATIONS_API_URL, {"name": name, "limit": 10})
    ]


if __name__ == "__main__":
    print(find_stations(name="Milano"))
