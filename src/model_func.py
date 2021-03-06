
import tensorflow as tf
import read_img as rim
import numpy as np
# -----------------------------------------------------------------------------------------------------------------
#                                MODEL ARCHITECTURE FUNCTIONS
# _________________________________________________________________________________________________________________

summ_list = []
# define weights
def weight_dict(shape,name):
    init = tf.truncated_normal(shape, stddev=0.1)
    return(tf.Variable(init,name=name))

# define bias--optional
def bias_dict(shape,name):
    init = tf.constant(0.1, shape=shape)
    return(tf.Variable(init,name=name))

# return convolution result --optional add bias
def conv2d(x, W, b,name,strides=1):
    x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME',name=name)
    x = tf.nn.bias_add(x,b)
    # act = tf.nn.relu(x)
    # conv_act = tf.summary.histogram('activations',act)
    return (x)

# define convolution layer
def conv_layer(inp, shape,name,summary=False):
    w_name = (name+'_w')
    b_name = (name+'_b')
    W = weight_dict(shape,w_name)
    b = bias_dict([shape[3]],b_name)
    # return(tf.nn.relu(conv2d(inp, W,name) + b))
    if(summary):
        weight_summ = tf.summary.histogram(w_name,W)
        bias_summ = tf.summary.histogram(b_name,b)
        # print(type(bias_summ))
        global summ_list
        summ_list.append(weight_summ)
        summ_list.append(bias_summ)
        # print(type(summ_list[-1]))
    return (conv2d(inp,W,b,name))

# batch normalization
def batch_n(convl,name,summary=False):
    bn = tf.layers.batch_normalization(convl)
    act = tf.nn.relu(bn)
    # tf.summary.histogram('batch-norms',bn)
    if(summary):
        bn_act_summ = tf.summary.histogram('activations',act)
        global summ_list
        summ_list.append(bn_act_summ)
    return(act)

# define max pooling function 2x2
def max_pool(x, strides, k,name):
    return (tf.nn.max_pool(x, strides=[1, 2, strides, 1], ksize=[1, 2, k, 1], padding='VALID',name=name))
# define average pooling function 2x2
def avg_pool(x,strides,k,name):
    return(tf.nn.avg_pool(x, strides=[1, 2, strides, 1], ksize=[1, 2, k, 1], padding='VALID',name=name))

#flatten layer
def flatten_l(inp,name):
    flatten_size=inp.shape[1]*inp.shape[2]*inp.shape[3]
    return (tf.reshape(inp,[-1,flatten_size],name=name) )

# dense layer
#args:
#@ inp : input from previous layer
#@ n_outp : output dimension-nodes
def dense_layer(inp, n_outp,name,summary=False):
    n_features=inp.shape[1].value
    w_name = (name+'_w')
    b_name = (name+'_b')
    w=weight_dict([n_features,n_outp],w_name)
    b=bias_dict([n_outp],b_name)
    outp=tf.matmul(inp,w,name=name)
    outp= tf.nn.bias_add(outp,b)
    if(summary):
        dens_w_summ = tf.summary.histogram(w_name,w)
        dens_b_summ = tf.summary.histogram(b_name,b)
        global summ_list
        summ_list.append(dens_w_summ)
        summ_list.append(dens_b_summ)
    return(outp)

#fully_connected layer -- a dense layer that apllies relu function
def fully_con(inp,n_outp,name,summary=False):
    fc=dense_layer(inp,n_outp,(name+'_dl'),summary)
    activ = tf.nn.relu(fc)
    if(summary):
        fc_act_summ = tf.summary.histogram('activations',activ)
        # print(type(fc_act_summ))
        global summ_list
        summ_list.append(fc_act_summ)
        # print(type(summ_list[-1]))
    return(activ)

def take_summ_list():
    global summ_list
    # print(type(summ_list[0]))
    # print(len(summ_list))
    return (summ_list)


# ------------------------------------------------------------------------------------------------------------
#                                   INPUT DATA PROCESSING
#_____________________________________________________________________________________________________________
# DATA preprocessing operations
# normalize min-max input data
def normalize( X):
    col_max = np.max(X, axis=0)
    col_min = np.min(X, axis=0)
    normX = np.divide(X - col_min, col_max - col_min)
    return normX

# returns splited line as string
def read_statistics():
    f = open('statistics','r')
    line = f.readline()
    line = line.split(',')

    return line

# use train data statistics to normalize
def mean_normalization(X,m,std):
    return ((X-m)/std)


# read input data
def input(network,n_tfiles,n_vfiles):
    # Xtrain_in,Ytrain_in : list of ndarray
    network.Xtrain_in, network.Ytrain_in, network.train_size = rim.read_Data("ASVspoof2017_V2_train_fbank", "train_info.txt",n_tfiles)  # Read Train data
    stats = read_statistics()
    network.mean = float(stats[0])
    network.std = float(stats[1])
    # Normalize input train set data
    # network.Xtrain_in = normalize(network.Xtrain_in)
    network.Xtrain_in = mean_normalization(network.Xtrain_in,network.mean,network.std)
    # read valiation data
    network.Xvalid_in, network.Yvalid_in, network.dev_size = rim.read_Data("ASVspoof2017_V2_train_dev", "dev_info.txt",n_vfiles)         # Read validation data
    # # Normalize input validation set data
    # network.Xvalid_in = normalize(network.Xvalid_in)
    network.Xvalid_in = mean_normalization(network.Xvalid_in,network.mean,network.std)

# read eval dataset
def eval_input(network,n_efiles):
    network.Xeval_in, network.Yeval_in, network.eval_size = rim.read_pred_data('ASVspoof2017_V2_train_eval','eval_info.txt')
    # print('$$\n')
    # print(network.Xeval_in)
    #rim.read_Data('ASVspoof2017_V2_train_eval','eval_info.txt',n_efiles)
    stats = read_statistics()
    network.mean = float(stats[0])
    network.std = float(stats[1])
    # Normalize
    # network.Xeval_in = normalize(network.Xeval_in)
    network.Xeval_in = mean_normalization(network.Xeval_in,network.mean,network.std)
# shuffle index so to get with random order the data
def shuffling( X,Y):
    indx=np.arange(len(X))          # create a array with indexes for X data
    np.random.shuffle(indx)
    X=X[indx]
    Y=Y[indx]
    # print("shuffle")
    # print(X)
    return X,Y

# take X batch and Ybatch
def read_nxt_batch(X,Y,batch_s,indx=0):
    if(indx+batch_s <len(X)):       # check and be sure that you're in range
        # print(Y.shape)
        X=X[indx:indx+batch_s]      # take a batch from shuffled data 0..255 is 256!
        Y=Y[indx:indx+batch_s]      # take a batch from shuffled labels
        indx+=batch_s               # increase indx, move to indx the next batch
        return(X,Y,indx)
    else:
        return None,None,None
