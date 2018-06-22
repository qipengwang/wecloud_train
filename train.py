# train.py
#!/usr/bin/env	python3

""" train network using pytorch
"""

#import argparse
import os
from datetime import datetime

import numpy as np
import torch
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms

from torch.utils.data import DataLoader
from dataset import *
from models.resnet import *
from torch.autograd import Variable

from tensorboardX import SummaryWriter
from settings import *

#parser = argparse.ArgumentParser(description='image classification with Pytorch')
#parser.add_argument('--')


#data preprocessing:
cifar100_training = CIFAR100Train(g_cifar_100_path)
train_mean, train_std = compute_mean_std(cifar100_training)
transform_train = transforms.Compose([
    transforms.Normalize(train_mean, train_std),
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15)
])
cifar100_training_loader = DataLoader(cifar100_training, shuffle=True, num_workers=2, batch_size=16)

cifar100_test = CIFAR100Test(g_cifar_100_path)
test_mean, test_std = compute_mean_std(cifar100_test)
transform_test = transforms.Compose([
    transforms.Normalize(test_mean, test_std)
])
cifar100_test_loader = DataLoader(cifar100_test, shuffle=True, num_workers=2, batch_size=16)

net = ResNet101().cuda()







loss_function = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.1, momentum=0.9, weight_decay=1e-4)
scheduler = optim.lr_scheduler.MultiStepLR(optimizer, milestones=[100, 150], gamma=0.1) #learning rate decay


def train(epoch):
    net.train()

    for batch_index, (labels, images) in enumerate(cifar100_training_loader):

        images = Variable(images.permute(0, 3, 1, 2).float())
        labels = Variable(labels)

        labels = labels.cuda()
        images = images.cuda()

        optimizer.zero_grad()
        outputs = net(images)
        loss = loss_function(outputs, labels)
        loss.backward()
        optimizer.step()

        print('Training Epoch: {epoch} [{trained_samples}/{total_samples}]\tLoss: {:0.4f}\t'.format(
            loss.data[0],
            epoch=epoch,
            trained_samples=batch_index * len(images),
            total_samples=len(cifar100_training)
        ))

        #update training loss for each iteration
        n_iter = (epoch - 1) * len(cifar100_training_loader) + batch_index + 1
        writer.add_scalar('Train/loss', loss.data[0], n_iter)

    for name, param in net.named_parameters():
        layer, attr = os.path.splitext(name)
        attr = attr[1:]
        writer.add_histogram("{}/{}".format(layer, attr), param, epoch)

def eval_training(epoch):
    net.eval()

    test_loss = 0.0 # cost function error
    correct = 0.0

    for (labels, images) in cifar100_test_loader:
        images = Variable(images.permute(0, 3, 1, 2).float()).cuda()
        labels = Variable(labels).cuda()

        outputs = net(images)
        loss = loss_function(outputs, labels)
        test_loss += loss.data[0]
        _, preds = outputs.max(1)
        correct += preds.eq(labels).sum().data[0]

    print(test_loss / len(cifar100_test))
    print('Test set: Average loss: {:.4f}, Accuracy: {:.4f}'.format(
        test_loss / len(cifar100_test),
        correct / len(cifar100_test)
    ))
    print()

    #add informations to tensorboard
    writer.add_scalar('Test/Average loss', test_loss / len(cifar100_test), epoch)
    writer.add_scalar('Test/Accuracy', correct / len(cifar100_test), epoch)

    return correct / len(cifar100_test)



if __name__ == '__main__':

    input_tensor = torch.Tensor(12, 3, 32, 32).cuda()
    res = net(Variable(input_tensor, requires_grad=True))

    #use tensorboard
    if not os.path.exists('runs'):
        os.mkdir('runs')
    writer = SummaryWriter(log_dir=os.path.join('runs', datetime.now().isoformat()))
    writer.add_graph(net, Variable(input_tensor, requires_grad=True))

    #create checkpoint folder to save model
    if not os.path.exists('checkpoint'):
        os.mkdir('checkpoint')
    checkpoint_path = os.path.join('checkpoint', 'resnet101-{epoch}.pt')

    best_acc = 0.0
    for epoch in range(1, 200):
        scheduler.step()
        train(epoch)
        acc = eval_training(epoch)

        #start to save best performance model after 120 epoch
        if epoch > 120 and best_acc < acc:
            torch.save(net.state_dict(), checkpoint_path.format(epoch=epoch))
            best_acc = acc
            continue

        if not epoch % 50:
            torch.save(net.state_dict(), checkpoint_path.format(epoch=epoch))

    writer.close()
        
 

    
