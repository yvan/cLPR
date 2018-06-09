'''
@yvan may 11 2018

This script generates cLPR data using pygame and is the basis
for a more general 3D data generator I will program at some future time.

Download the generated data here:
'''

import os
import sys
import pygame
import argparse
import datetime
import numpy as np
import wireframe as wf

class Projector(object):
    '''
    Makes 2D projections of 3d wireframes on a pygame screen.
    '''
    def __init__(self, width, height, fps, save_data, step_size):
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
        self.display_nodes = True
        self.display_faces = True
        # what color to paint nodes edges
        self.node_colors = [[0,255,0],[255,255,0],[255, 0, 0],[150,150,255],[0,255,255],[0,200,255],[255,200,255],[200,200,255]]
        # how big the 'points'/'nodes' are in our cube
        self.node_radius = 5
        # to slow down the viewer
        # default=None for testing set to 5, it will slow down generation a lot
        self.fps = fps
        # leave False unless testing
        self.limit_samples = False
        # use exsiting position and data
        self.save_data = save_data

    def add_wireframe(self, name, wireframe):
        '''
        Add a wireframe to our scene.
        '''
        self.wireframes[name] = wireframe

    def run(self, test_npy=False):
        '''
        Run pygame and dispaly our wireframes
        '''
        # clock to slow thigns down a bit to
        # get better images
        clockobject = pygame.time.Clock()
        running = True
        seq_step = 0
        # create our set of rotations
        if test_npy:
            data = np.load(test_npy)
            # for all nodes get the positions
            pos = data[:,:,:3]
            # for all nodes get the roations
            # rotation si the same across nodes
            # so we get the first one
            seq = data[:,:,3]
        else:
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
        key = list(self.wireframes.keys())[0]
        wireframe = self.wireframes[key]
        rotation_positions = np.zeros((row_count, wireframe.nodes.shape[0],6))

        while running:
            if self.fps: clockobject.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if test_npy:
                for radians, axis  in zip(tuple(seq[seq_step]), ('x','y','z')):
                    self.rotate_all(axis, radians)
                # set the cube nodes the stored positions
                cube.nodes = pos[seq_step]
            else:
                # go to the next rotation, recenter our wireframe
                for radians, axis in zip(seq[seq_step] , ('x','y','z')):
                    self.rotate_all(axis, radians)
                cube.center_wireframe((self.width//2, self.width//2, 0))

            # print every 100 steps the progress
            if not seq_step % 100: prog = round(seq_step/len(seq)*100, 2); print(f'progress: {prog}%')

            # get the shapes of the rotations and the wireframe node positions consistent
            # so they can both be inserted into the same np array
            if self.save_data:
                for _, wireframe in self.wireframes.items():
                    # seq step is already a 3 element array, so tile takes NX1
                    rotation_array = np.tile(np.array(seq[seq_step]), (wireframe.nodes.shape[0],1))
                    # combine the rotations and positions
                    rotation_positions[seq_step] = np.hstack((wireframe.nodes[:, :3], rotation_array))

            # keep track of which rotation we are on, if we are on
            # the right one, leave the run loop
            seq_step += 1
            if seq_step == len(seq) or seq_step == self.limit_samples:
                print(seq_step, len(seq))
                print('Stopping run.')
                running = False

            # update the display of our cube
            self.display()
            pygame.display.update()
            # save a picture, then reset the cube to its
            # original positions/rotations
            if self.save_data: self.save_projection(key, str(seq_step))
            cube.reset_nodes()

        # once we exit the run loop save the positions
        if self.save_data: self.save_wireframe_data(rotation_positions)
        pygame.quit()

    def display(self):
        '''
        Draw the wireframes on the pygame screen.
        '''
        self.screen.fill(self.background)
        for wireframe in self.wireframes.values():
            towardus_nodes = []
            nodes = wireframe.nodes
            if self.display_faces:
                for face_color in zip(wireframe.sorted_faces()):
                    color = face_color[0][1]
                    face = face_color[0][0]
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
                        poly_nodes = []
                        for node in face:
                            poly_nodes.append((nodes[node,0], nodes[node,1]))
                            towardus_nodes.append(node)
                        # draw all our faces
                        pygame.draw.polygon(self.screen,
                                            color,
                                            poly_nodes,
                                            0)
            if self.display_nodes:
                print(set(towardus_nodes))
                # for each node if there is no face in front of a node
                # then show the node
                for i, (node, color) in enumerate(zip(wireframe.nodes, self.node_colors)):
                    if i in towardus_nodes:
                        pygame.draw.circle(self.screen,
                                        color,
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

    def create_rotation_sequence(self):
        '''
        Autorotates through all possible combinations of x,y,z
        rotations and takes a screenshot.
        '''
        rotations = []
        for rot_x in np.arange(0, 6.3, 0.1):
            for rot_y in np.arange(0, 6.3, 0.1):
                for rot_z in np.arange(0, 6.3, 0.1):
                    rotations.append((rot_x,rot_y,rot_z))
        return rotations

    def save_wireframe_data(self, rotation_positions):
        '''
        Saves the wireframe data to a numpy file.
        Args:
            :param rotation_positions: (numpy array) N x Z x 6, where N is
            frames, Z is nodes, 6 is XYZ coordiantes and XYZ roations
        '''
        name = list(self.wireframes.keys())[0]
        np.save(f'data/{name}-{np.__version__}.npy', rotation_positions)

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

def parse_args(args):
    p = argparse.ArgumentParser()
    p.add_argument('-f', '--fps', type=int, default=None, help='The frames per second of the generation process.')
    p.add_argument('-s', '--step-size', type=float, default=0.3, help='The step size for the rotations')
    p.add_argument('-t', '--test-npy', type=str, help='Tests a numpy file to make sure it\'s good. This arg is the file to test.')
    p.add_argument('-d', '--data-save', action='store_true', help='Whether to save data.')
    return p.parse_args(args)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:]).__dict__
    fps = args['fps']
    step = args['step_size']
    test = args['test_npy']
    save = args['data_save']

    # this is the folder where our
    # images are saved
    if not os.path.exists('./imgs_bmp'):
        os.mkdir('imgs_bmp')

    p = Projector(256, 256, fps, save, step)
    cube_nodes = [[x,y,z] for x in (0,100) for y in (0,100) for z in (0,100)]
    cube_nodes = np.array(cube_nodes)
    cube_faces = [[0,1,3,2], [7,5,4,6], [4,5,1,0], [2,3,7,6], [0,2,6,4], [5,7,3,1]]
    cube_faces = np.array(cube_faces)
    cube_colors = [[255, 0, 0],[0,255,0],[0,0,255],[255,255,0],[255,0,255],[0,255,255]]
    cube_colors = np.array(cube_colors)
    cube = wf.Wireframe(cube_nodes, cube_faces, cube_colors)
    p.add_wireframe('cube1', cube)
    p.run(test_npy=test)

'''
Resources / Credits:

http://www.petercollingridge.co.uk/pygame-3d-graphics-tutorial/projecting-3d-objects
'''
