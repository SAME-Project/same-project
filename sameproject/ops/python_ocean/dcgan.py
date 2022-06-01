#!/usr/bin/env python
# coding: utf-8

# # SAME DCGAN

# In[1]:


# The code for the DCGAN generative model is taken from the official PyTorch docs https://pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html.

import argparse
import json
import logging
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.image as mpimg
import numpy as np
import os
import random
from pathlib import Path
import pickle
import sys
import time

import torch
import torch.nn as nn
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim as optim
import torch.utils.data
import torchvision.datasets as dset
import torchvision.transforms as transforms
import torchvision.utils as vutils



# ## Fetching data

# In[ ]:


def get_input(local=False):
    if local:
            
                #
        print("Reading local punks directory.")
        
        # Root directory for dataset
        filename = Path('data/punks/tealpunks')
        # filename = Path('data/punks-sample')
        # filename = Path('data/celeba')
        
            

        return filename
    print(cell['metadata'].get('tags', []))
    dids = os.getenv('DIDS', None)

    if not dids:
        print("No DIDs found in environment. Aborting.")
        return

    dids = json.loads(dids)

    cwd = os.getcwd()
    print('cwd', cwd)
        

    for did in dids:
        print('ls', f'/data/inputs/{did}/0')
        print('ls2', os.listdir(f'/data/inputs/'))
        filename = Path(f'/data/inputs/{did}/0')  # 0 for metadata service
        print(f"Reading asset file {filename}.")
        return filename



# # Train & test model

# In[ ]:


