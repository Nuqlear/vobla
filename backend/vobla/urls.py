from vobla.handlers import users, drops, sharex, open_api2, mimetypes
from vobla.utils import api_spec


api_url_patterns = [
    [r"/open_api2.json$", open_api2.OpenAPI2],
    [r"/users/signup$", users.SignupHandler],
    [r"/users/login$", users.LoginHandler],
    [r"/users/jwtcheck$", users.JWTCheckHandler],
    [r"/drops$", drops.UserDropsHandler],
    [r"/drops/(?P<drop_hash>[a-zA-Z0-9]{16})$", drops.DropHandler],
    [r"/drops/(?P<drop_hash>[a-zA-Z0-9]{16})/preview$", drops.DropPreviewHandler],
    [r"/drops/files/(?P<drop_file_hash>[a-zA-Z0-9]{16})$", drops.DropFileHandler],
    [r"/drops/upload/chunks$", drops.DropUploadChunksHandler],
    [r"/drops/upload/blob$", drops.DropUploadBlobHandler],
    [
        r"/drops/files/(?P<drop_file_hash>[a-zA-Z0-9]{16})/content$",
        drops.DropFileContentHandler,
    ],
    [r"/sharex$", sharex.SharexUploader],
    [r"/mimetypes/(?P<mimetype>[a-zA-Z0-9/_-]+)$", mimetypes.MimetypePreview],
]


url_patterns = api_url_patterns + [
    [
        r"/f/(?P<drop_file_hash>[a-zA-Z0-9]{16})$",
        type("ShortDropFileContentHandler", (drops.DropFileContentHandler,), {}),
    ],
    [
        r"/d/(?P<drop_hash>[a-zA-Z0-9]{16})/preview$",
        type("ShortDropPreviewHandler", (drops.DropPreviewHandler,), {}),
    ],
]


for ind, pattern in enumerate(url_patterns):
    if pattern in api_url_patterns:
        url_patterns[ind][0] = r"/api" + url_patterns[ind][0]
    if getattr(pattern[1], "api_spec_exists", False):
        api_spec.add_path(urlspec=pattern)
