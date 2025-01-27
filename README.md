<div align="center">
  <img height="240px" src="https://docs.google.com/drawings/d/e/2PACX-1vSl80T4MnWRsPX3KvlB2kn6zVdHdUleG_w2zBiLS7RxLGAHxiSYTnw3LZtXh__YMv6KcIOYOvkSt9PB/pub?w=841&h=350" alt="creme_logo"/>
</div>

<div align="center">
  <!-- Travis -->
  <a href="https://travis-ci.org/creme-ml/creme">
    <img src="https://img.shields.io/travis/creme-ml/creme/master.svg?style=for-the-badge" alt="travis" />
  </a>
  <!-- Codecov -->
  <a href="https://codecov.io/gh/creme-ml/creme">
    <img src="https://img.shields.io/codecov/c/gh/creme-ml/creme.svg?style=for-the-badge" alt="codecov" />
  </a>
  <!-- Codacy -->
  <a href="https://www.codacy.com/app/MaxHalford/creme">
    <img src="https://img.shields.io/codacy/grade/56da6d188f4a417da0b7eaa435303862.svg?style=for-the-badge" alt="codecov" />
  </a>
  <!-- PyPI -->
  <a href="https://pypi.org/project/creme">
    <img src="https://img.shields.io/pypi/v/creme.svg?style=for-the-badge" alt="pypi" />
  </a>
  <!-- License -->
  <a href="https://opensource.org/licenses/BSD-3-Clause">
    <img src="https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=for-the-badge" alt="bsd_3_license"/>
  </a>
</div>

<br/>

