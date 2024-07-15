## Getting Started

To get started with this project, you need to configure your environment variables. Follow the steps below to set up your environment:

### 1. Copy `.env.example` to `.env`

First, you need to create a `.env` file based on the `.env.example` file. This file contains all the necessary environment variables for the project. Run the following command in your terminal:

```sh
# linux
cp .env.example .env
```

```python
# create a python environment
python -m venv venv

# activate
venv/Scripts/activate (windows)
source venv/Scripts/activate (linux)

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

```bash
git clone -b lecture_agent repo
```
