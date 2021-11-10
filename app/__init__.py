import os
import pwd
from flask import Flask, abort, jsonify, make_response
from http import HTTPStatus

LOCAL_DIR = '/local'

def create_app(base_dir=LOCAL_DIR):
    app = Flask(__name__)
    app.config.from_object(__name__) 
    app.config.update(dict(
        BASE_DIR=base_dir,
    ))

    @app.route('/directories/<path:directory_path>/files')
    def directories(directory_path):
        """
        Gets the directory path from the url path.

        Returns:
        - a 400 response if path points to a file and not a directory.
        - a 404 response if the directory cannot be found.
        - a 200 response for valid directories.

        Example:
        path: /directories/animals/files
        response body:
        {
            "files": [
                {
                    "file_name": "cat.txt",
                    "owner": "'33152'",
                    "permissions": "'33152'",
                    "size": 100
                },
                {
                    "file_name": "dogs/",
                    "owner": "'33152'",
                    "permissions": "16832",
                    "size": 64
                }
            ]
        }
        """

        full_directory_path = os.path.join(app.config['BASE_DIR'], directory_path)
        if os.path.isfile(full_directory_path):
            return make_response(f'{directory_path} is a file not a directory.', HTTPStatus.BAD_REQUEST)
        if not os.path.isdir(full_directory_path):
            return make_response(f'Directory {directory_path} does not exist.', HTTPStatus.NOT_FOUND)

        files = os.listdir(full_directory_path)
        results = []
        for file_name in files:
            full_file_path = os.path.join(full_directory_path, file_name)
            file_stats = os.stat(full_file_path)
            results.append(
                {
                    'file_name': f'{file_name}/' if os.path.isdir(full_file_path) else file_name,
                    'owner': pwd.getpwuid(file_stats.st_uid).pw_name,
                    'permissions': str(file_stats.st_mode), # Getting the octal representation of file permissions
                    'size': file_stats.st_size,
                })
        return jsonify({'files': results})

    @app.route('/files/<path:file_path>')
    def files(file_path):
        """
        Gets the file path from the url.

        Returns:
        - a 400 response if path points to a directory and not a file.
        - a 404 response if the file cannot be found.
        - a 200 response for valid files.

        Example:
        path: /files/animals/cat.txt
        response body:
        {
            "contents": "I am a cat!"
        }
        """

        full_file_path = os.path.join(app.config['BASE_DIR'], file_path)
        if os.path.isdir(full_file_path):
            return make_response(f'{file_path} is a directory not a file.', HTTPStatus.BAD_REQUEST)
        if not os.path.isfile(full_file_path):
            return make_response(f'File {file_path} does not exist.', HTTPStatus.NOT_FOUND)

        with open(full_file_path, 'r') as f:
            return jsonify({'contents': f.read()})
    return app
