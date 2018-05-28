'''
@yvan may 13
'''

import os
import torch
import torch.nn as nn
from torch.utils import data
from torchvision.datasets import ImageFolder
from torchvision.utils import make_grid

# setup the data
batch_size = 64
image_path = os.path.join('.', 'imgs_jpg')
GPU_STATUS = (torch.cuda.is_available(), torch.__version__, torch.cuda.device_count())
print(f'GPU STATUS: {GPU_STATUS}')

cube_dataset = ImageFolder(image_path)
cube_loader = data.DataLoader(dataset=cube_dataset,
                              batch_size=batch_size,
                              shuffle=True,
                              num_workers=1)

# create a model
class Vae(nn.module):
    def __init__(self):
        super(Vae, self).__init__()
        self.main = nn.Sequential(

        
        )


# train the model
n_epochs = 10
for img in cube_loader:
