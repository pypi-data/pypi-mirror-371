import numpy as np

def get_gradient_map(projecters=None, x2d=None, grid=100):
    """
    get the gradient map for the inverse projection method

    projecters: the inverse projection method. It should have a inverse_transform method that can map the 2d points back to the original space
    x2d: the 2d points. 
    grid: the grid size for the gradient map.
    """
    # make grid
    # x2d = projecters.transform(x)
    
    x_max, x_min = np.max(x2d[:,0]), np.min(x2d[:,0])
    y_max, y_min = np.max(x2d[:,1]), np.min(x2d[:,1])
    pixel_width = (x_max - x_min) / grid
    pixel_height = (y_max - y_min) / grid
    # pixel_width =  1/grid
    # pixel_height = 1/grid

    grid_pad = grid + 2 

    xx, yy = np.meshgrid(np.linspace(x_min-pixel_width, x_max+pixel_width, grid_pad), np.linspace(y_min-pixel_height, y_max+pixel_height, grid_pad)) # make it 100*100 to reduce the computation
    xy = np.c_[xx.ravel(), yy.ravel()]
    # get the gradient
    ndgrid_padding = projecters.inverse_transform(xy)
    # print(ndgrid_padding.shape)
    
    # ndgrid_rec = ndgrid_rec
    ndgrid_padding = ndgrid_padding.reshape(grid_pad, grid_pad, -1)
    ## remove the padding for gradient map. 
    ## This is the inverse porjection for all the pixels. It can be cached for downstream use, such as decision boundary map
    ndgrid = ndgrid_padding[1:-1, 1:-1, :].reshape(grid*grid, -1)

    Dx = ndgrid_padding[2:, 1:-1] - ndgrid_padding[:-2, 1:-1]
    Dy = ndgrid_padding[1:-1, 2:] - ndgrid_padding[1:-1, :-2]

    ### original implementation
    w = 1/ grid
    Dx = Dx / (2 * w)
    Dy = Dy / (2 * w)
    ## just assume the pixel width and height are both 1
    # Dx = Dx / 2
    # Dy = Dy / 2

    # get the gradient norm
    D = np.sqrt(np.sum(Dx**2, axis=2) + np.sum(Dy**2, axis=2))
    ## This is the gradient map according to the equations in UnProjeciton paper 
    D = D.reshape(-1)

    ## not necessary to normalize the gradient map to [0,1] here
    # norm_D = D / np.max(D)

    ## return the gradient map and the inverse projection for all the pixels
    return  D, ndgrid