from wsiprocess.pytorch.wsidataset import WSIDataset
from wsiprocess.pytorch.utils import SegmentationDataset
from torch.utils.data import DataLoader

command = "segmentation CMU-1.ndpi CMU-1_segmentation.xml --verbose --save_to ./segmentationtest --ext jpg"
dataset = SegmentationDataset(WSIDataset(command=command.split(" ")))
dataloader = DataLoader(dataset, batch_size=32, shuffle=False, num_workers=4)

for image, mask in dataloader:
    print(image.shape, mask.shape)
    import sys
    sys.exit()
