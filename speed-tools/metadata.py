from importlib.metadata import version, metadata

PACKAGE = 'speed-tools'
VERSION = version(PACKAGE)
_meta = metadata(PACKAGE)
DESCRIPTION = _meta['summary']
REPOSITORY = _meta['project-url'].split(' ')[1]
