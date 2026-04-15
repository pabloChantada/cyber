import argparse
import math
from pathlib import Path

import pandas as pd
import torch

from p1_modelos.adestramento.RedeGAN import Xerador
from p1_modelos.utilidades import init_dataset

# --
parser = argparse.ArgumentParser(
    prog='xerar_dataset',
    description='Enriquecer o conxunto de adestramento con mostras sintéticas do xerador GAN',
    epilog='-    :)   -',
)
parser.add_argument('-id', dest='run_id', required=True, type=str,
                    help='Run ID do experimento GAN (ex: 9fc0df)')
parser.add_argument('-p', dest='porcentaxe', required=True, type=float,
                    help='Proporción de mostras reais no train resultante (0=todo sintético, 1=todo real)')
parser.add_argument('--pesos_dir', default='pesos', type=str,
                    help='Directorio raíz onde están os runs gardados (por defecto: pesos)')
parser.add_argument('--dataset', default='dataset', type=str,
                    help='Directorio orixinal do dataset (por defecto: dataset)')
parser.add_argument('--z_dim', default=16, type=int,
                    help='Dimensión do espazo latente do xerador (debe coincidir co adestramento)')
parser.add_argument('--batch_size', default=4096, type=int,
                    help='Tamaño de lote para a xeración (só afecta á velocidade)')
args = parser.parse_args()

if not (0.0 <= args.porcentaxe <= 1.0):
    parser.error(f'-p debe estar en [0, 1], pero recibiuse {args.porcentaxe}')

# -- localizar o run e cargar o xerador
run_dir = Path(args.pesos_dir) / args.run_id
G_path = run_dir / 'G_best.pth'

if not run_dir.exists():
    raise FileNotFoundError(f'Non se atopou o directorio do run: {run_dir}')
if not G_path.exists():
    raise FileNotFoundError(f'Non se atopou G_best.pth en: {run_dir}')

device = torch.device(
    'cuda' if torch.cuda.is_available()
    else 'mps' if torch.backends.mps.is_available()
    else 'cpu'
)
print(f'[*] Usando dispositivo: {device}')

# -- cargar dataset orixinal (só para obter X_train e o esquema de columnas)
X_train, y_train, y_train_bin, X_val, y_val, y_val_bin, X_test, y_test, y_test_bin = init_dataset(
    dataset=args.dataset, tensor=False
)

x_dim = X_train.shape[1]
n_real = len(X_train)

# -- instanciar e cargar o xerador
G = Xerador(args.z_dim, x_dim).to(device)
G.load_state_dict(torch.load(G_path, map_location=device))
G.eval()
print(f'[*] Xerador cargado desde: {G_path}')

# -- calcular cantas mostras sintéticas necesitamos
# porcentaxe = n_real_final / (n_real_final + n_sintetico)
# Se p=1 -> todo real, 0 sintéticas
# Se p=0 -> todo sintético, eliminamos as reais -> n_sintetico = n_real (mantemos o tamaño)
# En xeral: n_sintetico = n_real * (1 - p) / p  [cando p > 0]
#           e gardamos todas as reais se p > 0, ou ningunha se p = 0

if args.porcentaxe == 0.0:
    n_sintetico = n_real      # substituímos todo por sintético
    usar_reais = False
elif args.porcentaxe == 1.0:
    n_sintetico = 0
    usar_reais = True
else:
    # Mantemos todos os reais e engadimos os sintéticos necesarios
    n_sintetico = int(math.ceil(n_real * (1.0 - args.porcentaxe) / args.porcentaxe))
    usar_reais = True

print(f'[*] Mostras reais no train:     {n_real if usar_reais else 0}')
print(f'[*] Mostras sintéticas a xerar: {n_sintetico}')

# -- xerar mostras sintéticas en lotes
col_names = X_train.columns.tolist()
sintetico_chunks = []

remaining = n_sintetico
with torch.no_grad():
    while remaining > 0:
        batch = min(args.batch_size, remaining)
        z = torch.randn(batch, args.z_dim, device=device)
        fake = G(z).cpu().numpy()
        sintetico_chunks.append(pd.DataFrame(fake, columns=col_names))
        remaining -= batch

# -- construír o train final
parts = []

if usar_reais:
    df_real = X_train.copy()
    df_real['Label'] = y_train.values
    parts.append(df_real)

if n_sintetico > 0:
    df_sintetico = pd.concat(sintetico_chunks, ignore_index=True)
    # Axustar os dtypes das columnas sintéticas para que coincidan cos do train real
    # (as columnas booleanas / int do orixinal non deben quedar como float32)
    for col in col_names:
        orig_dtype = X_train[col].dtype
        try:
            df_sintetico[col] = df_sintetico[col].astype(orig_dtype)
        except (ValueError, TypeError):
            pass  # se non se pode converter, deixámolo como está
    # As mostras sintéticas son de clase MALICIOUS (1); etiquetámolas como tal
    df_sintetico['Label'] = 'SINTETICO'
    parts.append(df_sintetico)

df_train_final = pd.concat(parts, ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

# -- reconstruír val e test co Label orixinal
df_val = X_val.copy()
df_val['Label'] = y_val.values

df_test = X_test.copy()
df_test['Label'] = y_test.values

# -- gardar
out_dir = Path(f'dataset_{args.run_id}')
out_dir.mkdir(parents=True, exist_ok=True)

df_train_final.to_parquet(out_dir / 'train.parquet', index=False)
df_val.to_parquet(out_dir / 'val.parquet', index=False)
df_test.to_parquet(out_dir / 'test.parquet', index=False)

print(f'[*] Dataset gardado en: {out_dir}')
print(f'    train.parquet : {len(df_train_final):>8,} filas')
print(f'    val.parquet   : {len(df_val):>8,} filas')
print(f'    test.parquet  : {len(df_test):>8,} filas')
