pythonproto:
	rm -f grpc/pb/*.py
	python3 -m grpc_tools.protoc --proto_path=core_app/grpc/proto --python_out=core_app/grpc/pb --grpc_python_out=core_app/grpc/pb core_app/grpc/proto/*.proto
runserver:
	python3 manage.py run_grpc_server
setup:
	pip install -r stable-requirements.txt
dj_makemigrations:
	python3 manage.py makemigrations
dj_migrate:
	python3 manage.py migrate

.PHONY: pythonproto runserver setup dj_makemigrations dj_migrate