from wsiprocess.pytorch.wsidataset import WSIDataset, WSIsDataset
from torch.utils.data import DataLoader

command = "evaluation {} --no_patches --verbose -st ./evaluationtest"
datasets = []
for wsi in ["CMU-1.ndpi", "CMU-2.ndpi"]:
    datasets.append(WSIDataset(command=command.format(wsi).split(" ")))
dataset = WSIsDataset(datasets)

dataloader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=4)

for image in dataloader:
    print(image.shape)
    import sys
    sys.exit()
