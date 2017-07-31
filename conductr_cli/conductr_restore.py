import json
import os
import shutil
import tempfile
from pathlib import Path

import io

from requests_toolbelt import MultipartEncoder

from conductr_cli import control_protocol, bundle_utils
from conductr_cli.bundle_core_info import BundleCoreInfo


def restore(args):
    restore_directory = unpack_backup(args.backup)
    bundles_json = Path(os.path.join(restore_directory, 'bundles.json')).read_text()
    bundles_info = BundleCoreInfo.from_bundles(json.loads(bundles_json))
    # for bundle_info in bundles_info:
    #     load_bundle(args, restore_directory, bundle_info)
    bundle_info = bundles_info[0]
    load_bundle(args, restore_directory, bundle_info)


def unpack_backup(backup):
    restore_directory = tempfile.mkdtemp()
    shutil.unpack_archive(backup, restore_directory)
    return restore_directory


def load_bundle(args, restore_directory, bundle_info: BundleCoreInfo):

    bundle_zip_path = os.path.join(restore_directory, '{}.zip'.format(bundle_info.bundle_name_with_digest))
    files = []
    bundle = open(bundle_zip_path, 'rb')
    bundle_conf = bundle_utils.conf(bundle_zip_path)
    files.append(('bundleConf', ('bundle.conf', io.StringIO(bundle_conf))))

    files.append(('bundle', (bundle_info.bundle_name_with_digest, bundle)))

    if len(bundle_info.configuration_digest) != 0:
        bundle_configuration_path = os.path.join(restore_directory,
                                                 '{}.zip'.format(bundle_info.bundle_name_with_configuration_digest))
        bundle_conf_archive = open(bundle_configuration_path, 'rb')
        files.append(('configuration', (bundle_info.bundle_name_with_configuration_digest, bundle_conf_archive)))

    encoder = MultipartEncoder(files)
    response = control_protocol.load_bundle(args, encoder)
    print(response)


