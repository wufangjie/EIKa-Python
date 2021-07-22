import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import (RandomForestClassifier,
                              AdaBoostClassifier,
                              GradientBoostingClassifier,
                              ExtraTreesClassifier,
                              VotingClassifier,
                              RandomForestRegressor,
                              AdaBoostRegressor,
                              ExtraTreesRegressor,
                              GradientBoostingRegressor)
#from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression, ElasticNet
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC, SVR
from sklearn.model_selection import (GridSearchCV,
                                     cross_val_score,
                                     learning_curve)


__all__ = ['Dummy_sns', 'find_outliers',
           'make_model', 'GSCVWrapper',
           'plot_acc', 'plot_learning_curves', 'plot_feature_importances',
           'cls_models', 'reg_models']


class Dummy_sns:
    """
    import seaborn
    sns = seaborn     # the familiar sns
    sns = Dummy_sns() # if you want dummy sns, i.e. do not plot
    """
    def __getattribute__(self, key):
        return super().__getattribute__('__dummy__')

    def __dummy__(self, *args, **kwargs):
        return self


def find_outliers(df, features, n, times=1.5):
    """
    Outliers can have a dramatic effect on the prediction,
espacially for regression problems
    """
    count = np.zeros(len(df), dtype=int)
    for col in features:
        Q1 = np.percentile(df[col], 25) # if np.nan in df, return np.nan
        Q3 = np.percentile(df[col], 75)
        IQR = Q3 - Q1
        step = times * IQR
        count[(df[col] < Q1 - step) | (df[col] > Q3 + step)] += 1
    return np.nonzero(count > n)[0]


no_random_state_models = {
    'KNeighborsClassifier', 'LinearDiscriminantAnalysis', 'SVR',
    'LinearRegression'}


def make_model(mod, random_state=7, **mod_params):
    assert 'random_state' not in mod_params
    if mod.__name__ not in no_random_state_models:
        mod_params['random_state'] = random_state
    return mod(**mod_params)


class GSCVWrapper:
    def __init__(self, mod, mod_params=None, **cv_params):
        self.mod = mod
        self.mod_params = mod_params if mod_params else {}
        self.cv_params = cv_params
        self.name = mod.__class__.__name__
        self.mod_ = GridSearchCV(mod, mod_params, **cv_params)

    __str__ = __repr__ = lambda self: '<GSCV {}>'.format(self.name)

    def fit(self, X, y, **kwargs):
        print('\n-------\nmod: {}'.format(self))
        self.mod_.fit(X, y, **kwargs)
        # self.best_score_ = self.mod_.best_score_
        # self.best_params_ = self.mod_.best_params_
        # self.cv_results_ = self.mod_.cv_results_
        # 'mean_test_score', 'std_test_score'
        self.best_estimator_ = self.mod_.best_estimator_
        print('best_score: {}\nbest_params: {}'.format(
            self.mod_.best_score_, self.mod_.best_params_))

    def predict(self, X):
        return self.mod_.predict(X)

    def predict_proba(self, X):
        return self.mod_.predict_proba(X)


def plot_acc(mods, X, y, acc=None, **cv_params):
    if acc is None:
        acc = []
        for mod in mods:
            temp = cross_val_score(mod, X, y, **cv_params)
            acc.append((np.mean(temp), np.std(temp)))
        acc = np.array(acc)

    n = len(acc)
    plt.figure()
    plt.barh(range(n), acc[:, 0], height=1, edgecolor='w')
    [plt.plot([acc[i, 0] - acc[i, 1], acc[i, 0] + acc[i, 1]],
              [i, i], color='k') for i in range(n)]
    plt.yticks(range(n), [mod.__class__.__name__ for mod in mods])
    plt.grid('on', linestyle='--', axis='x')
    plt.show()
    return acc


def plot_learning_curves(mod, X, y,
                         train_sizes=np.linspace(0.1, 1, 5), **cv_params):
    """
    两条曲线差距过大, 过拟合
    两条曲线差距不大, 得分低, 欠拟合
    两条曲线差距不大, 得分高, 好模型
    开有就是看趋势
    """
    if hasattr(mod, 'best_estimator_'):
        mod = mod.best_estimator_
    train_sizes, train_scores, test_scores = learning_curve(
        mod, X, y, train_sizes=train_sizes, **cv_params)

    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    c1 = (0.12156862745098039, 0.4666666666666667, 0.7058823529411765)
    c2 = (1.0, 0.4980392156862745, 0.054901960784313725)

    plt.figure()
    plt.plot(train_sizes, train_scores_mean, 'o-', color=c1, label='train')
    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, color=c1, alpha=0.2)
    plt.plot(train_sizes, test_scores_mean, 'o-', color=c2, label='valid')
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, color=c2, alpha=0.2)
    plt.title('{} learning curves'.format(mod.__class__.__name__))
    plt.xlabel('Training examples')
    plt.ylabel('Score')
    plt.grid('on', linestyle='--')
    plt.legend()
    plt.show()


def plot_feature_importances(mod, features, top=20):
    if hasattr(mod, 'best_estimator_'):
        mod = mod.best_estimator_
    if hasattr(mod, 'feature_importances_'):
        fi = mod.feature_importances_
    else:
        print('"{}" object has no attribute "feature_importances_"'.format(
            mod.__class__.__name__))
        return

    features = np.asarray(features)
    index = np.argsort(-fi)[:top][::-1]
    n = len(index)

    plt.figure()
    plt.barh(range(n), fi[index], height=1, edgecolor='w')
    plt.title('{} feature importances'.format(mod.__class__.__name__))
    plt.xlabel('Importance')
    plt.yticks(range(n), features[index])
    plt.grid('on', linestyle='--', axis='x')
    plt.show()
    return fi




