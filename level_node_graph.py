from enum import Enum
class NodeType(Enum):
    FLOOR = 1
    STAIRS_UP = 2
    STAIRS_DOWN = 3
    DOOR = 4
    WALL = 5
    ROOF = 6

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.connected_nodes = []
        self.level = 0
        self.node_type = NodeType.FLOOR
        self.wall_dir = [1, 1, 1, 1]
        self.normal = [0,0,0]

    def connect_node(self, node):
        self.connected_nodes.append(node)

    def __repr__(self):
        return f"({self.x}, {self.y})lvl:{self.level} {self.node_type.name}"

    def __str__(self):
        return f"({self.x}, {self.y})lvl:{self.level} {self.node_type.name}"


class NodeGraph:
    def __init__(self):
        self.nodes = []
        self.split_paths_list = []

    def add_node(self,node):
        self.nodes.append(node)

    def find_node(self,x,y):
        for node in self.nodes:
            if node.x == x and node.y == y:
                return node

    def connect_nodes(self):
        directions = [(0,-1),(1,0),(0,1),(-1,0)]
        previous_nodes = []
        for node in self.nodes:
            for direction in directions:
                x = node.x+direction[0]
                y = node.y+direction[1]
                neighbour_node = self.find_node(x,y)

                if neighbour_node and neighbour_node not in previous_nodes:
                    node.connect_node(neighbour_node)
                    #print(f"connected {node} and {neighbour_node}")

            previous_nodes.append(node)

        #Reverse Pass for connecting nodes from right to left TODO: create function instead / better solution
        previous_nodes.clear()
        for node in reversed(self.nodes):
            for direction in directions:
                x = node.x + direction[0]
                y = node.y + direction[1]
                neighbour_node = self.find_node(x, y)

                if neighbour_node and neighbour_node not in previous_nodes:
                    node.connect_node(neighbour_node)
                    #print(f"connected {node} and {neighbour_node}")

            previous_nodes.append(node)

        start_node = self.nodes[0]
        self.set_height_dfs(start_node, start_node.level, 0, 1000)
        self.set_normals_dfs(start_node,0)

    #Recursively set height of connected nodes (Depth First Search)
    def set_height_dfs(self, node, level, depth, max_depth=1000, visited=None):
        if depth > max_depth:
            return

        if visited is None:
            visited = set()

        if node in visited:
            return

        visited.add(node)
        level += node.level
        node.level = level
        depth += 1

        for connected_node in node.connected_nodes:
            if connected_node not in visited:
                self.set_height_dfs(connected_node, level, depth, max_depth, visited)

    def set_wall_dir(self):
        directions = [(0,-1),(1,0),(0,1),(-1,0)]
        for i,node in enumerate(self.nodes):
            for j,direction in enumerate(directions):
                neighbour_node = self.find_node(node.x + direction[0],node.y + direction[1])
                if neighbour_node:
                    node.wall_dir[j] = 0

    def set_doors(self):
        for node in self.nodes:
            if node.node_type == NodeType.DOOR:
                for i,direction in enumerate(node.wall_dir):
                    if direction == 0:
                        node.wall_dir[i] = NodeType.DOOR.value

    def set_normals_dfs(self, node, depth, previous_node=None, max_depth=1000, visited=None):
        if depth > max_depth:
            return

        if visited is None:
            visited = set()

        if node in visited:
            return

        visited.add(node)
        depth += 1

        if previous_node is not None and node.normal == [0,0,0]:
             node.normal = [node.x - previous_node.x, 0,  node.y - previous_node.y]

        for connected_node in node.connected_nodes:
            if connected_node not in visited:
                node.normal = [connected_node.x - node.x, 0,  connected_node.y - node.y]
                if len(node.connected_nodes) > 2 or node.connected_nodes is None:
                    node.normal = previous_node.normal
                self.set_normals_dfs(connected_node, depth,node, max_depth, visited)

    def __repr__(self):
        return str(self.nodes) + " i:"+str(len(self.nodes))

    def __str__(self):
        return str(self.nodes) + " i:"+str(len(self.nodes))