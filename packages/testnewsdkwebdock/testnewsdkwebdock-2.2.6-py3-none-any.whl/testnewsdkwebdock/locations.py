from __future__ import annotations

from typing import List, TypedDict

from src.testnewsdkwebdock import req
from .req  import RequestOptions

class Location(TypedDict):
    id: str
    name: str
    city: str
    country: str
    description: str
    icon: str


class ListLocationsType(TypedDict):
    body: List[Location]


class Locations:
    def __init__(self, parent: "Webdock") -> None:
        self.parent = parent

    def list(self):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint="/locations",
                method="GET",
            ),
            ListLocationsType
        )


