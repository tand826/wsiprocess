from wsiprocess.pytorch.wsidataset import WSIDataset
from torch.utils.data import DataLoader

command = "evaluation {} --no_patches --verbose -st ./evaluationtest"

dataset = WSIDataset(command=command.format("CMU-1.ndpi").split(" "))
dataloader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=4)

for image in dataloader:
    print(image)
    import sys
    sys.exit()
