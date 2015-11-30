from urllib.request import urlretrieve
from urllib.parse import ParseResult, urlparse, urlunparse
from urllib.error import URLError
from pathlib import Path
import os


def resolve_bundle(cache_dir, uri):
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    try:
        bundle_name, bundle_url = get_url(uri)
        cached_file = cache_path(cache_dir, uri)
        print('Retrieving {}'.format(bundle_url))
        bundle_file, bundle_headers = urlretrieve(bundle_url, cached_file)
        return True, bundle_name, bundle_file
    except URLError:
        return False, None, None


def load_from_cache(cache_dir, uri):
    # When the supplied uri is a local filesystem, don't load from cache so file can be used as is
    parsed = urlparse(uri, scheme='file')
    if parsed.scheme == 'file':
        return False, None, None
    else:
        cached_file = cache_path(cache_dir, uri)
        if os.path.exists(cached_file):
            bundle_name = os.path.basename(cached_file)
            print('Retrieving from cache {}'.format(cached_file))
            return True, bundle_name, cached_file
        else:
            return False, None, None


def get_url(uri):
    parsed = urlparse(uri, scheme='file')
    op = Path(uri)
    np = str(op.cwd() / op if parsed.scheme == 'file' and op.root == '' else parsed.path)
    url = urlunparse(ParseResult(parsed.scheme, parsed.netloc, np, parsed.params, parsed.query, parsed.fragment))
    return url.split('/')[-1], url


def cache_path(cache_dir, uri):
    parsed = urlparse(uri, scheme='file')
    basename = os.path.basename(parsed.path)
    return '{}/{}'.format(cache_dir, basename)