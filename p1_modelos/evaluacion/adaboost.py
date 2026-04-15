import argparse
import pickle
from pathlib import Path

import yaml

from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score

from p1_modelos.utilidades.init_dataset import init_dataset

parser = argparse.ArgumentParser(prog='evaluacion do adaboost', epilog='-    :)   -')
parser.add_argument('-id',dest='execucion_id', default='a80650', type=str)
args = parser.parse_args()

random_state = 1995 # ano do adaboost

p = Path(f'pesos/{args.execucion_id}')
modelo_path = p / 'adaboost.pickle'

if not modelo_path.exists(): raise FileNotFoundError(f'[X] Non existe o modelo: {modelo_path}')

with open(p / 'solucion.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

adaboost = AdaBoostClassifier(n_estimators=config['n_estimators'], learning_rate=config['learning_rate'], random_state=random_state)

with open(modelo_path, 'rb') as f:
    adaboost = pickle.load(f)
    print(f'[*] Cargado modelo desde {modelo_path}')

X_train, y_train, y_train_bin, X_val, y_val, y_val_bin, X_test, y_test, y_test_bin = init_dataset('dataset')


y_test_predicho = adaboost.predict(X_test)

accuracy = accuracy_score(y_test, y_test_predicho)
precision = precision_score(y_test, y_test_predicho, average='micro', zero_division=0)
recall = recall_score(y_test, y_test_predicho, average='micro', zero_division=0)
f1 = f1_score(y_test, y_test_predicho, average='micro') # micro ten en conta o desbalanceo de clases
f1_macro = f1_score(y_test, y_test_predicho, average='macro', zero_division=0)
f1_weighted = f1_score(y_test, y_test_predicho, average='weighted', zero_division=0)

print('=== Metricas AdaBoost (test) ===')
print(f'Accuracy: {accuracy:.4f}')
print(f'Precision (micro): {precision:.4f}')
print(f'Recall (micro): {recall:.4f}')
print(f'F1 (micro): {f1:.4f}')
print(f'F1 (macro): {f1_macro:.4f}')
print(f'F1 (weighted): {f1_weighted:.4f}')
print('\nClassification report:')
print(classification_report(y_test, y_test_predicho, zero_division=0))
