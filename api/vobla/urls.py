from vobla.handlers import users, drops
from vobla.handlers import open_api2
from vobla.utils import api_spec


url_patterns = [
    [r"/open_api2.json$", open_api2.OpenAPI2],
    [r"/users/signup$", users.SignupHandler],
    [r"/users/login$", users.LoginHandler],
    [r"/users/jwtcheck$", users.JWTCheckHandler],
    [r"/drops/$", drops.UserDropsHandler],
    [r"/drops/(?P<drop_hash>[a-zA-Z0-9]{16})$", drops.DropHandler],
    [r"/drops/upload$", drops.DropsUploadHandler],
    [r"/drops/f/(?P<drop_file_hash>[a-zA-Z0-9]{16})$", drops.DropFilesHandler],
    [r"/drops/f/(?P<drop_file_hash>[a-zA-Z0-9]{16})/content$", drops.DropFilesContentHandler]
]

for ind, _ in enumerate(url_patterns):
    url_patterns[ind][0] = r"/api" + url_patterns[ind][0]
    if getattr(url_patterns[ind][1], 'api_spec_exists', False):
        api_spec.add_path(urlspec=url_patterns[ind])

