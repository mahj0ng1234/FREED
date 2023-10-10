import torch
import os
import re

from network import make_model
from option import args
from torchvision import transforms
from torchvision.datasets.folder import default_loader

use_gpu = torch.cuda.is_available()
data_transforms = transforms.Compose([
        transforms.Resize((384,128), interpolation=3),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])]
)

# get the MGN model
def loadNetwork(modelPath):
    # Load Collected data Trained model
    model = make_model(args)
    if use_gpu:
        train_dict = torch.load(modelPath)
    else:
        train_dict = torch.load(modelPath,map_location='cpu')
    model.load_state_dict(train_dict)
    # Change to test mode
    model = model.eval()
    if use_gpu:
        model = model.cuda()
    return model

# get the feature vector of an image via the model
def extractFeature(model, imgPath):

    features = torch.FloatTensor()
    img = default_loader(imgPath)
    img = data_transforms(img)
    img = img.unsqueeze(0)
    ff = torch.FloatTensor(img.size()[0], 2048).zero_()
    for i in range(2):
        if i == 1:
            img = img.index_select(3, torch.arange(img.size(3) - 1, -1, -1))
        if use_gpu:
            input_img = img.cuda()
        else:
            input_img = img
        outputs = model(input_img)
        f = outputs[0].data.cpu()
        ff = ff + f
    fnorm = torch.norm(ff, p=2, dim=1, keepdim=True)
    ff = ff.div(fnorm.expand_as(ff))

    features = torch.cat((features, ff), 0)
    return features

# get the feature vectors of gallery via the model
def extractFeatures(model, gallery):

    features = torch.FloatTensor()
    for imgPath in gallery:
        img = default_loader(imgPath)
        img = data_transforms(img)
        img = img.unsqueeze(0)
        ff = torch.FloatTensor(img.size()[0], 2048).zero_()
        for i in range(2):
            if i == 1:
                img = img.index_select(3, torch.arange(img.size(3) - 1, -1, -1))
            if use_gpu:
                input_img = img.cuda()
            else:
                input_img = img
            outputs = model(input_img)
            f = outputs[0].data.cpu()
            ff = ff + f
        fnorm = torch.norm(ff, p=2, dim=1, keepdim=True)
        ff = ff.div(fnorm.expand_as(ff))

        features = torch.cat((features, ff), 0)

    return features

def id(file_path):
    """
    :param file_path: unix style file path
    :return: person id
    """
    return int(file_path.split('\\')[-1].split('_')[0])

# jpg|jpeg|bmp|png|ppm|npy files
def list_pictures(directory, ext='jpg|jpeg|bmp|png|ppm|npy'):
    assert os.path.isdir(directory), 'dataset is not exists!{}'.format(directory)
    return sorted([os.path.join(root, f)
                   for root, _, files in os.walk(directory) for f in files
                   if re.match(r'([\w]+\.(?:' + ext + '))', f)])