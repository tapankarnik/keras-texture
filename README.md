**TODO**: 

- Weight initializers
    - Logistic Regression init. for `softmax` layers (esp. for large layers -- e.g., bilinear pooling output)
    - Try [ConvolutionAware](https://github.com/keras-team/keras-contrib/blob/master/keras_contrib/initializers/convaware.py) from `keras_contrib.initializers`
- Base CNN builders 
    - Convert weights from ResNet18/34 pre-trained `Caffe` models
    - Check out wide/dilated ResNet blocks from [keras-contrib/applications](https://github.com/keras-team/keras-contrib/blob/master/keras_contrib/applications))
- Fisher Vector encoding (using `cyvlfeat`)
    - Note that this is more like pooling than dimensionality reduction. Encoding of a set of `N` feature vectors with size `D` using a GMM with `k` clusters is `2*k*D`. And typically, `N ~ 2*k`.
- Tests and benchmarks

# keras-texture

Implementations of several `keras` layers and other utilities that are useful in constructing models for texture recognition and fine-grained classification problems. It is a work in progress, and currently the `tensorflow` backend is required.

Now develop-mode installable with `pip install -e .` The root module of package is `texture`.

# Requirements

- `numpy`
- `scikit-image`
- `keras`>=2.0
- `tensorflow`

Fisher vector encoding utilities in `texture.fisher` (planned) will require [cyvlfeat](https://github.com/menpo/cyvlfeat), which should be installed using `conda install -c menpo cyvlfeat`, if possible. This is not required for using the rest of the package, so it is not explicitly enforced in `setup.py`.

The TensorFlow requirement is also not explicitly enforced, due to the ambiguity between `tensorflow` and `tensorflow-gpu`. This package supports CPU or GPU versions, since some functionality (*e.g.*, Fisher vector encoding with ImageNet pretrained models) doesn't require a GPU.

# Contents

## `Encoding` Layer

The residual encoding layer proposed in [Deep TEN: Texture Encoding Network](https://arxiv.org/pdf/1612.02844.pdf) [*CVPR*, 2017]. This `keras` implementation is largely based on the [PyTorch-Encoding](https://github.com/zhanghang1989/PyTorch-Encoding) release by the paper authors.

<p align="center">
  <img src="./docs/Encoding-Layer_diagram.png?raw=true" alt="Encoding-Layer diagram"/>
</p>

The layer learns a `KxD` dictionary of codewords (a "codebook"), and codeword assignment `scale` weights. These are used to encode the residuals of an input of shape `NxD` or `HxWxD` with respect to the codewords. Includes optional L2 normalization of output vectors (`True` by default) and dropout (`None` by default). Unlike the `PyTorch-Encoding` version, only the number of codewords `K` needs to be specified at construction time -- the feature size `D` is inferred from the `input_shape`.

## `BilinearModel` Layer

`BilinearModel` is a trainable `keras` layer implementing the weighted outer product of inputs with shape `[(batches,N),(batches,M)]`. The original idea of bilinear modeling for computer vision problems was proposed in [Learning Bilinear Models for Two-Factor Problems in Vision](http://www.merl.com/publications/docs/TR96-37.pdf) [*CVPR*, 1997].

It is used in the `Deep Encoding Pooling Network (DEP)` proposed in [Deep Texture Manifold for Ground Terrain Recognition](https://arxiv.org/abs/1803.10896) [*CVPR*, 2018] to merge the output of an `Encoding` layer with the output of a standard global average pooling, where both features are extracted from `conv` output of the same `ResNet` base. The intuition is that the former represents textures (orderless encoding) and the latter represents spatially structured observations, so that "[the] outer product representation captures a pairwise correlation between the material texture encodings and spatial observation structures."

![DEP-Architecture](./docs/DEP_diagram.png)

## Bilinear `pooling`

`bilinearpooling.py` provides a few convenience functions for creating symmetric or asymmetric B-CNN models in Keras with bilinear pooling, as proposed in [Bilinear CNNs for Fine-grained Visual Recognition](http://vis-www.cs.umass.edu/bcnn/docs/bcnn_iccv15.pdf) (*ICCV*, 2015).

`bilinearpooling.pooling`:

- Average pooling of local feature vector outer products in `tensorflow`
- Includes element-wise signed square root and L2 normalization
- If using `combine`, you won't need to reference this explicitly

`bilinearpooling.combine`: 

- Takes two `keras` models `fA` and `fB` with output shapes `(N, H, W, cA)`, `(N, H, W, cB)`
- Maps `[fA.output, fB.output]` to shape `(N, cA, cB)` with `bilinear.pooling`
- Flattens, connects to `softmax` output using a specifiable number of `Dense` layers.
- Returns the resulting `keras.models.Model` instance

#### Usage Notes

- Be careful with reuse of single model for `fA` and `fB` (*e.g.*, asymmetry via different output layers). Weights will be shared if you use the same instantiation of the original model to generate both models.

See `build_demo.ipynb` for examples of constructing symmetric and asymmetric B-CNNs using pretrained `VGG19` and `Xception` models from `keras.applications`.

#### Benchmarks

Working on benchmarking models constructed with this implementation on the three benchmark datasets referenced in the original B-CNN paper:

- [Birds-200](http://www.vision.caltech.edu/visipedia/CUB-200-2011.html) (2011 version)
- [FGVC-Aircraft](http://www.robots.ox.ac.uk/~vgg/data/fgvc-aircraft/)
- [Cars](https://ai.stanford.edu/~jkrause/cars/car_dataset.html)

You can run the `benchmark.py` script to build a model for `Birds-200`, after collecting dataset into `npy` files with `collect_dataset.py`:
```
$ python benchmark.py --help
```
Note: right now includes 1x1 conv to reduce `D` from `512 -> 32`. The former induces a fully connected layer w/ over 50 million weights (`200*512^2`), so training is unreasonably slow.

## Further Improvements

#### Encoding

- `ResNet` based constructors for feature networks

#### Bilinear

- Add Logistic Regression initialization for `softmax` layer
- Add support for `fA` and `fB` to have different input shapes (technically only output shapes need to correspond).
- Add support for `fA` and `fB` to have different output shapes (crop/interpolate/pool to match them)

Would also like to add the matrix square root normalization layer as described in:
```
@inproceedings{lin2017impbcnn,
    Author = {Tsung-Yu Lin, and Subhransu Maji},
    Booktitle = {British Machine Vision Conference (BMVC)},
    Title = {Improved Bilinear Pooling with CNNs},
    Year = {2017}}
```
Authors claim this improves accuracy by several % on fine-grained recognition benchmarks.

#### DEP

- Utilities for combining a base CNN with `Encoding` & `BilinearModel` to create a `Deep Encoding Pooling Network`.

