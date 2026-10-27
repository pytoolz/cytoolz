import typing

VersionInfo = typing.TypedDict(
    "VersionInfo",
    {
        "version": str,
        "full-revisionid": str | None,
        "dirty": bool | None,
        "error": str | None,
        "date": str | None,
    },
)


def get_versions() -> VersionInfo: ...
