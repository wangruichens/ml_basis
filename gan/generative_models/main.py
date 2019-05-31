import os

## GAN Variants
from generative_models.GAN import GAN
from generative_models.CGAN import CGAN
from generative_models.infoGAN import infoGAN
from generative_models.ACGAN import ACGAN
from generative_models.EBGAN import EBGAN
from generative_models.WGAN import WGAN
from generative_models.WGAN_GP import WGAN_GP
from generative_models.DRAGAN import DRAGAN
from generative_models.LSGAN import LSGAN
from generative_models.BEGAN import BEGAN

## VAE Variants
from generative_models.VAE import VAE
from generative_models.CVAE import CVAE

from generative_models.utils import show_all_variables
from generative_models.utils import check_folder

import tensorflow as tf
import argparse

"""parsing and configuration"""


def parse_args():
    desc = "Tensorflow implementation of GAN collections"
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--gan_type', type=str, default='CVAE',
                        choices=['GAN', 'CGAN', 'infoGAN', 'ACGAN', 'EBGAN', 'BEGAN', 'WGAN', 'WGAN_GP', 'DRAGAN',
                                 'LSGAN', 'VAE', 'CVAE'],
                        help='The type of GAN')
    parser.add_argument('--dataset', type=str, default='mnist', choices=['mnist', 'fashion-mnist', 'celebA'],
                        help='The name of dataset')
    parser.add_argument('--epoch', type=int, default=20, help='The number of epochs to run')
    parser.add_argument('--batch_size', type=int, default=64, help='The size of batch')
    parser.add_argument('--z_dim', type=int, default=62, help='Dimension of noise vector')
    parser.add_argument('--checkpoint_dir', type=str, default='checkpoint',
                        help='Directory name to save the checkpoints')
    parser.add_argument('--result_dir', type=str, default='results',
                        help='Directory name to save the generated images')
    parser.add_argument('--log_dir', type=str, default='logs',
                        help='Directory name to save training logs')

    return check_args(parser.parse_args())


"""checking arguments"""


def check_args(args):
    # --checkpoint_dir
    check_folder(args.checkpoint_dir)
    # --result_dir
    check_folder(args.result_dir)
    # --result_dir
    check_folder(args.log_dir)
    # --epoch
    assert args.epoch >= 1, 'number of epochs must be larger than or equal to one'
    # --batch_size
    assert args.batch_size >= 1, 'batch size must be larger than or equal to one'
    # --z_dim
    assert args.z_dim >= 1, 'dimension of noise vector must be larger than or equal to one'
    return args


"""main"""


def main():
    # parse arguments
    args = parse_args()
    if args is None:
        exit()

    # open session
    models = [GAN, CGAN, infoGAN, ACGAN, EBGAN, WGAN, WGAN_GP, DRAGAN,
              LSGAN, BEGAN, VAE, CVAE]
    with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as sess:
        # declare instance for GAN

        gan = None
        for model in models:
            if args.gan_type == model.model_name:
                gan = model(sess,
                            epoch=args.epoch,
                            batch_size=args.batch_size,
                            z_dim=args.z_dim,
                            dataset_name=args.dataset,
                            checkpoint_dir=args.checkpoint_dir,
                            result_dir=args.result_dir,
                            log_dir=args.log_dir)
        if gan is None:
            raise Exception("[!] There is no option for " + args.gan_type)

        # build graph
        gan.build_model()

        # show network architecture
        show_all_variables()

        # launch the graph in a session
        gan.train()
        print(" [*] Training finished!")

        # visualize learned generator
        gan.visualize_results(args.epoch - 1)
        print(" [*] Testing finished!")


if __name__ == '__main__':
    main()