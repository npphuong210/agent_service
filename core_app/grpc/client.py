import grpc
import uuid
from pb import SystemPrompt_pb2
from pb import SystemPrompt_pb2_grpc
from pb import UUID_pb2
from google.protobuf.timestamp_pb2 import Timestamp




def create_system_prompt(stub):
    # Generate a new UUID for the SystemPrompt
    new_prompt_id = str(uuid.uuid4())
    system_prompt = SystemPrompt_pb2.SystemPrompt()
    system_prompt.id.value = new_prompt_id
    system_prompt.prompt_name = "thien122"
    system_prompt.prompt_content = "Thien.2221"
    # system_prompt.created_at = current_time.seconds
    # system_prompt.updated_at = current_time.seconds

    # Create the CreateSystemPromptRequest message
    create_response = SystemPrompt_pb2.CreateSystemPromptRequest(
        systemprompt=system_prompt
    )

    # Call the gRPC method
    response = stub.CreateSystemPrompt(create_response)
    
    print(f"Created SystemPrompt ID: {response.id.value}")
    
def get_systemprompt_prompt_by_id(stub):
    sp = SystemPrompt_pb2.GetSystemPromptRequest()
    print(sp)
    id ="bcb23e1d-cf2b-47d1-812a-6262969b4c60"
    sp.id.value = id
    system_prompt = stub.GetSystemPrompt(sp)
    
    
    a = system_prompt
    
    print(a)
    
    
def get_list_sp(stub):
    a = stub.ListSystemPrompts(SystemPrompt_pb2.ListSystemPromptsRequest())
    
    print(a)
    
def update_sp(stub):
    



def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = SystemPrompt_pb2_grpc.SystemPromptControllerStub(channel)
        #create_system_prompt(stub)
        #get_systemprompt_prompt_by_id(stub)
        get_list_sp(stub)

if __name__ == '__main__':
    run()
