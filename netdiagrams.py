import streamlit as st
import openai

# Set up OpenAI API key securely
openai.api_key = st.secrets["openai_key"]

def create_network_diagram(devices, connections):
    prompt = "Generate a network diagram that includes the following devices and connections:\n"
    for device in devices:
        prompt += f"- {device['type']} named {device['name']}\n"
    prompt += "Connections:\n"
    for conn in connections:
        prompt += f"- {conn['from']} to {conn['to']} using port {conn['port']} over {conn['protocol']} with {conn['encryption']} encryption\n"
    prompt += "The diagram should reflect network engineering standards. Output the diagram as a JSON object."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON diagrams and are a network engineer responsible for creating diagrams and documentation software and systems."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Failed to generate diagram: {str(e)}"

# Streamlit interface
st.set_page_config(page_title="NetDiagram Engineering Diagrams", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Network Diagram Generator 🤖")

# ... (rest of the Streamlit interface code remains unchanged)

if st.button('Generate Network Diagram'):
    if devices and connections:
        result = create_network_diagram(devices, connections)
        st.text("Here is your network diagram JSON:")
        st.json(result)
    else:
        st.warning("Please add devices and connections to generate the diagram.")