from datetime import datetime, timedelta

from trenitalia.solutions.api import find_cheap_solutions
from trenitalia.solutions.models import Solution
from trenitalia.stations.api import find_stations
from trenitalia.stations.models import Station


def _display_stations(stations: list[Station]):
    for i, station in enumerate(stations):
        print(f"{i}: {station.display_name}")


def _display_solutions(solutions: list[Solution]):
    print(f"\nSolutions for {solutions[0].departure_time.date()}:")
    for solution in solutions:
        min_price = min([offer.price for offer in solution.offers])
        print(
            f"\n{solution.origin} - {solution.destination}, {solution.departure_time}-{solution.arrival_time} ({solution.duration}): {min_price} €"
        )


def main():
    departing_station_input = input("Enter the departing station name:\n")
    departing_station_options = find_stations(name=departing_station_input)
    _display_stations(departing_station_options)
    selected_index = int(
        input(f"Select a departing station [0-{len(departing_station_options)}]: ")
    )
    departing_station = departing_station_options[selected_index]

    arrival_station_input = input("Enter the arrival station name:\n")
    arrival_station_options = find_stations(name=arrival_station_input)
    _display_stations(arrival_station_options)
    selected_index = int(
        input(f"Select an arrival station [0-{len(arrival_station_options)}]: ")
    )
    arrival_station = arrival_station_options[selected_index]

    departure_date_input = input("Enter a departure date (format: yyyy-mm-dd): \n")
    year, month, date = list(map(int, departure_date_input.split("-")))
    departure_date = datetime(year, month, date)

    cheap_solutions = find_cheap_solutions(
        arrival_id=arrival_station.id,
        departure_date=departure_date,
        departure_id=departing_station.id,
        max_price=35,
    )
    if cheap_solutions:
        _display_solutions(cheap_solutions)
        return

    print("No cheap solutions found for the date :(")
    days_before = int(input("Enter how many days in advance you could travel: "))
    days_after = int(input("Enter how many days after you could travel: "))
    for days_offset in range(-days_before, days_after):
        date = departure_date + timedelta(days=days_offset)
        print(f"Looking for a solution for {date.date()}...")
        cheap_solutions = find_cheap_solutions(
            arrival_id=arrival_station.id,
            departure_date=date,
            departure_id=departing_station.id,
            max_price=35,
        )
        if cheap_solutions:
            _display_solutions(cheap_solutions)
        else:
            print("No cheap solutions found for the date :(")


if __name__ == "__main__":
    main()
