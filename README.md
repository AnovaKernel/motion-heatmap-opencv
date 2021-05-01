# motion-heatmap-opencv
A repository to store codes and supportive material to the omonimous [Medium](https://medium.com/p/fd806e8a2340) article.
This code is an adaptation of the [Intel Motion Heatmap](https://github.com/intel-iot-devkit/python-cv-samples/tree/master/examples/motion-heatmap)

![](./heatmap_gif.gif)

# Run
Cone this repository, `cd` into the directory and run `python motion_heatmap.py `, if you want to use another video change the path in `motion_heatmap.py` in the `main()` function.

# Requirements
To run this script you will need python 3.6+ installed along with OpenCV  3.3.0+ and numpy.
Make also sure to have installed the MOG background subtractor by running:

`pip install opencv-contrib-python`

to make an executable you'd need pyinstaller
`pip install pyinstaller`


# create exe
`pyinstaller --onefile gui.spec`

# todo list
- customize max_value for color intensity
- specify a custom reference image
- error handling
- threading