# Welcome to this heatmap generator!

First, select your sourcematerial (video). Bear in mind that the result will be the best when the source is of good quality. Yes, GIGO. Above all the sourcematerial should be filmed from a stable position, e.g. from a tripod. A moving camera, even with some slight vibrations, will result in lots of noise.

The result will also be better when there is:
- No sun. Shadows will distort the picture and passing clouds will be seen as changes. So the actual chances (people moving) will be less visible.
- No wind. Moving objects such as trees might interfere with the outcome.
- No rain. Because who wants to be outside when it rains?!?

When your file is loaded, there's some settings you can adjust.

- Heat intensity. Sets the amount of effect movable objects will have on the heatmap. When theres a lot of movable objects, objects move slow or when the video is long, set the intensity lower. When there's not so much going on or when objects move fast, set the intensity higher. [NOT YET AVAILABLE]

- Heat colour. Comes in the red, yellow, blue or green taste. This might come in handy when you have multiple sourcevid's that you want to compare. [NOT YET AVAILABLE]

- Frameskip. This is the amount of frames it skips when analysing the next frame. So when set to 3, only 1 out of 4 frames will be analysed. This will make the analysing process go faster but the end result less precise. Keep in mind that this effects the heat intesity too. [NOT YET AVAILABLE]

- Max frames. (??) Sets the max of frames to render. Most video's have 24 or 30 frames per second, which is 1440 or 1800 frames per minute. [NOT YET AVAILABLE]

When you click 'Generate heatmap', it will generate 3 files:
1. A movie file in which you'll see the magic happen in real-time. Wow, such beautiful! This file can become quite big; about 1 gig per minute when the sourcematerial is HD.
2. A picture of the end result; the heatmap.
3. A picture of the end result without the reference frame. [NOT YET AVAILABLE]

So what are you waiting for? Go on and try it!

# Credits
This heatmap generator is forked from [robertosannazzaro's motion-heatmap-opencv](https://github.com/robertosannazzaro/motion-heatmap-opencv). His code is an adaptation of the [Intel Motion Heatmap](https://github.com/intel-iot-devkit/python-cv-samples/tree/master/examples/motion-heatmap)

![](./heatmap_gif.gif)
