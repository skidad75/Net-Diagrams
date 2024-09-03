import streamlit as st
import turtle
import io
from PIL import Image

# Set up OpenAI API key securely
openai.api_key = st.secrets["openai_key"]

def create_network_diagram(devices, connections):
    # Set up the turtle screen
    screen = turtle.Screen()
    screen.setup(800, 600)
    screen.title("Network Diagram")
    
    # Create a turtle object
    t = turtle.Turtle()
    t.speed(0)  # Fastest drawing speed
    
    # Define device positions (you may want to calculate these dynamically)
    positions = {device['name']: (x, y) for x, y, device in zip(range(-300, 301, 150), [0]*len(devices), devices)}
    
    # Draw devices
    for device in devices:
        x, y = positions[device['name']]
        t.penup()
        t.goto(x, y)
        t.pendown()
        
        # Draw a unique icon based on device type (simplified)
        if device['type'].lower() == 'router':
            t.circle(20)
        elif device['type'].lower() == 'switch':
            t.square(40)
        else:
            t.dot(20)
        
        t.penup()
        t.goto(x, y-30)
        t.write(device['name'], align="center")
    
    # Draw connections
    for conn in connections:
        start = positions[conn['from']]
        end = positions[conn['to']]
        t.penup()
        t.goto(start)
        t.pendown()
        t.goto((start[0] + end[0])/2, (start[1] + end[1])/2 + 50)  # Mid-point, raised
        t.goto(end)
        
        # Draw a lightning bolt icon at the midpoint
        mid_x, mid_y = (start[0] + end[0])/2, (start[1] + end[1])/2 + 50
        t.penup()
        t.goto(mid_x, mid_y)
        t.pendown()
        for _ in range(3):  # Simplified lightning bolt
            t.forward(10)
            t.backward(10)
            t.right(60)
    
    # Hide the turtle
    t.hideturtle()
    
    # Save the diagram as an image
    ps = screen.getcanvas().postscript(file="network_diagram.eps")
    img = Image.open("network_diagram.eps")
    img.save("network_diagram.png", "PNG")
    
    # Clean up
    screen.clear()
    screen.bye()
    
    return "network_diagram.png"

# Streamlit interface
st.set_page_config(page_title="NetDiagram Engineering Diagrams", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Network Diagram Generator 🤖")

# Initialize session state for devices and connections
if 'devices' not in st.session_state:
    st.session_state.devices = []
if 'connections' not in st.session_state:
    st.session_state.connections = []

# Add device form
with st.form(key='add_device_form'):
    device_type = st.text_input("Device Type")
    device_name = st.text_input("Device Name")
    if st.form_submit_button("Add Device"):
        st.session_state.devices.append({"type": device_type, "name": device_name})
        st.success(f"Added {device_type} named {device_name}")

# Add connection form
with st.form(key='add_connection_form'):
    from_device = st.selectbox("From Device", [d['name'] for d in st.session_state.devices])
    to_device = st.selectbox("To Device", [d['name'] for d in st.session_state.devices])
    port = st.text_input("Port")
    protocol = st.text_input("Protocol")
    encryption = st.text_input("Encryption")
    if st.form_submit_button("Add Connection"):
        st.session_state.connections.append({
            "from": from_device,
            "to": to_device,
            "port": port,
            "protocol": protocol,
            "encryption": encryption
        })
        st.success(f"Added connection from {from_device} to {to_device}")

# Display current devices and connections
st.subheader("Current Devices")
for device in st.session_state.devices:
    st.write(f"{device['type']} - {device['name']}")

st.subheader("Current Connections")
for conn in st.session_state.connections:
    st.write(f"{conn['from']} to {conn['to']} using port {conn['port']} over {conn['protocol']} with {conn['encryption']} encryption")

# Generate diagram button
if st.button('Generate Network Diagram'):
    if st.session_state.devices and st.session_state.connections:
        diagram_path = create_network_diagram(st.session_state.devices, st.session_state.connections)
        st.image(diagram_path, caption="Generated Network Diagram")
    else:
        st.warning("Please add devices and connections to generate the diagram.")