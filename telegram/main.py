import logging
import os
from datetime import datetime, timedelta

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from trenitalia.solutions.api import find_frecciayoung_solutions
from trenitalia.solutions.models import Solution
from trenitalia.stations.api import find_stations
from trenitalia.stations.models import Station

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# States (/start -> write departing station -> pick station -> write arrival station -> pick station -> enter date)
(
    PICK_DEPARTING_STATION,
    FIND_ARRIVAL_STATION,
    PICK_ARRIVAL_STATION,
    ENTER_DATE,
    ENTER_DAYS_BEFORE,
    ENTER_DAYS_AFTER,
    FIND_EXTENDED_SOLUTIONS,
) = range(7)

DEPARTING_STATIONS_ID_BY_NAME_KEY = "departing_stations"
DEPARTING_STATION_KEY = "departing_station"
ARRIVAL_STATIONS_ID_BY_NAME_KEY = "arrival_stations"
ARRIVAL_STATION_KEY = "arrival_station"
DEPARTURE_DATE_KEY = "departure_date"
DAYS_BEFORE_KEY = "days_before"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about the departing station."""
    await update.message.reply_text(
        "CiaoCiaoCiao! Sono FrecciaYoungSignorino e ti aiuterò a trovare i biglietti FrecciaYoung "
        "senza sbatta.\n\nDa che città/stazione vuoi partire?"
    )
    return PICK_DEPARTING_STATION


async def pick_departing_station(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Find the stations and let the user pick one."""
    station_search_text = update.message.text
    stations = find_stations(name=station_search_text)
    if not stations:
        raise ValueError(f"No departing station found for name {station_search_text}")
    reply_keyboard = [[station.display_name] for station in stations]

    # Store stations IDs in user_data
    stations_id_by_name = {station.display_name: station.id for station in stations}
    context.user_data[DEPARTING_STATIONS_ID_BY_NAME_KEY] = stations_id_by_name

    await update.message.reply_text(
        "Scegli la stazione.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Scegli la stazione...",
        ),
    )
    return FIND_ARRIVAL_STATION


async def find_arrival_station(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Save the picked station and ask the user about the arrival station"""
    stations_id_by_name = context.user_data[DEPARTING_STATIONS_ID_BY_NAME_KEY]
    departing_station = update.message.text
    departing_station_id = stations_id_by_name[departing_station]
    # Store departing station id
    context.user_data[DEPARTING_STATION_KEY] = departing_station_id

    await update.message.reply_text(
        "In che stazione/città vuoi arrivare?",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PICK_ARRIVAL_STATION


async def pick_arrival_station(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Find the stations and let the user pick one."""
    station_search_text = update.message.text
    stations = find_stations(name=station_search_text)
    if not stations:
        raise ValueError(f"No arrival station found for name {station_search_text}")
    reply_keyboard = [[station.display_name] for station in stations]

    # Store stations IDs in user_data
    stations_id_by_name = {station.display_name: station.id for station in stations}
    context.user_data[ARRIVAL_STATIONS_ID_BY_NAME_KEY] = stations_id_by_name

    await update.message.reply_text(
        "Scegli la stazione.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Scegli la stazione...",
        ),
    )
    return ENTER_DATE


