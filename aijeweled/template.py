import random

class Node:
    def __init__(self, node_id, node_type):
        self.node_id = node_id
        self.node_type = node_type  # 'input', 'output', 'hidden'
        self.activation = 0.0

class Connection:
    def __init__(self, in_node_id, out_node_id, weight):
        self.in_node_id = in_node_id
        self.out_node_id = out_node_id
        self.weight = weight
        self.enabled = True

class Genome:
    def __init__(self):
        self.nodes = {}  # Dictionary to store nodes
        self.connections = {}  # Dictionary to store connections

    def add_node(self, node_id, node_type):
        self.nodes[node_id] = Node(node_id, node_type)

    def add_connection(self, in_node_id, out_node_id, weight):
        self.connections[(in_node_id, out_node_id)] = Connection(in_node_id, out_node_id, weight)

    def activate(self, inputs):
        # Reset node activations
        for node in self.nodes.values():
            node.activation = 0.0

        # Set input node activations
        for i, input_value in enumerate(inputs):
            self.nodes[i].activation = input_value

        # Propagate activations through connections
        for connection in self.connections.values():
            if connection.enabled:
                self.nodes[connection.out_node_id].activation += \
                    self.nodes[connection.in_node_id].activation * connection.weight

        # Return activations of output nodes
        outputs = []
        for node_id, node in self.nodes.items():
            if node.node_type == 'output':
                outputs.append(node.activation)
        return outputs

    def print_genome(self):
        print("Nodes:")
        for node in self.nodes.values():
            print(f"Node {node.node_id}: Type={node.node_type}, Activation={node.activation}")
        print("Connections:")
        for conn in self.connections.values():
            print(f"Connection from {conn.in_node_id} to {conn.out_node_id}, Weight={conn.weight}, Enabled={conn.enabled}")

# Example usage
if __name__ == "__main__":
    # Create a sample genome
    genome = Genome()
    genome.add_node(0, 'input')
    genome.add_node(1, 'input')
    genome.add_node(2, 'output')
    genome.add_connection(0, 2, random.uniform(-1.0, 1.0))  # Random weight
    genome.add_connection(1, 2, random.uniform(-1.0, 1.0))  # Random weight

    # Print the genome structure
    genome.print_genome()

    # Example input
    input_data = [1.0,0.5]

    # Activate the genome with the input data
    outputs = genome.activate(input_data)

    # Print the output activations
    print("Output activations:", outputs)
