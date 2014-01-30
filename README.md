# sai

A simple API utility for invoking Ansible playbooks

This is not meant to be a replacement for Ansible [Tower](http://www.ansible.com/ansible-tower). If you are looking for more advanced and robust functionality, you should look at Tower instead. In fact, you should probably look at Tower regardless of the complexity of your need or requirement for more advanced functionality.

## Installation

These are very simple installation prcedures.  I'd recommend also using nginx, gunicorn, and something like upstart or supervisor.

An ansible playbook is likely to come soonish that can perform the installation.

1. `cd ~`
1. `virtualenv sai`
1. `cd sai`
1. `. bin/activate`
1. `git clone git://github.com/sivel/sai.git`
1. `pip install -r sai/requirements.txt`
1. `python runapp.py`

All ansible playbooks and related files should be placed within the `playbooks` directory at `~/sai/sai/playbooks` and all inventory files and scripts should be placed within the `inventory` directory at `~/sai/sai/playbooks/inventory`.

## Calling the API

The only API endpoint currently is to run a playbook, such as:

`curl http://sai.example.org:5000/api/v1/playbook/example-playbook/run`

In the above example, `example-playbook` is the name of the playbook to run, which will be looked for in the `playbooks` directory with either no extension, `.yml` or `.yaml`

### Sample Response

```json
{
    "hosts": [
        "localhost"
    ],
    "msg": "accepted",
    "playbook": "example-playbook",
    "skip_tags": null,
    "state": "accepted",
    "subset": [],
    "tags": [
        "all"
    ]
}
```

## Environment Variables

Several environment variables are exposed by sai to ansible, and by association, the ansible playbooks and inventory scripts.

```
SAI_REMOTE_ADDR
SAI_HTTP_HOST
SAI_QUERY_STRING
SAI_REQUEST_URI
SAI_PATH_INFO
SAI_REMOTE_USER
SAI_PLAYBOOK
```

In the case of a POST request to the API, you will additionally have a `SAI_POST_KEYS` environment variable, that is a comma separated list of uppercased POST keys.  There will also be environment variables for each key=value of the POST, in the format of `SAI_POST_<KEY>` where `<KEY>` is a value from `SAI_POST_KEYS`.

An example of POST data environment variables may look like:

```
SAI_POST_KEYS="PUB_KEY_DSA,PUB_KEY_RSA,PUB_KEY_ECDSA,INSTANCE_ID,HOSTNAME"
SAI_POST_PUB_KEY_DSA="pubkeydsawouldbehere"
SAI_POST_PUB_KEY_RSA="pubkeyrsawouldbehere"
SAI_POST_PUB_KEY_ECDSA="pubkeyecdsawouldbehere"
SAI_POST_INSTANCE_ID="iid-datasource-none"
SAI_POST_HOSTNAME="serer.example.org"
```

## Security

This application offers no security itself.  Use a web or proxy server in front for username/password protection.

Your playbooks and inventory scripts can also take advantage of the above environment variables to implement security and customization.

## Logging

This application provides no built in logging of actions.  It is recommended that you utilize a callback plugin within ansible for this purpose.

To utilize a callback plugin, create a directory at `~/sai/sai/playbooks/callback_plugins` and place your callback plugins inside of that directory.

Sai will make all of the same callbacks that the `ansible-playbook` command utilizes.