async def enter_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the picked arrival station and ask for the departure date."""
    stations_id_by_name = context.user_data[ARRIVAL_STATIONS_ID_BY_NAME_KEY]
    arrival_station = update.message.text
    arrival_station_id = stations_id_by_name[arrival_station]
    # Store arrival station id
    context.user_data[ARRIVAL_STATION_KEY] = arrival_station_id

    await update.message.reply_text(
        "Quando vuoi partire? (Inserisci la data in formato yyyy-mm-dd. Esempio: il 7 aprile 2024 sarebbe 2024-04-07)",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ENTER_DAYS_BEFORE


def _build_solutions_message(solutions: list[Solution]) -> str:
    message = ""
    for solution in solutions:
        min_price = min([offer.price for offer in solution.offers])
        message += f"\n{solution.origin} - {solution.destination}, {solution.departure_time.strftime('%Y-%m-%d %H:%M')}-{solution.arrival_time.strftime('%H:%M')} ({solution.duration}): {min_price} €"
    return message


async def enter_days_before(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Check if there is a trip in the specified date otherwise ask for how many days before they would travel."""
    year, month, date = list(map(int, update.message.text.split("-")))
    departure_date = datetime(year, month, date)

    cheap_solutions = find_frecciayoung_solutions(
        arrival_id=context.user_data[ARRIVAL_STATION_KEY],
        departure_date=departure_date,
        departure_id=context.user_data[DEPARTING_STATION_KEY],
    )
    if cheap_solutions:
        await update.message.reply_text(_build_solutions_message(cheap_solutions))
        return ConversationHandler.END

    # Store departure date
    context.user_data[DEPARTURE_DATE_KEY] = str(departure_date.date())
    # Ask for days before
    await update.message.reply_text(
        f"Non ho trovato nessun biglietto per la data {departure_date.date()}. Posso cercare nei giorni intorno alla data desiderata..."
        "Quanti giorni in anticipo potresti partire?",
        reply_markup=ReplyKeyboardMarkup(
            [[str(i)] for i in range(0, 6)],
            one_time_keyboard=True,
            input_field_placeholder="Scegli il numero di giorni...",
        ),
    )
    return ENTER_DAYS_AFTER


async def enter_days_after(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for how many days after they would travel."""
    context.user_data[DAYS_BEFORE_KEY] = int(update.message.text)
    await update.message.reply_text(
        "Quanti giorni dopo potresti partire?",
        reply_markup=ReplyKeyboardMarkup(
            [[str(i)] for i in range(0, 6)],
            one_time_keyboard=True,
            input_field_placeholder="Scegli il numero di giorni...",
        ),
    )
    return FIND_EXTENDED_SOLUTIONS


async def find_extended_solutions(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Find the solutions."""
    year, month, date = list(map(int, context.user_data[DEPARTURE_DATE_KEY].split("-")))
    departure_date = datetime(year, month, date)
    days_before = context.user_data[DAYS_BEFORE_KEY]
    days_after = int(update.message.text)
    departing_station = context.user_data[DEPARTING_STATION_KEY]
    arrival_station = context.user_data[ARRIVAL_STATION_KEY]
    cheap_solutions = []
    for days_offset in range(-days_before, days_after):
        date = departure_date + timedelta(days=days_offset)
        logger.info(f"Looking for a solution for {date.date()}...")
        cheap_solutions += find_frecciayoung_solutions(
            arrival_id=arrival_station,
            departure_date=date,
            departure_id=departing_station,
        )
    message = (
        _build_solutions_message(cheap_solutions)
        if cheap_solutions
        else "Spiacente non ho trovato nessun biglietto frecciayoung :(."
    )
    await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(
        f"Exception while handling an update: {context.error}. User data: {context.user_data}"
    )

    # Send message to user
    await update.message.reply_text(
        "Qualcosa è andato storto... prova ad inserire un altro valore o digita /sbatta per iniziare da capo :(",
        reply_markup=ReplyKeyboardRemove(),
    )


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & ~filters.COMMAND, start),
            CommandHandler("start", start),
        ],
        states={
            PICK_DEPARTING_STATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, pick_departing_station)
            ],
            FIND_ARRIVAL_STATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, find_arrival_station)
            ],
            PICK_ARRIVAL_STATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, pick_arrival_station)
            ],
            ENTER_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_date)],
            ENTER_DAYS_BEFORE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_days_before)
            ],
            ENTER_DAYS_AFTER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_days_after)
            ],
            FIND_EXTENDED_SOLUTIONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, find_extended_solutions)
            ],
        },
        fallbacks=[CommandHandler("sbatta", start)],
    )

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
