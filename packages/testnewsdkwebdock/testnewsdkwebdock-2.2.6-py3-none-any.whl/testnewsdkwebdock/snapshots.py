from __future__ import annotations

from typing import List, Literal, TypedDict

from src.testnewsdkwebdock import req
from .req import RequestOptions
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from testnewsdkwebdock import Webdock


class Snapshot(TypedDict):
    id: int
    name: str
    date: str
    type: Literal["daily", "weekly", "monthly"]
    virtualization: Literal["container", "kvm"]
    completed: bool
    deletable: bool

class CallBackHeader(TypedDict):
    x_callback_id: str

class SnapshotsCreateResponseType(TypedDict):
    body: Snapshot
    headers: CallBackHeader


class DeleteSnapShotResponseType(TypedDict):
    body: Snapshot
    headers: CallBackHeader


class ListSnapshotResponseType(TypedDict):
    body: List[Snapshot]


class RestoreSnapShotType(TypedDict):
    body: Snapshot
    headers: CallBackHeader


class Snapshots:
    def __init__(self, parent: "Webdock") -> None:
        self.parent = parent

    def create(self, *, serverSlug: str, name: str):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint=f"/servers/{serverSlug}/snapshots",
                method="POST",
                body={"name": name},
                headers=["X-Callback-ID"],
            ),
            SnapshotsCreateResponseType
        )

    def list(self, *, serverSlug: str):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint=f"/servers/{serverSlug}/snapshots",
                method="GET",
            ),
            ListSnapshotResponseType
        )

    def delete(self, *, serverSlug: str, snapshotId: int):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint=f"/servers/{serverSlug}/snapshots/{snapshotId}",
                method="DELETE",
                headers=["X-Callback-ID"],
            ),
            DeleteSnapShotResponseType
        )

    def restore(self, *, serverSlug: str, snapshotId: int):
        return req(
            RequestOptions(
                token=self.parent.string_token,
                endpoint=f"/servers/{serverSlug}/actions/restore",
                method="POST",
                headers=["X-Callback-ID"],
                body={"snapshotId": snapshotId},
            ),
            RestoreSnapShotType
        )


