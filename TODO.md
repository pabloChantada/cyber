Poner fina la memoria, comentar más extensamente cada paso en galego.

Cosas como.
    Mencionar que la distribución de los datos no sigue una normal para muchas columnas sino una power distribution de esas.
    Hablar acerca del balanceo de clases.
    Reejecutar los UMAPS y el PCA, mencionar que efectivamente el UMAP no cambia tras hacer el PCA, lo que significa que el PCA cunde.
    También falta dropear específicamente todas las columnas que no interesen al pCA (nos quedamos con 61 creo).
    Quitar el código que sobra y las barbaridades varias que pusimos.
    No olvidar las ganas de pasarlo bien.
    Mencionar lo de las columnas duplicadas y citar alguno de los papers acerca del dataset para que se vea que no lo inventamos.
    

---

# MODELOS
b45e56  -> modelo gan con: python -m p1_modelos.adestramento.gan -e 1000 -p_dropout 0.04 -z_dim 6 -b 512 -lr 0.0001 --num_workers 4 --eval_every 2

Epoca 428: ( 00m:15s )Val AUC-ROC=0.9430, Val Accuracy=0.9198, Pérdida Discriminador=0.2353, Pérdida Xerador=5.2398
Epoca 430: ( 00m:15s )Val AUC-ROC=0.9481, Val Accuracy=0.9294, Pérdida Discriminador=0.2208, Pérdida Xerador=5.3828
Epoca 432: ( 00m:15s )Val AUC-ROC=0.9425, Val Accuracy=0.9234, Pérdida Discriminador=0.2254, Pérdida Xerador=8.5753
Epoca 434: ( 00m:15s )Val AUC-ROC=0.9401, Val Accuracy=0.9203, Pérdida Discriminador=0.2431, Pérdida Xerador=5.0903
Epoca 436: ( 00m:15s )Val AUC-ROC=0.9392, Val Accuracy=0.9073, Pérdida Discriminador=0.2921, Pérdida Xerador=5.0455
Epoca 438: ( 00m:15s )Val AUC-ROC=0.9428, Val Accuracy=0.9269, Pérdida Discriminador=0.2315, Pérdida Xerador=6.8590
Epoca 440: ( 00m:15s )Val AUC-ROC=0.9495, Val Accuracy=0.9261, Pérdida Discriminador=0.2263, Pérdida Xerador=5.5899
Epoca 442: ( 00m:14s )Val AUC-ROC=0.9503, Val Accuracy=0.9295, Pérdida Discriminador=0.2566, Pérdida Xerador=4.3378
Epoca 444: ( 00m:14s )Val AUC-ROC=0.9448, Val Accuracy=0.9255, Pérdida Discriminador=0.2264, Pérdida Xerador=8.9615