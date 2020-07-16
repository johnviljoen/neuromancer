"""
# TODO: include reference in the datafiles and emulators
# TODO: extend datasets with time-varying constraints Ymin, Ymax, Umin, Umax
# TODO put in assert to check data equality after manipulations
# TODO Moving horizon dataset
"""
import os
from scipy.io import loadmat
import numpy as np
import pandas as pd
import torch
import plot
import emulators
import matplotlib.pyplot as plt


def min_max_denorm(M, Mmin, Mmax):
    """
    denormalize min max norm
    :param M: (2-d np.array) Data to be normalized
    :param Mmin: (int) Minimum value
    :param Mmax: (int) Maximum value
    :return: (2-d np.array) Un-normalized data
    """
    M_denorm = M*(Mmax - Mmin) + Mmin
    return np.nan_to_num(M_denorm)


def batch_data(data, nsteps):
    """

    :param data: np.array shape=(nsim, dim)
    :param nsteps: (int) n-step prediction horizon
    :return: torch.tensor shape=(nsteps, nsamples, dim)
    """
    nsplits = (data.shape[0]) // nsteps
    leftover = (data.shape[0]) % nsteps
    data = np.stack(np.split(data[:data.shape[0] - leftover], nsplits))  # nchunks X nsteps X nfeatures
    return torch.tensor(data, dtype=torch.float32).transpose(0, 1)  # nsteps X nsamples X nfeatures


def unbatch_data(data):
    """
    Data put back together into original sequence.

    :param data: (torch.Tensor, shape=(nsteps, nsamples, dim)
    :return:  (torch.Tensor, shape=(nsim, 1, dim)
    """
    return data.transpose(0, 1).reshape(-1, 1, data.shape[-1])


class DataDict(dict):
    """
    So we can add a name property to the dataset dictionaries
    """
    pass


