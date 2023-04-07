from wsiprocess.pytorch.wsidataset import WSIDataset
from wsiprocess.pytorch.utils import ClassificationDataset
from torch.utils.data import DataLoader


def foreground_fn(x):
    # inverse of input mask
    x = 1 - x
    return x


command = "classification CMU-1.ndpi CMU-1_classification.xml --on_foreground 0.01 --on_annotation 0.01 --no_patches --verbose --save_to ./classification_maskfn --ext jpg"
dataset = ClassificationDataset(WSIDataset(command=command.split(" "), foreground_fn=foreground_fn))
label_names = dataset.labels.columns
dataloader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=4)

for image, label in dataloader:

    print(image.shape, label.shape)
    import sys
    sys.exit()
