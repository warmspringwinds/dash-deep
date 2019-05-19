# Dash-deep

A pure python web service that is capable of

1. Creation and annotation of image segmentation datasets.
2. Running training and inference jobs.
3. Monitoring the progress of training jobs and related accuracy metrics.
4. Monitoring and halting of running jobs.

In other words, it is a pure python customizable version of [Nvidia DIGITS](https://github.com/NVIDIA/DIGITS) with
a focus on image segmentation task.

So far supports only Python 2 -- porting to Python 3 is in progress.

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