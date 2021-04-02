import os
import numpy as np
import scipy.stats as st
import torch
import torch.nn as nn
from os.path import join, isfile, isdir
from os import listdir
from torchvision import datasets, models, transforms
from utils import get_classes, get_dataset

CONFIDENCE_LEVEL = 0.95


# Gets confidence interval
def get_confidence_interval(class_accuracies, confidence):
    print(st.t.interval(CONFIDENCE_LEVEL, len(class_accuracies)-1,
                        loc=np.mean(class_accuracies),
                        scale=st.sem(class_accuracies)))


def get_accuracy(model, input_folder, class_num_direc):
    # Set device for CUDA
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    # Get classes
    classes = get_classes(input_folder)

    # Load in the model
    active_model = torch.load(model)
    active_model.eval()
    print("Loaded the model")

    # dictionary - key: class, value: [correct, total]
    counters = {}
    for tissue_class in classes:
        counters[tissue_class] = [0, 0]

    class_num_to_class = {i: get_classes(class_num_direc)[i] for i in range(len(get_classes(class_num_direc)))}

    # Begin processing the model's predictions, prints individual class accuracy
    for tissue_class in os.listdir(input_folder):
        # Correctness list
        correctness = []
        # Safety check
        if tissue_class.startswith("."):
            continue
        image_dataset = get_dataset(os.path.join(input_folder, tissue_class))
        dataloader = torch.utils.data.DataLoader(
            image_dataset,
            batch_size=16,
            shuffle=False,
            num_workers=4)

        for test_inputs, test_labels in dataloader:
            # Model predictions
            test_inputs = test_inputs.to(device)
            test_outputs = active_model(test_inputs)
            softmax_test_outputs = nn.Softmax()(test_outputs)
            confidences, test_preds = torch.max(softmax_test_outputs, 1)

            for i in range(test_preds.shape[0]):
                confidence = confidences[i].data.item()
                predicted_class = class_num_to_class[test_preds[i].data.item()]
                # Check if prediction is correct
                if predicted_class is tissue_class:
                    counters[tissue_class] = (counters.get(tissue_class)[0]+1,
                                              counters.get(tissue_class)[1])
                    correctness.append(1)
                else:
                    correctness.append(0)

                counters[tissue_class] = [counters.get(tissue_class)[0],
                                          counters.get(tissue_class)[1]+1]
        print("{}: {:.3}".format(
            tissue_class,
            counters.get(tissue_class)[0]/counters.get(tissue_class)[1]))
        get_confidence_interval(correctness, CONFIDENCE_LEVEL)

    # Combined class accuracy
    correct, total = 0.0, 0.0
    for key, value in counters.items():
        correct += value[0]
        total += value[1]
    print("Combined: {:.3}".format(correct/total))

    # Confidence interval
    class_accuracies = []
    for key, value in counters.items():
        class_accuracies.append(1.0*value[0]/value[1])
    get_confidence_interval(class_accuracies, CONFIDENCE_LEVEL)


if __name__ == "__main__":
    # Directory containing folders to sort out each class number's corresponding string
    class_num_direc = ""
    # Direct path to your model
    model_path = ""
    # Folder containing classes to test on (e.g. "val/class1/class1/*.jpg" and "val/class2/class2/*.jpg" should exist)
    folder_to_test_on = ""
    get_accuracy(model_path, folder_to_test_on)
