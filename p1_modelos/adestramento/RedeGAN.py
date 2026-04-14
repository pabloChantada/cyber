import torch.nn as nn

class Xerador(nn.Module):
    def __init__(self, z_dim, x_dim):
        super().__init__()
        self.rede = nn.Sequential(
            nn.Linear(z_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, x_dim)
        )

    def forward(self, z):
        return self.rede(z)

class Discriminador(nn.Module):
    def __init__(self, x_dim, p_dropout=0.1, numero_clases=2):
        super().__init__()

        self.rede = nn.Sequential(
            nn.Linear(x_dim, 256),
            nn.ReLU(),
            nn.Dropout(p_dropout),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, numero_clases)
        )

    def forward(self, x):
        return self.rede(x)
