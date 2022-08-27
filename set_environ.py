import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('~/.env')  # adjust as appropriate
print(load_dotenv(project_folder))
