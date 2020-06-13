import os
from pathlib import Path
from dotenv import load_dotenv
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


secret_key = os.getenv('SECRET_KEY', 'Optional default value')
gmap_key = os.getenv('GMAP_KEY', 'Optional default value')
other=os.getenv('OTHER', 'Optional default value')
print(secret_key)
print(gmap_key)
print(other)