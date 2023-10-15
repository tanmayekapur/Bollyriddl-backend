# Guessing Game Backend

**Description:** Backend Of Guessing Game with django rest framework

## Table of Contents

<!-- 1. [Features](#features)
2. [Requirements](#requirements) -->

1. [Installation](#installation)
    <!-- 4. [Configuration](#configuration) -->
    <!-- 5. [Usage](#usage) -->
    <!-- 6. [API Documentation](#api-documentation) (if applicable) -->
    <!-- 7. [Contributing](#contributing) -->
    <!-- 8. [License](#license) -->

<!-- ## Features -->

<!-- -   List the key features of your Django app.
-   Use bullet points to make the features easily scannable.
-   Mention any special functionalities or integrations. -->

<!-- ## Requirements -->

<!-- -   List the prerequisites and dependencies for running your Django app.
-   Include information about Python version, Django version, and any other packages or tools required. -->

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/tuffle-org/guessing-game-backend
    ```

2. Navigate to the project directory:

    ```bash
    cd your-django-app
    ```

3. Create a virtual environment (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4. Install project dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Perform database migrations:

    ```bash
    python manage.py migrate
    ```

6. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```
7. Start the development server:
    ```bash
    python manage.py runserver
    ```
8. Open your web browser and access the app at http://localhost:8000/.
