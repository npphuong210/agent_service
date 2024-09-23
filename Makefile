generateproto:
	python3 manage.py generateproto --model core_app.models.SystemPrompt --file core_app/grpc/proto/SystemPrompt.proto \
 	python3 manage.py generateproto --model core_app.models.LlmModel --file core_app/grpc/proto/LlmModel.proto \
   	python3 manage.py generateproto --model core_app.models.AgentTool --file core_app/grpc/proto/AgentTool.proto \
	python3 manage.py generateproto --model core_app.models.Agent --file core_app/grpc/proto/Agent.proto \
   	python3 manage.py generateproto --model core_app.models.Conversation --file core_app/grpc/proto/Conversation.proto \
   	python3 manage.py generateproto --model core_app.models.ExternalKnowledge --file core_app/grpc/proto/ExternalKownledge.proto \
   	python3 manage.py generateproto --model core_app.models.InternalKnowledge --file core_app/grpc/proto/InternalKownledge.proto \
	python3 manage.py generateproto --model django.contrib.auth.models.User --file core_app/grpc/proto/User.proto \

pythonproto:
	rm -f core_app/grpc/pb/*.py
	python3 -m grpc_tools.protoc --proto_path=core_app/grpc/proto --python_out=core_app/grpc/pb --grpc_python_out=core_app/grpc/pb core_app/grpc/proto/*.proto

.PHONY: generateproto pythonproto