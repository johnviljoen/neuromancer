# NeuroMANCER
## Neural Modules with Adaptive Nonlinear Constraints and 	Efficient Regularizations
![UML diagram](figs/class_diagram.png)

## Setup

##### Clone and install neuromancer, linear maps, and emulator packages
```console
user@machine:~$ mkdir ecosystem; cd ecosystem
user@machine:~$ git clone https://stash.pnnl.gov/scm/deepmpc/neuromancer.git
user@machine:~$ git clone https://stash.pnnl.gov/scm/deepmpc/psl.git
user@machine:~$ git clone https://stash.pnnl.gov/scm/deepmpc/slim.git

# Resulting file structure:
    ecosystem/
        neuromancer/
        psl/
        slim/
```

##### Create the environment via .yml (Linux)

```console
user@machine:~$ conda env create -f env.yml
(neuromancer) user@machine:~$ source activate neuromancer
```

##### If .yml env creation fails create the environment manually

```console
user@machine:~$ conda config --add channels conda-forge pytorch
user@machine:~$ conda create -n neuromancer python=3.7
user@machine:~$ source activate neuromancer
(neuromancer) user@machine:~$ conda install pytorch torchvision cudatoolkit=9.0 -c pytorch
(neuromancer) user@machine:~$ conda install scipy pandas matplotlib control pyts numba scikit-learn mlflow dill
(neuromancer) user@machine:~$ conda install -c powerai gym
```

##### install neuromancer ecosystem 

```console
(neuromancer) user@machine:~$ cd psl
(neuromancer) user@machine:~$ python setup.py develop
(neuromancer) user@machine:~$ cd ../slim
(neuromancer) user@machine:~$ python setup.py develop
(neuromancer) user@machine:~$ cd ../neuromancer
(neuromancer) user@machine:~$ python setup.py develop
```

### TODO
    [ ] Mini-batching
    [ ] Learn-rate scheduling
    [ ] Early stopping
    [ ] Multiple experiment time-series data
    [ ] Visualize learnable loss function evolution
    [ ] Generalize sliding window between 1 and nsteps
    [ ] Re-implement RNN state preservation for open loop simulation
    [ ] full trajectory estimators: This will entail only taking the first N-steps for all the non-static inputs
    [ ] Pytorch Extended Kalman Filter: 
            https://filterpy.readthedocs.io/en/latest/_modules/filterpy/kalman/EKF.html
    [ ] Implement LQR policy, similar structure to Linear Kalman Filter: 
            Scipy reference https://nbviewer.jupyter.org/url/argmin.net/code/little_LQR_demo.ipynb
    [ ] WandB logger
    [ ] stream plots for phase spaces of ODEs
    [ ] generate correlation network - https://python-graph-gallery.com/327-network-from-correlation-matrix/
    [ ] plot information-theoretic measures for time series data - 
            https: // elife - asu.github.io / PyInform / timeseries.html
    [ ] Doc strings
    [ ] Sphinx docs
    [ ] Package distribution via conda or pypi
    [ ] Look at this testing software to for automatic wider test coverage: 
            https://hypothesis.readthedocs.io/en/latest/