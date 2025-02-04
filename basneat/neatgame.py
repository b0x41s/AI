import random, math
import numpy as np
import pygame
import time
from flappygame import *
import matplotlib.pyplot as plt
import networkx as nx

class Node:
    def __init__(self, id, layer):
        self.id = id        # Unique identifier for the node
        self.layer = layer  # Layer in the network (e.g., input, hidden, output)
        self.value = 0.0    # The value held by the node, initially set to 0.0
        self.input_sum = 0.0  # Sum of inputs before activation
    
    def activate(self):
        # Clip the input sum to avoid overflow in the exp function
        # self.input_sum = np.clip(self.input_sum, -500, 500)
        #self.value = 1.0 / (1.0 + math.exp(-self.input_sum))
        self.value = math.tanh(self.input_sum)

class Connection:
    def __init__(self, from_node, to_node, weight, enabled=True):
        self.from_node = from_node  # The node from which the connection originates
        self.to_node = to_node      # The node to which the connection leads
        self.weight = weight        # The weight of the connection
        self.enabled = enabled      # Whether the connection is enabled or not

class Genome:
    def __init__(self, id):
        self.id = id
        self.nodes = []  # List to store nodes
        self.connections = []  # List to store connections
        self.node_id_counter = 0  # Counter for assigning unique node IDs
        self.connection_innovations = {}  # Dictionary to track unique connections
        self.fitness = 0.0  # Fitness value of the genome
        self.input_nodes = []
        self.output_nodes = []

    def add_node(self, layer):
        node = Node(self.node_id_counter, layer) # Create a new node with a unique ID and specified layer
        self.nodes.append(node) # Add the new node to the nodes list
        self.node_id_counter += 1 # Increment the node ID counter
        if layer == 0:  # Input layer
            self.input_nodes.append(node)
        elif layer == 1:  # Output layer
            self.output_nodes.append(node)
        return node # Return the newly created node 

    def add_connection(self, from_node, to_node, weight):
        key = (from_node.id, to_node.id)  # Create a unique key for the connection
        if key not in self.connection_innovations:
            self.connection_innovations[key] = len(self.connection_innovations) + 1  # Assign a unique innovation number
        innovation_number = self.connection_innovations[key]  # Retrieve the innovation number
        connection = Connection(from_node, to_node, weight)  # Create a new connection with the specified weight
        self.connections.append(connection)  # Add the new connection to the connections list

    def set_inputs(self, inputs):
        if len(inputs) != len(self.input_nodes):
            raise ValueError(f"Number of inputs ({len(inputs)}) does not match number of input nodes ({len(self.input_nodes)})")
        for i, value in enumerate(inputs):
            self.input_nodes[i].value = value

    def propagate(self):
        # Reset input sums for all nodes
        for node in self.nodes:
            node.input_sum = 0.0

        # Sum inputs for each node
        for connection in self.connections:
            if connection.enabled:
                connection.to_node.input_sum += connection.from_node.value * connection.weight

        # Activate nodes (excluding input nodes)
        for node in self.nodes:
            if node.layer != 0:
                node.activate()

    def get_outputs(self):
        return [node.value for node in self.output_nodes]

    def mutate_add_node(self):
        if not self.connections:  # If there are no connections, return immediately
            return
        connection = random.choice(self.connections)  # Select a random connection
        if not connection.enabled:  # If the connection is not enabled, return immediately
            return
        connection.enabled = False  # Disable the selected connection
        new_node = self.add_node((connection.from_node.layer + connection.to_node.layer) / 2)  # Add a new node in between
        self.add_connection(connection.from_node, new_node, 1.0)  # Add a connection from the original start node to the new node
        self.add_connection(new_node, connection.to_node, connection.weight)  # Add a connection from the new node to the original end node

    def mutate_add_connection(self):
        if len(self.nodes) < 2:  # If there are fewer than two nodes, return immediately
            return
        from_node = random.choice(self.nodes)  # Select a random starting node
        to_node = random.choice(self.nodes)  # Select a random ending node
        if from_node.layer == to_node.layer:  # If the nodes are in the same layer, return immediately
            return
        if from_node.layer > to_node.layer:  # Ensure connections go forward in layers
            from_node, to_node = to_node, from_node
        weight = np.random.uniform(-1.0, 1.0)  # Assign a random weight to the connection
        self.add_connection(from_node, to_node, weight)  # Add the new connection

  #  HIEROOO    
 
    # def crossover(self, parent1, parent2, id1, id2):
    #     newid = id1 + id2
    #     child = Genome(newid)

    #     # Inherit nodes from both parents
    #     for node in parent1.nodes:
    #         child.add_node(node.layer)
    #     for node in parent2.nodes:
    #         if not any(n.id == node.id for n in child.nodes):
    #             child.add_node(node.layer)

    #     # Create dictionaries of connections for easy lookup
    #     parent1_innovations = {(conn.from_node.id, conn.to_node.id): conn for conn in parent1.connections}
    #     parent2_innovations = {(conn.from_node.id, conn.to_node.id): conn for conn in parent2.connections}

    #     all_innovations = set(parent1_innovations.keys()).union(parent2_innovations.keys())

    #     for key in all_innovations:
    #         if key in parent1_innovations and key in parent2_innovations:
    #             if random.random() < 0.5:
    #                 selected_conn = parent1_innovations[key]
    #             else:
    #                 selected_conn = parent2_innovations[key]
    #         elif key in parent1_innovations:
    #             selected_conn = parent1_innovations[key]
    #         else:
    #             selected_conn = parent2_innovations[key]

    #         from_node_id, to_node_id = key
    #         from_node = next(node for node in child.nodes if node.id == from_node_id)
    #         to_node = next(node for node in child.nodes if node.id == to_node_id)
    #         child.add_connection(from_node, to_node, selected_conn.weight)

    #     return child

    # def mutate(self):
    #     mutation_rate = 0.2  # Example mutation rate, adjust as needed

    #     # Mutate node values (optional, based on specific implementation needs)
    #     for node in self.nodes:
    #         if random.random() < mutation_rate:
    #             node.value += np.random.uniform(-0.1, 0.1)  # Adjust mutation value range as needed

    #     # Mutate connection weights
    #     for conn in self.connections:
    #         if random.random() < mutation_rate:
    #             conn.weight += np.random.uniform(-0.1, 0.1)  # Adjust mutation value range as needed

    #     # Occasionally add new nodes or connections
    #     if random.random() < mutation_rate:
    #         self.mutate_add_node()

    #     if random.random() < mutation_rate:
    #         self.mutate_add_connection()

    def mutate(self):
        if random.random() < self.node_add_prob:
            self.mutate_add_node()
        if random.random() < self.conn_add_prob:
            self.mutate_add_connection()
        for conn in self.connections:
            if random.random() < self.weight_mutate_rate:
                conn.weight += np.random.uniform(-self.weight_mutate_power, self.weight_mutate_power)
                conn.weight = np.clip(conn.weight, -30, 30)    
    # Additional functions for mutating nodes and connections
    def mutate_add_node(self):
        if not self.connections:
            return
        connection = random.choice(self.connections)
        if not connection.enabled:
            return
        connection.enabled = False
        new_node = self.add_node((connection.from_node.layer + connection.to_node.layer) / 2)
        self.add_connection(connection.from_node, new_node, 1.0)
        self.add_connection(new_node, connection.to_node, connection.weight)

