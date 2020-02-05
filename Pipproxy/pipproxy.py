from urllib.parse import quote
from sys import platform
from typing import Optional
from os.path import exists, split
import configparser
import os
import click
import platform
import requests

def generate_proxy_config(protocol='http', host='10.6.100.71', port='3128', user=None, passw=None):

    user_and_pass = ''

    if user:
        user_and_pass = f'{quote(user)}:{quote(passw)}@'


    return f'{protocol}://{user_and_pass}{host}:{port}'


def create_file(path):
    folders, file = split(path)

    if folders:
        os.makedirs(folders, exist_ok=True)
    with open(path, 'w') as f:
        pass

def write_config(path, proxy_config:Optional[str]=None):
    path = os.path.expanduser(path)
    if not exists(path):
        create_file(path)

    config = configparser.ConfigParser()

    config.read(path)

    if 'global' not in config:
        config['global'] = {}

    global_ = config['global']

    if proxy_config:
        global_['proxy'] = proxy_config

    else:
        global_.pop('proxy')

    print(path, config['global']['proxy'])
    config.write(open(path, 'w'))


def check_proxy_config(path, show:bool=True):
    if not exists(path):
        return False

    config = configparser.ConfigParser()

    config.read(path)

    cond = 'global' in config and 'proxy' in config['global']

    if cond and show:
        return config['global']['proxy']

    return cond


@click.group()
def cli1():
    pass


@click.group()
def cli2():
    pass


def get_pip_conf_path():

    if platform.system() == 'Windows':
        drive = os.path.expanduser(os.path.expandvars('%APPDATA%'))
        drive = os.path.splitdrive(drive)[0]
        if os.path.exists(drive+'\\ProgramData'):
            return drive+'\\ProgramData\\pip\\pip.ini'

        return os.path.expanduser(os.path.expandvars(r'%APPDATA%\pip\pip.ini'))

    return os.path.expanduser('~/.pip/pip.conf')


def get_user_pass():
    pass


@cli2.command(help="Elimina la configuración del proxy")
def remove_config():
    path = get_pip_conf_path()
    if not exists(path):
        print("Error: there is not such file")
        return

    config = configparser.ConfigParser()

    config.read(path)

    cond = 'global' in config and 'proxy' in config['global']

    if cond:
        config['global'].pop('proxy')
        print('Deleted proxy config')

    print('There is not proxy config')


@cli1.command(help="Inscribe la configuración del proxy en la configuración de pip")
@click.option('--host', '-h', default='10.6.100.71', help='What is the ip direction of the proxy (default is UH proxy for students)')
@click.option('--port', '-p', default=3128, help='The port used by the proxy default is for squid (the most common)')
@click.option('--no-password', is_flag=True)
def inscribe(host, port, no_password):

    click.secho(f"Using: (http://{host}:{port}) for see more option use --help")

    user = None
    password = None

    if not no_password and click.confirm('¿Necesita usuario y contraseña?:'):
        user = click.prompt('Introduzca su usuario:')
        password = click.prompt('Contraseña:', hide_input=True)

    config = generate_proxy_config(host=host, port=port, user=user, passw=password)

    proxies = {
        "http": config,
        "https": config,
    }
    notwork = False
    confirm = True
    try:
        response = requests.get('https://pypi.org/',proxies=proxies, allow_redirects=True)
        if response.status_code != 200:
            notwork = True
    except requests.exceptions.RequestException as e:
        notwork = True
        print("Error during attemp conectio throw proxy")
        print(e)

    if notwork:
        print("Could not acces to https://pypi.org/ throw the proxy, so posibly don work.")
        confirm = click.confirm('Seguro que desea continuar?')

    if confirm:
        write_config(get_pip_conf_path(), config)


cli = click.CommandCollection(sources=[cli1, cli2])
if __name__ == "__main__":
    cli()