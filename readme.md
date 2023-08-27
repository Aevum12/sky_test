# Test Project

This project is designed to complete a test assignment.

## Description

This project is a web application for code quality checking written in Python using the pylint library. Users can upload
Python files (*.py) and receive code quality assessment results. Upon completion of the assessment, users are notified
via email.

## Requirements

To run the application, Docker needs to be installed.

## Installation

1. Clone the repository: `git clone https://github.com/Aevum12/sky_test.git`
2. Configure the email server in the `config.py` file under the `# mail server` section.
3. Set up the schedule for code checking in the `app.__init__.py` file using `CELERYBEAT_SCHEDULE`. By default, code
   checking runs every 10 seconds.
4. To start the project, execute the command `docker-compose up --build -d`.

## Usage

1. Open the application in your browser at `http://localhost:5001`.
2. Register a user using the `Register` button.
3. Upload a *.py file in the user account.
4. Wait for the code to be checked. The result will be displayed in the same user account.

