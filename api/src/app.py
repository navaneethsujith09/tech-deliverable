from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncIterator, Literal

from fastapi import FastAPI, Form, Query, status
from fastapi.responses import RedirectResponse
from typing_extensions import TypedDict

from services.database import JSONDatabase


class Quote(TypedDict):
    name: str
    message: str
    time: str


database: JSONDatabase[list[Quote]] = JSONDatabase("data/database.json")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Handle database management when running app."""
    if "quotes" not in database:
        print("Adding quotes entry to database")
        database["quotes"] = []

    yield

    database.close()


app = FastAPI(lifespan=lifespan)


@app.post("/quote")
def post_message(name: str = Form(), message: str = Form()) -> RedirectResponse:
    """
    Process a user submitting a new quote.
    You should not modify this function except for the return value.
    """
    now = datetime.now()
    quote = Quote(name=name, message=message, time=now.isoformat(timespec="seconds"))
    database["quotes"].append(quote)

    # You may modify the return value as needed to support other functionality
    return RedirectResponse("/", status.HTTP_303_SEE_OTHER)


# TODO: 
@app.get("/quotes")
def get_quotes(max_age: Literal["week", "month", "year", "all"] = Query("all")) -> list[Quote]:
    """
    Retrieve saved quotes, optionally filtered by age.
    """
    quotes = database["quotes"]

    if max_age == "all":
        return quotes

    now = datetime.now()
    cutoff_by_age = {
        "week": now - timedelta(weeks=1),
        "month": now - timedelta(days=30),
        "year": now - timedelta(days=365),
    }
    cutoff = cutoff_by_age[max_age]

    return [quote for quote in quotes if datetime.fromisoformat(quote["time"]) >= cutoff]
