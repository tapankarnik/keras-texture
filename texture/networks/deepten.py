"""

"""
import tensorflow as tf
from tensorflow.keras.layers import Input, Conv2D, Dense, Dropout, BatchNormalization
from tensorflow.keras.models import Model as KerasModel

from texture.layers import Encoding
from texture.networks.util import make_backbone, make_dense_layers

def deepten(num_classes,
            input_shape,
            backbone_cnn=None,
            encode_K=32,
            conv1x1=128,
            dense_layers=[],
            dropout_rate=None):
    '''Combine a backbone CNN + Encoding layer + Dense layers into a DeepTEN.

    Parameters
    ----------
    backbone_cnn : KerasModel or str
        Feature extraction network. If KerasModel, should output features (N, H, W, C).
        If str, loads the corresponding ImageNet model from `keras.applications`.
    n_classes : int
        Number of classes for softmax output layer
    input_shape : tuple of int, optional
        Shape of input image. Can be None, since Encoding layer allows variable input sizes.
    encode_K : int, optional
        Number of codewords to learn, default=32.
    conv1x1 : int, optional
        Add a 1x1 conv to reduce number of filters in backbone_cnn.output before Encoding layer, default=128.
    dense_layers : iterable of int, optional
        Sizes for additional Dense layers between Encoding.output and softmax, default=[].
    dropout_rate: float, optional
        Specify a dropout rate for Dense layers

    Returns
    -------
    DeepTEN : KerasModel
        Deep Texture Encoding Network
    '''
    assert backbone_cnn is not None
    backbone_model = make_backbone(backbone_cnn, input_shape)
    conv_output = backbone_model.output
    if conv1x1 is not None:
        conv_output = Conv2D(conv1x1, (1,1), activation='relu')(conv_output)
        conv_output = BatchNormalization()(conv_output)

    x = Encoding(encode_K, dropout=dropout_rate)(conv_output)
    x = make_dense_layers(dense_layers, dropout=dropout_rate)(x)
    pred = Dense(num_classes, activation='softmax')(x)

    model = KerasModel(inputs=backbone_model.input, outputs=pred)

    return model
