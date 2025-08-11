import networkx as nx
import matplotlib.pyplot as plt
import yaml

class SystemModeler:
    def __init__(self, directed=False):
        self.graph = nx.DiGraph() if directed else nx.Graph()
        self.directed = directed
        self.extracted_docker_compose = []

    def extract_dockercompose_into_dict(self, docker_compose_file_path):
        with open(docker_compose_file_path, 'r') as file:
            docker_compose_data = yaml.safe_load(file)

        services = docker_compose_data.get('services', {})
        networks = docker_compose_data.get('networks', {})
        volumes = docker_compose_data.get('volumes', {})
        """
        Todo:
        Extracts services, networks, and volumes from a Docker Compose file and returns them as a list of dictionaries.
        The list will look like this:
        [
            ('service_1', {'image': 'image_name', 'ports': ['80:80'], 'environment': {'ENV_VAR': 'value'}, 'depends_on': ['service_2'], 'networks': ['network_1']}),
            ('service_2', {'image': 'another_image', 'ports': ['8080:80'], 'environment': {'ENV_VAR2': 'value2'}, 'depends_on': [], 'networks': ['network_1']}),
            ...
        ]        
        """

        self.extracted_docker_compose = []

    def graph_data_from_dockercompose(self):
        """
        Todo:
        Converts the extracted Docker Compose data into a graph structure.
        use self.graph.add_edges_from(self.edges) to input the edges into the graph based on the extracted data and each of their connections.
        """

    def draw_graph(self, graph, output_path=None):
        """
        TODO: 
        Change the styling of the graph to make it easier to read.
        """
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=16, font_color='black', font_weight='bold', edge_color='gray')
        plt.title("System Graph Model")
        plt.show()
        if output_path:
            plt.savefig(output_path)
            print(f"Graph saved to {output_path}")
        else:
            plt.show()
    
if __name__ == "__main__":    
    modeler = SystemModeler()
    data_dict = modeler.extract_dockercompose_into_dict('docker-compose.yml')   
    # print(data_dict)
