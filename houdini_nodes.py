import hou


class HoudiniNodes:
    def __init__(self):
        self.node_network = None
        self.add_node = None
        self.attrib_node = None
        self.wrangle_node = None
        self.null_node = None
        self.module_subnet = None



    def create_nodes(self,graph, width_multiplier, height_multiplier):

        nodes = graph.nodes

        wrangle_string = ""

        obj = hou.node("obj/")

        #TODO: refactor this section
        try:
            self.node_network.layoutChildren()
        except:
            self.node_network = None

        if self.node_network is None:
            self.node_network = obj.createNode("geo","Generated_Level")
            self.add_node = self.node_network.createNode("add")
            self.attrib_node = self.node_network.createNode("attribcreate::2.0")
            self.wrangle_node = self.node_network.createNode("attribwrangle")
            self.null_node = self.node_network.createNode("null", "POINTS_OUT")
            self.module_subnet = self.node_network.createNode("martin.nyman2::Module_subnet::1.0")


        # Set Params

        self.attrib_node.setParms({
            "numattr": 5,
            "name1": "type",
            "default1v1": 1,
            "value1v1": 1,
            "type1": 1,
            "name2": "type_name",
            "string2": "DEFAULT",
            "type2": 3,
            "name3": "wall_dir",
            "size3": 4,
            "type3": 1,
            "name4": "module_width",
            "class4": 0,
            "value4v1": width_multiplier,
            "name5": "module_height",
            "class5": 0,
            "value5v1": height_multiplier

        })

        self.add_node.parm("points").set(len(nodes))

        for i, node in enumerate(graph.nodes):
            self.add_node.setParms({
                f"pt{i}x": node.x * width_multiplier,
                f"pt{i}y": node.level * height_multiplier,
                f"pt{i}z": node.y * width_multiplier,
            })

            wrangle_string += f"setpointattrib(0,'type',{i},{node.node_type.value});"
            wrangle_string += f"setpointattrib(0,'wall_dir',{i},{{{node.wall_dir[0]},{node.wall_dir[1]},{node.wall_dir[2]},{node.wall_dir[3]}}});"
            wrangle_string += f"setpointattrib(0,'type_name',{i},'{node.node_type.name}');"
            wrangle_string += f"setpointattrib(0,'level',{i},{node.level});"
            wrangle_string += f"setpointattrib(0,'N',{i},{{{node.normal[0]},{node.normal[1]},{node.normal[2]}}});\n"

        self.wrangle_node.setParms(
            {
                "class": 0,
                "snippet": wrangle_string
            }
        )


        # Set inputs
        self.attrib_node.setInput(0, self.add_node)
        self.wrangle_node.setInput(0, self.attrib_node)
        self.null_node.setInput(0, self.wrangle_node)
        self.module_subnet.setInput(0, self.null_node)

        self.module_subnet.setDisplayFlag(True)
        self.module_subnet.setRenderFlag(True)

        #self.create_wall_points(width_multiplier/2)

        self.node_network.layoutChildren()

    def create_wall_points(self, width):
        self.wall_add = self.node_network.createNode("add")
        points = self.null_node.geometry().points()
        for point in points:
            pos = point.position()
            wall_dirs = point.attribValue("wall_dir")
            if wall_dirs[0] == 1:
                new_pos = pos + hou.Vector3(0,0,-width)
                self.set_add_point(new_pos)
            if wall_dirs[1] == 1:
                new_pos = pos + hou.Vector3(width,0,0)
                self.set_add_point(new_pos)
            if wall_dirs[2] == 1:
                new_pos = pos + hou.Vector3(0,0,width)
                self.set_add_point(new_pos)
            if wall_dirs[3] == 1:
                new_pos = pos + hou.Vector3(-width,0,0)
                self.set_add_point(new_pos)

    def set_add_point(self, new_pos):
        add_points = self.wall_add.parm("points").eval() + 1
        self.wall_add.parm("points").set(add_points)
        self.wall_add.setParms({
            f"pt{add_points - 1}x": new_pos[0],
            f"pt{add_points - 1}y": new_pos[1],
            f"pt{add_points - 1}z": new_pos[2]
        })