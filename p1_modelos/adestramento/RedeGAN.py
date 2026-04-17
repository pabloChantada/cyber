import torch.nn as nn

class Xerador(nn.Module):
    def __init__(self, z_dim, x_dim):
        super().__init__()
        self.rede = nn.Sequential(
            nn.Linear(z_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, x_dim)
        )

    def forward(self, z):
        return self.rede(z)

class Discriminador(nn.Module):
    def __init__(self, x_dim, p_dropout=0.1, numero_clases=2):
        super().__init__()

        self.rede = nn.Sequential(
            nn.Linear(x_dim, 64),
            nn.ReLU(),
            nn.Dropout(p_dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, numero_clases)
        )

    def forward(self, x):
        return self.rede(x)
