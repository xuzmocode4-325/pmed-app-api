# Medical Equipment Sales Admin API 

## Dockerfile Specs:
*   `FROM python:3.13-alpine3.21` -  This instruction sets the base image for the Docker image to `python:3.13-alpine3.21`. This image is a lightweight Linux distribution based on Alpine Linux, with Python 3.13 pre-installed.
*   `LABEL maintainer="xuzmonomi.com"` - This adds metadata to the image, indicating that "xuzmonomi.com" is the maintainer of this image.
*   `ENV PYTHONBUFFERED=1` - This sets an environment variable `PYTHONBUFFERED` to `1`.  This ensures that the Python output is not buffered, which is useful for seeing logs in real-time.
*   `COPY ./requirements.txt /tmp/requirments.txt` - This instruction copies the `requirements.txt` file from the current directory (`./`) on the host to the `/tmp/requirments.txt` directory in the Docker image. This file likely contains a list of Python dependencies for the application.
*   `COPY ./requirements.dev.txt /tmp/requirements.dev.txt` - This copies the `requirements.dev.txt` file from the local directory to the `/tmp` directory in the Docker image. This file likely contains development-related Python dependencies.
*   `COPY ./app /app`[5] - This copies the entire `./app` directory from the host machine to the `/app` directory within the Docker image. This directory likely contains the application's source code.
*   `WORKDIR /app` - This sets the working directory for any subsequent `RUN`, `CMD`, `ENTRYPOINT`, `COPY`, and `ADD` instructions to `/app`. This means that commands will be executed from within this directory.
*   `EXPOSE 8000` - This exposes port 8000 on the container, making it accessible from the outside. However, it doesn't publish the port, which requires using the `-p` flag when running the container.
*   `ARG DEV=false` -  This defines a build-time argument named `DEV` and sets its default value to `false`. This argument can be used to conditionally execute commands during the image build process.
*   `RUN python -m venv /py && \ /py/bin/pip install --upgrade pip && \ apk add --update --no-cache postgresql-client && \ apk add --update --no-cache --virtual .tmp-build-deps \ build-base postgresql-dev musl-dev && \ /py/bin/pip install -r /tmp/requirments.txt && \ if [ $DEV = "true" ]; \ then /py/bin/pip install -r /tmp/requirements.dev.txt ; \ fi && \ rm -rf /tmp && \ apk del .tmp-build-deps && \ adduser \ --disabled-password \ --no-create-home \ app-user` - This `RUN` instruction executes a series of commands:
    *   `python -m venv /py` - Creates a Python virtual environment in the `/py` directory.
    *   `/py/bin/pip install --upgrade pip` -  Upgrades `pip` to the latest version within the virtual environment.
    *   `apk add --update --no-cache postgresql-client` - Installs the `postgresql-client` package using Alpine's package manager (`apk`). The `--no-cache` flag prevents caching the package, reducing the image size.
    *   `apk add --update --no-cache --virtual .tmp-build-deps build-base postgresql-dev musl-dev` - Installs build dependencies required for compiling Python packages with native extensions. The `--virtual .tmp-build-deps` creates a temporary installation environment named `.tmp-build-deps`.
    *   `/py/bin/pip install -r /tmp/requirments.txt` - Installs Python dependencies from the `requirements.txt` file within the virtual environment.
    *   `if [ $DEV = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt ; fi` - Conditionally installs development dependencies from `requirements.dev.txt` if the `DEV` argument is set to `"true"`.
    *   `rm -rf /tmp` - Removes the `/tmp` directory to clean up temporary files and reduce the image size.
    *   `apk del .tmp-build-deps` - Removes the temporary build dependencies installed earlier.
    *   `adduser --disabled-password --no-create-home app-user` - Adds a new user named `app-user` with a disabled password and without creating a home directory.
*   `ENV PATH="/py/bin:$PATH"` - This sets the `PATH` environment variable to include the virtual environment's binary directory (`/py/bin`), ensuring that the Python interpreter and other tools installed in the virtual environment are accessible.
*   `USER app-user` -  This specifies that the container should run as the `app-user` user, which improves security by preventing the application from running as the root user.


## Docker Compose Configs
A `docker-compose.yml` file is used to define and manage multi-container Docker applications. It allows you to configure application services using YAML rules. Here's an explanation of the provided `docker-compose.yml` file:

