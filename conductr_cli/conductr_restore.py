import json
import os
import shutil
import tempfile
from pathlib import Path

import io

import logging

from conductr_cli import control_protocol, bundle_utils, validation, conduct_load
from conductr_cli.bundle_core_info import BundleCoreInfo


@validation.handle_connection_error
@validation.handle_http_error
@validation.handle_wait_timeout_error
def restore(args):
    log = logging.getLogger(__name__)
    restore_directory = unpack_backup(args.backup)
    bundles_json = Path(os.path.join(restore_directory, 'bundles.json')).read_text()
    bundles_info = BundleCoreInfo.from_bundles(json.loads(bundles_json))
    load_errors = []
    for bundle_info in bundles_info:
        # noinspection PyBroadException
        try:
            bundle_id = process_bundle(args, restore_directory, bundle_info)
            log.info('Restored {} with bundleId : {} \n'.format(bundle_info.bundle_name, bundle_id))
        except:
            load_errors.append('{} could not be restored.'.format(bundle_info.bundle_name))

    for error in load_errors:
        log.error(error)


def unpack_backup(backup):
    restore_directory = tempfile.mkdtemp()
    shutil.unpack_archive(backup, restore_directory)
    return restore_directory


def process_bundle(args, restore_directory, bundle_info: BundleCoreInfo):
    log = logging.getLogger(__name__)
    log.info('Restoring bundle {}'.format(bundle_info.bundle_name))

    files = []

    bundle = '{}.zip'.format(bundle_info.bundle_name_with_digest)
    bundle_path = os.path.join(restore_directory, bundle)

    bundle_conf = bundle_utils.conf(bundle_path)
    files.append(('bundleConf', ('bundle.conf', io.StringIO(bundle_conf))))

    bundle_archive = open(bundle_path, 'rb')

    if len(bundle_info.configuration_digest) != 0:
        configuration = '{}.zip'.format(bundle_info.bundle_name_with_configuration_digest)
        bundle_configuration_path = os.path.join(restore_directory, configuration)

        bundle_conf_overlay = bundle_utils.conf(bundle_configuration_path)
        files.append(('bundleConfOverlay', ('bundle.conf', io.StringIO(bundle_conf_overlay))))

        files.append(('bundle', (bundle, bundle_archive)))

        configuration_archive = open(bundle_configuration_path, 'rb')
        files.append(('configuration', (configuration, configuration_archive)))
    else:
        files.append(('bundle', (bundle, bundle_archive)))

    multipart = conduct_load.create_multipart(log, files)
    response = control_protocol.load_bundle(args, multipart)

    return response['bundleId'] if args.long_ids else bundle_utils.short_id(response['bundleId'])
