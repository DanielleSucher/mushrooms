# Raw data imported from
#
#     Frank, A. & Asuncion, A. (2010). UCI Machine Learning Repository
#     [http://archive.ics.uci.edu/ml]. Irvine, CA: University of California,
#     School of Information and Computer Science.

from itertools import chain
from pybrain import datasets as ds
from pybrain.tools.shortcuts import buildNetwork
from pybrain.structure.modules import SoftmaxLayer
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.utilities import percentError

def transpose(ls):
    return zip(*ls)

def make_input_list(filename):
    return [line.strip().split(",") for line in open(filename)]

def collect_groups(input_list):
    return [list(sorted(set(group)))
            for group in transpose(input_list)]

def get_singleton_indices(ls):
    return [i
            for i, each in enumerate(ls)
            if len(each) < 2]

def remove_indices(ls, ixs):
    for i in sorted(ixs, reverse=True):
        ls.pop(i)

def get_options_count(groups):
    return map(len, groups)

def indices(input_list, groups):
    return [[group.index(word)
             for group, word in zip(groups, row)]
            for row in input_list]

def one_to_many(row, group_counts):
    return list(chain.from_iterable(
        [int(index==row_index)
         for index in xrange(gc)]
        for row_index, gc in zip(row, group_counts)))

def split_data(mix, ywidth):
    ys = [row[:ywidth] for row in mix]
    inputs = [row[ywidth:] for row in mix]
    return inputs, ys

def prep(filename):
    input_list = make_input_list(filename)
    groups = collect_groups(input_list)
    singleton_indices = get_singleton_indices(groups)
    for row in input_list + [groups]:
        remove_indices(row, singleton_indices)
    ixs = indices(input_list, groups)
    ixs, ys = split_data(ixs, 1)
    gc = get_options_count(groups)
    inputs = [one_to_many(row, gc)
              for row in ixs]
    return inputs, ys, gc

def train(args):
  inputs, ys, gc = args
  row_length = len(inputs[0])
  d = ds.ClassificationDataSet(
      row_length, nb_classes=2, class_labels=['Poisonous',
                                              'Edible'])
  d.setField('input', inputs)
  d.setField('target', ys)
  test, train = d.splitWithProportion(.25)
  test._convertToOneOfMany()
  train._convertToOneOfMany()

  hidden = row_length // 2
  print "indim:", train.indim
  net = buildNetwork(train.indim,
                     hidden,
                     train.outdim,
                     outclass=SoftmaxLayer)
  trainer = BackpropTrainer(net,
                            dataset=train,
                            momentum=0.0,
                            learningrate=0.1,
                            verbose=True,
                            weightdecay=0.0)
  for i in xrange(20):
      trainer.trainEpochs(1)
      trnresult = percentError(trainer.testOnClassData(),
                                train['class'])
      tstresult = percentError(
              trainer.testOnClassData(dataset=test),
              test['class'])
      print "epoch: %4d" % trainer.totalepochs, \
            "  train error: %5.2f%%" % trnresult, \
            "  test error: %5.2f%%" % tstresult
  return net, gc

def classify(network, gc, mushroom):
  return network.activate(one_to_many(mushroom, gc))

def test_prep():
    input_list = [[1, 2, 3, 4, 5, 4, 6],
                  [2, 1, 2, 4, 3, 6, 4],
                  [3, 1, 1, 4, 2, 4, 3]]
    groups = collect_groups(input_list)
    assert groups == [[1, 2, 3],
                      [1, 2],
                      [1, 2, 3],
                      [4],
                      [2, 3, 5],
                      [4, 6],
                      [3, 4, 6]]
    assert len(input_list[0]) == len(groups)
    old_length = len(input_list[0])
    singleton_indices = get_singleton_indices(groups)
    for row in input_list + [groups]:
        remove_indices(row, singleton_indices)
    assert len(input_list[0]) == len(groups) == old_length - 1
    ixs = indices(input_list, groups)
    assert ixs == [[0, 1, 2, 2, 0, 2],
                   [1, 0, 1, 1, 1, 1],
                   [2, 0, 0, 0, 0, 0]]
    ixs, ys = split_data(ixs, 1)
    groups.pop(0)
    assert ixs, ys == (
            [[0, 1, 2, 2, 0, 2],
             [1, 0, 1, 1, 1, 1],
             [2, 0, 0, 0, 0, 0]]
            [0, 1, 2])
    gc = get_options_count(groups)
    assert gc == [2, 3, 3, 2, 3]
    otm = [one_to_many(row, gc)
           for row in ixs]
    assert otm == [[0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1],
                   [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0],
                   [1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0]]

def test_get_singleton_indices():
    assert get_singleton_indices([[1, 2], [3], [4, 5, 4], [6]]) == [1, 3]

def test():
    test_get_singleton_indices()
    test_prep()
    train(prep("raw_data"))
    print "All OK."


if __name__ == "__main__":
  # test()
  train(prep("raw_data"))
