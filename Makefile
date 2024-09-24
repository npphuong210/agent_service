pythonproto:
	rm -f grpc/pb/*.py
	python3 -m grpc_tools.protoc --proto_path=core_app/grpc/proto --python_out=core_app/grpc/pb --grpc_python_out=core_app/grpc/pb grpc/proto/*.proto

.PHONY: pythonproto