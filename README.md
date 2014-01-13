# sai

A simple API utility for invoking Ansible playbooks

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

## Environment variables

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

## Security

This application offers no itself.  Use a web or proxy server in front for username/password protection.

Your playbooks and inventory scripts can also take advantage of the above environment variables to implement security.

## Logging

This application provides no built in logging of actions.  It is recommended that you utilize a callback plugin within ansible for this purpose.

To utilize a callback plugin, create a directory at `~/sai/sai/playbooks/callback_plugins` and place your callback plugins inside of that directory.

Sai will make all of the same callbacks that the `ansible-playbook` command utilizes.
