from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Offer:
    name: str
    price: float
    service_name: str

    @classmethod
    def from_api_response(cls, offer: dict[str, Any]) -> Offer:
        return cls(
            name=offer["name"],
            price=offer["price"]["amount"],
            service_name=offer["serviceName"],
        )


@dataclass(frozen=True)
class Solution:
    arrival_time: datetime
    departure_time: datetime
    destination: str
    duration: str
    origin: str
    offers: list[Offer]

    @classmethod
    def from_api_response(cls, solution: dict[str, Any]) -> Solution:
        offers = []
        for grid in solution["grids"]:
            for service in grid["services"]:
                for offer in service["offers"]:
                    if offer["price"] is not None and offer["status"] == "SALEABLE":
                        offers.append(Offer.from_api_response(offer))
        return cls(
            arrival_time=datetime.fromisoformat(solution["solution"]["arrivalTime"]),
            departure_time=datetime.fromisoformat(
                solution["solution"]["departureTime"]
            ),
            destination=solution["solution"]["destination"],
            duration=solution["solution"]["duration"],
            origin=solution["solution"]["origin"],
            offers=offers,
        )
