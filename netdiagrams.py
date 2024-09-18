import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io

# Initialize session state variables
if 'network_devices' not in st.session_state:
    st.session_state.network_devices = []

if 'network_connections' not in st.session_state:
    st.session_state.network_connections = []

if 'network_boundaries' not in st.session_state:
    st.session_state.network_boundaries = []

# Define device types and corresponding markers
DEVICE_MARKERS = {
    "VM": "o",
    "Server": "s",
    "Workstation": "^",
    "Network Device": "D",
    "Cloud Service": "*",  # Changed from 'cloud' to '*'
    "Firewall": "h",
    "Router": "d"
}

def create_network_diagram(network_devices, network_connections, network_boundaries):
    G = nx.Graph()
    fig, ax = plt.subplots(figsize=(15, 10))

    # Create boundary rectangles
    boundary_rects = {}
    num_boundaries = len(network_boundaries)
    boundary_width = 1.0 / (num_boundaries + 1)
    for i, boundary in enumerate(network_boundaries):
        x_start = i * boundary_width
        rect = patches.Rectangle((x_start, 0.1), boundary_width, 0.8, fill=False, linestyle='--', edgecolor='r')
        ax.add_patch(rect)
        ax.text(x_start + boundary_width/2, 0.95, boundary['name'], ha='center', va='top', fontsize=12, color='r')
        boundary_rects[boundary['name']] = (x_start, 0.1, boundary_width, 0.8)

    # Add all nodes to the graph first
    for device in network_devices:
        G.add_node(device['name'], device_type=device['type'], boundary=device['boundary'])

    # Create a spring layout for all nodes
    initial_pos = nx.spring_layout(G, k=0.5, iterations=50)

    # Now position the nodes
    pos = {}
    for device in network_devices:
        if device['type'] in ['Firewall', 'Router']:
            # Place firewalls and routers on the boundary
            boundary_rect = boundary_rects.get(device['boundary'])
            if boundary_rect:
                x = boundary_rect[0]
                y = 0.5  # Middle of the boundary
            else:
                x, y = initial_pos[device['name']]
        else:
            # Place other devices inside the boundary
            boundary_rect = boundary_rects.get(device['boundary'])
            if boundary_rect:
                x = boundary_rect[0] + boundary_rect[2] * (0.25 + 0.5 * initial_pos[device['name']][0])
                y = boundary_rect[1] + boundary_rect[3] * (0.25 + 0.5 * initial_pos[device['name']][1])
            else:
                x, y = initial_pos[device['name']]
        
        pos[device['name']] = (x, y)

    # Add edges (connections)
    for conn in network_connections:
        G.add_edge(conn['from'], conn['to'], port=conn['port'], protocol=conn['protocol'])

    # Draw the graph with different markers for each device type
    for device_type in DEVICE_MARKERS:
        node_list = [node for node in G.nodes() if G.nodes[node]['device_type'] == device_type]
        nx.draw_networkx_nodes(G, pos, nodelist=node_list, node_color='lightblue', 
                               node_size=3000, node_shape=DEVICE_MARKERS[device_type], ax=ax)

    # Draw edges
    nx.draw_networkx_edges(G, pos, ax=ax)

    # Add node labels
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)

    # Add edge labels
    edge_labels = nx.get_edge_attributes(G, 'port')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

    # Create legend
    legend_elements = [plt.Line2D([0], [0], marker=marker, color='w', label=device_type,
                                  markerfacecolor='lightblue', markersize=10)
                       for device_type, marker in DEVICE_MARKERS.items()]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))

    plt.title("Infrastructure Diagram", fontsize=16)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    return fig

def move_item(list_name, index, direction):
    item_list = st.session_state[list_name]
    if direction == "up" and index > 0:
        item_list[index], item_list[index-1] = item_list[index-1], item_list[index]
    elif direction == "down" and index < len(item_list) - 1:
        item_list[index], item_list[index+1] = item_list[index+1], item_list[index]

def main():
    st.set_page_config(page_title="Infrastructure Diagram Generator", layout="wide", initial_sidebar_state="auto", menu_items=None)

    # Add custom CSS to style the sidebar
    st.markdown("""
        <style>
        .sidebar .sidebar-content {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100vh;
        }
        .sidebar-bottom {
            margin-top: auto;
            padding-bottom: 1rem;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main content
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
            device_type = st.selectbox("Device Type", list(DEVICE_MARKERS.keys()))
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
                    st.text(f"{DEVICE_MARKERS[item['type']]} {item['type']} - {item['name']}")
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

    # Sidebar content
    st.sidebar.header("Infrastructure Diagram Generator")
    
    # Add "Buy Me A Coffee" link to the bottom of the sidebar
    st.sidebar.markdown(
        """
        <div class="sidebar-bottom">
        <p>If you find this tool useful and want to support its development, consider buying me a coffee!</p>
        <a href="https://buymeacoffee.com/skidad75" target="_blank">
        <img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;">
        </a>
        <p>Created with ❤️ by <a href="https://github.com/skidad75" target="_blank">Ryan</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()