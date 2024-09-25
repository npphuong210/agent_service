import grpc
import uuid
from pb import SystemPrompt_pb2
from pb import SystemPrompt_pb2_grpc
from pb import User_pb2
from pb import User_pb2_grpc
from pb import LlmModel_pb2
from pb import LlmModel_pb2_grpc
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
    system_prompt = SystemPrompt_pb2.SystemPrompt(
            id=UUID_pb2.UUID(value="bcb23e1d-cf2b-47d1-812a-6262969b4c60"),
            prompt_name="Updated Prompt",
            prompt_content="This is the updated content."
        )

    request = SystemPrompt_pb2.UpdateSystemPromptRequest(systemprompt=system_prompt)
    stub.UpdateSystemPrompt(request)
    print('ssuc')

def delete_sp(stub):
    id = UUID_pb2.UUID(value = "12ec7c30-a4c0-417a-bc47-1ed98d13e69e")
    a = SystemPrompt_pb2.DeleteSystemPromptRequest(id=id)
    stub.DeleteSystemPrompt(a)
    print('deleted')
    
    
def create_user(stub):
    try:
        # Generate a new UUID for the user

        # Create a new User message
        user1 = User_pb2.User()
        user1.username="username"
        user1.password="password"
        user1.email="em@gg.com"
        

        # Create the CreateUserRequest message
        create_request = User_pb2.CreateUserRequest(
            user=user1
        )

        print(create_request)
        # Call the gRPC method
        response = stub.CreateUser(create_request)

        # Print the created user's UUID from the response
        print(f"Created user ID: {response.id.value}")
    except grpc.RpcError as e:
        # Capture gRPC errors and log
        print(f"gRPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        # Capture any other exceptions and log
        print(f"Error: {str(e)}")
        
def get_user(stub, id):
    u = User_pb2.GetUserRequest()
    u.id.value = id
    system_prompt = stub.GetUser(u)
    
    a = system_prompt
    
    return a
    
    
def get_list_user(stub):
    
    a = stub.ListUsers(User_pb2.ListUsersRequest())
    
    print(a)
    
def update_user(stub):
    u = User_pb2.User(
            id=UUID_pb2.UUID(value="2"),
            username='thien',
            email='thien@gmail.com'
        )

    request = User_pb2.UpdateUserRequest(user=u)
    stub.UpdateUser(request)
    print('ssuc')
    
def delete_user(stub):
    id = UUID_pb2.UUID(value = "2")
    a = User_pb2.DeleteUserRequest(id=id)
    stub.DeleteUser(a)
    print('deleted')
    
    
def create_llm(stub, stube_user):
    llm = LlmModel_pb2.LlmModel()
    id = str(uuid.uuid4())
    # llm.id.value = id
    llm.llm_name="bap1"
    llm.provider="openai"
    llm.model_version="gpt-4o-mini"
    llm.api_key = "dakjdkasldjwadlakj"
    

    llm.user_id.value = "1" 
    print(llm)
    
    create_request = LlmModel_pb2.CreateLlmModelRequest(
        llmmodel=llm
    )
    print(create_request)
    response = stub.CreateLlmModel(create_request)
    print(response)
    
def get_llm(stub):
    u = LlmModel_pb2.GetLlmModelRequest()
    u.id.value = str("50b444b9-20f1-460d-b87b-bebf804fa298")
    system_prompt = stub.GetLlmModel(u)
    
    a = system_prompt
    
    print(a)

def get_list_llm(stub):
    
    a = stub.ListLlmModels(LlmModel_pb2.ListLlmModelsRequest())
    
    print(a)
    
def update_llm(stub):
    u = LlmModel_pb2.LlmModel(
            id=UUID_pb2.UUID(value="50b444b9-20f1-460d-b87b-bebf804fa298"),
            llm_name="bapmodified",
            provider="openai",
            model_version="gpt-4o-mini",
            api_key = "dakjdkasldjwadlakj",
            user_id = UUID_pb2.UUID(value="1")
        )

    request = LlmModel_pb2.UpdateLlmModelRequest(llmmodel=u)
    stub.UpdateLlmModel(request)
    print('ssuc')
    
def delete_llm(stub):
    id = UUID_pb2.UUID(value = "50b444b9-20f1-460d-b87b-bebf804fa298")
    a = LlmModel_pb2.DeleteLlmModelRequest(id=id)
    stub.DeleteLlmModel(a)
    print('deleted')

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        #stub = SystemPrompt_pb2_grpc.SystemPromptControllerStub(channel)
        stub_user = User_pb2_grpc.UserControllerStub(channel)
        stub = LlmModel_pb2_grpc.LlmModelControllerStub(channel)
        
        
        
        #create_system_prompt(stub)
        #get_systemprompt_prompt_by_id(stub)
        #get_list_sp(stub)
        #update_sp(stub)
        #delete_sp(stub)
        #create_user(stub)
        #get_user(stub)      
        #get_list_user(stub)  
        #update_user(stub)
        #delete_user(stub)
        #create_llm(stub, stub_user)
        #get_llm(stub)
        #get_list_llm(stub)
        #update_llm(stub)
        delete_llm(stub)
    


if __name__ == '__main__':
    run()
