import os
from typing import Optional
from utils.logging import LOG


def sanitize_path(base_path: str, filename: str) -> Optional[str]:
    """
    Path sanitiser for wildcard index serving

    Returns the absolute path of the filename joined to the base_path - but requires that
    that absolute path eventually ends up as a subfolder of the base_path. i.e. prevents "../.." shenanigans
    by the "filename"

    If the file at the sanitized path actually exists - then return the path
    If there is no file - then return None

    See https://stackoverflow.com/questions/13939120/sanitizing-a-file-path-in-python
    """
    # basepath should be absolute. Example: '/home/person/src/public'
    # filename is relative to base. Example: 'image.jpg' or 'subdir1/subdir2/image.jpg'

    try:
        filepath = os.path.join(base_path, filename)
        # at this point filepath can look like '/home/person/src/public/../../usr/secret.txt

        # resolves symbolic links and /../
        real_filepath = os.path.realpath(filepath)
        # then real_filepath will look like '/home/person/secret.txt'

        # now we have resolved the joined path to something concrete - we also double check
        # that the final path is within the original base path
        prefix = os.path.commonpath((base_path, real_filepath))

        if prefix != base_path:
            raise Exception(f"'{filename}' as a path resolved to outside the base of the http server")

        # we only want to serve up real files
        if os.path.isfile(real_filepath):
            return real_filepath

    except Exception as ex:
        # note that there is a code path through here where we *don't* raise an exception and just
        # return None - we want to save the logging here for more exceptional cases
        LOG.error(ex)

    return None
