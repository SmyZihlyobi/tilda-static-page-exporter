# Tilda Static Pages Exporter

This Python script exports static pages from a [Tilda.cc](https://tilda.cc) project using the Tilda API and saves them locally to your server. It also listens to a webhook, so your pages always remain up-to-date. You can use this script to host your website on your own server and synchronize it with the Tilda page builder.

**Note**: Exporting static pages from Tilda using the API requires a Tilda Business account.

## Prerequisites

- Python 3.7+
- A Tilda Business account
- Tilda API keys: public key and secret key

## Installation

### Docker

You can use `docker-compose.yml` to run this service in Docker.

The exported pages will be saved in the `./static` directory inside the project folder (you can change this in `docker-compose.yml` in the `volumes` section)
1. Clone the repository to your server. 

    ```sh
    git clone https://github.com/SmyZihlyobi/tilda-static-page-exporter.git
    ```
1. Copy the `env.example` file to `.env` and fill in the API keys and other parameters.
1. Run the service
    ```sh
    docker compose up -d
    ```
1. The service should become available at `http://your-ip:8000` (if you haven't changed the default port in the .env file). 

It is recommended to use this service behind a reverse-proxy with HTTPS enabled, but it's up to you.

### Manual Setup
First, you need to install the dependencies: `pip install -r requirements.txt`

You can run the project in server mode using uvicorn:
```sh
python3 main.py
```

## Usage

To export static pages from a Tilda.cc project, you need to set up a webhook in your Tilda account that will call the server URL where the script is running. Here's how to do it:

1. Log in to your Tilda account and open the project you want to export.
2. Click the "Export project" button in the top-right corner.
3. In the "Export project" dialog, click the "Add webhook" button.
4. In the "Add webhook" dialog, enter the URL of your server followed by `/webhook` (e.g., `https://your-server.com/webhook`).
5. Click the "Add webhook" button to save the webhook.

Now, every time you publish a page in the project, Tilda will send a `GET` request to your server URL with the `projectid` parameter.

The script will extract the project and its pages, saving images, scripts, and styles to your server and creating HTML files for each page.

## Configuration

All settings are stored in the `.env` file. Here's a description of the available parameters:

```env
# API keys
TILDA_PUBLIC_KEY=""      # Tilda API public key
TILDA_SECRET_KEY=""      # Tilda API secret key
TILDA_PROJECT_ID=""      # Tilda project ID

# Server settings
TILDA_HOST="0.0.0.0"     # Host to bind the server
TILDA_PORT=8000          # Port to bind the server

# File storage paths
TILDA_STATIC_PATH_PREFIX=/static/  # Prefix path for static files
TILDA_HTML_PATH=/static/           # Path for HTML files
TILDA_IMAGES_PATH=/static/images/  # Path for images
TILDA_CSS_PATH=/static/css/        # Path for CSS files
TILDA_JS_PATH=/static/js/          # Path for JavaScript files

# Git settings (optional)
PUSH_TO_GIT=false                 # Enable/disable automatic Git push
GIT_USERNAME=""                   # Git username
GIT_TOKEN=""                      # Git access token
GIT_REMOTE_URL=""                 # Remote repository URL
GIT_CONFIG_NAME="Tilda Exporter"  # Git config username
GIT_CONFIG_EMAIL="tilda-exporter@example.com"  # Git config email
```

## Limitations
1. The script supports only one Tilda project at a time.
2. Automatic Git synchronization is currently disabled (skill issue).
3. A Tilda Business account with API access is required for operation.

# TODO
 - fix auto commit in docker
