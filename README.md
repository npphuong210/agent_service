## Getting Started

To get started with this project, you need to configure your environment variables. Follow the steps below to set up your environment:

### 1. Copy `.env.example` to `.env`

First, you need to create a `.env` file based on the `.env.example` file. This file contains all the necessary environment variables for the project. Run the following command in your terminal:

```sh
# linux
cp .env.example .env
```

### 2. Set Up a Python Virtual Environment

Next, create and activate a Python virtual environment to isolate your project dependencies.

```python
# create a python environment
python -m venv venv

# activate
venv/Scripts/activate (windows)
source venv/Scripts/activate (linux)
```

### 3. Install Project Dependencies

With the virtual environment activated, install the necessary dependencies using pip:

```python
# Install dependencies
pip install -r requirements.txt
```

### 4. Configure the Database

Run the following commands to create and apply the database migrations:

```python
# Run database migrations
python manage.py makemigrations
python manage.py migrate
```

### 5. Start the Development Server

Finally, start the development server to run your application:

```python
python manage.py runserver
```

### 6. Create super user

```python
python manage.py createsuperuser
```

## API Endpoints

Here are the API endpoints available in this project:

### Admin Panel

- **Manage Database:** `http://127.0.0.1:8000/admin/`
  - Access the Django admin panel to manage the database and other admin tasks.

### Conversation Management

- **Manage Conversations:** `http://127.0.0.1:8000/conversation/`
  - Endpoint to manage conversations.
  - **Get a Single Conversation:** `http://127.0.0.1:8000/conversation/{id}/`
    - Replace `{id}` with the ID of the specific conversation.
  - **Post a Conversation:**
    - Send a POST request with the following JSON structure:
    ```json
    {
      "prompt_name": "",
      "gpt_model": "",
      "chat_history": "", // Optional
      "metadata": "" // Optional
    }
    ```

### System Prompt Management

- **Manage System Prompts:** `http://127.0.0.1:8000/system-prompt/`
  - Endpoint to manage system prompts.
  - **Get a Single System Prompt:** `http://127.0.0.1:8000/system-prompt/{id}/`
    - Replace `{id}` with the ID of the specific system prompt.
  - **Post a System Prompt:**
    - System prompts must be managed via the admin panel.

### Agent Queries

- **Post Query for Agent Execution:** `http://127.0.0.1:8000/agent`
  - Endpoint to post queries for agent execution.

---

Ensure that your server is running before attempting to access these endpoints
