# Welcome to my file system management project!

This app provides a simple RESTful API that can be used to get more information about the host file system.

 A base directory can be specified when starting up the app. After the the base directory is set, then all paths used to access files and directories should be relative to that directory.

## How to run
The app can be run using the command below in your command line. Be sure to indicate the root directory before running. 

```
docker build --tag file_system_app . && docker run --mount type=bind,source={path to root directory},target=/local --publish 5000:5000 file_system_app
```

## How to access endpoints

The following curl commands can be used to access the endpoints:

```
curl --request GET \
  --url http://localhost:5000/directories/{path_to_dir}/files
```

```
curl --request GET \
  --url http://localhost:5000/files/{path_to_file}
```

## How to run tests
```
docker build --tag file_system_app --target test .
```
If you see no failures, then the tests ran successfully. 

## This app provides two endpoints:
### GET /directories/:directory_path/files
This endpoint can be used to get all of the directories/ files within a directory. 
### GET /file/:file_path
This endpoint can be used to get the contents of a given file. 

More detailed specs can be found in the swagger.yaml file in this repo. 

## Assumptions made
1. Directories will not contain more than a couple hundred files or subdirectories. I did not implement pagination on the list endpoint for this reason.
2. The app will not be run outside the dockerized container. I've hardcoded `/local` as the root directory within the app. This assumption breaks as soon as you run the app outside of the container.

## Caveats / Bugs
1. The owners on the files in the response of `/directories/:directory_path/files` endpoint do not accurately reflect the owners on the file system. All owners are `root` because users aren't correctly imported into the container.
2. The naming of the `/directories/:directory_path/files` is a little weird given that it returns both files and directories. Also the schema between a file object in `files/:file_path` and `/directories/:directory_path/files` is inconsistent.
3. I could have much more comprehensive testing on both endpoints. Testing subdirectories, many files returned in the list view, differing permissions and owners.
4. If I had more time, I would have set up a linter to lint my files. I tried my best to keep good style but a linter would catch some ugly style.
5. All the endpoints are stuffed within the `app\__init__.py` file along with the create app logic. Ideally, I would want to separate the instantiation of the app from endpoint logic. This is ok for this project because my app is very small but would quickly grow out of control. 
6. I have no validation that the base directory passed in at runtime is actually a valid directory. This could result in a suboptimal user experience if the user accidentally passes in a directory that does not exist.
7. I have no error handling / testing that files can actually be accessed by the user running the app. There could be a potential security vulnerbility where the user can access files they normally would not have access to (I have not tested this to confirm though).

## Total time spent
I probably spent around 10 hours in total on this assignment. Since I was new to Docker, I spent a solid amount of time (maybe 3-4 hours) debugging issues that came up / learning more about Docker. Even then I wasn't able to get to the bottom of the issue I was experiencing :(. 

I also decided to use Flask for the first time. I'm mostly used to Django but wanted to use Flask because it was lighter weight than a Django app and seemed better suited for this project. As a result, I probably spent much more time looking up documentation and figuring things out than I would have if I had used a framework I was more familiar with. That being said Flask was pretty straightforward to use, and I'm actually glad that I decided to choose it over Django. Plus it gave me the opportunity to learn something new. 