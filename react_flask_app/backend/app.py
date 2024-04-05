from flask import Flask, render_template, request, jsonify, g 
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from matplotlib.lines import Line2D

from neuromancer import psl
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader

from neuromancer.system import Node, System
from neuromancer.dynamics import integrators, ode
from neuromancer.trainer import Trainer
from neuromancer.problem import Problem
from neuromancer.loggers import BasicLogger
from neuromancer.dataset import DictDataset
from neuromancer.constraint import variable
from neuromancer.loss import PenaltyLoss
from neuromancer. modules import blocks
from neuromancer.psl.plot import get_colors
import torch 
import os 
import sys
import pprint
import json 
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
problem_components = {'Components':[]}
dataset_dict = {}
canvas_map = None 
edges = None 
nodes = None 
child_blocks = {}
loss_list = [] 
chosen_integrator = None 
DATASET_ID_FOUND = "None" 
traversed_ids = {}
problem_dict = {} 
problem_id = ""

variables_list = {}
x = variable("X")
xhat = variable('xn')[:, :-1, :]



def get_data(sys, nsim, nsteps, ts, bs):
    """
    :param nsteps: (int) Number of timesteps for each batch of training data
    :param sys: (psl.system)
    :param ts: (float) step size
    :param bs: (int) batch size

    """
    train_sim, dev_sim, test_sim = [sys.simulate(nsim=nsim, ts=ts) for i in range(3)]
    nx = sys.nx
    nbatch = nsim//nsteps
    length = (nsim//nsteps) * nsteps

    trainX = train_sim['X'][:length].reshape(nbatch, nsteps, nx)
    trainX = torch.tensor(trainX, dtype=torch.float32)
    train_data = DictDataset({'X': trainX, 'xn': trainX[:, 0:1, :]}, name='train')
    train_loader = DataLoader(train_data, batch_size=bs,
                              collate_fn=train_data.collate_fn, shuffle=True)

    devX = dev_sim['X'][:length].reshape(nbatch, nsteps, nx)
    devX = torch.tensor(devX, dtype=torch.float32)
    dev_data = DictDataset({'X': devX, 'xn': devX[:, 0:1, :]}, name='dev')
    dev_loader = DataLoader(dev_data, batch_size=bs,
                            collate_fn=dev_data.collate_fn, shuffle=True)

    testX = test_sim['X'][:length].reshape(1, nsim, nx)
    testX = torch.tensor(testX, dtype=torch.float32)
    test_data = {'X': testX, 'xn': testX[:, 0:1, :]}

    return train_loader, dev_loader, test_data






@app.route('/plot-system', methods=['POST'])
def plot_system(): 

    global dataset_dict
   

    if not request.is_json:
        return jsonify({'error': 'Request must contain JSON data'}), 400
    
    # Get the JSON data from the request body
    data = request.get_json()
   
    
    
    system_name = data['system']

    num_simulations = int(data['numSimulations'])
    id = data['id']
    
    system = psl.systems[system_name]
    modelSystem = system()
    ts = modelSystem.ts
    raw = modelSystem.simulate(nsim=num_simulations, ts=ts)
    data = {"Y": raw['Y'].tolist()}
    
    
    response_data = {
        'System_name': system_name, 
        'Num_simulations': num_simulations, 
        'Y_data': data,
        'nx': modelSystem.nx, 
    }
    
    train_loader, dev_loader, test_data = get_data(modelSystem, num_simulations, nsteps=2, ts=ts, bs=100)
    data_instance_dict = {}
    data_instance_dict['train_loader'] = train_loader 
    data_instance_dict['dev_loader'] = dev_loader 
    data_instance_dict['test_data'] = test_data 
    data_instance_dict['nx'] = modelSystem.nx
    data_instance_dict['bs'] = 100
    data_instance_dict['ts'] = ts
    data_instance_dict['nsteps'] = 2 
    data_instance_dict['num_simulations'] = num_simulations 
    data_instance_dict['system_name'] = system_name

    dataset_dict[id] = data_instance_dict
    
    return jsonify(response_data)
        
 



def pltOL_App(Y, Ytrain=None, U=None, D=None, X=None, figname=None):
    """
    plot trained open loop dataset
    Ytrue: ground truth training signal
    Ytrain: trained model response
    """

    plot_setup = [(name, notation, array) for
                  name, notation, array in
                  zip(['Outputs', 'States', 'Inputs', 'Disturbances'],
                      ['Y', 'X', 'U', 'D'], [Y, X, U, D]) if
                  array is not None]
    img_buffer = BytesIO()
    fig, ax = plt.subplots(nrows=len(plot_setup), ncols=1, figsize=(20, 16), squeeze=False)

    custom_lines = [Line2D([0], [0], color='gray', lw=4, linestyle='-'),
                    Line2D([0], [0], color='gray', lw=4, linestyle='--')]
    for j, (name, notation, array) in enumerate(plot_setup):
        if notation == 'Y' and Ytrain is not None:
            colors = get_colors(array.shape[1]+1)
            for k in range(array.shape[1]):
                ax[j, 0].plot(Ytrain[:, k], '--', linewidth=2, c=colors[k])
                ax[j, 0].plot(array[:, k], '-', linewidth=2, c=colors[k])
                ax[j, 0].legend(custom_lines, ['True', 'Pred'])
        else:
            ax[j, 0].plot(array, linewidth=2)
        ax[j, 0].grid(True)
        ax[j, 0].set_title(name, fontsize=14)
        ax[j, 0].set_xlabel('Time', fontsize=14)
        ax[j, 0].set_ylabel(notation, fontsize=14)
        ax[j, 0].tick_params(axis='x', labelsize=14)
        ax[j, 0].tick_params(axis='y', labelsize=14)
    #plt.tight_layout()

    # Save the plot to a BytesIO object

    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    # Encode the image to base64
    img_str = base64.b64encode(img_buffer.read()).decode('utf-8')

    plt.close()

    return f"data:image/png;base64,{img_str}"


string_fix = lambda x:  x[1:-1]

@app.route('/receive_problem_data', methods=['POST'])
def receive_problem_data():
    global canvas_map 
    global nodes 
    global edges 
    global problem_dict
    global problem_id
    
    if not request.is_json:
        return jsonify({'error': 'Request must contain JSON data'}), 400
 
    data = request.get_json()['data']

    canvas_map_entries = data['canvas_map_entries']
    problem_id = data['problem_id']
    canvas_map = {}
    problem_dict[problem_id] = None #initiaize to none
    
    for entry in canvas_map_entries:
        id = (entry['id'])
        block_info = entry['blockInfo']
      
        new_block_info = {}
        for k,v in block_info.items(): 
            new_block_info[k] = v
            
        canvas_map[id] = new_block_info
    print("CANVAS MAP ")
    print(canvas_map)


    nodes = data['nodes']
    edges = data['edges']

    find_dataset_info()
    parse_edges(edges)
    construct_problem_after_parsing()

    # Do whatever processing you need with canvas_map, nodes, and edges

    return jsonify({'message': 'Problem created successfully =' + problem_id})


        

def create_neuromancer_block(block_info_dict): 
    info_from_canvas_map = canvas_map[block_info_dict['id']]
    block_name = block_info_dict['name']
    data_instance_dict = dataset_dict[DATASET_ID_FOUND]
    nx = data_instance_dict['nx']
    if block_name == 'mlp': 
        fx = blocks.MLP(nx, nx, bias=True,
                     linear_map=torch.nn.Linear,
                     nonlin=torch.nn.ReLU,
                     hsizes=[60, 60, 60])
    elif block_name == 'resmlp': 
        fx = blocks.ResMLP(nx, nx, bias=True,
                     linear_map=torch.nn.Linear,
                     nonlin=torch.nn.ReLU,
                     hsizes=[60, 60, 60])
        
    elif block_name == 'rnn': 
        fx = blocks.RNN(nx, nx, bias=True,
                     linear_map=torch.nn.Linear,
                     nonlin=torch.nn.ReLU,
                     hsizes=[60, 60, 60])
    return fx 

def create_neuromancer_integrator(block_info_dict, my_child_block): 
    info_from_canvas_map = canvas_map[block_info_dict['id']]
    block_name = block_info_dict['name']
    data_instance_dict = dataset_dict[DATASET_ID_FOUND]
    ts = data_instance_dict['ts']
    if block_name == 'diff_eq_integrator -- euler': 
        integrator = integrators.DiffEqIntegrator(my_child_block, h=ts, method='euler')
    elif block_name == 'diff_eq_integrator -- rk4': 
        integrator = integrators.DiffEqIntegrator(my_child_block, h=ts, method='rk4')
 
    return integrator 

def create_neuromancer_loss(block_info_dict): 
    global x 
    global xhat
    global loss_list
    global variable_list

    info_from_canvas_map = canvas_map[block_info_dict['id']]
    block_name = block_info_dict['name']
    data_instance_dict = dataset_dict[DATASET_ID_FOUND]
    if block_name == 'reference tracking': 
        reference_loss = (xhat == x)^2
        reference_loss.name = "ref_loss"       
        loss_list.append(reference_loss)     
    elif block_name == 'finite difference':
        xFD = (x[:, 1:, :] - x[:, :-1, :])
        xhatFD = (xhat[:, 1:, :] - xhat[:, :-1, :] )
        variables_list['xhatFD'] = xhatFD
        variable_list['xFD'] = xFD
        
        fd_loss = 2.*(variable_list['xFD'] == variables_list['xhatFD'])^2
        fd_loss.name = 'FD_loss'
        
        loss_list.append(fd_loss)
 



def lookup(id): 
    if canvas_map is not None: 
        if id in canvas_map: 
            block_info_dict = canvas_map[id]
            class_type = block_info_dict['classType']
            return class_type, block_info_dict
    return None, None



def find_dataset_info(): 
    global DATASET_ID_FOUND 
    
    for edge in edges: 
        src_id = edge['source']
        target_id = edge['target']
        print("SRC ID ", src_id)
        src_class, src_block_info_dict = lookup(src_id)
        if src_class == 'neuromancer_dataset': 

            DATASET_ID_FOUND = src_id 
            break 

    return 


def get_edges_from_node(node, edges):
    [{'source': 'dataset_z96hj5433', 'sourceHandle': None, 'target': ':rb:', 'targetHandle': None, 'id': 'reactflow__edge-dataset_z96hj5433-:rb:'}, {'source': ':rb:', 'sourceHandle': None, 'target': ':r7:', 'targetHandle': None, 'id': 'reactflow__edge-:rb:-:r7:'}]

    node_edges = []
    print("in get edges from node")
    print(edges)
    for edge in edges:
        start = edge['source']
        end = edge['target']
        if start == node:
            node_edges.append(edge)
    return node_edges






def parse_edges(edge_list, only_targets=False): 
    if len(edge_list) == 0: 
        return
    global child_blocks
    global chosen_integrator
    global traversed_ids
    global loss_list


    for edge in edge_list: 
        src_id = edge['source']
        target_id = edge['target']
        print("SRC ID ", src_id)
        print("TARGET ID ", target_id)
        print("traversed ids ", traversed_ids)

        if not only_targets: 
            if not src_id in list(traversed_ids.keys()): 
                src_class, src_block_info_dict = lookup(src_id)
                if src_class == 'neuromancer_dataset': 
                    traversed_ids[src_id] = True 
                    pass 
                elif src_class == 'neuromancer_block': 
                    block = create_neuromancer_block(src_block_info_dict)
                    child_blocks[src_id] = block #i am the child block of this source 
                    traversed_ids[src_id] = True 
                    print("SOURCE   REATED BLOCK")
                elif src_class == 'neuromancer_loss': 
                    create_neuromancer_loss(src_block_info_dict)
                 
                    traversed_ids[src_id] = True 
                    print("SOURCE   CREATED LOSS")
                    
                elif src_class == 'neuromancer_integrator': 
                    edges_from_here_list = get_edges_from_node(src_id, edges)
                    print("RUNNING ON NEW EDGE LIST ", edges_from_here_list)
                    parse_edges(edges_from_here_list, only_targets=True)
                    if src_id in child_blocks: 
                        my_child_block = child_blocks[src_id]
                        integrator =  create_neuromancer_integrator(src_block_info_dict, my_child_block)
                        chosen_integrator = integrator 
                        traversed_ids[src_id] = True 
                        print("SOURCE   CREATED INTEGRATOR ")

        if not target_id in list(traversed_ids.keys()): 
            target_class, target_block_info_dict = lookup(target_id)
            if target_class == 'neuromancer_dataset': 
                pass 
            elif target_class == 'neuromancer_block': 
                block = create_neuromancer_block(target_block_info_dict)
                child_blocks[src_id] = block #i am the child block of this source 
                traversed_ids[target_id] = True 
                print(" TARGET   CREATED BLOCK")

            elif target_class == 'neuromancer_loss': 
                create_neuromancer_loss(target_block_info_dict)
                
                traversed_ids[target_id] = True 
                print(" TARGET CREATED LOSS")
                
            elif target_class == 'neuromancer_integrator': 
                edges_from_here_list = get_edges_from_node(target_id, edges)
                print("RUNNING ON NEW EDGE LIST ", edges_from_here_list)
                parse_edges(edges_from_here_list, only_targets=True)
                
                if src_id in child_blocks: 
                        my_child_block = child_blocks[src_id]
                        integrator =  create_neuromancer_integrator(src_block_info_dict, my_child_block)
                        chosen_integrator = integrator 
                        traversed_ids[target_id] = True 
                        print(" TARGET CREATED INTEGRATOR ")


       
           
def construct_problem_after_parsing(): 
    objectives = loss_list
    print("OBJECTIVES ", objectives)
    constraints = []
    # create constrained optimization loss
    loss = PenaltyLoss(objectives, constraints)
    model = Node(chosen_integrator, ['xn'], ['xn'], name='NODE')
    nsteps = dataset_dict[DATASET_ID_FOUND]['nsteps']
    dynamics_model = System([model], name='system', nsteps=nsteps)
    problem = Problem([dynamics_model], loss)
    print("   !!!!!!!!!!!!!!!!!!!!!!!! PROBLEM CREATED   !!!!!!!!!!!!!!!!!!!!!!!! ")
    print(problem)

    problem_dict[problem_id] = problem

    
@app.route('/train_neuromancer_problem', methods=['POST'])
def train_neuromancer_problem(): 
    data = request.get_json()
    print("DATA TRAIN ", data)

    problem = problem_dict[problem_id]
    data_instance_dict = dataset_dict[DATASET_ID_FOUND]
    train_loader, dev_loader, test_data = data_instance_dict['train_loader'], data_instance_dict['dev_loader'], data_instance_dict['test_data']

    optimizer = torch.optim.Adam(problem.parameters(), lr=0.001)
    logger = BasicLogger(args=None, savedir='test', verbosity=1,
                     stdout=['dev_loss', 'train_loss'])
    # define neuromancer trainer
    trainer = Trainer(
        problem,
        train_loader,
        dev_loader,
        test_data,
        optimizer,
        patience=50,
        warmup=100,
        epochs=10,
        eval_metric="dev_loss",
        train_metric="train_loss",
        dev_metric="dev_loss",
        test_metric="dev_loss",
        logger=logger
    )

    trainer.train()

    return jsonify({'message': 'Trained successfully =' + problem_id})











       


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