`creme` is a library for online machine learning, also known as in**creme**ntal learning. Online learning is a machine learning regime where a model learns one observation at a time. This is in contrast to batch learning where all the data is processed in one go. Incremental learning is desirable when the data is too big to fit in memory, or simply when it isn't available all at once. `creme`'s API is heavily inspired from that of [scikit-learn](https://scikit-learn.org/stable/), enough so that users who are familiar with it should feel right at home.

## Useful links

- [Documentation](https://creme-ml.github.io/)
  - [API reference](https://creme-ml.github.io/api.html)
  - [User guide](https://creme-ml.github.io/user-guide.html)
  - [Benchmarks](https://creme-ml.github.io/benchmarks.html)
- [Issue tracker](https://github.com/creme-ml/creme/issues)
- [Package releases](https://pypi.org/project/creme/#history)
- [Change history](CHANGELOG.md)
- PyData Amsterdam 2019 presentation ([slides](https://maxhalford.github.io/slides/creme-pydata/), video incoming)
- [Blog post from pyimagesearch for image classification](https://www.pyimagesearch.com/2019/06/17/online-incremental-learning-with-keras-and-creme/)

## Installation

:point_up: `creme` is tested with Python 3.6 and above.

`creme` mostly relies on Python's standard library. Sometimes it relies on `numpy`, `scipy`, and `scikit-learn` so as not to reinvent the wheel. `creme` can simply be installed with `pip`.

```sh
pip install creme
```

## Quick example

In the following snippet we'll be fitting an online logistic regression. The weights of the model will be optimized with the [AdaGrad](http://akyrillidis.github.io/notes/AdaGrad) algorithm. We'll scale the data so that each variable has a mean of 0 and a standard deviation of 1. The standard scaling and the logistic regression are combined into a pipeline using the `|` operator. We'll be using the `stream.iter_sklearn_dataset` function for streaming over the [Wisconsin breast cancer dataset](http://archive.ics.uci.edu/ml/datasets/breast+cancer+wisconsin+%28diagnostic%29). We'll measure the [F1-score](https://www.wikiwand.com/en/F1_score) using [progressive validation](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.153.3925&rep=rep1&type=pdf).

```python
>>> from creme import compose
>>> from creme import linear_model
>>> from creme import metrics
>>> from creme import model_selection
>>> from creme import optim
>>> from creme import preprocessing
>>> from creme import stream
>>> from sklearn import datasets

>>> X_y = stream.iter_sklearn_dataset(
...     dataset=datasets.load_breast_cancer(),
...     shuffle=True,
...     random_state=42
... )

>>> scaler = preprocessing.StandardScaler()
>>> lin_reg = linear_model.LogisticRegression(optimizer=optim.AdaGrad())
>>> model = scaler | lin_reg

>>> metric = metrics.F1()

>>> for x, y in X_y:
...     y_pred = model.predict_one(x)
...     model = model.fit_one(x, y)
...     metric = metric.update(y, y_pred)

>>> metric
F1: 0.97191

```

## Comparison with other solutions

- [scikit-learn](https://scikit-learn.org/stable/): [Some](https://scikit-learn.org/stable/modules/computing.html#incremental-learning) of it's estimators have a `partial_fit` method which allows them to update themselves with new observations. However, online learning isn't treated as a first class citizen, which can make things awkward. You should definitely use scikit-learn if your data fits in memory and that you can afford retraining your model from scratch every time new data is available.
- [Vowpal Wabbit](https://github.com/VowpalWabbit/vowpal_wabbit/wiki): VW is probably the fastest out-of-core learning system available. At it's core it implements a state-of-the-art adaptive gradient descent algorithm with many tricks. It also has some mechanisms for doing [active learning](https://www.wikiwand.com/en/Active_learning_(machine_learning)) and using [bandits](https://www.wikiwand.com/en/Multi-armed_bandit). However it isn't a "true" online learning system as it assumes the data is available in a file and can be looped over multiple times. Also it is somewhat difficult to [grok](https://www.wikiwand.com/en/Grok) for newcomers.
- [LIBOL](https://github.com/LIBOL/SOL): This is a good library written by academics with some great documentation. It's written in C++ and seems to be pretty fast. However it only focuses on the learning aspect of online learning, not on other mundane yet useful tasks such as feature extraction and preprocessing. Moreover it hasn't been updated for a few years.
- [Spark Streaming](https://spark.apache.org/docs/latest/streaming-programming-guide.html): This is an extension of [Apache Spark](https://www.wikiwand.com/en/Apache_Spark) which caters to big data practitioners. It processes data in mini-batches instead of actually doing real streaming operations. It also has some compatibility with the [MLlib](https://spark.apache.org/docs/latest/ml-guide.html) for implementing online learning algorithms, such as [streaming linear regression](https://spark.apache.org/docs/latest/mllib-linear-methods.html#streaming-linear-regression) and [streaming k-means](https://spark.apache.org/docs/latest/mllib-clustering.html#streaming-k-means). However it is a somewhat overwhelming solution which might be a bit overkill for certain use cases.
- [TensorFlow](https://www.wikiwand.com/en/TensorFlow): Deep learning systems are in some sense online learning systems because they use online gradient descent. However, popular libraries are mostly attuned to batch situations. Because frameworks such as [Keras](https://keras.io/) and [PyTorch](https://pytorch.org/) are so popular and very well backed, there is no real point in implementing neural networks in creme. Additionally, for a lot of problems neural networks might not be the right tool, and you might want to use a simple logistic regression or a decision tree (for which online algorithms exist).

Feel free to open an issue if you feel like other solutions are worth mentioning.

## Contributing

Like many subfields of machine learning, online learning is far from being an exact science and so there is still a lot to do. Feel free to contribute in any way you like, we're always open to new ideas and approaches. If you want to contribute to the code base please check out the [`CONTRIBUTING.md` file](`CONTRIBUTING.md`). Also take a look at the [issue tracker](https://github.com/creme-ml/creme/issues) and see if anything takes your fancy.

Last but not least you are more than welcome to share with us how you're using `creme` or online learning in general! We believe that online learning solves a lot of pain points in practice and we would love to share experiences.

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind are welcome!

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore -->
<table><tr><td align="center"><a href="https://maxhalford.github.io"><img src="https://avatars1.githubusercontent.com/u/8095957?v=4" width="100px;" alt="Max Halford"/><br /><sub><b>Max Halford</b></sub></a><br /><a href="#projectManagement-MaxHalford" title="Project Management">📆</a> <a href="https://github.com/Max Halford/creme/commits?author=MaxHalford" title="Code">💻</a></td><td align="center"><a href="https://github.com/AdilZouitine"><img src="https://avatars0.githubusercontent.com/u/24889239?v=4" width="100px;" alt="AdilZouitine"/><br /><sub><b>AdilZouitine</b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=AdilZouitine" title="Code">💻</a></td><td align="center"><a href="https://github.com/raphaelsty"><img src="https://avatars3.githubusercontent.com/u/24591024?v=4" width="100px;" alt="Raphael Sourty"/><br /><sub><b>Raphael Sourty</b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=raphaelsty" title="Code">💻</a></td><td align="center"><a href="http://www.linkedin.com/in/gbolmier"><img src="https://avatars0.githubusercontent.com/u/25319692?v=4" width="100px;" alt="Geoffrey Bolmier"/><br /><sub><b>Geoffrey Bolmier</b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=gbolmier" title="Code">💻</a></td><td align="center"><a href="http://koaning.io"><img src="https://avatars1.githubusercontent.com/u/1019791?v=4" width="100px;" alt="vincent d warmerdam "/><br /><sub><b>vincent d warmerdam </b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=koaning" title="Code">💻</a></td><td align="center"><a href="https://github.com/VaysseRobin"><img src="https://avatars2.githubusercontent.com/u/32324822?v=4" width="100px;" alt="VaysseRobin"/><br /><sub><b>VaysseRobin</b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=VaysseRobin" title="Code">💻</a></td><td align="center"><a href="https://github.com/tweakyllama"><img src="https://avatars0.githubusercontent.com/u/7049400?v=4" width="100px;" alt="Lygon Bowen-West"/><br /><sub><b>Lygon Bowen-West</b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=tweakyllama" title="Code">💻</a></td></tr><tr><td align="center"><a href="https://github.com/flegac"><img src="https://avatars2.githubusercontent.com/u/4342302?v=4" width="100px;" alt="Florent Le Gac"/><br /><sub><b>Florent Le Gac</b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=flegac" title="Code">💻</a></td></tr></table>

<!-- ALL-CONTRIBUTORS-LIST:END -->

## License

See the [license file](LICENSE).
