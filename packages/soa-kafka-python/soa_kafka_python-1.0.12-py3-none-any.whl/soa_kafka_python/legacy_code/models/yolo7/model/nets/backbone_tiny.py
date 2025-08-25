from functools import wraps

from keras import backend as K
from keras.initializers import RandomNormal
from keras.layers import (Add, BatchNormalization, Concatenate, Conv2D, Layer,
                          MaxPooling2D, ZeroPadding2D, LeakyReLU)
from keras.regularizers import l2
from ..utils.utils import compose


class SiLU(Layer):
    def __init__(self, **kwargs):
        super(SiLU, self).__init__(**kwargs)
        self.supports_masking = True

    def call(self, inputs):
        return inputs * K.sigmoid(inputs)

    def get_config(self):
        config = super(SiLU, self).get_config()
        return config

    def compute_output_shape(self, input_shape):
        return input_shape

#------------------------------------------------------#
#   DarknetConv2D
#   if stride is 2, use customized padding
#------------------------------------------------------#
@wraps(Conv2D)
def DarknetConv2D(*args, **kwargs):
    darknet_conv_kwargs = {'kernel_initializer' : RandomNormal(stddev=0.02), 'kernel_regularizer' : l2(kwargs.get('weight_decay', 0))}
    darknet_conv_kwargs['padding'] = 'valid' if kwargs.get('strides')==(2, 2) else 'same'   
    try:
        del kwargs['weight_decay']
    except:
        pass
    darknet_conv_kwargs.update(kwargs)
    return Conv2D(*args, **darknet_conv_kwargs)
    
#---------------------------------------------------#
#   conv block -> DarknetConv2D + BatchNormalization + SiLU
#   DarknetConv2D + BatchNormalization + SiLU
#---------------------------------------------------#
def DarknetConv2D_BN_SiLU(*args, **kwargs):
    no_bias_kwargs = {'use_bias': False}
    no_bias_kwargs.update(kwargs)
    if "name" in kwargs.keys():
        no_bias_kwargs['name'] = kwargs['name'] + '.conv'
    return compose(
        DarknetConv2D(*args, **no_bias_kwargs),
        BatchNormalization(momentum = 0.97, epsilon = 0.001, name = kwargs['name'] + '.bn'),
        SiLU())

def DarknetConv2D_BN_Leaky(*args, **kwargs):
    no_bias_kwargs = {'use_bias': False}
    no_bias_kwargs.update(kwargs)
    if "name" in kwargs.keys():
        no_bias_kwargs['name'] = kwargs['name'] + '.conv'
    return compose(
        DarknetConv2D(*args, **no_bias_kwargs),
        BatchNormalization(momentum = 0.97, epsilon = 0.001, name = kwargs['name'] + '.bn'),
        LeakyReLU(0.1))

def Multi_Concat_Block(x, c2, c3, n=4, e=1, ids=[0], weight_decay=5e-4, name = ""):
    c_ = int(c2 * e)
        
    x_1 = DarknetConv2D_BN_SiLU(c_, (1, 1), weight_decay=weight_decay, name = name + '.cv1')(x)
    x_2 = DarknetConv2D_BN_SiLU(c_, (1, 1), weight_decay=weight_decay, name = name + '.cv2')(x)
    
    x_all = [x_1, x_2]
    for i in range(n):
        x_2 = DarknetConv2D_BN_SiLU(c2, (3, 3), weight_decay=weight_decay, name = name + '.cv3.' + str(i))(x_2)
        x_all.append(x_2)
    y = Concatenate(axis=-1)([x_all[id] for id in ids])
    y = DarknetConv2D_BN_SiLU(c3, (1, 1), weight_decay=weight_decay, name = name + '.cv4')(y)
    return y

def Transition_Block(x):
    #----------------------------------------------------------------#
    #   ZeroPadding2D and 2x2 conv to compress h,w
    #----------------------------------------------------------------#
    y = MaxPooling2D((2, 2), strides=(2, 2))(x)
    return y

def darknet_body(x, transition_channels, block_channels, n): # for yolo7 tiny
    #-----------------------------------------------#
    #   640, 640, 3
    #-----------------------------------------------#
    ids = [-1, -2, -3, -4]
    #---------------------------------------------------#
    #   base_channels default is 64
    #---------------------------------------------------#
    # 320, 320, 3 => 320, 320, 64
    x = ZeroPadding2D(((1, 1),(1, 1)))(x)
    x = DarknetConv2D_BN_Leaky(transition_channels * 2, (3, 3), strides = (2, 2), name = 'backbone.stem')(x)
    
    # 320, 320, 64 => 160, 160, 128
    x = ZeroPadding2D(((1, 1),(1, 1)))(x)
    x = DarknetConv2D_BN_Leaky(transition_channels * 4, (3, 3), strides = (2, 2), name = 'backbone.dark2.0')(x)
    x = Multi_Concat_Block(x, block_channels * 2, transition_channels * 4, n=n, ids=ids, name = 'backbone.dark2.1')
    
    # 160, 160, 128 => 80, 80, 256
    x = Transition_Block(x)
    x = Multi_Concat_Block(x, block_channels * 4, transition_channels * 8, n=n, ids=ids, name = 'backbone.dark3.1')
    feat1 = x
    
    # 80, 80, 256 => 40, 40, 512
    x = Transition_Block(x)
    x = Multi_Concat_Block(x, block_channels * 8, transition_channels * 16, n=n, ids=ids, name = 'backbone.dark4.1')
    feat2 = x
    
    # 40, 40, 512 => 20, 20, 1024
    x = Transition_Block(x)
    x = Multi_Concat_Block(x, block_channels * 16, transition_channels * 32, n=n, ids=ids, name = 'backbone.dark5.1')
    feat3 = x
    return feat1, feat2, feat3


