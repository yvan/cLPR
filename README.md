cLPR: Generating A 3D Dataset for learning pose and rotation

Today I'm releasing the cLPR dataset, a baseline dataset for doing work in 3D machine learning. The name stands for Cubes for Learning Pose and Rotation. The goal is to provide a nice baseline dataset of a simple colored 3D cube in many different positions for testing machine learning algorithms whose goal is to learn about pose and rotation.

The dataset contains 32x32, 64x64, 128x128, 500x500 jpg images of the cube (2d projections of the 3d object). It also includes a numpy file which contains for every frame the position of the nodes, and the rotations applied to them. The file is called `cube-XXX.npy` where `XXX` is the numpy version used to dump the file. The [code](https://github.com/yvan/cLPR) used to generate the dataset is on github. It's always good to have the code yourself that way you can check any details you want and even generate your own version of the data.

The dataset is produced using a package called 'pygame' which is a package originally designed for making little python games. The package is nice because it lets you easily draw and render objects in 2d or 3d. OpenGL is another option. I didn't use it for a few reasons (it's hard to use, lots of jargon, difficult to read the code). In the future we may have an OpenGL version of the data generator for GPU optimized data generation. I wanted the code to be easy enough for someone with limited experience and basic knowledge of matrix multiplication to understand and accessible to people without GPU access.

Let's go over how the code works.

Step 1 Create a wireframe

First we create a wireframe of the cube. This wireframe consists of nodes, edges, and faces. The nodes are points in space, each represneted with x,y,z coordinates. We store all the nodes in an Nx3 numpy array. Edges are two nodes (the indices of the nodes in the numpy array). Faces are 4 nodes connected together (again the indices of the nodes in the numpy array).

You can create a wireframe like this:

```python
# create the nodes
cube_nodes = [[x,y,z] for x in (0,1) for y in (0,1) for z in (0,1)]
cube_nodes = np.array(cube_nodes)
# create the facecolors
cube_faces = [[0,1,3,2], [7,5,4,6], [4,5,1,0], [2,3,7,6], [0,2,6,4], [5,7,3,1]]
cube_faces = np.array(cube_faces)
# add colors for the faces
cube_colors = [[255, 255, 255], [154,205,50], [128,0,0], [70,130,180], [75,0,130], [199,21,133]]
# create a cube with both
cube_colors = np.array(cube_colors)
cube = Wireframe(cube_nodes, cube_faces, cube_colors)
```

I use to create 8 nodes, 6 faces, and 24 edges. You don't actually need to specify edges, just nodes and faces. This creates a cube. You can run in bash:

```bash
python wireframe.py
```

The only dependencies are python's `copy` module and `numpy`. It will automatically create a cube and print the nodes, edges, and faces.

Step 2 Generate rotations

Then I generate a set of rotations I'd like to apply in 3D to the nodes of the cube (the corners of the cube). To generate the ro


Step 3 Render the wireframe


Conclusion


Step 4 Apply one rotation and re-center the cube

Step 5 Reset the cube nodes to their initial positon

Step 6 Repeat from step 3

While I do this I screen shot the pygame screen after every rotation, and store position information in a numpy array.

Thanks

I want to thank express my profound thanks to [peter collingridge](http://www.petercollingridge.co.uk) who has some really great pygame tutorials, and while I have done other [blogs](LINKTOMYBLOGPOST) with pygame his overview was very helpful and the structure of my code borrows heavily from his python 2 implementation.
