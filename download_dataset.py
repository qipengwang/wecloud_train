import torchvision
import torchvision.transforms as transforms
from conf import settings

transform_train = transforms.Compose([
        #transforms.ToPILImage(),
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ToTensor(),
        transforms.Normalize(settings.CIFAR100_TRAIN_MEAN,
        settings.CIFAR100_TRAIN_STD)
    ])
transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(settings.CIFAR100_TRAIN_MEAN,
        settings.CIFAR100_TRAIN_STD)
    ])
cifar100_training = torchvision.datasets.CIFAR100(root='./data', train=True, download=True, transform=transform_train)
cifar100_test = torchvision.datasets.CIFAR100(root='./data', train=False, download=True, transform=transform_test)