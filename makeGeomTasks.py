# coding: utf8

from task import Task
from geomPrimitives import tcanvas
import png
import os

rootdir = "./data/geom/"


def fileToArray(fname):
    r = png.Reader(filename=fname)
    array = [[y for y in x[3::4]] for x in r.read()[2]]
    flatten = [item for sublist in array for item in sublist]
    return flatten


def pretty_string(shape, size):
    out = ""
    nl = "\n"
    out += "╭"
    out += "─" * (size * 2)
    out += "╮"
    out += nl
    for j in range(size):
        out += "│"
        for i in range(size):
            if int(shape[j * size + (i % size)]) == 0:
                out += "░░"
            else:
                out += "██"
        out += "│"
        out += nl
    out += "╰"
    out += "─" * (size * 2)
    out += "╯"
    out += nl
    return out


def pretty_print(shape, size):
    print((pretty_string(shape, size)))


def allTasks():
    return next(os.walk(rootdir))[1]


def makeTasks(subfolders):
    problems = []

    if subfolders == ['all']:
        subfolders = allTasks()

    def problem(n, examples, needToTrain=False):
        outputType = tcanvas
        task = Task(n,
                    outputType,
                    [((), y) for _, y in examples])
        task.mustTrain = needToTrain
        problems.append(task)

    for subfolder in subfolders:
        for _, _, files in os.walk(rootdir + subfolder):
            for f in files:
                needed = False if subfolder == "behaviour" else True
                if f.endswith("_l.png"):
                    problem(subfolder+"_"+f,
                            [([], fileToArray(rootdir + subfolder + '/' + f))],
                            needToTrain=needed)

    return problems


if __name__ == "__main__":
    allTasks()
    tasks = makeTasks(['all'])
    for t in tasks:
        print((t))
        x, y = t.examples[0]
        pretty_print(y, 64)
        print()