def create_offspring(top_genomes):
    parent1, parent2 = top_genomes
    id1, id2 = top_genomes[0].id, top_genomes[1].id
    child = parent1.crossover(parent1, parent2, id1, id2)
    child.mutate()
    return child

def eval_genomes(genomes):
    """
    Runs the simulation of the current population of birds and sets their fitness based on the distance they reach in the game.
    """
    global WIN, gen  # Use the global variables WIN (game window) and gen (generation count)
    win = WIN  # Assign the game window to the local variable win
    gen += 1  # Increment the generation count

    # Start by creating lists to hold the genome itself, the neural network associated with the genome,
    # and the bird object that uses that network to play
    nets = []  # List to store the neural networks
    birds = []  # List to store the bird objects
    ge = []  # List to store the genome objects
    base = Base(FLOOR)  # Create a Base object for the game floor
    pipes = [Pipe(700)]  # Create a list of pipes with the first pipe at position 700
    score = 0  # Initialize the score to 0

    for genome in genomes:
        genome.fitness = 0  # Start with a fitness level of 0 for each genome
        net = genome  # Using the custom Genome class directly as the neural network
        nets.append(net)  # Add the neural network to the nets list
        birds.append(Bird(230, 350))  # Create a Bird object and add it to the birds list
        ge.append(genome)  # Add the genome to the ge list

    clock = pygame.time.Clock()  # Create a Clock object to control the game's frame rate

    run = True  # Set the run flag to True to start the game loop

    # Time tracking variables
    start_time = pygame.time.get_ticks()
    last_second_time = start_time

    while run and len(birds) > 0:  # Run the game loop as long as run is True and there are birds alive
        clock.tick(30)  # Limit the game to 30 frames per second
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - start_time) / 1000.0  # Convert milliseconds to seconds

        # Add 1 point to score every second
        if current_time - last_second_time >= 1000:
            score += 1
            last_second_time = current_time

        for event in pygame.event.get():  # Check for events in the game
            if event.type == pygame.QUIT:  # If the quit event is triggered
                run = False  # Set run to False to stop the game loop
                pygame.quit()  # Quit the pygame library
                quit()  # Exit the program
                break  # Break out of the event loop

        pipe_ind = 0  # Initialize the pipe index to 0
        if len(birds) > 0:  # If there are birds still alive
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                # If there is more than one pipe and the first bird has passed the first pipe
                pipe_ind = 1  # Set the pipe index to 1 to use the second pipe for neural network input

        for x, bird in enumerate(birds):  # For each bird in the birds list
            ge[x].fitness += 0.1  # Increase the bird's fitness by 0.1 for each frame it stays alive
            bird.move()  # Move the bird

            # Send bird location, top pipe location, and bottom pipe location to the neural network
            net = nets[birds.index(bird)]  # Get the neural network for the current bird
            inputs = (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom))
            # Create the input tuple for the neural network
            net.set_inputs(inputs)  # Set the inputs for the neural network
            net.propagate()  # Propagate the inputs through the neural network
            output = net.get_outputs()  # Get the outputs from the neural network

            if output[0] > 0.5:  # If the output value is greater than 0.5
                bird.jump()  # Make the bird jump

        base.move()  # Move the base

        rem = []  # List to store pipes that need to be removed
        add_pipe = False  # Flag to check if a new pipe needs to be added
        for pipe in pipes:  # For each pipe in the pipes list
            pipe.move()  # Move the pipe
            for bird in birds:  # For each bird in the birds list
                if pipe.collide(bird, win):  # Check for collision between the bird and the pipe
                    ge[birds.index(bird)].fitness -= 1  # Decrease the bird's fitness if it collides with a pipe
                    nets.pop(birds.index(bird))  # Remove the neural network for the collided bird
                    ge.pop(birds.index(bird))  # Remove the genome for the collided bird
                    birds.pop(birds.index(bird))  # Remove the collided bird

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # If the pipe is off the screen to the left
                rem.append(pipe)  # Add the pipe to the rem list

            if not pipe.passed and pipe.x < bird.x:  # If the bird has passed the pipe
                pipe.passed = True  # Set the pipe's passed flag to True
                add_pipe = True  # Set add_pipe to True to add a new pipe

        if add_pipe:  # If a new pipe needs to be added
            score += 1  # Increase the score
            for genome in ge:  # For each genome still in the game
                genome.fitness += 5  # Increase the fitness for passing a pipe
            pipes.append(Pipe(WIN_WIDTH))  # Add a new pipe to the pipes list

        for r in rem:  # For each pipe in the rem list
            pipes.remove(r)  # Remove the pipe from the pipes list

        for bird in birds:  # For each bird in the birds list
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                # If the bird hits the floor or goes too high
                nets.pop(birds.index(bird))  # Remove the neural network for the bird
                #ge.pop(birds.index(bird))  # Remove the genome for the bird
                birds.pop(birds.index(bird))  # Remove the bird from the birds list

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)  # Draw the game window with the updated game state

    # Track the top two genomes by fitness score after the game loop
    if ge:  # Ensure ge is not empty
        top_two_genomes = sorted(ge, key=lambda g: g.fitness, reverse=True)[:2]
        avg_fitness = sum(genome.fitness for genome in ge) / len(ge)
        print(f"Generation {gen}: Avg Fitness = {avg_fitness:.2f}, Top Fitness = {top_two_genomes[0].fitness:.2f}")

        for i, genome in enumerate(top_two_genomes):
            print(f"Top {i+1} Genome: Fitness {genome.fitness} Genome: ID = {genome.id}")
            print(f'''
            {genome.input_nodes[0].value} 0 
                
                                                0 {genome.output_nodes[0].value}

            {genome.input_nodes[1].value} 0     

                                                0 {genome.output_nodes[1].value}

            {genome.input_nodes[2].value} 0     
                ''')
    else:
        print("no more genomes")
        top_two_genomes = []

    return top_two_genomes  # Return the top two genomes if needed elsewhere