########################################################################
# cv_params
########################################################################
# 一般我能用到的 cv_params 也就是以下四个
# (scoring=None, cv=None, verbose=0, n_jobs=1)
# cv: 交叉验证折数
# n_jobs: 使用 cpu 数 (-1 表示全部),
# 也可以通过以下方式 multiprocessing 的 cpu_count 函数获取
# scoring: 看 sklearn.metrics 模块就行, make_scorer, None 的话用模型自带的方法




########################################################################
# Common models
########################################################################

cls_models = [
    [KNeighborsClassifier, # 主要是调 k, 距离和组合
     {'n_neighbors': [5, 10],
      'weights'    : ['uniform', 'distance']
     }],

    [LogisticRegression, # 调参就是加正则, 其中 1/C 是正则系数
     {'penalty': ['l1', 'l2'],
      'C'      : [0.1, 0.5, 1, 2, 5, 10],
      'solver' : ['liblinear']
     }],

    [MLPClassifier, # 不建议用, 我用 theano
     {'hidden_layer_sizes': [(100,), (300,), (100, 100)],
      'activation'        : ['relu', 'logistic', 'tanh'],
      'alpha'             : [0.0001, 0.001]
     }],

    [SVC,
     {'kernel'     : ['rbf'],
      'probability': [True],
      'gamma'      : [0.001, 0.01, 0.1, 1],
      'C'          : [1, 10, 50, 100, 200, 400, 1000]
     }],

    [DecisionTreeClassifier,
     {'max_depth'        : [None],
      'splitter'         : ['best', 'random'],
      'max_features'     : [1, 3, 10],
      'min_samples_split': [2, 3, 10],
      'min_samples_leaf' : [1, 3, 10],
      'criterion'        : ['gini'] # 'entropy'
     }],

    [AdaBoostClassifier,
     {'algorithm'    : ['SAMME', 'SAMME.R'],
      'n_estimators' : [100, 200],
      'learning_rate': [0.0001, 0.001, 0.01, 0.1, 0.2, 0.3, 1.5]
     }],

    [GradientBoostingClassifier,
     {'loss'            : ['deviance'],
      'max_depth'       : [4, 8],
      'max_features'    : [0.1, 0.3],
      'min_samples_leaf': [1, 3, 9],
      'n_estimators'    : [100, 300],
      'learning_rate'   : [0.01, 0.05],
     }],

    [ExtraTreesClassifier,
     {'max_depth'        : [None],
      'bootstrap'        : [False],
      'max_features'     : [0.1, 0.3], # [1, 3, 9],
      'min_samples_split': [2, 3, 9],
      'min_samples_leaf' : [1, 3, 9],
      'n_estimators'     : [100, 300],
      'criterion'        : ['gini'] # 'entropy'
     }],

    [RandomForestClassifier,
     {'max_depth'        : [None],
      'bootstrap'        : [False],
      'max_features'     : [0.1, 0.3], # [1, 3, 9],
      'min_samples_split': [2, 3, 9],
      'min_samples_leaf' : [1, 3, 9],
      'n_estimators'     : [100, 300],
      'criterion'        : ['gini'] # 'entropy'
     }],

    # [LinearDiscriminantAnalysis,
    #  {'solver'   : ['lsqr', 'eigen'],
    #   'shrinkage': [0.01, 0.1, 0.25, 0.5, 1]
    #  }],

]

reg_models = [
    [ElasticNet,
     {'alpha'   : np.logspace(-1, 1, 3),
      'l1_ratio': [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1],
     }],

    [RandomForestRegressor,
     {'max_depth'        : [None],
      'bootstrap'        : [False],
      'max_features'     : [0.1, 0.3], # [1, 3, 9],
      'min_samples_split': [2, 3, 9],
      'min_samples_leaf' : [1, 3, 9],
      'n_estimators'     : [100, 300],
      'criterion'        : ['mse'],
     }],

    # [AdaBoostRegressor,
    #  {'loss'         : ['linear', 'square'],
    #   'n_estimators' : [100, 200],
    #   'learning_rate': [0.0001, 0.001, 0.01, 0.1, 0.2, 0.3, 1.5]
    #  }],

    [ExtraTreesRegressor,
     {'max_depth'        : [None],
      'bootstrap'        : [False],
      'max_features'     : [0.1, 0.3], # [1, 3, 9],
      'min_samples_split': [2, 3, 9],
      'min_samples_leaf' : [1, 3, 9],
      'n_estimators'     : [100, 300],
      'criterion'        : ['mse'],
     }],

    [GradientBoostingRegressor,
     {'loss'            : ['ls'],
      'max_depth'       : [3, 4, 5], # 8
      'max_features'    : [0.1, 0.2, 0.3],
      'min_samples_leaf': [1, 2],#, 9],
      'n_estimators'    : [100, 200], # 300
      'learning_rate'   : [0.01, 0.05],
     }],

    [SVR,
     {'kernel'     : ['rbf'],
      'gamma'      : [0.001, 0.01, 0.1, 1],
      'C'          : [1, 5, 10, 50, 100, 200]#, 400, 1000]
     }]

    # [MLPClassifier, # 不建议用, 我用 theano
    #  {'hidden_layer_sizes': [(100,), (300,), (100, 100)],
    #   'activation'        : ['relu', 'logistic', 'tanh'],
    #   'alpha'             : [0.0001, 0.001]
    #  }],
]
