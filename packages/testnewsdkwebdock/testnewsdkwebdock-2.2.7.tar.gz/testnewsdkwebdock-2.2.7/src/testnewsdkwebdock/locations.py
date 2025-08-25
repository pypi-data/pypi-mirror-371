from __future__ import annotations

from typing import List, TypedDict
 
from testnewsdkwebdock import req
from testnewsdkwebdock.req  import RequestOptions
 
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from testnewsdkwebdock import Webdock


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


