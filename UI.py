import streamlit as st
import requests


def get_agent():
    response = requests.get("http://127.0.0.1:8000/agent")
    agent_name = []
    for agent in response.json():
        agent_name.append(agent['agent_name'])
        
    return agent_name


# Define the Streamlit pages
def home():
    st.title("Welcome to the Chatbot")

def create_agent():
    st.title("Create Agent")
    
    agent_name = st.text_input("Agent Name")
    llm = st.selectbox("LLM", ["GPT3.5", "LLAMA3", "Gemini"])
    prompt = st.selectbox("Select Prompt", ["Prompt 1", "Prompt 2"])  # Add actual prompts
    tools = st.multiselect("Select Tools", ["Tool 1", "Tool 2"])  # Add actual tools
    
    if st.button("Create Agent"):
        agent_data = {
            "agent_name": agent_name,
            "llm": llm,
            "prompt": prompt,
            "tools": tools
        }
        response = requests.post("http://127.0.0.1:8000/agent", json=agent_data)
        if response.status_code == 201:
            st.success("Agent created successfully!")
        else:
            st.error("Failed to create agent.")

def manage_agents():
    st.title("Manage Agents")
    
    response = requests.get("http://127.0.0.1:8000/agent")
    if response.status_code == 200:
        agents = response.json()
        for agent in agents:
            st.write(agent)
    else:
        st.error("Failed to load agents.")

def chat_window():
    st.title("Chat Window")
    
    agent_id = st.selectbox("Select Agent", ["Agent 1", "Agent 2"])  # Populate dynamically
    user_message = st.text_input("Your Message")
    
    if st.button("Send"):
        chat_data = {
            "agent_id": agent_id,
            "message": user_message
        }
        response = requests.post("http://127.0.0.1:8000/answer", json=chat_data)
        if response.status_code == 200:
            st.write(response.json())
        else:
            st.error("Failed to send message.")

# Map pages to function names
PAGES = {
    "Home": home,
    "Create Agent": create_agent,
    "Manage Agents": manage_agents,
    "Chat Window": chat_window
}

def main():
    st.sidebar.title("ChatGPT 4.0")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))
    page = PAGES[selection]
    page()

if __name__ == "__main__":
    main()
