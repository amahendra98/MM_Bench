"""
This file serves as a training interface for training the network
"""
# Built in
import glob
import os
import shutil
import sys
sys.path.append('../utils/')

# Torch

# Own
import flag_reader
from utils import data_reader
from class_wrapper import Network
from model_maker import MDN
from utils.helper_functions import put_param_into_folder, write_flags_and_BVE

def training_from_flag(flags):
    """
    Training interface. 1. Read data 2. initialize network 3. train network 4. record flags
    :param flag: The training flags read from command line or parameter.py
    :return: None
    """
    # Get the data
    train_loader, test_loader = data_reader.read_data(flags)
    print("Making network now")

    # Make Network
    ntwk = Network(MDN, flags, train_loader, test_loader)

    # Training process
    print("Start training now...")
    ntwk.train()

    # Do the house keeping, write the parameters and put into folder, also use pickle to save the flags obejct
    write_flags_and_BVE(flags, ntwk.best_validation_loss, ntwk.ckpt_dir)


def retrain_different_dataset(index):
     """
     This function is to evaluate all different datasets in the model with one function call
     """
     from utils.helper_functions import load_flags
     data_set_list = ["meta_material","robotic_arm","sine_wave","ballistics"]
     for train_model in data_set_list:
        flags = load_flags(os.path.join("models", train_model))
        #if train_model is 'meta_material':
        #    flags.data_dir = os.path.join('../', 'Simulated_DataSets', 'Meta_material_Neural_Simulator')
        flags.model_name = "retrain" + str(index) + train_model
        flags.ckpt_dir = 'models/'
        flags.batch_size = 1024
        flags.train_step = 500
        flags.test_ratio = 0.2
        flags.stop_threshold = -float('inf')
        training_from_flag(flags)

def hyperswipe():
    """
    This is for doing hyperswiping for the model parameters
    """
    reg_scale_list =  [1e-4, 5e-4, 5e-5, 0]
    layer_size_list = [250, 500, 1000]
    num_gauss_list = [2,3,4,5, 6,7,8,9]
    #num_gauss_list = [5, 10, 15, 20, 25, 30]
    for reg_scale in reg_scale_list:
        for layer_num in range(4,10):
            for layer_size in layer_size_list:
                for num_gaussian in num_gauss_list:
                    flags = flag_reader.read_flag()  	#setting the base case
                    flags.reg_scale = reg_scale
                    linear = [layer_size  for j in range(layer_num)]
                    linear[0] = 2000
                    linear[-1] = 14
                    flags.linear = linear
                    flags.num_gaussian = num_gaussian
                    flags.model_name = flags.data_set + '_gaussian_'+str(num_gaussian) + '_layer_num_' + str(layer_num) + '_unit_' + str(layer_size) + '_lr_' + str(flags.lr) + '_reg_scale_' + str(reg_scale)
                    try:
                        training_from_flag(flags)
                    except RuntimeError as e:
                        print("Failing the device-side assert for MDN mdn.sample function! doing 3 retries now:")
                        for j in range(3):
                            try:
                                print("trying number ", j)
                                training_from_flag(flags)
                                break;
                            except:
                                print("Failing again! try again")
                                    
                                    


if __name__ == '__main__':
    # torch.manual_seed(1)
    # torch.cuda.manual_seed(1)
    # Read the parameters to be set
    flags = flag_reader.read_flag()
    
    hyperswipe()
    # Call the train from flag function
    #training_from_flag(flags)

    # Do the retraining for all the data set to get the training 
    #for i in range(10):
    #    retrain_different_dataset(i)
