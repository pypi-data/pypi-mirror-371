from __future__ import annotations

from typing import List, Literal, TypedDict

from webdock.utils import RequestOptions, req
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from webdock import Webdock

class CreateScriptBodyType(TypedDict):
    name: str
    filename: str
    content: str


class CreateScriptResponseType(TypedDict):
    body: Script

class ResponseHeaders(TypedDict):
    x_callback_id: str


class Script(TypedDict):
    id: int
    name: str
    path: str
    lastRun: str | None
    lastRunCallbackId: str | None
    created: str

class GetScriptResponse(TypedDict):
    body: Script

class CreateScriptOnServerResponse(TypedDict):
    headers: ResponseHeaders
    body: Script

class DeleteScriptOnServerResponse(TypedDict):
    headers: ResponseHeaders

class ExecuteScriptOnServerResponse(TypedDict):
    headers: ResponseHeaders
 


class ListScriptsOnServerResponseType(TypedDict):
    body: List[Script]


class ListScriptsResponseType(TypedDict):
    body: List[dict]

class UpdateAccountScriptResponseType(TypedDict):
    body: Script

class Scripts:
    def __init__(self, parent: "Webdock") -> None:
        self.parent = parent

    def createAccountScript(self, *, name: str, filename: str, content: str):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint="/account/scripts",
                method="POST",
                body={"content": content, "filename": filename, "name": name},
            ),
            CreateScriptResponseType
        )

    def deployAccountScriptOnServer(
        self,
        *,
        scriptId: int,
        path: str,
        makeScriptExecutable: bool,
        executeImmediately: bool,
        serverSlug: str,
    ):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint=f"/servers/{serverSlug}/scripts",
                method="POST",
                body={
                    "scriptId": scriptId,
                    "path": path,
                    "makeScriptExecutable": makeScriptExecutable,
                    "executeImmediately": executeImmediately,
                },
                headers=["X-Callback-ID"],
            ),
            CreateScriptOnServerResponse
        )

    def deleteAccountScript(self, *, id: int):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint=f"/account/scripts/{id}",
                method="DELETE",
            ),
            None
        )

    def deleteScriptFromServer(self, *, serverSlug: str, scriptId: int):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint=f"/servers/{serverSlug}/scripts/{scriptId}",
                method="DELETE",
                headers=["X-Callback-ID"],
            ),
            DeleteScriptOnServerResponse
        )

    def executeOnServer(self, *, serverSlug: str, scriptID: int):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint=f"/servers/{serverSlug}/scripts/{scriptID}/execute",
                method="POST",
                headers=["X-Callback-ID"],
            ),
            ExecuteScriptOnServerResponse
        )

    def getAccountScriptById(self, *, scriptId: int):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint=f"/account/scripts/{scriptId}",
                method="GET",
            ),
            GetScriptResponse
        )

    def listAccountScripts(self):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint="/account/scripts",
                method="GET",
            ),
            ListScriptsResponseType
        )

    def listServerScripts(self, *, serverSlug: str):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint=f"/servers/{serverSlug}/scripts",
                method="GET",
            ),
            ListScriptsOnServerResponseType
        )


    def updateAccountScript(self, *, id: int, name: str, filename: str, content: str):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint=f"/account/scripts/{id}",
                method="PATCH",
                body={"name": name, "filename": filename, "content": content},
            ),
            UpdateAccountScriptResponseType
        )


