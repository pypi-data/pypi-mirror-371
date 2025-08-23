# solver.py

import sys,os

import hipo
import sys, re, os
#import json
import commentjson as json
import argparse


parser = argparse.ArgumentParser()

parser.add_argument('config', type=str)
parser.add_argument('-Afn', type=str)
parser.add_argument('-bfn', type=str)
parser.add_argument('-device', type=str, default='cpu')

args = parser.parse_args()

print(f'args are {args}')



params = json.load(open(args.config))

if args.Afn and args.bfn:
    A = hipo.ParCSRMatrix()
    A.loadFromFile(args.Afn)
    b = hipo.ParMatrix()
    b.loadFromFile(args.bfn)
else:
    testcase = hipo.gallery.createTestCase(params['testcase'])
    ret = testcase.generate()
    print(ret)
    A = ret['A']
    b = ret['b']


if b.getSize() == 0:
    b.resize(A.getRows(), 1)
    b.fill(1)

# transfer the matrix and vector to device.
dev = hipo.Device(args.device)
A = A.toDevice(dev)
b = b.toDevice(dev)

print('desc', args.device, dev, A, b)

# use device to finish the computation.
precond = hipo.createPrecond(params["preconditioner"])
precond.setup(A)
solver = hipo.createSolver(params["solver"])
solver.setup(A)

out = solver.solve(precond, A, b)
