import hashlib
import time
import pickle
from pathlib import Path
import json

def gardar_experimento_adaboost(parametros, historial, solucion):

    execucion_id = hashlib.sha1(str(time.time_ns()).encode('utf-8')).hexdigest()[:6]
    
    p = Path(f'pesos/{execucion_id}')
    p.mkdir(parents=True, exist_ok=True)
    
    with open(p / 'adaboost.pickle', 'wb') as f:
        pickle.dump(parametros, f, pickle.HIGHEST_PROTOCOL)
        print(f'[*] Jardados os millores parámetros do adaboost en pesos/{execucion_id}/adaboost.pickle')
    
    with open(p / 'historial.json', 'w', encoding='utf-8') as f:
        json.dump(
            historial,
            f,
            ensure_ascii=False,
            indent=2,
            default=lambda obj: obj.item() if hasattr(obj, 'item') else str(obj),
        )
        print(f'[*] Jardado o historial de búsqueda de parametros do adaboost en pesos/{execucion_id}/historial.json')
    
    with open(p / 'solucion.yaml', 'w', encoding='utf-8') as f:
        f.write('n_estimators: ' + str(solucion['n_estimators']) + '\n')
        f.write('learning_rate: ' + str(solucion['learning_rate']) + '\n')
        print(f'[*] Jardada a mellor solución en pesos/{execucion_id}/solucion.yaml')