*   **`services`**: This section defines the different containers (services) that make up the application[1].

    *   **`app`**: This service represents the main application container.
        *   **`build`**: Specifies how to build the image for this service.
            *   **`context: .`**: Sets the build context to the current directory, meaning the Dockerfile (if used) and other necessary files are located here.
            *   **`args`**: Defines build-time arguments.
                *   `- DEV=true`: Sets the `DEV` argument to `true` during the build process. This is used to conditionally execute commands in the Dockerfile, to install development dependencies or configure the application for development mode.
        *   **`ports`**: Exposes port 8000 on the container to port 8000 on the host machine, making the application accessible from outside the Docker network.
            *   `- "8000:8000"`
        *   **`volumes`**: Defines volume mappings between the host and the container.
            *   `- "./app:/app"`: Mounts the `./app` directory on the host to the `/app` directory in the container. This allows code changes on the host to be reflected inside the container, which is useful for development.
        *   **`command`**: Specifies the command to run when the container starts.
            *   `sh -c "python manage.py wait_for_db && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"`: This command executes a shell script that first waits for the database to be available, then applies any pending database migrations, and finally starts the Django development server on host `0.0.0.0` and port `8000`.
        *   **`environment`**: Sets environment variables for the container.
            *   `- DB_HOST=db`: Sets the database host to `db`. Because Docker Compose uses the service names for automatic DNS resolution, `db` will resolve to the database container's IP address[1].
            *   `- DB_NAME=devdb`: Sets the database name to `devdb`.
            *   `- DB_USER=devuser`: Sets the database user to `devuser`.
            *   `- DB_PASS=changeme`: Sets the database password to `changeme`.
        *   **`depends_on`**: Specifies that this service depends on the `db` service.  Docker Compose will start the `db` service before the `app` service.
            *   `- db`
    *   **`db`**: This service represents the PostgreSQL database container.
        *   **`image`**: Uses the `postgres:17.2-alpine3.21` image from Docker Hub, which is a lightweight version of PostgreSQL.
        *   **`volumes`**: Defines volume mappings for the container.
            *   `- dev-db-data:/var/lib/postgresql/data`: Mounts a named volume `dev-db-data` to the `/var/lib/postgresql/data` directory in the container, which is where PostgreSQL stores its data. This ensures that the database data persists even when the container is stopped or removed.
        *   **`environment`**: Sets environment variables for the container.
            *   `- POSTGRES_DB=devdb`: Sets the database name to `devdb`.
            *   `- POSTGRES_USER=devuser`: Sets the database user to `devuser`.
            *   `- POSTGRES_PASSWORD=changeme`: Sets the database password to `changeme`.
*   **`volumes`**: This section defines the named volumes used by the services.
    *   **`dev-db-data`**: This is a named volume used by the `db` service to persist the database data.  Docker manages the creation and storage of this volume.

In summary, this `docker-compose.yml` file defines a multi-container application consisting of an application service (`app`) and a PostgreSQL database service (`db`). The application is configured to connect to the database using environment variables, and the database data is persisted using a named volume. The `DEV=true` argument suggests that this configuration is intended for a development environment[1][2]. Using `docker-compose up`  will start the application and all of its services.


## Linting
Linting is configured through `flake8`, a Python tool that wraps other tools like `pycodestyle`, `pyflakes`, and `mccabe` to enforce coding style and detect errors. It's used to maintain code quality and consistency in Python projects. The `flake 8` package is installed as a dev requirment in the docker image using pip. The configurations for the `flake8` package are stored in the root of the app directory in the `.flake8` file. The configurations for `flake8` are as follows: 

*   `[flake8]`
    *   This section header indicates that the following options are for the `flake8` tool.
*   `exclude =`
    *   This option specifies a comma-separated list of files or directories that `flake8` should ignore during its analysis. In this case, the following are excluded:
        *   `migrations` - This likely refers to a directory containing database migration files. These files are often auto-generated and may not adhere to the same strict style guidelines as application code.
        *   `__pycache__` - This directory is automatically created by Python to store compiled bytecode files. There's no need to lint these.
        *   `manage.py` - This is a Django management script. While it's Python code, it might have specific formatting needs or conventions that differ from the rest of the project, or it might be automatically generated.
        *   `settings.py` - This is a Django settings file. Similar to `manage.py`, it may have specific formatting needs or automatically generated content that you don't want to strictly lint.

In essence, this configuration tells `flake8` to skip checking the style and potential errors in the `migrations` directory, `__pycache__` directories, and the `manage.py` and `settings.py` files. This is a common practice to avoid unnecessary warnings or errors in generated or configuration-specific files, focusing `flake8`'s analysis on the core application code.


## Testing



## Docker Commands
*   **`docker build .`** - This instruction builds the docker image using the specifications defined in the `Dockerfile`. 

*   **`docker compose run --rm app sh -c "[django-commands]"`** - This command runs the docker image and passes in commands to the shell. 

    *    `docker compose`: runs a docker compose command
    *    `run`: starts a specific containder defined in congig
    *    `--rm`: removes the container
    *    `app`: the name of the service
    *    `sh -c`: passes in a shell command


## User API Features

- Anyone from the public can create a profile
- Only one account per email address
- Password must follow certain rules, can be configured
- Access to a profile requires registration and authentication
- Authenticated users can update profile information
- Users can be created via the admin portal
- Admin / staff profiles can view all other profile details
- Non admin users can apply for a doctor profile
- Doctor profiles can manage their own events
- Doctor profiles require approval by an admin user


## Event API Features

- Allows authenticated and verified doctors to create, edit, update or delete events created on their own profiles
- Allows staff users to create, edit, update and delete events for all profiles
- Denies any and all requests from unauthenticated users, non staff profiles and authenticated but unverified doctors and users

## Procedures API Features





