import json
import os
import tempfile
from http import HTTPStatus
from pathlib import Path

import flask_unittest
from unittest.mock import patch

from app import create_app

class TestFiles(flask_unittest.ClientTestCase):
    """
    Test class for testing the /files/:file_path endpoint.
    """
    app = create_app()
    URL_TEMPLATE = '/files/{}'

    def setUp(self, client):
        self.app.config['BASE_DIR'] = tempfile.gettempdir()

    def test_is_directory_not_file(self, client):
        """
        Tests 400 error is returned when a specified file is actually a directory.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = os.path.basename(str(Path(temp_dir)))
            response = client.get(self.URL_TEMPLATE.format(dir_path))

            self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
            self.assertEqual(f'{dir_path} is a directory not a file.', response.get_data(as_text=True))

    def test_does_not_exist(self, client):
        """
        Tests 404 error is returned when a specified file does not exist.
        """
        file_path = 'foo.txt'
        response = client.get(self.URL_TEMPLATE.format(file_path))

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(f'File {file_path} does not exist.', response.get_data(as_text=True))

    def test_empty_file(self, client):
        """
        Tests an empty file with no contents.
        """
        with tempfile.NamedTemporaryFile() as temp_file:
            file_path = os.path.basename(temp_file.name)
            response = client.get(self.URL_TEMPLATE.format(file_path))

            self.assertEqual(response.status_code, HTTPStatus.OK)
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['contents'], '')

    def test_file_contents(self, client):
        """
        Tests payload for a specified file.
        """
        file_content = 'cat is cool \n blah'
        with tempfile.NamedTemporaryFile() as temp_file:
            # Writing file contents to the temporary file
            with open(temp_file.name, 'w') as f:
                f.write(file_content)

            file_path = os.path.basename(temp_file.name)
            response = client.get(self.URL_TEMPLATE.format(file_path))

            self.assertEqual(response.status_code, HTTPStatus.OK)
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['contents'], file_content)

if __name__ == "__main__":
    unittest.main()
