import numpy as np
import os
from keras.layers import (Add, BatchNormalization, Concatenate, Conv2D, Input,
                                    Lambda, MaxPooling2D, UpSampling2D)
from keras.models import Model

from .backbone import (DarknetConv2D, DarknetConv2D_BN_SiLU,
                           Multi_Concat_Block, SiLU, Transition_Block,
                           darknet_body)
from ..utils.utils import get_anchors, get_classes
from ..utils.utils_bbox import DecodeBox


def SPPCSPC(x, c2, n=1, shortcut=False, g=1, e=0.5, k=(5, 9, 13), weight_decay=5e-4, name=""):
    c_ = int(2 * c2 * e)  # hidden channels
    x1 = DarknetConv2D_BN_SiLU(c_, (1, 1), weight_decay=weight_decay, name = name + '.cv1')(x)
    x1 = DarknetConv2D_BN_SiLU(c_, (3, 3), weight_decay=weight_decay, name = name + '.cv3')(x1)
    x1 = DarknetConv2D_BN_SiLU(c_, (1, 1), weight_decay=weight_decay, name = name + '.cv4')(x1)
    
    y1 = Concatenate(axis=-1)([x1] + [MaxPooling2D(pool_size=(m, m), strides=(1, 1), padding='same')(x1) for m in k])
    y1 = DarknetConv2D_BN_SiLU(c_, (1, 1), weight_decay=weight_decay, name = name + '.cv5')(y1)
    y1 = DarknetConv2D_BN_SiLU(c_, (3, 3), weight_decay=weight_decay, name = name + '.cv6')(y1)
    
    y2 = DarknetConv2D_BN_SiLU(c_, (1, 1), weight_decay=weight_decay, name = name + '.cv2')(x)
    out = Concatenate(axis=-1)([y1, y2])
    out = DarknetConv2D_BN_SiLU(c2, (1, 1), weight_decay=weight_decay, name = name + '.cv7')(out)
    
    return out

