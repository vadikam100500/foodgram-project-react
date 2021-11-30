import os
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(root_dir)

BASE_DIR = Path(__file__).resolve().parent.parent

root_dir_content = os.listdir(BASE_DIR)
PROJECT_DIR_NAME = 'foodgram_project'
if (
        PROJECT_DIR_NAME not in root_dir_content
        or not os.path.isdir(os.path.join(BASE_DIR, PROJECT_DIR_NAME))
):
    assert False, (
        f'В директории `{BASE_DIR}` не найдена '
        f'папка c проектом `{PROJECT_DIR_NAME}`. '
    )

MANAGE_PATH = os.path.join(BASE_DIR)
project_dir_content = os.listdir(MANAGE_PATH)
FILENAME = 'manage.py'
if FILENAME not in project_dir_content:
    assert False, (
        f'В директории `{MANAGE_PATH}` не найден файл `{FILENAME}`. '
    )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

pytest_plugins = [
    'tests.fixtures.fixture_user',
    'tests.fixtures.fixture_data',
]
