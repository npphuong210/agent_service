# Table of Contents
- [1. Getting Started](#getting-started)
- [2. API Endpoints](#api-endpoints)
- [3. gRPC](#grpc)


## 1. Getting Started

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
python3 -m venv venv

# activate
venv/Scripts/activate (windows)
source venv/Scripts/activate (linux)
```

### 3. Install Project Dependencies

Make sure install PortAudio. Unless You will encounter the error from pip install requirement below

```bash
sudo apt install portaudio19-dev 
```

Make sure install cmake for face recognition.
```bash
sudo apt install cmake
```

Make sure install tessaract-ocr for OCR
```bash
sudo apt-get install tesseract-ocr -y
sudo apt-get install tesseract-ocr-all -y
```

With the virtual environment activated, install the necessary dependencies using pip:

```python
# Install dependencies
pip install -r stable-requirements.txt # this is a freeze requirements which work smoothly dev environment
```

If Makefile is available. (Linux only)

```bash
Make setup # to install all the dependencies above
```

### 4. Configure the Database

Run the following commands to apply the database migrations:

```python
# Apply database migrations
python3 manage.py migrate
```

```bash
# https://github.com/pgvector/pgvector
# make sure add pgvector into postgres.
# if psql installed.
psql -U yourusername -d yourdatabase -c "CREATE EXTENSION vector;"

# if you have some trouble about makemigrations or migrate.
# Do it when you have no idea how to fix the errors. (Not recommended)
psql -U yourusername -d yourdatabase -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
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

### 7. Celery setup
A current task is deleting image that expires after 24 hours.

If you do not have Redis installed, you can install it using the following command:
```bash
sudo apt-get install redis-server
```

To verify that Redis is running properly, you can use the Redis CLI:
```bash
redis-cli ping # You should receive a response of "PONG".
```
Update Environment Variables (.env)
```bash
# Celery broker URL
CELERY_BROKER_URL='redis://localhost:6379/0'
```

In separate terminal windows, start the Celery worker and the Celery Beat scheduler:
```bash
celery -A django_basic worker --loglevel=info
#detach mode
celery -A django_basic worker -l info -f /tmp/celery_worker.log --detach
```
```bash
celery -A django_basic beat --loglevel=info
#detach mode
celery -A django_basic beat -l info -f /tmp/celery_beat.log --detach
```


## API Endpoints

Here are the API endpoints available in this project:

### Admin Panel

- **Manage Database:** `http://127.0.0.1:8000/admin/`
  - Access the Django admin panel to manage the database and other admin tasks.

### System Prompt Management

- **Manage System Prompts:** `http://127.0.0.1:8000/system-prompt/`
  - Endpoint to manage system prompts.
  - **Get a Single System Prompt:** `http://127.0.0.1:8000/system-prompt/{id}/`
    - Replace `{id}` with the ID of the specific system prompt.
  - **Post a System Prompt:**
    - Send a POST request with the following JSON structure:
    ```json
    {
      "prompt_name": "",
      "prompt_content": ""
    }
    ---
    ```

### External Knowledge ( Database )

- ** User Database:** `http://127.0.0.1:8000/admin/core_app/externalknowledge/`
  - Endpoint to User Database.
  - **Post an External Knowledge:**
    - Send a POST request with the following JSON structure:
    ```json
    {
      "subject": "",
      "chapter": "",
      "content": ""
    }
    ```

### Agent tools

- **Mange Agent Tools:** `http://127.0.0.1:8000/admin/core_app/agenttool/`
  - Endpoint to Agent Tools.
  - **Post Agent tools:**
  - Send a POST request with the following JSON structure:
  ```json
  {
    "tool_name": "",
    "args_schema": [
       {}
    ],
    "description": ""
  }
  ```

### Agent

- **Mange Agents:** `http://127.0.0.1:8000/admin/core_app/agent/`
- Endpoint to Agents.
- **Post Agents:**
- Send a POST request with the following JSON structure:

  ```json
  {
    "agent_name": "",
    "llm": "",
    "tools": [
       ""
    ]
  }
  ```

### Conversation Management

- **Manage Conversations:** `http://127.0.0.1:8000/conversation/`
  - Endpoint to manage conversations.
  - **Get a Single Conversation:** `http://127.0.0.1:8000/conversation/{id}/`
    - Replace `{id}` with the ID of the specific conversation.
  - **Post Conversation:**
    - Send a POST request with the following JSON structure:
    ```json
    {
      "agent": "", // id
      "chat_history": []  // [{"", ""}]
    }
    ```

### Answer Mangement

- **Answer**: `http://127.0.0.1:8000/answer/`
  - Endpoint to manage Answer
  - **Post an Answer:** `http://127.0.0.1:8000/answer/`
  - Send a POST request with the following JSON structure:
    ```json
    {
      "conversation_id": "",
      "message": ""
    }
    ```

### Streaming Mangement

- **Streaming**: `http://127.0.0.1:8000/streaming/`
  - Endpoint to manage Streaming
  - **Post a Streaming:** `http://127.0.0.1:8000/streaming/`
  - Send a POST request with the following JSON structure:
    ```json
    {
      "conversation_id": "",
      "message": ""
    }
    ```

## gRPC

### Project Structure

**Proto Files**: `core_app/grpc/proto`
- `ocr_service.proto`
- `stt_service.proto`

**Client File**: `core_app/grpc/client.py`
- A Python client for testing requests to the gRPC server.

**Loggings**: `document_processing.log`
- Check the logs of server.

### How to Run the gRPC Server

To run the gRPC services, execute the following command:

```bash
python3 manage.py run_grpc_server <port> # default: 50051, python3 manage.py run_grpc_server 6443
```

### OCRService gRPC API

**Service**: `OCRSservice`

**Method**: `CreateTextFromFile(FileRequest) returns (FileResponse)`

This method processes an OCR request by accepting a file and returning the processed text.

#### Request: `FileRequest`
- **file_name**: Name of the file being sent (string).
- **file**: File data (in `bytes` format).

#### Response: `FileResponse`
- **message**: Text response notifies error or success message.
- **text**: Text response related to the processed file.

---

### Speech-to-Text Service gRPC API

**Service**: `STTService`

#### Methods:  
1. **`UploadAudio (AudioFileRequest) returns (TranscriptionResponse)`**  
   This method transcribes a complete audio file into text.

   ##### Request: `AudioFileRequest`
   - **file_data**: Full audio file in binary (`bytes`) format.

   ##### Response: `TranscriptionResponse`
   - **transcription**: Text transcription of the uploaded audio.

2. **`StreamAudio (stream AudioChunkRequest) returns (stream TranscriptionStreamingResponse)`**  
   This method streams audio chunks in real time and provides live transcription.

   ##### Request: `AudioChunkRequest`
   - **chunk_data**: A chunk of audio in binary (`bytes`) format.

   ##### Response: `TranscriptionStreamingResponse`
   - **transcription**: Text transcription of the streamed audio chunk.

---

## Configuration Guide

### 1. Add Trusted Origins for CSRF Protection
To allow your Django application to accept requests from specific domains, update the `settings.py` file:

```python
# settings.py
CSRF_TRUSTED_ORIGINS = ['https://your-domain.com']  # Add your trusted domain(s) here
```

### 2. Running Django on a Custom Port
By default, Django runs on port 8000. To run the Django development server on a different port, use the following command:
```bash
python manage.py runserver <port>
```

For example, to run the server on port 7000:
```bash
python manage.py runserver 7000
```
### 3.Adjusting the gRPC Server Port
To change the gRPC server's port, modify the add_insecure_port method in core_app/grpc/grpc_server.py:

```python
# core_app/grpc/grpc_server.py
server.add_insecure_port('0.0.0.0:<port>')  # Replace <port> with your desired port number
```
For example, to change the gRPC server to port 60051:

```python
server.add_insecure_port('0.0.0.0:60051')
```

### Flow

Add sysprompt -> Agent tool -> Agent -> Conversation.

Ensure that your server is running before attempting to access these endpoints

version: '3.11'

## Overview:
1. Bash Script (script.sh):

- This script loads environment variables, checks for Docker containers, handles building, starting containers, running migrations, and creating a Django superuser.

2. Dockerfile:

- Builds a Python environment using a slim image, installs dependencies, converts .env and .sh files to Unix format, and sets up Django.

3. Docker Compose (docker-compose.yml):

- Defines services for PostgreSQL (db), initializes the database (db-init), and runs the Django web application (web).

## Recommendations:
- Environment Variables Loading: 

The bash script correctly loads environment variables from the .env file. It checks if the required variables `(DB_NAME, DB_USERNAME, DB_PASSWORD)` are set before proceeding.

- Container Handling: 

The script checks if the container llm-service-web-1 exists and manages its state appropriately (stopping, rebuilding, or starting as needed).

- Database Migrations & Superuser Creation:

Superuser Creation Check: Make sure the variable superuser_exists is defined and properly checks for the existence of a superuser before attempting to create one.To check it run this below command in your Command Prompt

```
docker-compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='admin').exists())" | grep -q 'True' && echo "Superuser exists." || echo "Superuser does not exist."

```

## Running the Project
### Prerequisites
- Docker
- Docker Compose
### Running `script.sh`
On Linux
1. Give execute permissions (if needed):
``` 
chmod +x script.sh
```
2. Run the script:
```
./script.sh
```
On Windows
1. Using Git Bash:
- Open Git Bash.
- Navigate to the directory containing `script.sh`.
```
cd path/to/your/script
```
- Run the script 
```
./script.sh
```
2. Using Windows Subsystem for Linux (WSL):
- Open your WSL terminal (e.g., Ubuntu).
- Navigate to the directory containing `script.sh`.
```
cd /mnt/c/path/to/your/script
```
- Run the script
```
./script.sh
```

## Prompt instructions:

## 1. Cấu Trúc Content

System prompt bao gồm ba phần chính: Ngữ Cảnh, Chức Năng, và Mô Tả Chi Tiết.

### Ngữ Cảnh (Context)

Ngữ cảnh cung cấp bối cảnh tổng quát về mục tiêu và phạm vi của chatbot. Bạn cần mô tả vai trò của chatbot và những gì người dùng có thể mong đợi.

- Ví dụ:

`Bạn là một trợ lý học tập ảo, giúp người dùng tìm kiếm và cung cấp tài liệu học tập từ cơ sở dữ liệu dựa trên embedding của môn học và chương tương ứng.`

### Chức Năng (Functionality)

Chức năng mô tả các hành động chính mà chatbot có thể thực hiện. Bao gồm các công cụ mà chatbot có thể sử dụng.

- Ví dụ:

```
Chức năng của bạn bao gồm:
- Nhận yêu cầu tìm kiếm tài liệu từ người dùng.
- Kiểm tra và xác nhận thông tin về môn học và chương.
- Tìm kiếm thông tin liên quan trong cơ sở dữ liệu.
- Trả lời người dùng với các tài liệu chính xác.
```

### Mô Tả Chi Tiết (Detailed Description)

Mô tả chi tiết cung cấp hướng dẫn cụ thể về cách chatbot xử lý các yêu cầu từ người dùng. Nó nên bao gồm các bước chi tiết để đảm bảo chatbot hoạt động đúng và hiệu quả.

- Ví dụ:

```
1. Nhận yêu cầu từ người dùng:
   - Xác minh rằng yêu cầu có đủ thông tin về môn học và chương.
   - Nếu thiếu thông tin, yêu cầu người dùng cung cấp đầy đủ chi tiết.

2. Xử lý yêu cầu:
   - Truy vấn embedding của môn học và chương từ cơ sở dữ liệu.
   - Sử dụng embedding để tìm kiếm tài liệu tương ứng trong cơ sở dữ liệu.

3. Trả lời người dùng:
   - Cung cấp tài liệu phù hợp với yêu cầu của người dùng.
   - Đảm bảo tài liệu chính xác và đáp ứng đúng nhu cầu.
```

## 2. Hướng Dẫn Khi Kết Hợp Với Tool

Khi sử dụng các công cụ, phần mô tả chi tiết cần bao gồm cách sử dụng các công cụ này trong quá trình xử lý yêu cầu.

- Ví dụ:

Với tool embedding

```
Khi sử dụng embedding tool:
- Lấy embedding của môn học và chương từ cơ sở dữ liệu bằng cách sử dụng lệnh `get_embedding(subject, chapter)`.
- Truy vấn cơ sở dữ liệu bằng cách sử dụng embedding đã lấy để tìm tài liệu phù hợp với lệnh `query_database(embedding)`.

Ví dụ chi tiết:
1.Nhận yêu cầu từ người dùng:
   - "Môn học": Toán
   - "Chương": Đại số

2. Xử lý yêu cầu:
   - Lấy embedding của môn học và chương bằng lệnh: `embedding = get_embedding("Toán", "Đại số")`
   - Truy vấn cơ sở dữ liệu với embedding đã lấy: `documents = query_database(embedding)`

3. Trả lời người dùng:
   - Cung cấp danh sách tài liệu liên quan: `Here are the documents related to Đại số in Toán: [Document List]`
```

Với tool wikipedia

```
Khi sử dụng tool `query_from_wikipedia`:
- Truy vấn Wikipedia với chủ đề cụ thể bằng cách sử dụng lệnh `query_from_wikipedia(topic)`.

Ví dụ chi tiết:
1. Nhận yêu cầu từ người dùng:
   - "Môn học": Lịch sử
   - "Chủ đề": Chiến tranh thế giới thứ hai

2. Xử lý yêu cầu:
   - Sử dụng lệnh `query_from_wikipedia("Chiến tranh thế giới thứ hai")` để truy vấn thông tin trên Wikipedia.

3. Trả lời người dùng:
   - Cung cấp thông tin liên quan đến chủ đề Chiến tranh thế giới thứ hai: `Here is the information related to Chiến tranh thế giới thứ hai: [Extracted Information]` - huynn2
```