def fusion_rep_vgg(fuse_layers, trained_model, infer_model):
    for layer_name, use_bias, use_bn in fuse_layers:

        conv_kxk_weights = trained_model.get_layer(layer_name + '.rbr_dense.0').get_weights()[0]
        conv_1x1_weights = trained_model.get_layer(layer_name + '.rbr_1x1.0').get_weights()[0]

        if use_bias:
            conv_kxk_bias = trained_model.get_layer(layer_name + '.rbr_dense.0').get_weights()[1]
            conv_1x1_bias = trained_model.get_layer(layer_name + '.rbr_1x1.0').get_weights()[1]
        else:
            conv_kxk_bias = np.zeros((conv_kxk_weights.shape[-1],))
            conv_1x1_bias = np.zeros((conv_1x1_weights.shape[-1],))

        if use_bn:
            gammas_kxk, betas_kxk, means_kxk, var_kxk = trained_model.get_layer(layer_name + '.rbr_dense.1').get_weights()
            gammas_1x1, betas_1x1, means_1x1, var_1x1 = trained_model.get_layer(layer_name + '.rbr_1x1.1').get_weights()

        else:
            gammas_1x1, betas_1x1, means_1x1, var_1x1 = [np.ones((conv_1x1_weights.shape[-1],)),
                                                         np.zeros((conv_1x1_weights.shape[-1],)),
                                                         np.zeros((conv_1x1_weights.shape[-1],)),
                                                         np.ones((conv_1x1_weights.shape[-1],))]
            gammas_kxk, betas_kxk, means_kxk, var_kxk = [np.ones((conv_kxk_weights.shape[-1],)),
                                                         np.zeros((conv_kxk_weights.shape[-1],)),
                                                         np.zeros((conv_kxk_weights.shape[-1],)),
                                                         np.ones((conv_kxk_weights.shape[-1],))]
        gammas_res, betas_res, means_res, var_res = [np.ones((conv_1x1_weights.shape[-1],)),
                                                     np.zeros((conv_1x1_weights.shape[-1],)),
                                                     np.zeros((conv_1x1_weights.shape[-1],)),
                                                     np.ones((conv_1x1_weights.shape[-1],))]

        # _fuse_bn_tensor(self.rbr_dense)
        w_kxk = (gammas_kxk / np.sqrt(np.add(var_kxk, 1e-3))) * conv_kxk_weights
        b_kxk = (((conv_kxk_bias - means_kxk) * gammas_kxk) / np.sqrt(np.add(var_kxk, 1e-3))) + betas_kxk
        
        # _fuse_bn_tensor(self.rbr_dense)
        kernel_size = w_kxk.shape[0]
        in_channels = w_kxk.shape[2]
        w_1x1 = np.zeros_like(w_kxk)
        w_1x1[kernel_size // 2, kernel_size // 2, :, :] = (gammas_1x1 / np.sqrt(np.add(var_1x1, 1e-3))) * conv_1x1_weights
        b_1x1 = (((conv_1x1_bias - means_1x1) * gammas_1x1) / np.sqrt(np.add(var_1x1, 1e-3))) + betas_1x1

        w_res = np.zeros_like(w_kxk)
        for i in range(in_channels):
            w_res[kernel_size // 2, kernel_size // 2, i % in_channels, i] = 1
        w_res = ((gammas_res / np.sqrt(np.add(var_res, 1e-3))) * w_res)
        b_res = (((0 - means_res) * gammas_res) / np.sqrt(np.add(var_res, 1e-3))) + betas_res

        weight = [w_res, w_1x1, w_kxk]
        bias = [b_res, b_1x1, b_kxk]
        
        infer_model.get_layer(layer_name).set_weights([np.array(weight).sum(axis=0), np.array(bias).sum(axis=0)])

def RepConv(x, c2, mode="train", weight_decay=5e-4, name=""):
    if mode == "predict":
        out = DarknetConv2D(c2, (3, 3), name = name, use_bias=True, weight_decay=weight_decay, padding='same')(x)
        out = SiLU()(out)
    elif mode == "train":
        x1 = DarknetConv2D(c2, (3, 3), name = name + '.rbr_dense.0', use_bias=False, weight_decay=weight_decay, padding='same')(x)
        x1 = BatchNormalization(momentum = 0.97, epsilon = 0.001, name = name + '.rbr_dense.1')(x1)
        x2 = DarknetConv2D(c2, (1, 1), name = name + '.rbr_1x1.0', use_bias=False, weight_decay=weight_decay, padding='same')(x)
        x2 = BatchNormalization(momentum = 0.97, epsilon = 0.001, name = name + '.rbr_1x1.1')(x2)
        
        out = Add()([x1, x2])
        out = SiLU()(out)
    return out

#---------------------------------------------------#
#   Panet
#---------------------------------------------------#
def yolo_body(input_shape, anchors_mask, num_classes, phi, weight_decay=5e-4, mode="train"):
    #-----------------------------------------------#
    #   yolov7 version based parameters
    #-----------------------------------------------#
    transition_channels = {'l' : 32, 'x' : 40}[phi]
    block_channels      = 32
    panet_channels      = {'l' : 32, 'x' : 64}[phi]
    e       = {'l' : 2, 'x' : 1}[phi]
    n       = {'l' : 4, 'x' : 6}[phi]
    ids     = {'l' : [-1, -2, -3, -4, -5, -6], 'x' : [-1, -3, -5, -7, -8]}[phi]

    inputs      = Input(input_shape)
    #---------------------------------------------------#   
    #   generate backbone and get 3 feature layers：
    #   80, 80, 256
    #   40, 40, 1024
    #   20, 20, 1024
    #---------------------------------------------------#
    feat1, feat2, feat3 = darknet_body(inputs, transition_channels, block_channels, n, phi, weight_decay)
    #feat1, feat2, feat3 = darknet_body(inputs, transition_channels, block_channels, n)

    # 20, 20, 1024 -> 20, 20, 512
    P5          = SPPCSPC(feat3, transition_channels * 16, weight_decay=weight_decay, name="sppcspc")
    P5_conv     = DarknetConv2D_BN_SiLU(transition_channels * 8, (1, 1), weight_decay=weight_decay, name="conv_for_P5")(P5)
    P5_upsample = UpSampling2D()(P5_conv)
    P4          = Concatenate(axis=-1)([DarknetConv2D_BN_SiLU(transition_channels * 8, (1, 1), weight_decay=weight_decay, name="conv_for_feat2")(feat2), P5_upsample])
    P4          = Multi_Concat_Block(P4, panet_channels * 4, transition_channels * 8, e=e, n=n, ids=ids, weight_decay=weight_decay, name="conv3_for_upsample1")

    P4_conv     = DarknetConv2D_BN_SiLU(transition_channels * 4, (1, 1), weight_decay=weight_decay, name="conv_for_P4")(P4)
    P4_upsample = UpSampling2D()(P4_conv)
    P3          = Concatenate(axis=-1)([DarknetConv2D_BN_SiLU(transition_channels * 4, (1, 1), weight_decay=weight_decay, name="conv_for_feat1")(feat1), P4_upsample])
    P3          = Multi_Concat_Block(P3, panet_channels * 2, transition_channels * 4, e=e, n=n, ids=ids, weight_decay=weight_decay, name="conv3_for_upsample2")
        
    P3_downsample = Transition_Block(P3, transition_channels * 4, weight_decay=weight_decay, name="down_sample1")
    P4 = Concatenate(axis=-1)([P3_downsample, P4])
    P4 = Multi_Concat_Block(P4, panet_channels * 4, transition_channels * 8, e=e, n=n, ids=ids, weight_decay=weight_decay, name="conv3_for_downsample1")

    P4_downsample = Transition_Block(P4, transition_channels * 8, weight_decay=weight_decay, name="down_sample2")
    P5 = Concatenate(axis=-1)([P4_downsample, P5])
    P5 = Multi_Concat_Block(P5, panet_channels * 8, transition_channels * 16, e=e, n=n, ids=ids, weight_decay=weight_decay, name="conv3_for_downsample2")
    
    if phi == "l":
        P3 = RepConv(P3, transition_channels * 8, mode, weight_decay=weight_decay, name="rep_conv_1")
        P4 = RepConv(P4, transition_channels * 16, mode, weight_decay=weight_decay, name="rep_conv_2")
        P5 = RepConv(P5, transition_channels * 32, mode, weight_decay=weight_decay, name="rep_conv_3")
    else:
        P3 = DarknetConv2D_BN_SiLU(transition_channels * 8, (3, 3), strides=(1, 1), weight_decay=weight_decay, name="rep_conv_1")(P3)
        P4 = DarknetConv2D_BN_SiLU(transition_channels * 16, (3, 3), strides=(1, 1), weight_decay=weight_decay, name="rep_conv_2")(P4)
        P5 = DarknetConv2D_BN_SiLU(transition_channels * 32, (3, 3), strides=(1, 1), weight_decay=weight_decay, name="rep_conv_3")(P5)

    # len(anchors_mask[2]) = 3
    # 5 + num_classes -> 4 + 1 + num_classes
    # 4 prior bx regression coef，1 to fix sigmoid to [0-1]，num_classes is num of class
    # bs, 20, 20, 3 * (4 + 1 + num_classes)
    out2 = DarknetConv2D(len(anchors_mask[2]) * (5 + num_classes), (1, 1), weight_decay=weight_decay, strides = (1, 1), name = 'yolo_head_P3')(P3)
    out1 = DarknetConv2D(len(anchors_mask[1]) * (5 + num_classes), (1, 1), weight_decay=weight_decay, strides = (1, 1), name = 'yolo_head_P4')(P4)
    out0 = DarknetConv2D(len(anchors_mask[0]) * (5 + num_classes), (1, 1), weight_decay=weight_decay, strides = (1, 1), name = 'yolo_head_P5')(P5)
    return Model(inputs, [out0, out1, out2])

def get_model(model_path, classes_path, anchors_path, input_shape, confidence, nms_iou, letterbox_image):
    phi = 'l'
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
    tmp_model = yolo_body([None, None, 3], anchors_mask, num_classes, phi)
    tmp_model.load_weights(model_path, by_name=True)
    
    if phi == "l":
        fuse_layers = [
            ["rep_conv_1", False, True],
            ["rep_conv_2", False, True],
            ["rep_conv_3", False, True],
        ]
        model_fuse = yolo_body([None, None, 3], anchors_mask, num_classes, phi, mode="predict")
        model_fuse.load_weights(model_path, by_name=True)

        fusion_rep_vgg(fuse_layers, tmp_model, model_fuse)
        del tmp_model
        gc.collect()
        tmp_model= model_fuse
    print('{} model, anchors, and classes loaded.'.format(model_path))

    input_image_shape = Input([2,],batch_size=1)
    inputs  = [*tmp_model.output, input_image_shape]
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
    yolo_model = Model([tmp_model.input, input_image_shape], outputs)
    
    return yolo_model