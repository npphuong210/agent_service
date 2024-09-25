import grpc
from concurrent import futures

# Import generated gRPC modules
# from pb.Agent_pb2_grpc import add_AgentServicer_to_server
# from pb.AgentTool_pb2_grpc import add_AgentToolServicer_to_server
# from pb.Conversation_pb2_grpc import add_ConversationServicer_to_server
# from pb.ExternalKownledge_pb2_grpc import add_ExternalKnowledgeServicer_to_server
# from pb.InternalKownledge_pb2_grpc import add_InternalKnowledgeServicer_to_server
# from pb.LlmModel_pb2_grpc import add_LlmModelServicer_to_server
from core_app.grpc.pb.SystemPrompt_pb2_grpc import add_SystemPromptControllerServicer_to_server
# from pb.User_pb2_grpc import add_UserServicer_to_server
# from pb.UUID_pb2_grpc import add_UUIDServicer_to_server

# Import your service implementations
from .grpc_handlers import (
    SystemPromptControllerServicer
)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Register services
    # add_AgentServicer_to_server(AgentServicerImplementation(), server)
    # add_AgentToolServicer_to_server(AgentToolServicerImplementation(), server)
    # add_ConversationServicer_to_server(ConversationServicerImplementation(), server)
    # add_ExternalKnowledgeServicer_to_server(ExternalKnowledgeServicerImplementation(), server)
    # add_InternalKnowledgeServicer_to_server(InternalKnowledgeServicerImplementation(), server)
    # add_LlmModelServicer_to_server(LlmModelServicerImplementation(), server)
    add_SystemPromptControllerServicer_to_server(SystemPromptControllerServicer(), server)
    # add_UserServicer_to_server(UserServicerImplementation(), server)
    # add_UUIDServicer_to_server(UUIDServicerImplementation(), server)
    
    # Start the server
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
