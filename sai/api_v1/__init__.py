import os
import sai

import ansible.playbook
import ansible.constants as C
import ansible.utils.template

from ansible import errors
from ansible import callbacks
from flask import Blueprint, current_app, request, abort, jsonify
from threading import Thread


bp = Blueprint('sai-api-v1', __name__)


class PlaybookCallbacks(object):
    def on_start(self):
        callbacks.call_callback_module('playbook_on_start')

    def on_notify(self, host, handler):
        callbacks.call_callback_module('playbook_on_notify', host, handler)

    def on_no_hosts_matched(self):
        callbacks.call_callback_module('playbook_on_no_hosts_matched')

    def on_no_hosts_remaining(self):
        callbacks.call_callback_module('playbook_on_no_hosts_remaining')

    def on_task_start(self, name, is_conditional):
        callbacks.call_callback_module('playbook_on_task_start', name,
                                       is_conditional)

    def on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None,
                       confirm=False, salt_size=None, salt=None, default=None):
        callbacks.call_callback_module('playbook_on_vars_prompt', varname,
                                       private=private, prompt=prompt,
                                       encrypt=encrypt, confirm=confirm,
                                       salt_size=salt_size, salt=None,
                                       default=default)

    def on_setup(self):
        callbacks.call_callback_module('playbook_on_setup')

    def on_import_for_host(self, host, imported_file):
        callbacks.call_callback_module('playbook_on_import_for_host', host,
                                       imported_file)

    def on_not_import_for_host(self, host, missing_file):
        callbacks.call_callback_module('playbook_on_not_import_for_host', host,
                                       missing_file)

    def on_play_start(self, pattern):
        callbacks.call_callback_module('playbook_on_play_start', pattern)

    def on_stats(self, stats):
        callbacks.call_callback_module('playbook_on_stats', stats)


class PlaybookRun(Thread):
    def __init__(self, current_app, playbook_cb, pb):
        self.pb = pb
        self.current_app = current_app
        self.playbook_cb = playbook_cb
        Thread.__init__(self)

    def run(self):
        try:
            self.pb.run()
        except errors.AnsibleError as e:
            self.current_app.logger.debug('%s' % e)
        else:
            self.playbook_cb.on_stats(self.pb.stats)


@bp.route('/playbook/<playbook>/run')
def playbook_run(playbook):
    playbooks_path = current_app.config.get('playbooks_path')
    inventory_path = os.path.join(playbooks_path, 'inventory')
    callbacks_path = os.path.join(playbooks_path, 'callback_plugins')

    os.environ.update({
        'SAI_REMOTE_ADDR': request.remote_addr,
        'SAI_HTTP_HOST': request.host,
        'SAI_QUERY_STRING': request.query_string
    })

    try:
        subset = (request.args.get('subset').replace(',',':')
                  .replace(";",":").lstrip('@'))
        subset_split = subset.split(':')
    except AttributeError:
        subset = None
        subset_split = []

    only_tags = str(request.args.get('tags', 'all')).split(',')
    try:
        skip_tags = request.args.get('skip_tags').split(',')
    except AttributeError:
        skip_tags = None

    try:
        inventory = ansible.inventory.Inventory(inventory_path)
    except errors.AnsibleError as e:
        if not os.path.isdir(inventory_path):
            msg = ('The path to the inventory directory '
                   '(%s) does not exist.' % inventory_path)
        else:
            msg = '%s' % e

        current_app.logger.error(msg)
        return (jsonify(playbook=playbook, hosts=[],
                   tags=only_tags, skip_tags=skip_tags,
                   subset=subset_split, state='error',
                   msg='Inventory directory missing or non-parsable inventory '
                       'file'),
                500)
    else:
        inventory.subset(subset)

    if len(inventory.list_hosts()) == 0:
        current_app.logger.error('No hosts matched within the '
                                 'inventory directory (%s).' % inventory_path)
        return (jsonify(playbook=playbook, hosts=inventory.list_hosts(),
                   tags=only_tags, skip_tags=skip_tags,
                   subset=subset_split, state='error',
                   msg='No hosts matched'),
                400)

    files = ['%s%s' % (playbook, ext) for ext in C.YAML_FILENAME_EXTENSIONS]
    for possible_file in files:
        playbook_file = os.path.join(playbooks_path, possible_file)
        if not os.path.isfile(playbook_file):
            playbook_file = None
        else:
            break

    if playbook_file is None:
        current_app.logger.error('Playbook (%s) not found' % playbook)
        return (jsonify(playbook=playbook, hosts=inventory.list_hosts(),
                   tags=only_tags, skip_tags=skip_tags,
                   subset=subset_split, state='error',
                   msg='Playbook not found'),
                404)

    inventory.set_playbook_basedir(playbooks_path)
    stats = callbacks.AggregateStats()
    playbook_cb = PlaybookCallbacks()
    runner_cb = callbacks.DefaultRunnerCallbacks()

    pb = ansible.playbook.PlayBook(
        playbook=playbook_file,
        inventory=inventory,
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        stats=stats,
        only_tags=only_tags,
        skip_tags=skip_tags,
    )

    t = PlaybookRun(sai.app, playbook_cb, pb)
    t.start()

    return (jsonify(playbook=playbook, hosts=inventory.list_hosts(),
                   tags=only_tags, skip_tags=skip_tags,
                   subset=subset_split, state='accepted',
                   msg='accepted'),
            202)