def run_model(local=False):

    t0 = time.time()
        
        #
    filename = get_input(local)
    if not filename:
        print("Could not retrieve filename.")
        return
    
    from PIL import Image
    with open(filename) as datafile:
        print(type(datafile))
        print(datafile)
        datafile.seek(0)
        img = Image.open(datafile)
        print('@@@', img)
    
    
    teal_images = sorted(list(filename.glob('*')))
    
    print(teal_images)
    
    results_dir = Path('results')
    
    if not results_dir.exists():
        results_dir.mkdir()
    
    if local:
        img0 = mpimg.imread(teal_images[0])
        img1 = mpimg.imread(teal_images[1])
        fig, ax = plt.subplots(1,2)
        ax[0].imshow(img0)
        ax[1].imshow(img1)
        [a.axis('off') for a in ax]
        plt.savefig(results_dir / "sample.png")
    
    # Set random seed for reproducibility
    manualSeed = 999
    #manualSeed = random.randint(1, 10000) # use if you want new results
    print("Random Seed: ", manualSeed)
    random.seed(manualSeed)
    torch.manual_seed(manualSeed)
    
    # Training parameters
    workers = 2
    batch_size = 128
    image_size = 64
    nc = 3
    nz = 100
    ngf = 64
    ndf = 64
    num_epochs = 5
    lr = 0.0002
    beta1 = 0.5
    ngpu = 1
    
    # We can use an image folder dataset the way we have it setup.
    # Create the dataset
    dataset = dset.ImageFolder(root=filename.parent,
                                transform=transforms.Compose([
                                    transforms.Resize(image_size),
                                    transforms.CenterCrop(image_size),
                                    transforms.ToTensor(),
                                    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
                                ]))
    # Create the dataloader
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size,
                                                shuffle=True, num_workers=workers)
    
    # Decide which device we want to run on
    device = torch.device("cuda:0" if (torch.cuda.is_available() and ngpu > 0) else "cpu")
    
    # custom weights initialization called on netG and netD
    def weights_init(m):
        classname = m.__class__.__name__
        if classname.find('Conv') != -1:
            nn.init.normal_(m.weight.data, 0.0, 0.02)
        elif classname.find('BatchNorm') != -1:
            nn.init.normal_(m.weight.data, 1.0, 0.02)
            nn.init.constant_(m.bias.data, 0)
    
    # Generator Code
    class Generator(nn.Module):
        def __init__(self, ngpu):
            super(Generator, self).__init__()
            self.ngpu = ngpu
            self.main = nn.Sequential(
                    # input is Z, going into a convolution
                    nn.ConvTranspose2d( nz, ngf * 8, 4, 1, 0, bias=False),
                    nn.BatchNorm2d(ngf * 8),
                    nn.ReLU(True),
                    # state size. (ngf*8) x 4 x 4
                    nn.ConvTranspose2d(ngf * 8, ngf * 4, 4, 2, 1, bias=False),
                    nn.BatchNorm2d(ngf * 4),
                    nn.ReLU(True),
                    # state size. (ngf*4) x 8 x 8
                    nn.ConvTranspose2d( ngf * 4, ngf * 2, 4, 2, 1, bias=False),
                    nn.BatchNorm2d(ngf * 2),
                    nn.ReLU(True),
                    # state size. (ngf*2) x 16 x 16
                    nn.ConvTranspose2d( ngf * 2, ngf, 4, 2, 1, bias=False),
                    nn.BatchNorm2d(ngf),
                    nn.ReLU(True),
                    # state size. (ngf) x 32 x 32
                    nn.ConvTranspose2d( ngf, nc, 4, 2, 1, bias=False),
                    nn.Tanh()
                    # state size. (nc) x 64 x 64
                )
    
        def forward(self, input):
            return self.main(input)
    
    # Create the generator
    netG = Generator(ngpu).to(device)
    
    # Handle multi-gpu if desired
    if (device.type == 'cuda') and (ngpu > 1):
        netG = nn.DataParallel(netG, list(range(ngpu)))
    
    # Apply the weights_init function to randomly initialize all weights
    #  to mean=0, stdev=0.02.
    netG.apply(weights_init)
    
    # Print the model
    print(netG)
    
    class Discriminator(nn.Module):
        def __init__(self, ngpu):
            super(Discriminator, self).__init__()
            self.ngpu = ngpu
            self.main = nn.Sequential(
                    # input is (nc) x 64 x 64
                    nn.Conv2d(nc, ndf, 4, 2, 1, bias=False),
                    nn.LeakyReLU(0.2, inplace=True),
                    # state size. (ndf) x 32 x 32
                    nn.Conv2d(ndf, ndf * 2, 4, 2, 1, bias=False),
                    nn.BatchNorm2d(ndf * 2),
                    nn.LeakyReLU(0.2, inplace=True),
                    # state size. (ndf*2) x 16 x 16
                    nn.Conv2d(ndf * 2, ndf * 4, 4, 2, 1, bias=False),
                    nn.BatchNorm2d(ndf * 4),
                    nn.LeakyReLU(0.2, inplace=True),
                    # state size. (ndf*4) x 8 x 8
                    nn.Conv2d(ndf * 4, ndf * 8, 4, 2, 1, bias=False),
                    nn.BatchNorm2d(ndf * 8),
                    nn.LeakyReLU(0.2, inplace=True),
                    # state size. (ndf*8) x 4 x 4
                    nn.Conv2d(ndf * 8, 1, 4, 1, 0, bias=False),
                    nn.Sigmoid()
                )
    
        def forward(self, input):
            return self.main(input)
    
        # Create the Discriminator
    netD = Discriminator(ngpu).to(device)
    
        # Handle multi-gpu if desired
    if (device.type == 'cuda') and (ngpu > 1):
        netD = nn.DataParallel(netD, list(range(ngpu)))
    
        # Apply the weights_init function to randomly initialize all weights
        #  to mean=0, stdev=0.2.
    netD.apply(weights_init)
    
        # Print the model
    print(netD)
    
        # Initialize BCELoss function
    criterion = nn.BCELoss()
    
        # Create batch of latent vectors that we will use to visualize
        #  the progression of the generator
    fixed_noise = torch.randn(64, nz, 1, 1, device=device)
    
        # Establish convention for real and fake labels during training
    real_label = 1.
    fake_label = 0.
    
        # Setup Adam optimizers for both G and D
    optimizerD = optim.Adam(netD.parameters(), lr=lr, betas=(beta1, 0.999))
    optimizerG = optim.Adam(netG.parameters(), lr=lr, betas=(beta1, 0.999))
    
        # Training Loop
    
        # Lists to keep track of progress
    img_list = []
    G_losses = []
    D_losses = []
    iters = 0
    
    print("Starting Training Loop...")
        # For each epoch
    for epoch in range(num_epochs):
            # For each batch in the dataloader
        for i, data in enumerate(dataloader, 0):
    
                ############################
                # (1) Update D network: maximize log(D(x)) + log(1 - D(G(z)))
                ###########################
                ## Train with all-real batch
            netD.zero_grad()
                # Format batch
            real_cpu = data[0].to(device)
            b_size = real_cpu.size(0)
            label = torch.full((b_size,), real_label, dtype=torch.float, device=device)
                # Forward pass real batch through D
            output = netD(real_cpu).view(-1)
                # Calculate loss on all-real batch
            errD_real = criterion(output, label)
                # Calculate gradients for D in backward pass
            errD_real.backward()
            D_x = output.mean().item()
    
                ## Train with all-fake batch
                # Generate batch of latent vectors
            noise = torch.randn(b_size, nz, 1, 1, device=device)
                # Generate fake image batch with G
            fake = netG(noise)
            label.fill_(fake_label)
                # Classify all fake batch with D
            output = netD(fake.detach()).view(-1)
                # Calculate D's loss on the all-fake batch
            errD_fake = criterion(output, label)
                # Calculate the gradients for this batch, accumulated (summed) with previous gradients
            errD_fake.backward()
            D_G_z1 = output.mean().item()
                # Compute error of D as sum over the fake and the real batches
            errD = errD_real + errD_fake
                # Update D
            optimizerD.step()
    
                ############################
                # (2) Update G network: maximize log(D(G(z)))
                ###########################
            netG.zero_grad()
            label.fill_(real_label)  # fake labels are real for generator cost
                # Since we just updated D, perform another forward pass of all-fake batch through D
            output = netD(fake).view(-1)
                # Calculate G's loss based on this output
            errG = criterion(output, label)
                # Calculate gradients for G
            errG.backward()
            D_G_z2 = output.mean().item()
                # Update G
            optimizerG.step()
    
                # Output training stats
            if i % 50 == 0:
                print('[%d/%d][%d/%d]\tLoss_D: %.4f\tLoss_G: %.4f\tD(x): %.4f\tD(G(z)): %.4f / %.4f'
                        % (epoch, num_epochs, i, len(dataloader),
                            errD.item(), errG.item(), D_x, D_G_z1, D_G_z2))
    
                # Save Losses for plotting later
            G_losses.append(errG.item())
            D_losses.append(errD.item())
    
                # Check how the generator is doing by saving G's output on fixed_noise
            if (iters % 500 == 0) or ((epoch == num_epochs-1) and (i == len(dataloader)-1)):
                with torch.no_grad():
                    fake = netG(fixed_noise).detach().cpu()
                img_list.append(vutils.make_grid(fake, padding=2, normalize=True))
    
            iters += 1
    
    
    filename = results_dir / 'punks.pickle' if local else "/data/outputs/result"
    with open(filename, 'wb') as pickle_file:
        print(f"Pickling results in {filename}")
        pickle.dump(img_list[-1], pickle_file)
    
    t1 = time.time()
    total = t1-t0
    
    print('Time: ', total)
    
        



# In[ ]:







# In[ ]:







# In[ ]:







# In[ ]:







# In[ ]:







# In[ ]:







# In[ ]:






