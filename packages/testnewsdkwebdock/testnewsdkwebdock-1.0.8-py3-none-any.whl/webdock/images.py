from __future__ import annotations

from typing import List, Literal, TypedDict

from webdock.utils.req import RequestOptions, req

class ServerImage(TypedDict):
    slug: str
    name: str
    webServer: Literal["Apache", "Nginx", None]
    phpVersion: str | None


class ListImageTypeResponse(TypedDict):
    body: List[ServerImage]


class Images:
    def __init__(self, parent: "Webdock") -> None:
        self.parent = parent

    def list(self):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint="/images",
                headers=[],
                method="GET",
            ),
            ListImageTypeResponse
        )


