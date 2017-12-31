from vobla.handlers import users, drops
from vobla.handlers import open_api2
from vobla.utils import api_spec


api_patterns = [
    [r"/open_api2.json$", open_api2.OpenAPI2],
    [r"/users/signup$", users.SignupHandler],
    [r"/users/login$", users.LoginHandler],
    [r"/users/jwtcheck$", users.JWTCheckHandler],
    [r"/drops/$", drops.UserDropsHandler],
    [r"/drops/(?P<drop_hash>[a-zA-Z0-9]{16})$", drops.DropHandler],
    [
        r"/drops/files/(?P<drop_file_hash>[a-zA-Z0-9]{16})$",
        drops.DropFileHandler
    ],
    [r"/drops/upload$", drops.DropUploadHandler]
]


for ind, _ in enumerate(api_patterns):
    api_patterns[ind][0] = r"/api" + api_patterns[ind][0]


url_patterns = api_patterns + [
    [
        r"/f/(?P<drop_file_hash>[a-zA-Z0-9]{16})/$",
        drops.DropFileContentHandler
    ]
]


for pattern in url_patterns:
    if getattr(pattern[1], 'api_spec_exists', False):
        api_spec.add_path(urlspec=pattern)
