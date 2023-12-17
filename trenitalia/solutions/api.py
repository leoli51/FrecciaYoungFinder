from datetime import datetime

from trenitalia.exceptions import TrenitaliaAPIException
from trenitalia.solutions.models import Solution
from trenitalia.utils import api

FIND_SOLUTIONS_API_URL = (
    "https://www.lefrecce.it/Channels.Website.BFF.WEB/website/ticket/solutions"
)


def find_solutions(
    *, arrival_id: int, departure_date: datetime, departure_id: int
) -> list[Solution]:
    solutions = []
    iteration = 0
    last_fetched_solutions = 10
    while last_fetched_solutions == 10:
        request_body = {
            "departureLocationId": departure_id,
            "arrivalLocationId": arrival_id,
            "departureTime": departure_date.isoformat(),
            # "returnDepartureTime": (stringa, opzionale) Se specificato, ritorna soluzioni A/R con la data/ora di ritorno indicata, in formato ISO date,
            "adults": 1,
            "children": 0,
            "criteria": {
                "frecceOnly": True,
                "regionalOnly": False,
                "noChanges": True,
                "order": "DEPARTURE_DATE",  # "DEPARTURE_DATE", "ARRIVAL_DATE", "FASTEST", "CHEAPEST"
                "limit": 10,
                "offset": 10 * iteration,
            },
            "advancedSearchRequest": {
                "bestFare": False,
            },
        }
        response = api.post(FIND_SOLUTIONS_API_URL, None, request_body)

        if response.get("type") == "ERROR":
            raise TrenitaliaAPIException(response.get("message"))

        last_solutions = [
            Solution.from_api_response(solution)
            for solution in response["solutions"]
            if solution["solution"]["status"] == "SALEABLE"
        ]
        solutions += last_solutions
        last_fetched_solutions = len(last_solutions)
        iteration += 1
    return solutions


def find_cheap_solutions(
    *, arrival_id: int, departure_date: datetime, departure_id: int, max_price: float
) -> list[Solution]:
    return [
        solution
        for solution in find_solutions(
            arrival_id=arrival_id,
            departure_date=departure_date,
            departure_id=departure_id,
        )
        if any(map(lambda offer: offer.price <= max_price, solution.offers))
    ]


def find_frecciayoung_solutions(
    *,
    arrival_id: int,
    departure_date: datetime,
    departure_id: int,
) -> list[Solution]:
    return [
        solution
        for solution in find_solutions(
            arrival_id=arrival_id,
            departure_date=departure_date,
            departure_id=departure_id,
        )
        if any(map(lambda offer: offer.name == "FrecciaYOUNG", solution.offers))
    ]


if __name__ == "__main__":
    solutions = find_solutions(
        departure_id=830001650,
        arrival_id=830008349,
        departure_date=datetime(2023, 12, 18),
    )
    print(len(solutions))
    for solution in solutions:
        print(solution)
        print()
