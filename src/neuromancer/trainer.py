"""


"""
from copy import deepcopy

import torch
from torch.optim.lr_scheduler import ReduceLROnPlateau


import numpy as np

from neuromancer.loggers import BasicLogger
from neuromancer.problem import Problem
from neuromancer.callbacks import Callback
from neuromancer.problem import LitProblem
from neuromancer.dataset import LitDataModule
import lightning.pytorch as pl 
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.callbacks.early_stopping import EarlyStopping



def move_batch_to_device(batch, device="cpu"):
    return {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in batch.items()}


class LitTrainer(pl.Trainer):
    def __init__(self, epochs=1000, monitor_metric='dev_loss', train_metric='train_loss', dev_metric='dev_loss', test_metric='test_loss', eval_metric='train_loss',
                 patience=None, warmup=0, clip=100.0, custom_optimizer=None, save_weights=True, weight_path='./', weight_name=None, devices='auto', strategy='auto', accelerator='auto', profiler=None, \
                    custom_training_step=None):
        
        """
        A Neuromancer-specific custom trainer class inheriting from PyTorch Lightning's Trainer. 
        This class is mainly a wrapper to interface with the user through fit()

        For more information please see: https://lightning.ai/docs/pytorch/stable/common/trainer.html

        :param epochs: Number of epochs for training. Defaults to 1000.
        :param monitor_metric: Metric used for model checkpointing. Defaults to 'dev_loss'.
        :param train_metric: Metric for training. Defaults to 'train_loss'.
        :param dev_metric: Metric for development/validation. Defaults to 'dev_loss'.
        :param test_metric: Metric for testing. Defaults to 'test_loss'. Currently unused
        :param eval_metric: Metric for evaluation. Defaults to 'train_loss'.Currently unused
        :param patience: Number of epochs to wait for improvement before early stopping. Defaults to None (no patience)
        :param warmup: Number of warmup epochs. Defaults to 0.
        :param clip: Gradient clipping value, by norm. Defaults to 100.0.
        :param custom_optimizer: Optimizer to be used during training. If None (default), an Adam optimizer with learning rate of 0.001 will be used. 
        :param save_weights: Whether to save weights. Defaults to True.
        :param weight_path: Path to save weights. Defaults to './'.
        :param weight_name: Name of the weight file. By default, filename is None and will be set to '{epoch}-{step}', where “epoch” and “step” match the number of finished epoch and optimizer steps respectively.
        :param devices: Device assignment strategy. Defaults to 'auto'.
        :param strategy: Strategy for distributed training. Defaults to 'auto'.
        :param accelerator: Accelerator type. Defaults to 'auto'.
        :param profiler: Profiler to use. Defaults to None (no profiling)
        :param custom_training_step: Custom training step function, if desired. Defaults to None, in which case the standard training step procedure is executed

        """
        self.epochs = epochs
        self.monitor_metric = monitor_metric
        self.train_metric = train_metric
        self.dev_metric = dev_metric
        self.test_metric = test_metric
        self.eval_metric = eval_metric
        self.patience = patience
        self.warmup = warmup
        self.clip = clip
        self.save_weights = save_weights
        self.weight_path = weight_path
        self.weight_name = weight_name
        self.devices = devices
        self.custom_optimizer = custom_optimizer
        self.profiler = profiler 
        self.custom_training_step = custom_training_step

        self.lit_problem = None
        self.lit_data_module = None 

        
        self.early_stopping = EarlyStopping(monitor=self.monitor_metric, patience=self.patience)
        self.model_checkpoint = ModelCheckpoint(save_weights_only=True, monitor=self.monitor_metric, dirpath=self.weight_path, filename=self.weight_name, \
                                                mode='min', every_n_epochs=1, verbose=True)

        if self.patience and self.save_weights: 
            super().__init__(max_epochs=self.epochs, callbacks=[self.model_checkpoint, self.early_stopping], \
                             devices=self.devices, strategy=strategy, accelerator=accelerator, gradient_clip_val=clip, profiler=self.profiler)
        elif self.patience is None and self.save_weights: 
            super().__init__(max_epochs=self.epochs, callbacks=[self.model_checkpoint], devices=self.devices, \
                             strategy=strategy, accelerator=accelerator, gradient_clip_val=clip, profiler=self.profiler)
        elif self.patience and self.save_weights is False: 
            super().__init__(max_epochs=self.epochs, callbacks=[self.early_stopping], devices=self.devices, \
                             strategy=strategy, accelerator=accelerator, gradient_clip_val=clip, profiler=self.profiler)
        else: 
            super().__init__(max_epochs=self.epochs, devices=self.devices, strategy=strategy, accelerator=accelerator, \
                             gradient_clip_val=clip, profiler=self.profiler)

    def get_weights(self):
        # Get state dict of best model
        best_model = self.lit_problem.problem.state_dict()
        return best_model

    def fit(self, problem, data_setup_function, **kwargs):
        """
        Fits (trains) a base neuromancer Problem to a data defined by a data setup function). 
        This function will also instantiate a Lightning version of the provided Problem 
        and LightningDataModule associated with the data setup function

        :param problem: A Neuromancer Problem() we want to train/fit
        :param data_setup_function: A function that returns train/dev/test Neuromancer DictDatasets as well as batch_size to use
        """

        self.lit_problem = LitProblem(problem,self.train_metric, self.dev_metric, self.test_metric, custom_training_step=self.custom_training_step )
        self.lit_data_module = LitDataModule(data_setup_function, **kwargs)
        super().fit(self.lit_problem, self.lit_data_module)



