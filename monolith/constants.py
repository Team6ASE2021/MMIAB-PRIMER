import os

"""
just some constants to be used for file uploading, maybe this will store secrets (NOT ON THE PUBLIC REPO)
in the future
"""
_UPLOAD_FOLDER = os.path.join("static", "assets")

_MAX_CONTENT_LENGTH = 16 * 1024 * 1024

_ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png"]
