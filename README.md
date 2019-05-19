# Dash-deep

A pure python web service (based on [plotly/dash](https://github.com/plotly/dash)) that is capable of

1. Creation, annotation and updating of image segmentation datasets.
2. Running training and inference jobs.
3. Monitoring the progress of training jobs and related accuracy metrics.
4. Monitoring and halting of running jobs.
5. GPU memory and utilization monitoring.

In other words, it is a pure python customizable version of [Nvidia DIGITS](https://github.com/NVIDIA/DIGITS) with
a focus on image segmentation task.

So far supports only Python 2 -- porting to Python 3 is in progress.

## Image annotation

We have a support for simple web based image uploading and annotation.
This can be used to create a new dataset, make your annotations and run the training code.
So far the tool supports:

1. Zooming in and out
2. Magic lasso
3. Rectangle selection
4. Cropping.

See a simple example below:

<p align="center">
  <img src="https://github.com/warmspringwinds/dash-deep/blob/master/imgs/gif_hair_demo.gif" width="40%" align="middle">
</p>

## Training accuracy/loss monitoring

We support real-time monitoring of training metrics which can be customized,
but by default support validation accuracy and training loss.

<p align="center">
  <img src="https://github.com/warmspringwinds/dash-deep/blob/master/imgs/plot_demo.gif" width="40%" align="middle">
</p>

## Updating annotations of existing dataset

You can update saved dataset any time

<p align="center">
  <img src="https://github.com/warmspringwinds/dash-deep/blob/master/imgs/gif_update_dataset_demo.gif" width="40%" align="middle">
</p>

## Running

To start the server run:

```
 python -m dash_deep.index run_server <ip_address> <port>
```

You can use ip address of ```0.0.0.0``` which will automatically use the network ip
of the machine that you are running the server on.

Open browser and navigate to:

```
<ip_address>:<port>/
```

To get the help page, call:

```
 python -m dash_deep.index --help
```

The default login name and pass are ```hello``` and ```world```.