class Trainer:
    """
    Class encapsulating boilerplate PyTorch training code. Training procedure is somewhat
    extensible through methods in Callback objects associated with training and evaluation
    waypoints.
    """
    def __init__(
        self,
        problem: Problem,
        train_data: torch.utils.data.DataLoader,
        dev_data: torch.utils.data.DataLoader = None,
        test_data: torch.utils.data.DataLoader = None,
        optimizer: torch.optim.Optimizer = None,
        logger: BasicLogger = None,
        callback=Callback(),
        lr_scheduler=False,
        epochs=1000,
        epoch_verbose=1,
        patience=5,
        warmup=0,
        train_metric="train_loss",
        dev_metric="dev_loss",
        test_metric="test_loss",
        eval_metric="dev_loss",
        eval_mode="min",
        clip=100.0,
        device="cpu"
    ):
        """

        :param problem: Object which defines multi-objective loss function and computational graph
        :param dataset: Batched (over chunks of time if sequence data) dataset for non-stochastic gradient descent
        :param optimizer: Pytorch optimizer
        :param logger: Object for logging results
        :param epochs: (int) Number of epochs to train
        :param epoch_verbose (int) printing epoch metric at each i-th epoch
        :param patience: (int) Number of epochs to allow no improvement before early stopping
        :param warmup: (int) How many epochs to wait before enacting early stopping policy
        :param eval_metric: (str) Performance metric for model selection and early stopping
        """
        self.model = problem
        self.optimizer = optimizer if optimizer is not None else torch.optim.Adam(problem.parameters(), 0.01, betas=(0.0, 0.9))
        self.train_data = train_data
        self.dev_data = dev_data
        self.test_data = test_data
        self.callback = callback
        self.logger = logger
        self.epochs = epochs
        self.current_epoch = 0
        self.epoch_verbose = epoch_verbose
        if logger is not None:
            self.logger.log_weights(self.model)
        self.train_metric = train_metric
        self.dev_metric = dev_metric
        self.test_metric = test_metric
        self.eval_metric = eval_metric
        self._eval_min = eval_mode == "min"
        self.lr_scheduler = (
            ReduceLROnPlateau(self.optimizer, mode="min", factor=0.5, patience=100)
            if lr_scheduler
            else None
        )
        self.patience = patience
        self.warmup = warmup
        self.badcount = 0
        self.clip = clip
        self.best_devloss = np.finfo(np.float32).max if self._eval_min else 0.
        self.best_model = deepcopy(self.model.state_dict())
        self.device = device

    def train(self):
        """
        Optimize model according to train_metric and validate per-epoch according to eval_metric.
        Trains for self.epochs and terminates early if self.patience threshold is exceeded.
        """
        self.callback.begin_train(self)

        try:
            for i in range(self.current_epoch, self.current_epoch+self.epochs):

                self.model.train()
                losses = []
                for t_batch in self.train_data:
                    t_batch['epoch'] = i
                    t_batch = move_batch_to_device(t_batch, self.device)
                    output = self.model(t_batch)
                    self.optimizer.zero_grad()
                    output[self.train_metric].backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.clip)
                    self.optimizer.step()
                    losses.append(output[self.train_metric])
                    self.callback.end_batch(self, output)

                output[f'mean_{self.train_metric}'] = torch.mean(torch.stack(losses))
                self.callback.begin_epoch(self, output)

                if self.lr_scheduler is not None:
                    self.lr_scheduler.step(output[f'mean_{self.train_metric}'])

                with torch.set_grad_enabled(self.model.grad_inference):
                    self.model.eval()
                    if self.dev_data is not None:
                        losses = []
                        for d_batch in self.dev_data:
                            d_batch = move_batch_to_device(d_batch, self.device)
                            eval_output = self.model(d_batch)
                            losses.append(eval_output[self.dev_metric])
                        eval_output[f'mean_{self.dev_metric}'] = torch.mean(torch.stack(losses))
                        output = {**output, **eval_output}
                    self.callback.begin_eval(self, output)  # Used for alternate dev evaluation

                    if (self._eval_min and output[self.eval_metric] < self.best_devloss)\
                            or (not self._eval_min and output[self.eval_metric] > self.best_devloss):
                        self.best_model = deepcopy(self.model.state_dict())
                        self.best_devloss = output[self.eval_metric]
                        self.badcount = 0
                    else:
                        if i > self.warmup:
                            self.badcount += 1
                    if self.logger is not None:
                        self.logger.log_metrics(output, step=i)
                    else:
                        mean_loss = output[f'mean_{self.train_metric}']
                        if i % (self.epoch_verbose) == 0:
                            print(f'epoch: {i}  {self.train_metric}: {mean_loss}')

                    self.callback.end_eval(self, output)  # visualizations

                    self.callback.end_epoch(self, output)

                    if self.badcount > self.patience:
                        print('Early stopping!!!')
                        break
                    self.current_epoch = i + 1

        except KeyboardInterrupt:
            print("Interrupted training loop.")

        self.callback.end_train(self, output)  # write training visualizations

        # Assign best weights to the model
        self.model.load_state_dict(self.best_model)

        if self.logger is not None:
            self.logger.log_artifacts({
                "best_model_state_dict.pth": self.best_model,
                "best_model.pth": self.model,
            })
        return self.best_model

    def test(self, best_model):
        """
        Evaluate the model on all data splits.
        """
        self.model.load_state_dict(best_model, strict=False)
        self.model.eval()

        with torch.set_grad_enabled(self.model.grad_inference):
            self.callback.begin_test(self)
            output = {}
            for dset, metric in zip([self.train_data, self.dev_data, self.test_data],
                                    [self.train_metric, self.dev_metric, self.test_metric]):
                losses = []
                for batch in dset:
                    batch = move_batch_to_device(batch, self.device)
                    batch_output = self.model(batch)
                    losses.append(batch_output[metric])
                output[f'mean_{metric}'] = torch.mean(torch.stack(losses))
                output = {**output, **batch_output}

        self.callback.end_test(self, output)

        if self.logger is not None:
            self.logger.log_metrics({f"best_{k}": v for k, v in output.items()})

        return output

    def evaluate(self, best_model):
        """
        This method is deprecated. Use self.test instead.
        """
        return self.test(best_model)