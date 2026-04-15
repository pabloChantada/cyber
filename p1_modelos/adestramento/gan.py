import argparse
import csv
import math
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from .RedeGAN import Xerador, Discriminador
from p1_modelos.utilidades import init_dataset, avaliar_discriminador, crear_run_dir, gardar_yaml_args, append_rows_csv

#--
parser = argparse.ArgumentParser(prog='optimizacion bayesiana do adaboost', epilog='-    :)   -')
parser.add_argument('-e',dest='epocas', default=30, type=int)  
parser.add_argument('-p_dropout', default=0.1, type=float)  
parser.add_argument('-z_dim', default=16, type=int)  
parser.add_argument('-b', dest='batch_size', default=256, type=int)  
parser.add_argument('--eval_every', default=10, type=int)
parser.add_argument('-lr', default=1e-4, type=float)  
parser.add_argument('--csv_flush_every', default=5, type=int)
parser.add_argument('--num_workers', default=None, type=int)
args = parser.parse_args()








run_id, run_dir = crear_run_dir(Path('pesos'))
gardar_yaml_args(run_dir / 'args.yaml', vars(args), run_id)

metrics_csv = run_dir / 'metricas.csv'
with metrics_csv.open('w', newline='', encoding='utf-8') as f_csv:
    writer = csv.DictWriter(
        f_csv,
        fieldnames=['epoca', 'val_auc_roc', 'val_accuracy', 'perdida_discriminador', 'perdida_xerador', 'is_best'],
    )
    writer.writeheader()

print(f'[*] Run ID: {run_id}')
print(f'[*] Artefactos en: {run_dir}')

X_train, y_train, y_train_bin, X_val, y_val, y_val_bin, X_test, y_test, y_test_bin = init_dataset(tensor=True)

x_dim = X_train.shape[1]

G = Xerador(args.z_dim, x_dim)
D = Discriminador(x_dim, p_dropout=args.p_dropout,numero_clases=1)

device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
G = G.to(device)
D = D.to(device)

criterion = nn.BCEWithLogitsLoss()
optim_G = torch.optim.Adam(G.parameters(), lr=args.lr, betas=(0.5, 0.999))
optim_D = torch.optim.Adam(D.parameters(), lr=args.lr, betas=(0.5, 0.999))


loader = DataLoader(TensorDataset(X_train, y_train_bin), batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)
val_loader = DataLoader(TensorDataset(X_val, y_val_bin), batch_size=args.batch_size, shuffle=False, num_workers=args.num_workers)

best_val_auc = float('-inf')
csv_buffer = []
inicio_bloque = time.time()

for epoca in range(args.epocas):
    for (ejemplos, etiquetas) in loader:

        ejemplos = ejemplos.to(device)
        etiquetas = etiquetas.to(device)

        unos = torch.ones_like(etiquetas)
        ceros = torch.zeros_like(etiquetas)

        #-- discriminador
        z = torch.randn(ejemplos.size(0), args.z_dim, device=device)
        fake = G(z)

        D_ejemplos = D(ejemplos)
        D_fake = D(fake.detach())

        perdida_ejemplos = criterion(D_ejemplos, etiquetas)
        perdida_fake = criterion(D_fake, ceros)

        perdida_discriminador = perdida_ejemplos + perdida_fake

        optim_D.zero_grad()
        perdida_discriminador.backward()
        optim_D.step()

        #-- xerador
        z = torch.randn(ejemplos.size(0), args.z_dim, device=device)
        fake = G(z)

        perdida_generador = criterion(D(fake), unos)

        optim_G.zero_grad()
        perdida_generador.backward()
        optim_G.step()


    if (epoca + 1) % args.eval_every == 0:
        tempo_bloque_seg = int(time.time() - inicio_bloque)
        minutos_bloque, segundos_bloque = divmod(tempo_bloque_seg, 60)
        auc_roc_val, accuracy_val = avaliar_discriminador(D, val_loader, device)
        is_best = 0
        if not math.isnan(auc_roc_val) and auc_roc_val > best_val_auc:
            best_val_auc = auc_roc_val
            is_best = 1
            torch.save(D.state_dict(), run_dir / 'D_best.pth')
            torch.save(G.state_dict(), run_dir / 'G_best.pth')

        csv_buffer.append(
            {
                'epoca': epoca + 1,
                'val_auc_roc': float(auc_roc_val),
                'val_accuracy': float(accuracy_val),
                'perdida_discriminador': float(perdida_discriminador.item()),
                'perdida_xerador': float(perdida_generador.item()),
                'is_best': is_best,
            }
        )
        if len(csv_buffer) >= args.csv_flush_every:
            append_rows_csv(metrics_csv, csv_buffer)
            csv_buffer.clear()

        print(
            f"Epoca {epoca + 1}: ( {minutos_bloque:02d}m:{segundos_bloque:02d}s )"
            f"Val AUC-ROC={auc_roc_val:.4f}, Val Accuracy={accuracy_val:.4f}, "
            f"Pérdida Discriminador={perdida_discriminador.item():.4f}, Pérdida Xerador={perdida_generador.item():.4f}"
        )
        inicio_bloque = time.time()

if csv_buffer:
    append_rows_csv(metrics_csv, csv_buffer)
