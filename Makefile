pythonproto:
	rm -f grpc/pb/*.py
	python3 -m grpc_tools.protoc --proto_path=core_app/grpc/proto --python_out=core_app/grpc/pb --grpc_python_out=core_app/grpc/pb core_app/grpc/proto/*.proto
grpcrun:
	python3 manage.py run_grpc_server
setup:
	sudo apt install portaudio19-dev
	sudo apt install cmake
	pip install -r stable-requirements.txt
dj_makemigrations:
	python3 manage.py makemigrations
dj_migrate:
	python3 manage.py migrate
dj_run:
	python3 manage.py runserver
create_vector:
	sudo psql -U postgres -d agent_service -c"CREATE VECTOR EXTENSION";
schema_rm:
	sudo su - postgres
	psql -U postgres -d agent_service -c"DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

.PHONY: pythonproto grpcrun setup dj_makemigrations dj_migrate dj_run