import os
from pathlib import Path


base_path = Path(os.getcwd()) / "vobla" / "media"
mimetypes = {"text/": "code", "application/octet-stream": "binary"}
default_mimetype = "application/octet-stream"
for key in mimetypes:
    mimetypes[key] = base_path / f"{mimetypes[key]}.png"
default_mimetype = mimetypes.get(default_mimetype)


def get_mimetype_preview(mimetype: str):
    for key in mimetypes:
        if mimetype.startswith(key):
            return mimetypes[key]
    return default_mimetype
