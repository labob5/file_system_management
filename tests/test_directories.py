import json
import os
import pwd
import tempfile
from http import HTTPStatus
from pathlib import Path

import flask_unittest
from unittest.mock import patch

from weave_grid import create_app

class TestDirectories(flask_unittest.ClientTestCase):
    """
    Test class for testing the /directories/:directory_path/files endpoint.
    """
    app = create_app()
    URL_TEMPLATE = '/directories/{}/files'

    def setUp(self, client):
        self.app.config['BASE_DIR'] = tempfile.gettempdir()

    def test_is_file_not_directory(self, client):
        """
        Tests 400 error is returned when a specified directory is actually a file.
        """
        with tempfile.NamedTemporaryFile() as temp_file:
            file_path = os.path.basename(temp_file.name)
            response = client.get(self.URL_TEMPLATE.format(file_path))

            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(f'{file_path} is a file not a directory.', response.get_data(as_text=True))

    def test_does_not_exist(self, client):
        """
        Tests 404 error is returned when a specified directory does not exist.
        """
        dir_path = 'foo'
        response = client.get(self.URL_TEMPLATE.format(dir_path))

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(f'Directory {dir_path} does not exist.', response.get_data(as_text=True))

    def test_empty_dir(self, client):
        """
        Tests an empty directory with no files.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = os.path.basename(str(Path(temp_dir)))
            response = client.get(self.URL_TEMPLATE.format(dir_path))

            self.assertEqual(response.status_code, HTTPStatus.OK)
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual({'files':[]}, data)

    def test_file_in_dir(self, client):
        """
        Tests payload for a file within the specified directory.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            with tempfile.NamedTemporaryFile(dir=temp_dir) as temp_file:
                file_path = os.path.basename(temp_file.name)
                dir_path = os.path.basename(str(Path(temp_dir)))
                response = client.get(self.URL_TEMPLATE.format(dir_path))

                self.assertEqual(response.status_code, HTTPStatus.OK)
                data = json.loads(response.get_data(as_text=True))
                self.assertCountEqual(data['files'], [
                    {
                        'file_name': file_path,
                        'owner': pwd.getpwuid(os.getuid())[0],
                        'permissions': '33152',
                        'size': 0,
                    }
                ])

    def test_hidden_file_in_dir(self, client):
        """
        Tests that hidden files are returned in the payload.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            with tempfile.NamedTemporaryFile(prefix='.hidden', dir=temp_dir) as temp_file:
                file_path = os.path.basename(temp_file.name)
                dir_path = os.path.basename(str(Path(temp_dir)))
                response = client.get(self.URL_TEMPLATE.format(dir_path))

                self.assertEqual(response.status_code, HTTPStatus.OK)
                data = json.loads(response.get_data(as_text=True))
                self.assertCountEqual(data['files'], [
                    {
                        'file_name': file_path,
                        'owner': pwd.getpwuid(os.getuid())[0],
                        'permissions': '33152',
                        'size': 0,
                    }
                ])

    def test_nested_dir(self, client):
        """
        Tests payload for a directory within the specified directory. 
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            with tempfile.TemporaryDirectory(dir=temp_dir) as nested_temp_dir:
                dir_path = os.path.basename(str(Path(temp_dir)))
                nested_temp_dir = os.path.basename(str(Path(nested_temp_dir)))

                response = client.get(self.URL_TEMPLATE.format(dir_path))
                self.assertEqual(response.status_code, HTTPStatus.OK)
                data = json.loads(response.get_data(as_text=True))
                self.assertCountEqual(data['files'], [
                    {
                        'file_name': f'{nested_temp_dir}/',
                        'owner': pwd.getpwuid(os.getuid())[0],
                        'permissions': '16832',
                        'size': os.path.getsize(temp_dir),
                    }
                ])

if __name__ == "__main__":
    unittest.main()
