from configparser import ConfigParser

def create_config(user_id):
    config = ConfigParser()
    config.add_section('creadentials')
    config.set('creadentials', 'user_id', str(user_id))
    with open('config.ini', 'w') as f:
        config.write(f)

def get_config():
    config = ConfigParser()
    config.read('config.ini')
    return config