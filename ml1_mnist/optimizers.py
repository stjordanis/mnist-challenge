import numpy as np

from utils import print_inline, width_format, Stopwatch


def get_optimizer(optimizer_name, **params):
    for k, v in globals().items():
        if k.lower() == optimizer_name.lower():
            return v(**params)
    raise ValueError("invalid optimizer name '{0}'".format(optimizer_name))


class BaseOptimizer(object):
    def __init__(self, max_epochs=100, tol=1e-4, verbose=False):
        self.max_epochs = max_epochs
        self.tol = tol
        self.verbose = verbose

    def _setup(self, nnet):
        pass

    def update(self, nnet):
        raise NotImplementedError()

    def train_epoch(self, nnet):
        self._setup(nnet)
        losses = []
        for X_batch, y_batch in nnet.batch_iter():
            if self.verbose: print_inline('.')
            loss = np.mean(nnet.update(X_batch, y_batch))
            self.update(nnet)
            losses.append(loss)
        if self.verbose: print
        return np.mean(losses) # epoch loss

    def optimize(self, nnet):
        loss_history = []
        timer = Stopwatch(verbose=False).start()
        for i in xrange(self.max_epochs):
            if self.verbose:
                print_inline('Epoch {0:>{1}}/{2} '.format(i + 1, len(str(self.max_epochs)), self.max_epochs))
            loss = self.train_epoch(nnet)
            loss_history.append(loss)
            msg = 'elapsed: {0} sec'.format(width_format(timer.elapsed(), default_width=5, max_precision=2))
            msg += ' - loss: {0}'.format(width_format(loss, default_width=5, max_precision=4))
            score = nnet._metric(nnet._y, nnet.validate())
            # TODO: change acc to metric name
            msg += ' - acc.: {0}'.format(width_format(score, default_width=6, max_precision=4))
            if nnet._X_val:
                val_loss = nnet._loss(nnet._y_val, nnet.validate_proba(nnet._X_val))
                val_score = nnet._metric(nnet._y_val, nnet.validate(nnet._X_val))
                msg += ' - val. loss: {0}'.format(width_format(val_loss, default_width=5, max_precision=4))
                # TODO: fix acc.
                msg += ' - val. acc.: {0:.4f}'.format(width_format(val_score, default_width=6, max_precision=4))
            if self.verbose: print msg
            # TODO: save learning curves
        return loss_history


class Adam(BaseOptimizer):
    def __init__(self, learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-8, **params):
        self.learning_rate = learning_rate
        self.beta_1 = beta_1
        self.beta_2 = beta_2
        self.epsilon = epsilon
        self.t = 1
        super(Adam, self).__init__(**params)

    def update(self, nnet):
        pass