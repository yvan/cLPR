'''
@yvan may 11 2018

This script generates cLPR data using pygame and is the basis for a more general
3D data generator I will program at some future time.

Download the generated data here:


'''
import sys
import pygame
import datetime
import numpy as np
import wireframe as wf

class Projector(object):
    '''
    Makes 2D projections of 3d wireframes on a pygame screen.
    '''
    def __init__(self, width, height):
        # setup pygame
        self.width = width
        self.height = height
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Wireframe Display')
        self.background = (10,10,50)
        # where we will store our cube
        self.wireframes = {}
        # whether to display different parts
        self.display_nodes = False
        self.display_edges = False
        self.display_faces = True
        # what color to paint nodes edges
        self.node_color = (255, 255, 255)
        self.edge_color = (255, 255, 255)
        # how big the 'points'/'nodes' are in our cube
        self.node_radius = 4
        # to slow down the viewer
        self.fps = 5
        # primarily for testing or redueced generation
        self.limit_samples = 100

    def add_wireframe(self, name, wireframe):
        '''
        Add a wireframe to our scene.
        '''
        self.wireframes[name] = wireframe

    def run(self):
        '''
        Run pygame and dispaly our wireframes
        '''
        # clock to slow thigns down a bit to
        # get better images
        clockobject = pygame.time.Clock()
        running = True
        seq_step = 0
        # create our set of rotations
        seq = self.create_rotation_sequence()
        # store a numpy array for every wireframe
        # some may differ. this will allow us to
        # create entire scenes and learn them later
        # if we want to do that
        if self.limit_samples:
            row_count = self.limit_samples
        else:
            row_count = len(seq)

        # get the only wireframe (the cube)
        # and initialize a numpy array
        # every row in rotaitons_positions
        # is a frame, then there is a dimension
        # for nodes, then 6 columns, 3 for XYZ coords,
        # 3 for XYZ rotations in radians
        wireframe = self.wireframes['cube']
        rotation_positions = np.zeros((row_count, wireframe.nodes.shape[0],6))

        while running:
            clockobject.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # go to the next rotation, recenter our wireframe
            for radians, axis in zip(seq[seq_step] , ('x','y','z')*len(seq)):
                self.rotate_all(axis, radians)
            cube.center_wireframe((self.width//2, self.width//2,0))

            # print every 100 steps the progress
            if not seq_step % 100: prog = seq_step/len(seq); print(f'{prog}')

            # get the shapes of the rotations and the wireframe node positions consistent
            # so they can both be inserted into the same np array
            for _, wireframe in self.wireframes.items():
                # seq step is already a 3 element array, so tile takes NX1
                rotation_array = np.tile(np.array(seq[seq_step]), (wireframe.nodes.shape[0],1))
                # combine the rotations and positions
                rotation_positions[seq_step] = np.hstack((wireframe.nodes[:, :3], rotation_array))

            # keep track of which rotation we are on, if we are on
            # the right one, leave the run loop
            seq_step += 1
            if seq_step == len(seq) or seq_step == self.limit_samples:
                running = False

            # update the display of our cube
            self.display()
            pygame.display.update()
            # save a picture, then reset the cube to its original positions/rotations
            # self.save_projection('cube', str(seq_step))
            cube.reset_nodes()

        # once we exit the run loop save the positions
        self.save_wireframe_data(rotation_positions)
        pygame.quit()
        sys.exit()

    def display(self):
        '''
        Draw the wireframes on the pygame screen.
        '''
        self.screen.fill(self.background)
        for wireframe in self.wireframes.values():
            nodes = wireframe.nodes
            if self.display_faces:
                for face, color in zip(wireframe.sorted_faces(), wireframe.facecolors):
                    vector1 = (nodes[face[1]] - nodes[face[0]])[:3]
                    vector2 = (nodes[face[2]] - nodes[face[0]])[:3]

                    # see this https://www.mathsisfun.com/algebra/vectors-cross-product.html
                    normal = np.cross(vector1, vector2)
                    # now multiply it by the negative z axis to
                    # see that the normal points towards us in some way
                    # we only want to display those graphics
                    # (because thats what we 'see')
                    towards_us = np.dot(normal, np.array([0,0,-1]))

                    if towards_us:
                        # draw all our faces
                        pygame.draw.polygon(self.screen,
                                            color,
                                            [(nodes[node,0], nodes[node,1]) for node in face],
                                            0)

                        if self.display_edges:
                            for n1, n2 in wireframe.edges:
                                if n1 in face or n2 in face:
                                    pygame.draw.aaline(self.screen,
                                                    self.edge_color,
                                                    wireframe.nodes[n1,:2],
                                                    wireframe.nodes[n2,:2],
                                                    1
                                                )

            if self.display_nodes:
                for node in wireframe.nodes:
                    pygame.draw.circle(self.screen,
                                    self.node_color,
                                    (int(node[0]), int(node[1])),
                                    self.node_radius,
                                    0
                                    )
    def translate_all(self, vector):
        '''
        Translate all wireframes on the screen.
        Args:
            :param vector: (list) a vector that tells us how to translate the wireframe
        '''
        matrix = wf.create_translation_matrix(*vector)
        for _, wireframe in self.wireframes.items():
            wireframe.transform(matrix)

    def scale_all(self, scale):
        '''
        Scale all the wireframes on the the screen.
        Args:
            :param scale: (float) The parameter (scale>1-bigger, scale<1-smaller)
            telling pygame to scale the wireframes up or down.
        '''
        matrix = wf.create_scale_matrix(scale, self.width/2, self.height/2, 0)
        for _, wireframe in self.wireframes.items():
            wireframe.transform(matrix)

    def rotate_all(self, axis, radians):
        '''
        Rotate all wireframes in the screen.
        Args:
            :axis: The axis on which to rotate x, y, z
            :param radians: The amount in radians to rotate by
        '''
        rotate_func_name = 'create_rot_' + axis
        rotation_matrix = getattr(wf, rotate_func_name)(radians)
        for _,wireframe in self.wireframes.items():
            wireframe.transform(rotation_matrix)


    def save_projection(self, name, idx=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')):
        '''
        Saves the pygame screen as an image.
        Args:
            :param name: name to give to your image.
            :param idx: an index value to pass in for naming your files, so this
            is an external counter you pass in
            if you don't pass one in the datetime for right now is used.
        '''
        pygame.image.save(self.screen, f'imgs_bmp/{name}_index_{idx}.bmp')

    def rotate_randomly(self):
        '''
        Rotates randomly.
        '''
        rand_n = np.random.random()
        if rand_n < 0.3 :
            self.rotate_all('x',  0.05)
        elif rand_n > 0.3 and rand_n < 0.6:
            self.rotate_all('y',  0.05)
        else:
            self.rotate_all('z', 0.05)

    def create_rotation_sequence(self):
        '''
        Autorotates through all possible combinations of x,y,z
        rotations and takes a screenshot.
        '''
        rotations = []
        for rot_x in np.arange(0, 6.3, 0.3):
            for rot_y in np.arange(0, 6.3, 0.3):
                for rot_z in np.arange(0, 6.3, 0.3):
                    rotations.append((rot_x,rot_y,rot_z))
        return rotations

    def save_wireframe_data(self, rotation_positions):
        '''
        Saves the wireframe data to a numpy file.
        Args:
            :param rotation_positions: (numpy array) N x Z x 6, where N is
            frames, Z is nodes, 6 is XYZ coordiantes and XYZ roations
        '''
        name = 'cube'
        np.save(f'data/{name}-{np.__version__}.npy', rotation_positions)

if __name__ == '__main__':
    p = Projector(500, 500)
    cube_nodes = [[x,y,z] for x in (0,150) for y in (0,150) for z in (0,150)]
    cube_nodes = np.array(cube_nodes)
    cube_faces = [[0,1,3,2], [7,5,4,6], [4,5,1,0], [2,3,7,6], [0,2,6,4], [5,7,3,1]]
    cube_faces = np.array(cube_faces)
    cube_colors = [
    [255, 255, 255],
    [154,205,50],
    [128,0,0],
    [70,130,180],
    [75,0,130],
    [199,21,133]
    ]
    cube_colors = np.array(cube_colors)
    cube = wf.Wireframe(cube_nodes, cube_faces, cube_colors)
    p.add_wireframe('cube', cube)
    p.run()

'''
Resources / Credits:

http://www.petercollingridge.co.uk/pygame-3d-graphics-tutorial/projecting-3d-objects
'''
