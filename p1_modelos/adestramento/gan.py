import argparse

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from .RedeGAN import Xerador, Discriminador
from p1_modelos.utilidades.init_dataset import init_dataset

#--
parser = argparse.ArgumentParser(prog='optimizacion bayesiana do adaboost', epilog='-    :)   -')
parser.add_argument('-e',dest='epocas', default=30, type=int)  
parser.add_argument('-p_dropout', default=0.1, type=float)  
parser.add_argument('-z_dim', default=16, type=int)  
parser.add_argument('-b', dest='batch_size', default=256, type=int)  
args = parser.parse_args()

X_train, y_train, y_train_bin, X_val, y_val, y_val_bin, X_test, y_test, y_test_bin = init_dataset(tensor=True)

x_dim = X_train.shape[1]

G = Xerador(args.z_dim, x_dim)
D = Discriminador(x_dim, p_dropout=args.p_dropout,numero_clases=1)

device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
G = G.to(device)
D = D.to(device)

criterion = nn.BCEWithLogitsLoss()
optim_G = torch.optim.Adam(G.parameters(), lr=1e-4, betas=(0.5, 0.999))
optim_D = torch.optim.Adam(D.parameters(), lr=1e-4, betas=(0.5, 0.999))


loader = DataLoader(TensorDataset(X_train, y_train_bin), batch_size=args.batch_size, shuffle=True)


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

    print(f"Epoca {epoca}: Pérdida Discriminador={perdida_discriminador.item():.4f}, Pérdida Xerador={perdida_generador.item():.4f}")
