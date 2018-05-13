'''
@yvan May 5 2018

vectorized implementation fo the 3d cube viewer.
'''

import copy
import numpy as np

def create_translation_matrix(dx=0, dy=0, dz=0):
    '''
    Return a matrix for the translation along vector (dx, dy ,dz)
    Args:
        :param dx: (numeric) value to trsanlate in the x axis
        :param dy: (numeric) value to trsanlate in the y axis
        :param dz: (numeric) value to trsanlate in the z axis
    '''
    return np.array([
                    [1,0,0,0],
                    [0,1,0,0],
                    [0,0,1,0],
                    [dx,dy,dz,1]
                    ])

def create_scale_matrix(s, cx=0, cy=0, cz=0):
    '''
    Return a matrix to scale along axes centered on cx, cy, cz
    Args:
        :param s: (numeric) the scaling factor for resizing the wireframes
        :param cx: (numeric) center x value
        :param cy: (numeric) center y value
        :param cz: (numeric) center z value
    '''
    return np.array([
                    [s,0,0,0],
                    [0,s,0,0],
                    [0,0,s,0],
                    [cx*(1-s),cy*(1-s),cz*(1-s),1]
                    ])

def create_rot_x(radians):
    '''
    Create a rotation matrix for rotating however many radians around x.
    Args:
        :param radians: (numeric) the amount of radians to rotate by
    '''
    c = np.cos(radians)
    s = np.sin(radians)
    return np.array([
                    [1,0,0,0],
                    [0,c,-s,0],
                    [0,s,c,0],
                    [0,0,0,1]
                    ])

def create_rot_y(radians):
    '''
    Create a rotation matrix for rotating around y by radians.
    Args:
        :param radians: (numeric) the amount of radians to rotate by
    '''
    c = np.cos(radians)
    s = np.sin(radians)
    return np.array([
                    [c,0,s,0],
                    [0,1,0,0],
                    [-s,0,c,0],
                    [0,0,0,1]
                    ])

def create_rot_z(radians):
    '''
    Create a rotation matrix for rotating around z by radians.
    Args:
        :param radians: (numeric) the amount of radians to rotate by
    '''
    c = np.cos(radians)
    s = np.sin(radians)
    return np.array([
                    [c,-s,0,0],
                    [s,c,0,0],
                    [0,0,1,0],
                    [0,0,0,1]
                    ])

class Wireframe(object):
    '''
    A wireframe for our 3d model.
    '''
    def __init__(self, nodes, faces=[], facecolors=[]):
        '''
        Creates our wireframe
        Args:
            :param nodes: (list) a numpy array of N X 3 where N is the number of
             nodes the 3 columns are X Y Z coordinates of each point.
            :param faces: (list) a numpy array of N X Z where N is the number of
             faces and Z is the number of nodes in the face, each column (Z) is
             a node, order matters
            :param facecolors: (list) a numpy array of N X 3 where N is the
            number of faces and the columns are RGB values of colors
        '''
        self.nodes = np.zeros((0,nodes.shape[1]))
        ones_col = np.ones((len(nodes), 1))
        self.nodes = np.hstack((nodes, ones_col))
        self.nodes_initial = copy.deepcopy(self.nodes)
        self.edges = np.zeros((0,2)).astype(np.int)
        self.faces = faces
        self.facecolors = facecolors

        if self.faces != [] and self.facecolors != []:
            for node_list, color in zip(faces, facecolors):
                if all(node < len(self.nodes) for node in node_list):
                    new_edges = [[node_list[n-1], node_list[n]] for n in range(len(node_list))]
                    self.edges = np.vstack((self.edges, new_edges))

            assert self.faces.shape[0] == self.facecolors.shape[0],\
            'Faces and colors need the same shape!'

    def reset_nodes(self):
        '''
        Reset the list of nodes to how they were originally.
        '''
        self.nodes = copy.deepcopy(self.nodes_initial)

    def output_nodes(self):
        '''
        Print the nodes of the wireframe. x,y,z are position parameters,
        e is an extra parameter to make matrix multiplication easier.
        '''
        print(f'\n---{self.nodes.shape[0]} nodes (x, y, z, _) --- ')
        if self.nodes == []:
            print('There are no nodes!')
        else:
            for i, (x,y,z,e) in enumerate(self.nodes):
                print(f'{i} ({x}, {y}, {z}, {e})')

    def output_edges(self):
        '''
        Print the edges of the wireframe
        '''
        print(f'\n--- {self.edges.shape[0]} edges (p1 <-> p2) --- ')
        if self.edges == []:
            print('There are no edges!')
        else:
            for i, (node1, node2) in enumerate(self.edges):
                print(f'{i} {node1} - {node2}')

    def output_faces(self):
        '''
        Print faces of the wireframe
        '''
        print(f'\n---{self.faces.shape[0]} faces --- ')
        if self.faces == []:
            print('There are no faces!')
        else:
            for i, nodes in enumerate(self.faces):
                f = ', '.join([f'{n}' for n in nodes])
                print(f'{i}: {f}')

    def transform(self, matrix):
        '''
        Apply an arbitrary transformation matrix via bultin python dot product operator.
        '''
        self.nodes = self.nodes @ matrix

    def find_center(self):
        '''
        Find the center of our cube.
        '''
        # go column by column find the smallest x,y,z
        min_values = self.nodes[:,:-1].min(axis=0)
        # got through each column adn find the biggest x,y,z
        max_values = self.nodes[:,:-1].max(axis=0)
        # add them together and divide by 2
        return 0.5*(min_values + max_values)

    def center_wireframe(self, screen_center):
        '''
        Performs a translation on the wireframe such that its
        find_center would return the middle of the screen.
        Args:
            :param screen_center: (tuple) that give the x,y,z coordinated of the center.
        '''
        # find the center of the cube
        c = self.find_center()
        # find the difference between the center
        # and the screen center
        diff = screen_center - c
        mt = create_translation_matrix(*diff)
        self.transform(mt)

    def sorted_faces(self):
        # sorts faces byt the minimum Z value of all their nodes
        # the minimum z value is whats closer to our viewpoint
        # needs to also return the colors so they are correct
        # with the new sorted array
        return sorted(zip(self.faces,self.facecolors), key=lambda face: min(self.nodes[f,2] for f in face[0]))

if __name__ == '__main__':
    cube_nodes = [[x,y,z] for x in (0,1) for y in (0,1) for z in (0,1)]
    cube_nodes = np.array(cube_nodes)
    cube_faces = [[0,1,3,2], [7,5,4,6], [4,5,1,0], [2,3,7,6], [0,2,6,4], [5,7,3,1]]
    cube_faces = np.array(cube_faces)
    cube_colors = [[255, 255, 255], [154,205,50], [128,0,0], [70,130,180], [75,0,130], [199,21,133]]
    cube_colors = np.array(cube_colors)
    cube = Wireframe(cube_nodes, cube_faces, cube_colors)
    cube.output_nodes()
    cube.output_edges()
    cube.output_faces()

'''
Resources/Credits:

http://codentronix.com/2011/04/21/rotating-3d-wireframe-cube-with-python/
http://www.petercollingridge.co.uk/pygame-3d-graphics-tutorial/nodes-and-edges
http://www.petercollingridge.co.uk/pygame-physics-simulation
'''
