import shutil, os
import pandas as pd

labels = pd.read_csv("weed-gan/labels/labels.csv")
labels = labels.sort_values('Species')

class_names = list(labels.Species.unique())

train_images = '/images'
train_cat = '/train_'
for i in class_names:
	os.makedirs(os.path.join('train_', i))

for c in class_names: # Category Name
	for i in list(labels[labels['Species']==c]['Filename']): # Image Id
		get_image = os.path.join('images', i) # Path to Images
		move_image_to_cat = shutil.copy(get_image, 'train_/'+c)


for c in class_names:

    train_path = os.path.join('set' ,c , 'train/')
    test_path  = os.path.join('set', c , 'test/')

    in_path    = os.path.join('train_' , c)

    os.makedirs(train_path , exist_ok=True)
    os.makedirs(test_path, exist_ok=True)

    filenames = os.listdir(in_path)

    no_of_pictures = len(filenames)

    test_set = int(len(filenames) * 0.3)
    train_set= len(filenames) - test_set

    test_imgs = filenames[:test_set]
    train_imgs = filenames[test_set:]

    for test_img in test_imgs:
        shutil.move( in_path + '/'  + test_img, test_path + test_img)
    for train_img in train_imgs:
        shutil.move( in_path + '/' + train_img, train_path + train_img)