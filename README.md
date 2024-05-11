# techcrunch-scraper

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Contributors](#contributors)
- [License](#license)

## Introduction
`techcrunch-scraper` is a Django-based application designed to scrape and store articles from TechCrunch based on specific keywords.<!-- or categories --> It integrates Celery for task scheduling and Redis as a message broker, supporting asynchronous task processing.

## Installation
This project is containerized with Docker, ensuring a straightforward setup. Follow these steps to get started:

### Prerequisites
- Docker
- Docker Compose

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/CodeSymphonyy/techcrunch-scraper.git
   cd techcrunch-scraper
   ```

2. Build and run the containers:
   ```bash
   docker-compose up --build
   ```

3. Create a superuser account for Django admin:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```
   Follow the prompts to set the username, email, and password.

## Usage
Once the application is running, access the Django admin interface by navigating to [http://localhost:8000](http://localhost:8000). Use the superuser credentials you created to log in.

### Scrape TechCrunch
- Go to the Keywords section and click on 'SCRAPE NEW KEYWORDS'. Enter a search term and start the scraping task.

### Download Results
- After scraping, download links for the articles (by category or keyword) can be accessed on Articles linked in the admin dashboard.
There are two important actions for articles:
  - **Export articles by categories**
  - **Export articles by keyword**

### Monitoring Celery Tasks with Flower
- To monitor tasks, access the Flower dashboard by navigating to [http://localhost:5555](http://localhost:5555). Flower provides a real-time view of the task queue, ongoing tasks, and task history.

## Features
- **Keyword-based scraping**: Scrape articles by specific keywords.
<!-- - **Category-based scraping**: Automatically scrape articles by category at scheduled times. -->
- **Data export**: Export scraped data in CSV and JSON formats, zipped for convenience.
- **Admin interface customization**: Custom Django admin actions and pages for better management.

## Dependencies
This project is built using:
- Django 4.2
- Celery
- Redis
- Docker and Docker Compose

See `requirements.txt` for a complete list of Python package dependencies.

## Configuration
Configuration is managed via Django's settings module and environment variables. Key settings include:
- `DEBUG` mode
- Database configuration
- Celery configuration

Adjust settings in `local_settings.py` and `.env` files as needed.

### Setting Up Configuration Files

1. **Local Settings**:
   - A sample configuration file `sample_settings.py` is provided as a template.
   - Copy `sample_settings.py` to `local_settings.py` and modify it according to your local environment.
   - This file should not be committed to version control as it contains settings specific to your environment.

2. **Environment Variables**:
   - A sample environment file `.env.sample` is provided.
   - Copy `.env.sample` to `.env` and adjust the variables to suit your deployment needs.
   - The `.env` file will contain sensitive information such as database configurations and secret keys, hence it should also not be committed to your version control system.

## Documentation
Additional documentation detailing API endpoints, modules, and tasks is available under the `docs/` directory (if applicable).

## Troubleshooting
- **Celery tasks not running**: Ensure the Redis service is running and reachable.
- **Static files not found**: Run `python manage.py collectstatic` to collect static files into the static directory.

## License

This software is proprietary and protected under copyright laws. CodeSymphonyy retains all rights to the software, and it is available for use under the following conditions:

- The software may be used on up to three devices owned by the user.
- The user is not permitted to modify, distribute, or sublicense the software.
- This license does not grant any rights to the source code or to make derivative works.

For the full license terms, please refer to the License Agreement included with the software or contact CodeSymphonyy for more details.
