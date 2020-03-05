import csv
import numpy as np

from torch.utils.data import DataLoader
import torchvision.datasets as datasets
import torchvision.transforms as transforms

class DataHelper():
    def __init__(self, sequence_max_length=1024):
        self.alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:’"/|_#$%ˆ&*˜‘+=<>()[]{} '
        self.char_dict = {}
        self.UNK = 68
        self.sequence_max_length = sequence_max_length
        for i,c in enumerate(self.alphabet):
            self.char_dict[c] = i+1

    def char2vec(self, text):
        data = np.zeros(self.sequence_max_length)
        for i in range(0, len(text)):
            if i >= self.sequence_max_length:
                return data
            elif text[i] in self.char_dict:
                data[i] = self.char_dict[text[i]]
            else:
                data[i] = self.UNK
        return np.array(data)

    def load_csv_file(self, filename, num_classes, train=True, one_hot=False):
        if train:
            s1 = 120000
        else:
            s1 = 7600
        all_data =np.zeros(shape=(s1, self.sequence_max_length), dtype=np.int)
        labels =np.zeros(shape=(s1, 1), dtype=np.int)

        # labels = []
        with open(filename) as f:
            reader = csv.DictReader(f, fieldnames=['class'], restkey='fields')
            # reader = np.genfromtxt(f)
            for i,row in enumerate(reader):
                if one_hot:
                    one_hot = np.zeros(num_classes)
                    one_hot[int(row['class']) - 1] = 1
                    labels[i] = one_hot
                else:
                    labels[i] = int(row['class']) - 1
                text = row['fields'][-1].lower()
                all_data[i] = self.char2vec(text)
        f.close()
        return all_data, labels

    def load_dataset(self, dataset_path):
        with open(dataset_path+"classes.txt") as f:
            classes = []
            for line in f:
                classes.append(line.strip())
        f.close()
        num_classes = len(classes)
        train_data, train_label = self.load_csv_file(dataset_path + 'train.csv', num_classes)
        test_data, test_label = self.load_csv_file(dataset_path + 'test.csv', num_classes, train=False)
        print(train_data.shape, test_data.shape)
        return train_data, train_label, test_data, test_label

    def batch_iter(self, data, batch_size, num_epochs, shuffle=True):
        data_size = len(data)
        num_batches_per_epoch = int((len(data)-1)/batch_size) + 1
        # for epoch in range(num_epochs):
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            shuffled_data = data[shuffle_indices]
        else:
            shuffled_data = data
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            batch = shuffled_data[start_index:end_index]
            # batch_data, label = batch[:,  self.sequence_max_length-1], batch[:, -1]
            batch_data, label = np.split(batch, [self.sequence_max_length],axis=1)
            yield np.array(batch_data, dtype=np.int), label


def get_mnist_loaders(batch_size=128, test_batch_size=1000, perc=1.0):
    transform_train = transforms.Compose([
            transforms.RandomCrop(28, padding=4),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,)),
        ])

    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,)),
    ])

    train_loader = DataLoader(
        datasets.MNIST(root='.data/mnist', train=True, download=True, transform=transform_train), batch_size=batch_size,
        shuffle=True, num_workers=2, drop_last=True
    )

    train_eval_loader = DataLoader(
        datasets.MNIST(root='.data/mnist', train=True, download=True, transform=transform_test),
        batch_size=test_batch_size, shuffle=True, num_workers=2, drop_last=True
    )

    test_loader = DataLoader(
        datasets.MNIST(root='.data/mnist', train=False, download=True, transform=transform_test),
        batch_size=test_batch_size, shuffle=False, num_workers=2, drop_last=True
    )

    return train_loader, test_loader, train_eval_loader

def get_gz_loaders(batch_size=128, test_batch_size=1000, perc=1.0):
    transform_train = transforms.Compose([
            # transforms.RandomCrop(28, padding=4),
            transforms.Grayscale(num_output_channels=1),
            # transforms.CenterCrop((64,64)),
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,)),
        ])

    transform_test = transforms.Compose([
        transforms.Grayscale(num_output_channels=1),
        # transforms.CenterCrop((64,64)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,)),
    ])

    gz_root = '/mnt/f/IITH/research/physics/galaxy_zoo/\
                GalaxyClassification/imageFolder_small'

    train_loader = DataLoader(
        datasets.ImageFolder(root=gz_root
            # ,train=True, download=True
            , transform=transform_train
        ),batch_size=batch_size,
        shuffle=True, num_workers=2, drop_last=True
    )

    train_eval_loader = DataLoader(
        datasets.ImageFolder(root=gz_root
            # , train=True, download=True
            , transform=transform_test
            ),batch_size=test_batch_size, shuffle=True, num_workers=2, drop_last=True
    )

    test_loader = DataLoader(
        datasets.ImageFolder(root=gz_root
            # , train=False, download=True
            , transform=transform_test
            ),batch_size=test_batch_size, shuffle=False, num_workers=2, drop_last=True
    )

    return train_loader, test_loader, train_eval_loader


def get_cifar_loaders(batch_size=128, test_batch_size=1000):

    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])


    train_loader = DataLoader(
        datasets.CIFAR10(root='.data/cifar', train=True, download=True, transform=transform_train), batch_size=batch_size,
        shuffle=True, num_workers=3)

    test_loader = DataLoader(
        datasets.CIFAR10(root='.data/cifar', train=False, download=True, transform=transform_test),
        batch_size=test_batch_size, shuffle=False, num_workers=3)

    return train_loader, test_loader, None


if __name__ == '__main__':
    sequence_max_length = 1014
    batch_size = 32
    num_epochs = 32
    database_path = '.data/ag_news/'
    data_helper = DataHelper(sequence_max_length=sequence_max_length)
    train_data, train_label, test_data, test_label = data_helper.load_dataset(database_path)
    train_batches = data_helper.batch_iter(np.column_stack((train_data, train_label)), batch_size, num_epochs)
    for batch in train_batches:
        train_data_b,label = batch
        break