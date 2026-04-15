import argparse

from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import f1_score

from bayes_opt import BayesianOptimization

from p1_modelos.utilidades import init_dataset, gardar_experimento_adaboost

#--

parser = argparse.ArgumentParser(prog='optimizacion bayesiana do adaboost', epilog='-    :)   -')
parser.add_argument('-p',dest='puntos', default=10, type=int)  
parser.add_argument('-i',dest='iteracions', default=20, type=int)
parser.add_argument('-d',dest='dataset', default='dataset', type=str)
parser.add_argument('-b', '--binary', dest='binary', action='store_true')
args = parser.parse_args()

X_train, y_train, y_train_bin, X_val, y_val, y_val_bin, X_test, y_test, y_test_bin = init_dataset(args.dataset)

y_train_target = y_train_bin if args.binary else y_train
y_val_target = y_val_bin if args.binary else y_val

random_state = 1995 # ano do adaboost

# https://github.com/bayesian-optimization/BayesianOptimization

def funcion_perdida_adaboost(n_estimators, learning_rate):
    adaboost = AdaBoostClassifier(n_estimators=n_estimators, learning_rate=learning_rate, random_state=random_state)
    adaboost.fit(X_train, y_train_target)
    y_val_predicho = adaboost.predict(X_val)
    return f1_score(y_val_target, y_val_predicho, average='micro') # micro ten en conta o desbalanceo de clases

optimizador = BayesianOptimization(
    f=funcion_perdida_adaboost,
    # https://github.com/bayesian-optimization/BayesianOptimization/blob/master/examples/parameter_types.ipynb
    pbounds={'n_estimators': (15, 500, int), 'learning_rate': (0.0001, 2)},
   random_state=random_state,
)

optimizador.maximize(
    init_points=args.puntos,
    n_iter=args.iteracions,
)


solucion = optimizador.max['params']
#solucion = {
#    'n_estimators': int(round(solucion['n_estimators'])),
#    'learning_rate': float(solucion['learning_rate']),
#}

adaboost = AdaBoostClassifier(n_estimators=solucion['n_estimators'], learning_rate=solucion['learning_rate'], random_state=random_state)
adaboost.fit(X_train, y_train_target)
parametros = adaboost.get_params()

gardar_experimento_adaboost(parametros, optimizador.res, solucion)
