import numpy as np
import os
#from tensorflow import keras
from keras.layers import (Add, BatchNormalization, Concatenate, Conv2D, Input,
                          Lambda, MaxPooling2D, UpSampling2D, ZeroPadding2D)
from keras.models import Model
from ..nets.backbone_tiny import (DarknetConv2D, DarknetConv2D_BN_Leaky,
                           Multi_Concat_Block, SiLU, Transition_Block,
                           darknet_body)
from ..utils.utils import get_anchors, get_classes
from ..utils.utils_bbox import DecodeBox


def SPPCSPC(x, c2, n=1, shortcut=False, g=1, e=0.5, k=(13, 9, 5), name=""):
    c_ = int(2 * c2 * e)  # hidden channels
    x1 = DarknetConv2D_BN_Leaky(c_, (1, 1), name = name + '.cv1')(x)
    
    y1 = Concatenate(axis=-1)([MaxPooling2D(pool_size=(m, m), strides=(1, 1), padding='same')(x1) for m in k] + [x1])
    y1 = DarknetConv2D_BN_Leaky(c_, (1, 1), name = name + '.cv3')(y1)
    
    y2 = DarknetConv2D_BN_Leaky(c_, (1, 1), name = name + '.cv2')(x)
    out = Concatenate(axis=-1)([y1, y2])
    out = DarknetConv2D_BN_Leaky(c2, (1, 1), name = name + '.cv4')(out)
    
    return out

#---------------------------------------------------#
#   Panet
#---------------------------------------------------#
def yolo_body(input_shape, anchors_mask, num_classes):
    #-----------------------------------------------#
    #  yolov7-tiny params
    #-----------------------------------------------#
    transition_channels = 16
    block_channels      = 16
    panet_channels      = 16
    e                   = 1
    n                   = 2
    ids                 = [-1, -2, -3, -4]
    #-----------------------------------------------#
    #   input 640, 640, 3
    #-----------------------------------------------#

    inputs      = Input(input_shape)
    #---------------------------------------------------#   
    #   80, 80, 256
    #   40, 40, 512
    #   20, 20, 1024
    #---------------------------------------------------#
    feat1, feat2, feat3 = darknet_body(inputs, transition_channels, block_channels, n)

    # 20, 20, 1024 -> 20, 20, 512
    P5          = SPPCSPC(feat3, transition_channels * 16, name="sppcspc")
    P5_conv     = DarknetConv2D_BN_Leaky(transition_channels * 8, (1, 1), name="conv_for_P5")(P5)
    P5_upsample = UpSampling2D()(P5_conv)
    P4          = Concatenate(axis=-1)([DarknetConv2D_BN_Leaky(transition_channels * 8, (1, 1), name="conv_for_feat2")(feat2), P5_upsample])
    P4          = Multi_Concat_Block(P4, panet_channels * 4, transition_channels * 8, e=e, n=n, ids=ids, name="conv3_for_upsample1")

    P4_conv     = DarknetConv2D_BN_Leaky(transition_channels * 4, (1, 1), name="conv_for_P4")(P4)
    P4_upsample = UpSampling2D()(P4_conv)
    P3          = Concatenate(axis=-1)([DarknetConv2D_BN_Leaky(transition_channels * 4, (1, 1), name="conv_for_feat1")(feat1), P4_upsample])
    P3          = Multi_Concat_Block(P3, panet_channels * 2, transition_channels * 4, e=e, n=n, ids=ids, name="conv3_for_upsample2")
        
    P3_downsample = ZeroPadding2D(((1, 1),(1, 1)))(P3)
    P3_downsample = DarknetConv2D_BN_Leaky(transition_channels * 8, (3, 3), strides = (2, 2), name = 'down_sample1')(P3_downsample)
    P4 = Concatenate(axis=-1)([P3_downsample, P4])
    P4 = Multi_Concat_Block(P4, panet_channels * 4, transition_channels * 8, e=e, n=n, ids=ids, name="conv3_for_downsample1")

    P4_downsample = ZeroPadding2D(((1, 1),(1, 1)))(P4)
    P4_downsample = DarknetConv2D_BN_Leaky(transition_channels * 16, (3, 3), strides = (2, 2), name = 'down_sample2')(P4_downsample)
    P5 = Concatenate(axis=-1)([P4_downsample, P5])
    P5 = Multi_Concat_Block(P5, panet_channels * 8, transition_channels * 16, e=e, n=n, ids=ids, name="conv3_for_downsample2")
    
    P3 = DarknetConv2D_BN_Leaky(transition_channels * 8, (3, 3), strides=(1, 1), name="rep_conv_1")(P3)
    P4 = DarknetConv2D_BN_Leaky(transition_channels * 16, (3, 3), strides=(1, 1), name="rep_conv_2")(P4)
    P5 = DarknetConv2D_BN_Leaky(transition_channels * 32, (3, 3), strides=(1, 1), name="rep_conv_3")(P5)

    # len(anchors_mask[2]) = 3
    # 5 + num_classes -> 4 + 1 + num_classes
    # 4 is coef of anchor，1 is sigmoid norm to 0-1，num_classes
    # bs, 20, 20, 3 * (4 + 1 + num_classes)
    out2 = DarknetConv2D(len(anchors_mask[2]) * (5 + num_classes), (1, 1), strides = (1, 1), name = 'yolo_head_P3')(P3)
    out1 = DarknetConv2D(len(anchors_mask[1]) * (5 + num_classes), (1, 1), strides = (1, 1), name = 'yolo_head_P4')(P4)
    out0 = DarknetConv2D(len(anchors_mask[0]) * (5 + num_classes), (1, 1), strides = (1, 1), name = 'yolo_head_P5')(P5)
    return Model(inputs, [out0, out1, out2])

