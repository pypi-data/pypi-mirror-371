# Inverse Projections

A Python package implementing inverse projection techniques for dimensionality reduction. Map points from low-dimensional visualizations back to high-dimensional space.

## Features

- **Neural Network Inverse (NNinv)**: Deep learning approach using PyTorch
- **Inverse LAMP (ILAMP)**: Local Affine Multidimensional Projection inverse mapping
- **RBF Inverse**: Radial Basis Function interpolation
- **Multilateration**: Geometric triangulation-based approach
- **Gradient Maps**: Quality assessment for inverse projections

## Installation

```bash
pip install inverse-projections
```

## Quick Start

```python
from inverse_projections import NNinv, ILAMP, RBFinv
import numpy as np
from sklearn.manifold import TSNE

# Your high-dimensional data
X = np.random.rand(1000, 50)

# Create 2D projection
X2d = MDS().fit_transform(X)

# Train inverse projection
nninv = NNinv()
nninv.fit(X2d, X)

# Map new 2D points back to high-dimensional space
new_2d_points = np.random.rand(10, 2)
reconstructed = nninv.transform(new_2d_points)
```

## Examples

See the `examples/` directory for detailed demonstrations:
- `demo.ipynb`: MNIST dataset comparison
- `demo_gradient_map.ipynb`: Quality assessment with gradient maps

## Methods

All methods follow sklearn-compatible API with `fit()`, `transform()`, and `inverse_transform()` methods.

## Reference

Based on the following research papers:
- **iLAMP:** dos Santos Amorim, E. P., Brazil, E. V., Daniels, J., Joia, P., Nonato, L. G., & Sousa, M. C. (2012). iLAMP: Exploring high-dimensional spacing through backward multidimensional projection. _Proc. IEEE VAST_. https://doi.org/10.1109/VAST.2012.6400489

- **RBFinv:** Amorim, E., Vital Brazil, E., Mena-Chalco, J., Velho, L., Nonato, L. G., Samavati, F., & Costa Sousa, M. (2015). Facing the high-dimensions: Inverse projection with radial basis functions. _Computers & Graphics_. https://doi.org/10.1016/j.cag.2015.02.009

- **NNinv:** Espadoto, M., Rodrigues, F. C. M., Hirata, N. S. T., & Hirata Jr, R. (2019). Deep Learning Inverse Multidimensional Projections. _Proc. EuroVA_. https://doi.org/10.2312/eurova.20191118

- **NNinv:** Espadoto, M., Appleby, G., Suh, A., Cashman, D., Li, M., Scheidegger, C. E., Anderson, E. W., Chang, R., & Telea, A. C. (2021). UnProjection: Leveraging Inverse-Projections for Visual Analytics of High-Dimensional Data. _IEEE TVCG_. https://doi.org/10.1109/TVCG.2021.3125576

- **MDSinv:** Blumberg, D., Wang, Y., Telea, A., Keim, D. A., & Dennig, F. L. (2024). Inverting Multidimensional Scaling Projections Using Data Point Multilateration. _Proceed EuroVA_


## License

MIT License