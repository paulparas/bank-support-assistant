from openai import OpenAI
import configparser
from openai import OpenAI

config = configparser.ConfigParser()
config.read('config.properties')

def get_openai_client():
    api_key = config.get('OpenAI', 'api_key')
    client = OpenAI(api_key=api_key)
    return client