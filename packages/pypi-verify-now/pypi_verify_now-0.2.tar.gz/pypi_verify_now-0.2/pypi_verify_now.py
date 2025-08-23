#!/usr/bin/env python

import http.client
import io
import json
import os
import subprocess
import sys
import tomllib

from pathlib import Path

def parse_config(config_path):
    try:
        with config_path.open('r') as f:
            splitted = (line.split() for line in f)
            return {name: url for (name, url) in splitted}
    except FileNotFoundError:
        return {}

def save_config(config_path, config):
    with config_path.open('w') as f:
        for (name, url) in sorted(config.items()):
            print(f"{name:<49} {url}", file=f)

def run_pip_lock(pip_args):
    proc = subprocess.Popen(['pip', '--isolated', 'lock', '-qq', '-o', '-', *pip_args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r := proc.wait():
        raise Exception(f"pip returned status {r}:\n{proc.stderr.read().decode().strip()}")
    return tomllib.load(proc.stdout)

def verify_attestations(name, url):
    proc = subprocess.Popen(['pypi-attestations', 'verify', 'pypi', '--repository', url, f"pypi:{name}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.wait(), proc.stdout.read().decode().strip()

def pypi_get_repo_url(name, version, filename):
    conn = http.client.HTTPSConnection('pypi.org', 443)
    conn.request('GET', f"/integrity/{name}/{version}/{filename}/provenance")
    if (response := conn.getresponse()).status != 200:
        return None
    match json.load(response)['attestation_bundles'][0]['publisher']:
        case {'kind': 'GitHub', 'repository': R}: return f"https://github.com/{R}"
        case {'kind': 'GitLab', 'repository': R}: return f"https://gitlab.com/{R}"
        case {'kind': K}: raise Exception(f"Unknown publisher {K}")

def main(pip_args, tofu, strict, config_path):
    failed = 0

    # read config from file
    config = parse_config(config_path)

    # make pip generate a lock file for the arguments provided in pip_args
    lock_file = run_pip_lock(pip_args)

    for pkg in lock_file['packages']:

        # check PyPI Integrity API to see if there currently is an attestation
        # FIXME: this will probably break for packages with only sdist
        has_attestation = bool(url := pypi_get_repo_url(pkg['name'], pkg['version'], pkg['wheels'][0]['name']))

        # if TOFU mode, update config according to information from PyPI Integrity API
        if tofu and has_attestation and pkg['name'] not in config:
            config[pkg['name']] = url

        # check if an attestation is expected according to config, if so, verify it
        expect_attestation = pkg['name'] in config
        err, msg = verify_attestations(pkg['wheels'][0]['name'], config.get(pkg['name'], 'https://github.com/j0057/unknown')) \
                   if has_attestation or expect_attestation \
                   else (None, None)

        # interpret results
        match has_attestation or expect_attestation, err, msg:
            case False, _, _:
                print(f"UNKNOWN: {pkg['name']}")
                failed += int(strict)
            case True,  0, M:
                print(f"OK: {pkg['name']}")
            case True,  E, M:
                print(f"FAIL: {pkg['name']} ({M})")
                failed += 1

    # update config on disk
    if tofu:
        save_config(config_path, config)

    return failed

if __name__ == '__main__':
    settings = {
        'tofu': os.environ.get('TOFU', '0') == '1',
        'strict': os.environ.get('STRICT', '0') == '1',
        'config_path': Path(os.environ.get('FILENAME', '.provenance.txt')),
    }
    failed = main(sys.argv[1:], **settings)
    exit_code = (failed + (failed & 0xff == 0x00 if failed >> 8 else 0)) & 0xff
    sys.exit(exit_code)
