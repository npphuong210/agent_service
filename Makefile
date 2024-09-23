generate-proto:
	python3 manage.py generateproto --model core_app.models.SystemPrompt --file core_app/grpc/SystemPrompt.proto
 	python3 manage.py generateproto --model core_app.models.LlmModel --file core_app/grpc/LlmModel.proto
   	python3 manage.py generateproto --model core_app.models.AgentTool --file core_app/grpc/AgentTool.proto
   	python3 manage.py generateproto --model core_app.models.Agent --file core_app/grpc/Agent.proto
   	python3 manage.py generateproto --model core_app.models.Conversation --file core_app/grpc/Conversation.proto
   	python3 manage.py generateproto --model core_app.models.ExternalKnowledge --file core_app/grpc/ExternalKownledge.proto
   	python3 manage.py generateproto --model core_app.models.InternalKnowledge --file core_app/grpc/InternalKownledge.proto

python-proto:
	python3 -m grpc_tools.protoc --proto_path=core_app/grpc --python_out=core_app/grpc --grpc_python_out=core_app/grpc core_app/grpc/*.proto

.PHONY: generate-proto python-proto