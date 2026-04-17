from sklearn.metrics import roc_auc_score
import torch

def avaliar_discriminador(discriminador, data_loader, device, multiclase=False, benign_idx=None):
    estaba_entrenando = discriminador.training
    discriminador.eval()

    todas_probs = []
    todas_etiquetas = []

    with torch.no_grad():
        for exemplos_val, etiquetas_val in data_loader:
            exemplos_val = exemplos_val.to(device)
            etiquetas_val = etiquetas_val.to(device)

            if multiclase:
                logits = discriminador(exemplos_val)
                probs = torch.softmax(logits, dim=1)
            else:
                probs = torch.sigmoid(discriminador(exemplos_val))
            todas_probs.append(probs.cpu())
            todas_etiquetas.append(etiquetas_val.cpu())

    probs = torch.cat(todas_probs, dim=0)
    etiquetas = torch.cat(todas_etiquetas, dim=0)

    if multiclase:
        if benign_idx is None:
            raise ValueError("benign_idx é obrigatorio cando multiclase=True")

        predicions = torch.argmax(probs, dim=1)
        accuracy = (predicions == etiquetas).float().mean().item()

        etiquetas_ataque = (etiquetas != benign_idx).int()
        probs_ataque = 1.0 - probs[:, benign_idx]
        try:
            auc_roc = roc_auc_score(etiquetas_ataque.numpy().ravel(), probs_ataque.numpy().ravel())
        except ValueError:
            auc_roc = float("nan")
    else:
        predicions = (probs >= 0.5).float()
        accuracy = (predicions == etiquetas).float().mean().item()

        try:
            auc_roc = roc_auc_score(etiquetas.numpy().ravel(), probs.numpy().ravel())
        except ValueError:
            auc_roc = float("nan")

    if estaba_entrenando:
        discriminador.train()

    return auc_roc, accuracy
