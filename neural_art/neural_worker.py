import json
import os
import threading
import time
import multiprocessing
from multiprocessing import Process

import deeppy as dp
import numpy as np
import scipy.misc
from sqlalchemy.ext.automap import automap_base

import response
from matconvnet import vgg_net
from style_network import StyleNetwork


def weight_tuple(tuples_array):
    try:
        array = []
        for s in tuples_array:
            conv_idx, weight = map(float, s)
            array.append((conv_idx, weight,))
        return array
    except:
        raise TypeError('weights must by "int,float"')


def float_range(x):
    x = float(x)
    if x < 0.0 or x > 1.0:
        raise TypeError("%r not in range [0, 1]" % x)
    return x


def weight_array(weights):
    array = np.zeros(19)
    for idx, weight in weights:
        array[idx] = weight
    norm = np.sum(array)
    if norm > 0:
        array /= norm
    return array


def imread(path):
    return scipy.misc.imread(path).astype(dp.float_)


def imsave(path, img):
    img = np.clip(img, 0, 255).astype(np.uint8)
    scipy.misc.imsave(path, img)


def to_bc01(img):
    return np.transpose(img, (2, 0, 1))[np.newaxis, ...]


def to_rgb(img):
    return np.transpose(img[0], (1, 2, 0))


class Argument(object):
    def _callable(self, obj):
        return hasattr(obj, '__call__') or hasattr(obj, '__bases__')

    def __init__(self, name, arg_class, required=False, default=None, choices=None):
        if not self._callable(arg_class):
            raise ValueError('{0} is not callable!'.format(str(arg_class)))

        self.name = name
        self.type = arg_class
        if default is not None:
            self.value = arg_class(default)
        else:
            self.value = None
        self.required = required
        self.choices = choices


class ArgumentContainer(object):
    def __init__(self, arguments):
        self.arguments = arguments
        for arg, val in arguments.items():
            setattr(self, arg, val)


class ArgumentParser(object):
    def __init__(self, arguments=[]):
        self.arguments = arguments

    def add_argument(self, name, type, required=False, default=None, choices=None):
        self.arguments.append(Argument(
            name, type, required, default, choices
        ))

    def parse_args(self, given_args):
        args = {}

        for arg in self.arguments:
            if arg.name not in given_args and arg.required:
                raise ValueError('Value is required for {0} argument!'.format(arg.name))
            if arg.choices:
                if arg.value not in arg.choices:
                    raise ValueError('Value for {0} argument is incorrect!'.format(arg.name))
            args[arg.name] = arg.type(given_args[arg.name]) if arg.name in given_args else arg.value

        return ArgumentContainer(args)


def init_args(given_args):
    parser = ArgumentParser()
    parser.add_argument('subject', required=True, type=str)
    parser.add_argument('style', required=True, type=str)
    parser.add_argument('output', required=True, type=str)
    parser.add_argument('init', default=None, type=str)
    parser.add_argument('init_noise', default=0.0, type=float_range)
    parser.add_argument('random_seed', default=None, type=int)
    parser.add_argument('animation', default='animation', type=str)
    parser.add_argument('iterations', default=500, type=int)
    parser.add_argument('learn_rate', default=2.0, type=float)
    parser.add_argument('smoothness', type=float, default=5e-8)
    parser.add_argument('subject_weights', type=weight_tuple,
                        default=[(9, 1,)])
    parser.add_argument('style_weights', type=weight_tuple,
                        default=[(0, 1), (2, 1), (4, 1), (8, 1), (12, 1)])
    parser.add_argument('subject_ratio', type=float, default=2e-2)
    parser.add_argument('pool_method', default='avg', type=str,
                        choices=['max', 'avg'])
    return parser.parse_args(given_args)


class ImageProcessor(threading.Thread):

    def __init__(self, engine, Session):
        threading.Thread.__init__(self)
        self.engine = engine
        self.Session = Session
        self._stop = threading.Event()
        self._skip = False

    def stop(self):
        self._stop.set()

    def skip(self):
        self._skip = True

    def stopped(self):
        return self._stop.is_set()

    def run(self):
        print(threading.current_thread())
        Session = self.Session
        engine = self.engine

        network = 'neural_art/imagenet-vgg-verydeep-19.mat'
        session = Session()
        Base = automap_base()
        Base.prepare(engine, reflect=True)

        Image = Base.classes.images
        Queue = Base.classes.queue

        while not self.stopped():
            cur_img = session.query(Queue).first()
            if not cur_img:
                time.sleep(1)
            else:
                id = cur_img.ID
                given_args = json.loads(cur_img.Args)

                img_info = session.query(Image).filter(Image.ID == id).first()
                given_args['subject'] = img_info.Subject
                given_args['style'] = img_info.Style
                given_args['output'] = img_info.Result

                args = init_args(given_args)

                session.delete(cur_img)

                img_info.Status = response.image_processing_started()

                Session.commit()

                if args.random_seed is not None:
                    np.random.seed(args.random_seed)

                layers, pixel_mean = vgg_net(network, pool_method=args.pool_method)
                # Inputs
                style_img = imread(args.style) - pixel_mean
                subject_img = imread(args.subject) - pixel_mean
                if args.init is None:
                    init_img = subject_img
                else:
                    init_img = imread(args.init) - pixel_mean
                noise = np.random.normal(size=init_img.shape, scale=np.std(init_img)*1e-1)
                init_img = init_img * (1 - args.init_noise) + noise * args.init_noise

                # Setup network
                subject_weights = weight_array(args.subject_weights) * args.subject_ratio
                style_weights = weight_array(args.style_weights)
                net = StyleNetwork(layers, to_bc01(init_img), to_bc01(subject_img),
                                   to_bc01(style_img), subject_weights, style_weights,
                                   args.smoothness)

                # Repaint image
                def net_img():
                    return to_rgb(net.image) + pixel_mean

                if not os.path.exists(args.animation):
                    os.mkdir(args.animation)
                params = net.params
                learn_rule = dp.Adam(learn_rate=args.learn_rate)
                learn_rule_states = [learn_rule.init_state(p) for p in params]
                for i in range(args.iterations):
                    if self._skip:
                        break
                    img_info.Status = response.image_iterations_progress(i + 1, args.iterations)
                    Session.commit()
                    imsave(os.path.join(args.animation, '%.4d.png' % i), net_img())
                    cost = np.mean(net.update())
                    for param, state in zip(params, learn_rule_states):
                        learn_rule.step(param, state)
                    print('Iteration: %i, cost: %.4f' % (i, cost))
                if not self._skip:
                    imsave(args.output, net_img())
                    img_info.Status = response.image_processing_ended()
                self._skip = False
                Session.commit()