class Dataset:

    def __init__(self, system=None, nsim=None, norm='UDY',
                 nsteps=32, device='cpu', sequences=dict(),
                 savedir='test'):
        """

        :param system: (str) Identifier for dataset.
        :param nsim: (int) Total number of time steps in data sequence
        :param norm: (str) String of letters corresponding to data to be normalized
        :param nsteps: (int) N-step prediction horizon for batching data
        :param device: (str) String identifier of device to place data on, e.g. 'cpu', 'cuda:0'
        :param sequences: (dict str: np.array) Dictionary of supplemental data
        """
        print(system)
        self.savedir = savedir
        self.system, self.nsim, self.norm, self.nsteps, self.device = system, nsim, norm, nsteps, device
        data = self.load_data()
        for k, v in sequences.items():
            assert v.shape[0] == data['Y'][0].shape
        data = {**data, **sequences}
        self.data = data
        self.min_max_norms, self.dims, nstep_data, loop_data = dict(), dict(), dict(), dict()
        for k, v in data.items():
            v = v.reshape(v.shape[0], -1)
            vnorm, vmin, vmax = self.normalize(v)
            v = vnorm
            self.min_max_norms.update({k+'min': vmin, k+'max': vmax})
            self.dims[k], self.dims[k+'p'], self.dims[k+'f'] = v.shape[1], v.shape[1], v.shape[1]
            loop_data[k+'p'] = torch.tensor(v[:-nsteps], dtype=torch.float32).to(device)
            loop_data[k + 'f'] = torch.tensor(v[nsteps:], dtype=torch.float32).to(device)
            nstep_data[k + 'p'] = batch_data(loop_data[k+'p'], nsteps).to(device)
            nstep_data[k + 'f'] = batch_data(loop_data[k+'f'], nsteps).to(device)
            data[k] = v
        plot.plot_traj(data, figname=os.path.join(self.savedir, f'{system}.png'))

        self.train_data, self.dev_data, self.test_data = self.split_train_test_dev(nstep_data)
        self.train_loop = self.unbatch(self.train_data)
        self.dev_loop = self.unbatch(self.dev_data)
        self.test_loop = self.unbatch(self.test_data)
        self.train_data.name, self.dev_data.name, self.test_data.name = 'nstep_train', 'nstep_dev', 'nstep_test'
        self.train_loop.name, self.dev_loop.name, self.test_loop.name = 'loop_train', 'loop_dev', 'loop_test'
        plot.plot_traj({k: torch.cat([self.train_loop[k],
                                      self.dev_loop[k],
                                      self.test_loop[k]]).squeeze(1).cpu().detach().numpy()
                        for k in self.train_data.keys()}, figname=os.path.join(self.savedir, f'{system}_open.png'))
        plt.close('all')

    def load_data(self):
        assert self.system is None and len(self.sequences) > 0, \
            'User must provide data via the sequences argument for basic Dataset. ' +\
            'Use FileDataset or EmulatorDataset for predefined datasets'
        return dict()

    def normalize(self, M, Mmin=None, Mmax=None):
            """
            :param M: (2-d np.array) Data to be normalized
            :param Mmin: (int) Optional minimum. If not provided is inferred from data.
            :param Mmax: (int) Optional maximum. If not provided is inferred from data.
            :return: (2-d np.array) Min-max normalized data
            """
            Mmin = M.min(axis=0).reshape(1, -1) if Mmin is None else Mmin
            Mmax = M.max(axis=0).reshape(1, -1) if Mmax is None else Mmax
            M_norm = (M - Mmin) / (Mmax - Mmin)
            return np.nan_to_num(M_norm), Mmin.squeeze(), Mmax.squeeze()

    def split_train_test_dev(self, data):
        """

        :param data: (dict, str: 3-d np.array) Complete dataset. dims=(nsteps, nsamples, dim)
        :return: (3-tuple) Dictionarys for train, dev, and test sets
        """
        train_data, dev_data, test_data = DataDict(), DataDict(), DataDict()
        train_idx = (list(data.values())[0].shape[1] // 3)
        dev_idx = train_idx * 2
        for k, v in data.items():
            if data is not None:
                train_data[k] = v[:, :train_idx, :]
                dev_data[k] = v[:, train_idx:dev_idx, :]
                test_data[k] = v[:, dev_idx:, :]
        return train_data, dev_data, test_data

    def unbatch(self, data):
        """

        :param data: (dict, str: 3-d np.array) Data broken into samples of n-step prediction horizon sequences
        :return: (dict, str: 3-d np.array) Data put back together into original sequence. dims=(nsim, 1, dim)
        """
        unbatched_data = DataDict()
        for k, v in data.items():
            unbatched_data[k] = unbatch_data(v)
        return unbatched_data


class EmulatorDataset(Dataset):

    def load_data(self):
        """
        dataset creation from the emulator. system argument to init should be the name of a registered emulator
        return: (dict, str: 2-d np.array)
        """
        systems = emulators.systems  # list of available emulators
        model = systems[self.system]()  # instantiate model class
        if isinstance(model, emulators.GymWrapper):
            model.parameters(system=self.system)
        elif isinstance(model, emulators.BuildingEnvelope):
            model.parameters(system=self.system, linear=True)
        else:
            model.parameters()

        X, Y, U, D = model.simulate(nsim=self.nsim)  # simulate open loop
        data = dict()
        for d, k in zip([Y, U, D], ['Y', 'U', 'D']):
            if d is not None:
                data[k] = d
        return data


class FileDataset(Dataset):

    def load_data(self):
        """
        Load data from files. system argument to init should be a file path to the dataset file
        :return: (dict, str: 2-d np.array)
        """
        ninit = 0
        Y, U, D = None, None, None
        systems_datapaths = {'tank': './datasets/NLIN_SISO_two_tank/NLIN_two_tank_SISO.mat',
                             'vehicle3': './datasets/NLIN_MIMO_vehicle/NLIN_MIMO_vehicle3.mat',
                             'aero': './datasets/NLIN_MIMO_Aerodynamic/NLIN_MIMO_Aerodynamic.mat',
                             'flexy_air': './datasets/Flexy_air/flexy_air_data.csv'}
        if self.system in systems_datapaths.keys():
            file_path = systems_datapaths[self.system]
        else:
            file_path = self.system
        file_type = file_path.split(".")[-1]
        if file_type == 'mat':
            file = loadmat(file_path)
            Y = file.get("y", None)  # outputs
            U = file.get("u", None)  # inputs
            D = file.get("d", None)  # disturbances
        elif file_type == 'csv':
            data = pd.read_csv(file_path)
            Y = data.filter(regex='y').values if data.filter(regex='y').values.size != 0 else None
            U = data.filter(regex='u').values if data.filter(regex='u').values.size != 0 else None
            D = data.filter(regex='d').values if data.filter(regex='d').values.size != 0 else None
        data = dict()
        for d, k in zip([Y, U, D], ['Y', 'U', 'D']):
            if d is not None:
                data[k] = d[ninit:self.nsim, :]
        return data


if __name__ == '__main__':

    systems = {'tank': 'datafile', 'vehicle3': 'datafile', 'aero': 'datafile', 'flexy_air': 'datafile',
               'TwoTank': 'emulator', 'LorenzSystem': 'emulator',
               'Lorenz96': 'emulator', 'VanDerPol': 'emulator', 'ThomasAttractor': 'emulator',
               'RosslerAttractor': 'emulator', 'LotkaVolterra': 'emulator', 'Brusselator1D': 'emulator',
               'ChuaCircuit': 'emulator', 'Duffing': 'emulator', 'UniversalOscillator': 'emulator',
               'HindmarshRose': 'emulator',
               'SimpleSingleZone': 'emulator', 'Pendulum-v0': 'emulator',
               'CartPole-v1': 'emulator', 'Acrobot-v1': 'emulator',
               'MountainCar-v0': 'emulator', 'MountainCarContinuous-v0': 'emulator',
               'Reno_full': 'emulator', 'Reno_ROM40': 'emulator', 'RenoLight_full': 'emulator',
               'RenoLight_ROM40': 'emulator', 'Old_full': 'emulator',
               'Old_ROM40': 'emulator', 'HollandschHuys_full': 'emulator',
               'HollandschHuys_ROM100': 'emulator', 'Infrax_full': 'emulator',
               'Infrax_ROM100': 'emulator'}

    for system, data_type in systems.items():
        if data_type == 'emulator':
            dataset = EmulatorDataset(system)
        elif data_type == 'datafile':
            dataset = FileDataset(system)


