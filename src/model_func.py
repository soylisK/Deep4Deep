
import tensorflow as tf
import read_img as rim
import numpy as np
# ------define architecture functions--------------------------------------------------------------

# define weights
def weight_dict(shape,name):
    init = tf.truncated_normal(shape, stddev=0.1)
    return(tf.Variable(init,name=name))

# define bias--optional
def bias_dict(shape,name):
    init = tf.constant(0.1, shape=shape)
    return(tf.Variable(init,name=name))

# return convolution result --optional add bias
def conv2d(x, W, name,stride=1):
    return(tf.nn.conv2d(x, W, strides=[1, stride, stride, 1], padding='SAME',name=name))

# define convolution layer
def conv_layer(inp, shape,name):
    W = weight_dict(shape,(name+'_w'))
    b = bias_dict([shape[3]],(name+'_b'))
    # return(tf.nn.relu(conv2d(inp, W,name) + b))
    return (conv2d(inp,W,name)+b)

# define max pooling function
def max_pool(x, stride, k,name):
    return (tf.nn.max_pool(x, strides=[1, 2, stride, 1], ksize=[1, 2, k, 1], padding='VALID',name=name))



#flatten layer
def flatten_l(inp,name):
    flatten_size=inp.shape[1]*inp.shape[2]*inp.shape[3]
    return (tf.reshape(inp,[-1,flatten_size],name=name) )

# dense layer
#args:
#@ inp : input from previous layer
#@ n_outp : output dimension-nodes
def dense_layer(inp, n_outp,name):
    n_features=inp.shape[1].value
    w=weight_dict([n_features,n_outp],(name+'_w'))
    b=bias_dict([n_outp],(name+'_b'))
    return(tf.matmul(inp,w,name=name)+b)

#fully_connected layer -- a dense layer that apllies relu function
def fully_con(inp,n_outp,name):
    fc=dense_layer(inp,n_outp,(name+'_dl'))
    return(tf.nn.relu(fc,name=(name+'_relu')))

#Last Layer -output layer decides a class with a possibility
#args:
#@inp : input tensor from previous layers
#@n_outp : output nodes --number of classes at output
def outp_layer(inp,n_outp,name):
    outp=dense_layer(inp,n_outp,name)
    return(tf.nn.softmax(outp))

# batch normalization
def batch_n(convl,name):
    return (tf.nn.relu(tf.contrib.layers.batch_norm(convl,scale=True)))
# -------------------------------------------------------------------------------------------------------

# DATA preprocessing operations
# normalize input data
def normalize( X):
    col_max = np.max(X, axis=0)
    col_min = np.min(X, axis=0)
    normX = np.divide(X - col_min, col_max - col_min)
    return normX

# read input data
def input(network,n_tfiles,n_vfiles):
    # Xtrain_in,Ytrain_in : list of ndarray
    network.Xtrain_in, network.Ytrain_in, network.train_size = rim.read_Data("ASVspoof2017_V2_train_fbank", "train_info.txt",n_tfiles)  # Read Train data
    # Normalize input train set data
    network.Xtrain_in = normalize(network.Xtrain_in)
    # read valiation data
    network.Xvalid_in, network.Yvalid_in, network.dev_size = rim.read_Data("ASVspoof2017_V2_train_dev", "dev_info.txt",n_vfiles)         # Read validation data
    # # Normalize input validation set data
    network.Xvalid_in = normalize(network.Xvalid_in)


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
