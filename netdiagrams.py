import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import io

# Initialize session state variables
if 'network_devices' not in st.session_state:
    st.session_state.network_devices = []

if 'network_connections' not in st.session_state:
    st.session_state.network_connections = []

if 'network_boundaries' not in st.session_state:
    st.session_state.network_boundaries = []

# Define device icons
DEVICE_ICONS = {
    "VM": "💻",
    "Server": "🖥️",
    "Workstation": "🖱️",
    "Network Device": "🌐",
    "Cloud Service": "☁️"
}

def create_network_diagram(network_devices, network_connections, network_boundaries):
    G = nx.Graph()

    # Add nodes (devices)
    for device in network_devices:
        G.add_node(device['name'], device_type=device['type'])

    # Add edges (connections)
    for conn in network_connections:
        G.add_edge(conn['from'], conn['to'], port=conn['port'], protocol=conn['protocol'])

    # Create a layout for our nodes 
    pos = nx.spring_layout(G)

    fig, ax = plt.subplots(figsize=(15, 10))

    # Draw the graph
    nx.draw(G, pos, with_labels=False, node_color='lightblue', node_size=3000)

    # Add node labels with icons
    for node, (x, y) in pos.items():
        device_type = G.nodes[node]['device_type']
        icon = DEVICE_ICONS.get(device_type, "❓")
        plt.text(x, y, f"{icon} {node}", fontsize=8, ha='center', va='center')

    # Add edge labels
    edge_labels = nx.get_edge_attributes(G, 'port')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Draw boundaries
    num_boundaries = len(network_boundaries)
    boundary_width = 1.0 / (num_boundaries + 1)
    for i, boundary in enumerate(network_boundaries):
        x_start = (i + 1) * boundary_width
        plt.axvline(x=x_start, ymin=0.05, ymax=0.95, color='r', linestyle='--')
        plt.text(x_start, 0.98, boundary['name'], fontsize=12, color='r', ha='center', va='top', rotation=90)

    plt.title("Infrastructure Diagram", fontsize=16)
    plt.axis('off')
    return fig

def move_item(list_name, index, direction):
    item_list = st.session_state[list_name]
    if direction == "up" and index > 0:
        item_list[index], item_list[index-1] = item_list[index-1], item_list[index]
    elif direction == "down" and index < len(item_list) - 1:
        item_list[index], item_list[index+1] = item_list[index+1], item_list[index]

st.set_page_config(page_title="Infrastructure Diagram Generator", layout="wide", initial_sidebar_state="auto", menu_items=None)

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stApp { max-width: 1200px; margin: 0 auto; }
    .stButton>button { background-color: #0066cc; color: white; }
    .stTextInput>div>div>input, .stSelectbox>div>div>select { background-color: white; }
    h1, h2, h3 { color: #333; }
    .stAlert { background-color: #e6f2ff; color: #0066cc; border: 1px solid #0066cc; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

st.title("Infrastructure Diagram Generator 📊")

# Reorder the columns for the forms
col1, col2, col3 = st.columns(3)

# Add boundary form (now first)
with col1:
    st.subheader("1. Add Boundary")
    with st.form(key='add_boundary_form'):
        boundary_name = st.text_input("Boundary Name")
        if st.form_submit_button("Add Boundary"):
            st.session_state.network_boundaries.append({"name": boundary_name})
            st.success(f"Added boundary {boundary_name}")

# Add device form (now second)
with col2:
    st.subheader("2. Add Device")
    with st.form(key='add_device_form'):
        device_type = st.selectbox("Device Type", list(DEVICE_ICONS.keys()))
        device_name = st.text_input("Device Name")
        boundary = st.selectbox("Boundary", [""] + [b['name'] for b in st.session_state.network_boundaries])
        if st.form_submit_button("Add Device"):
            st.session_state.network_devices.append({"type": device_type, "name": device_name, "boundary": boundary})
            st.success(f"Added {device_type} named {device_name}")

# Add connection form (now third)
with col3:
    st.subheader("3. Add Connection")
    with st.form(key='add_connection_form'):
        from_device = st.selectbox("From Device", [d['name'] for d in st.session_state.network_devices])
        to_device = st.selectbox("To Device", [d['name'] for d in st.session_state.network_devices])
        port = st.text_input("Port")
        protocol = st.selectbox("Protocol", ["TCP", "UDP", "HTTPS", "Custom"])
        if st.form_submit_button("Add Connection"):
            st.session_state.network_connections.append({
                "from": from_device,
                "to": to_device,
                "port": port,
                "protocol": protocol
            })
            st.success(f"Added connection from {from_device} to {to_device}")

# Display current boundaries, devices, and connections with reordering functionality
st.subheader("Current Infrastructure Items")
for item_type, items in [
    ("network_boundaries", st.session_state.network_boundaries),
    ("network_devices", st.session_state.network_devices),
    ("network_connections", st.session_state.network_connections)
]:
    st.write(f"**{item_type.replace('_', ' ').title()}:**")
    for i, item in enumerate(items):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            if item_type == "network_boundaries":
                st.text(f"{item['name']}")
            elif item_type == "network_devices":
                st.text(f"{DEVICE_ICONS[item['type']]} {item['type']} - {item['name']}")
            else:
                st.text(f"{item['from']} to {item['to']}")
        with col2:
            if st.button("↑", key=f"{item_type}_up_{i}"):
                move_item(item_type, i, "up")
                st.experimental_rerun()
        with col3:
            if st.button("↓", key=f"{item_type}_down_{i}"):
                move_item(item_type, i, "down")
                st.experimental_rerun()

# Generate diagram button
if st.button('Generate Infrastructure Diagram', key='generate_button'):
    if st.session_state.network_devices and st.session_state.network_connections:
        fig = create_network_diagram(st.session_state.network_devices, st.session_state.network_connections, st.session_state.network_boundaries)
        
        # Display the diagram
        st.pyplot(fig)
        
        # Create PDF for download
        pdf_buffer = io.BytesIO()
        fig.savefig(pdf_buffer, format='pdf', bbox_inches='tight')
        pdf_buffer.seek(0)
        
        # Add download button for PDF export
        st.download_button(
            label="Download Infrastructure Diagram (PDF)",
            data=pdf_buffer,
            file_name="infrastructure_diagram.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Please add devices and connections to generate the diagram.")