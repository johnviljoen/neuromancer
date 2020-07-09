"""
"""
from copy import deepcopy
import torch
import numpy as np
from logger import BasicLogger
from visuals import Visualizer, NoOpVisualizer
from loops import Problem
from dataset import Dataset


class Trainer:

    def __init__(self, problem: Problem, dataset: Dataset, optimizer: torch.optim.Optimizer,
                 logger: BasicLogger = BasicLogger(), visualizer: Visualizer = NoOpVisualizer(), epochs=1000):
        super().__init__()
        self.model = problem
        self.optimizer = optimizer
        self.dataset = dataset
        self.logger = logger
        self.visualizer = visualizer
        self.epochs = epochs
        self.logger.log_weights(self.model)

    def train(self):

        best_looploss = np.finfo(np.float32).max
        best_model = deepcopy(self.model.state_dict())
        self.visualizer.train()

        for i in range(self.epochs):

            self.model.train()
            output = self.model(self.dataset.train_data)
            self.optimizer.zero_grad()
            output['loss'].backward()
            self.optimizer.step()

            with torch.no_grad():
                self.model.eval()
                dev_nstep_output = self.model(self.dataset.dev_data)
                dev_loop_output = self.model(self.dataset.dev_loop)
                self.logger.log_metrics({**dev_nstep_output, **dev_loop_output}, step=i)
                if dev_loop_output['loss'] < best_looploss:
                    best_model = deepcopy(self.model.state_dict())
                    best_looploss = dev_loop_output['dev_loop_loss']
                self.visualizer.plot({**dev_nstep_output, **dev_loop_output}, self.dataset, self.model.state_dict())

        plots = self.visualizer.output()
        self.logger.save_artifacts({'best_model.pth': best_model, **plots})

        return best_model

    def evaluate(self, best_model):

        self.visualizer.eval()
        self.model.load_state_dict(best_model)

        with torch.no_grad():
            ########################################
            ########## NSTEP TRAIN RESPONSE ########
            ########################################
            all_output = dict()
            for dset, dname in zip([self.dataset.train_data, self.dataset.dev_data, self.dataset.test_data],
                                   ['train', 'dev', 'test']):
                output = self.model(dset)
                self.logger.log_metrics(output)
                all_output = {**all_output, **output}
            self.visualizer.plot(all_output, self.dataset, best_model)

            ########################################
            ########## OPEN LOOP RESPONSE ##########
            ########################################
            all_output = dict()
            for data, dname in zip([self.dataset.train_loop, self.dataset.dev_loop, self.dataset.test_loop],
                                   ['train', 'dev', 'test']):
                output = self.model(data)
                self.logger.log_metrics(output)
                all_output = {**all_output, **output}
            self.visualizer.plot(all_output, self.dataset, best_model)
        plots = self.visualizer.output()
        self.logger.log_artifacts(plots)





