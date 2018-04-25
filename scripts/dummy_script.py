import argparse

def get_parser():

    parser = argparse.ArgumentParser(description="Image Segmentation training script")

    parser.add_argument("--batch-size", type=int, default=100,
                        help="Number of images sent to the network in one step.")

    parser.add_argument("--data-dir", type=str,# default=DATA_DIRECTORY,
                        help="Path to the directory containing the PASCAL VOC dataset.")


    parser.add_argument("--learning-rate", type=float,# default=LEARNING_RATE,
                        help="Base learning rate for training with polynomial decay.")

    parser.add_argument("--num-classes", type=int,# default=NUM_CLASSES,
                        help="Number of classes to predict (including background).")

    parser.add_argument("square", help="display a square of a given number")

    return parser

