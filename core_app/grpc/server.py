from concurrent import futures
import grpc
from pb import SystemPrompt_pb2
from pb import SystemPrompt_pb2_grpc
import uuid
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

import sys
import os

# Add the root directory of your project to the Python path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# In-memory database for SystemPrompts
system_prompts_db = {}

class SystemPromptControllerServicer(SystemPrompt_pb2_grpc.SystemPromptControllerServicer):
    def CreateSystemPrompt(self, request, context):
        
        
        print(request)
        
        
        
        print('\n-----------------------\n')
        print(request.systemprompt.id.value)
        # # Generate a new UUID for the SystemPrompt
        # new_id = uuid.uuid4()
        # current_time = Timestamp()
        # current_time.GetCurrentTime()

        # # Create a new SystemPrompt
        # system_prompt = SystemPrompt_pb2.SystemPrompt(
        #     id=new_id,
        #     created_at=current_time,
        #     updated_at=current_time,
        #     prompt_name=request.systemprompt.prompt_name,
        #     prompt_content=request.systemprompt.prompt_content,
        # )

        # # Save it to the in-memory database
        # system_prompts_db[str(new_id)] = system_prompt

        # return SystemPrompt_pb2.CreateSystemPromptResponse(id=SystemPrompt_pb2.UUID(value=str(new_id)))

    # def GetSystemPrompt(self, request, context):
    #     system_prompt_id = request.id.value
    #     if system_prompt_id in system_prompts_db:
    #         return SystemPrompt_pb2.GetSystemPromptResponse(systemprompt=system_prompts_db[system_prompt_id])
    #     else:
    #         context.set_code(grpc.StatusCode.NOT_FOUND)
    #         context.set_details('SystemPrompt not found')
    #         return SystemPrompt_pb2.GetSystemPromptResponse()

    # def ListSystemPrompts(self, request, context):
    #     return SystemPrompt_pb2.ListSystemPromptsResponse(systemprompts=list(system_prompts_db.values()))

    # def UpdateSystemPrompt(self, request, context):
    #     system_prompt_id = request.systemprompt.id.value
    #     if system_prompt_id in system_prompts_db:
    #         # Update the system prompt
    #         current_time = Timestamp()
    #         current_time.GetCurrentTime()

    #         updated_system_prompt = SystemPrompt_pb2.SystemPrompt(
    #             id=request.systemprompt.id,
    #             created_at=system_prompts_db[system_prompt_id].created_at,
    #             updated_at=current_time,
    #             prompt_name=request.systemprompt.prompt_name,
    #             prompt_content=request.systemprompt.prompt_content,
    #         )

    #         # Save updated system prompt
    #         system_prompts_db[system_prompt_id] = updated_system_prompt

    #         return SystemPrompt_pb2.UpdateSystemPromptResponse()
    #     else:
    #         context.set_code(grpc.StatusCode.NOT_FOUND)
    #         context.set_details('SystemPrompt not found')
    #         return SystemPrompt_pb2.UpdateSystemPromptResponse()

    # def DeleteSystemPrompt(self, request, context):
    #     system_prompt_id = request.id.value
    #     if system_prompt_id in system_prompts_db:
    #         del system_prompts_db[system_prompt_id]
    #         return SystemPrompt_pb2.DeleteSystemPromptResponse()
    #     else:
    #         context.set_code(grpc.StatusCode.NOT_FOUND)
    #         context.set_details('SystemPrompt not found')
    #         return SystemPrompt_pb2.DeleteSystemPromptResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    SystemPrompt_pb2_grpc.add_SystemPromptControllerServicer_to_server(SystemPromptControllerServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC server running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
