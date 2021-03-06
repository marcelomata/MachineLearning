import matplotlib.pyplot as plt

from b_NaiveBayes.Original.Basic import *
from b_NaiveBayes.Original.MultinomialNB import MultinomialNB

from Util.Util import DataUtil


class GaussianNB(NaiveBayes):
    GaussianNBTiming = Timing()

    @GaussianNBTiming.timeit(level=1, prefix="[API] ")
    def feed_data(self, x, y, sample_weight=None):
        if sample_weight is not None:
            sample_weight = np.asarray(sample_weight)
        x = np.array([list(map(lambda c: float(c), sample)) for sample in x])
        labels = list(set(y))
        label_dic = {label: i for i, label in enumerate(labels)}
        y = np.array([label_dic[yy] for yy in y])
        cat_counter = np.bincount(y)
        labels = [y == value for value in range(len(cat_counter))]
        labelled_x = [x[label].T for label in labels]

        self._x, self._y = x.T, y
        self._labelled_x, self._label_zip = labelled_x, labels
        self._cat_counter, self.label_dic = cat_counter, {i: _l for _l, i in label_dic.items()}
        self.feed_sample_weight(sample_weight)

    @GaussianNBTiming.timeit(level=1, prefix="[Core] ")
    def feed_sample_weight(self, sample_weight=None):
        if sample_weight is not None:
            local_weights = sample_weight * len(sample_weight)
            for i, label in enumerate(self._label_zip):
                self._labelled_x[i] *= local_weights[label]

    @GaussianNBTiming.timeit(level=1, prefix="[Core] ")
    def _fit(self, lb):
        n_category = len(self._cat_counter)
        p_category = self.get_prior_probability(lb)
        data = [
            NBFunctions.gaussian_maximum_likelihood(
                self._labelled_x, n_category, dim) for dim in range(len(self._x))]
        self._data = data

        def func(input_x, tar_category):
            rs = 1
            for d, xx in enumerate(input_x):
                rs *= data[d][tar_category](xx)
            return rs * p_category[tar_category]

        return func

    def visualize(self, save=False):
        colors = plt.cm.Paired([i / len(self.label_dic) for i in range(len(self.label_dic))])
        colors = {_cat: _color for _cat, _color in zip(self.label_dic.values(), colors)}
        for j in range(len(self._x)):
            tmp_data = self._x[j]
            x_min, x_max = np.min(tmp_data), np.max(tmp_data)
            gap = x_max - x_min
            tmp_x = np.linspace(x_min-0.1*gap, x_max+0.1*gap, 200)
            title = "$j = {}$".format(j + 1)
            plt.figure()
            plt.title(title)
            for c in range(len(self.label_dic)):
                plt.plot(tmp_x, [self._data[j][c](xx) for xx in tmp_x],
                         c=colors[self.label_dic[c]], label="class: {}".format(self.label_dic[c]))
            plt.xlim(x_min-0.2*gap, x_max+0.2*gap)
            plt.legend()
            if not save:
                plt.show()
            else:
                plt.savefig("d{}".format(j + 1))

if __name__ == '__main__':
    import time

    xs, ys = DataUtil.get_dataset("mushroom", "../../_Data/mushroom.txt", tar_idx=0)
    nb = MultinomialNB()
    nb.feed_data(xs, ys)
    xs, ys = nb["x"].tolist(), nb["y"].tolist()

    train_num = 6000
    x_train, x_test = xs[:train_num], xs[train_num:]
    y_train, y_test = ys[:train_num], ys[train_num:]

    learning_time = time.time()
    nb = GaussianNB()
    nb.fit(x_train, y_train)
    learning_time = time.time() - learning_time

    estimation_time = time.time()
    nb.evaluate(x_train, y_train)
    nb.evaluate(x_test, y_test)
    estimation_time = time.time() - estimation_time

    print(
        "Model building  : {:12.6} s\n"
        "Estimation      : {:12.6} s\n"
        "Total           : {:12.6} s".format(
            learning_time, estimation_time,
            learning_time + estimation_time
        )
    )
    nb.show_timing_log()
    nb.visualize()