def draw_genome(genome):
    G = nx.DiGraph()

    pos = {}
    layer_nodes = {}
    for node in genome.nodes:
        if node.layer not in layer_nodes:
            layer_nodes[node.layer] = []
        layer_nodes[node.layer].append(node.id)

    for layer, nodes in layer_nodes.items():
        for i, node_id in enumerate(nodes):
            pos[node_id] = (layer, i)

    for connection in genome.connections:
        if connection.enabled:
            G.add_edge(connection.from_node.id, connection.to_node.id, weight=connection.weight)

    edge_labels = {(u, v): f'{d["weight"]:.2f}' for u, v, d in G.edges(data=True)}
    nx.draw(G, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=10, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title(f"Genome ID: {genome.id}")
    plt.pause(0.1)

def draw_genome_pygame(genome, screen, width, height):
    screen.fill(WHITE)
    
    layer_distances = {0: 50, 1: width - 50}
    node_radius = 20
    pos = {}

    # Draw input nodes
    input_layer_nodes = sorted(genome.input_nodes, key=lambda n: n.id)
    for i, node in enumerate(input_layer_nodes):
        x = layer_distances[0]
        y = (i + 1) * height / (len(input_layer_nodes) + 1)
        pos[node.id] = (x, y)
        pygame.draw.circle(screen, BLUE, (x, y), node_radius)
        pygame.draw.circle(screen, BLACK, (x, y), node_radius, 1)
        text = pygame.font.Font(None, 24).render(str(node.id), True, BLACK)
        screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

    # Draw output nodes
    output_layer_nodes = sorted(genome.output_nodes, key=lambda n: n.id)
    for i, node in enumerate(output_layer_nodes):
        x = layer_distances[1]
        y = (i + 1) * height / (len(output_layer_nodes) + 1)
        pos[node.id] = (x, y)
        pygame.draw.circle(screen, RED, (x, y), node_radius)
        pygame.draw.circle(screen, BLACK, (x, y), node_radius, 1)
        text = pygame.font.Font(None, 24).render(str(node.id), True, BLACK)
        screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

    # Draw connections
    for connection in genome.connections:
        if connection.enabled:
            from_pos = pos[connection.from_node.id]
            to_pos = pos[connection.to_node.id]
            color = GREEN if connection.weight > 0 else RED
            pygame.draw.line(screen, color, from_pos, to_pos, 2)

    pygame.display.flip()


# Example usage after eval_genomes
if __name__ == "__main__":
    initial_population_size = 50
    population = [Genome(_) for _ in range(initial_population_size)]

    for genome in population:
        for _ in range(3):
            genome.add_node(0)
        for _ in range(2):
            genome.add_node(1)
        genome.add_connection(genome.nodes[0], genome.nodes[3], random.uniform(-1.0, 1.0))
        genome.add_connection(genome.nodes[1], genome.nodes[4], random.uniform(-1.0, 1.0))
        genome.mutate_add_node()
        genome.mutate_add_connection()

    generation = 0
    while True:
        top_two_genomes = eval_genomes(population)


        #draw_genome(population[0])
        if len(top_two_genomes) < 2:
            break
        new_population = [create_offspring(top_two_genomes) for _ in range(initial_population_size)]
        generation += 1

        # Adaptive mutation rate
        for genome in new_population:
            genome.mutate_rate = max(0.1, 0.5 - 0.01 * generation)  # Example adaptation

        population = new_population