def get_model(model_path, classes_path, anchors_path, input_shape, confidence, nms_iou, letterbox_image):
    model_path = os.path.expanduser(model_path)
    assert model_path.endswith('.h5'), 'Keras model or weights must be a .h5 file.'
    anchors_mask = [[6, 7, 8], [3, 4, 5], [0, 1, 2]]
    # classes_path = 'assets\\frozen_models\\fallen_cartridge\\voc_classes.txt'
    # anchors_path = 'assets\\frozen_models\\fallen_cartridge\\yolo_anchors.txt'
    # input_shape = [640, 640]
    # confidence = 0.5
    # nms_iou = 0.3
    max_boxes = 100
    #letterbox_image = True
    # Keras model or weights must be a .h5 file
    model_path = os.path.expanduser(model_path)
    class_names, num_classes = get_classes(classes_path)
    anchors, num_anchors     = get_anchors(anchors_path)
    model = yolo_body([None, None, 3], anchors_mask, num_classes)
    model.load_weights(model_path, by_name=True)
    
    # if self.phi == "l":
    #     fuse_layers = [
    #         ["rep_conv_1", False, True],
    #         ["rep_conv_2", False, True],
    #         ["rep_conv_3", False, True],
    #     ]
    #     self.model_fuse = yolo_body([None, None, 3], self.anchors_mask, self.num_classes, self.phi, mode="predict")
    #     self.model_fuse.load_weights(self.model_path, by_name=True)

    #     fusion_rep_vgg(fuse_layers, self.model, self.model_fuse)
    #     del self.model
    #     gc.collect()
    #     self.model = self.model_fuse
    print('{} model, anchors, and classes loaded.'.format(model_path))

    input_image_shape = Input([2,],batch_size=1)
    inputs  = [*model.output, input_image_shape]
    outputs = Lambda(
        DecodeBox, 
        output_shape = (1,), 
        name = 'yolo_eval',
        arguments = {
        'anchors'           : anchors, 
        'num_classes'       : num_classes, 
        'input_shape'       : input_shape, 
        'anchor_mask'       : anchors_mask,
        'confidence'        : confidence, 
        'nms_iou'           : nms_iou, 
        'max_boxes'         : max_boxes, 
        'letterbox_image'   : letterbox_image
        }
    )(inputs)
    
    return Model([model.input, input_image_shape], outputs)