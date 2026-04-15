import pandas as pd

def init_dataset(dataset='dataset', tensor=False):
    print(f'[*] Usando os arquivos .parquet do directorio {dataset}') 

    train = pd.read_parquet(dataset + "/train.parquet")
    val = pd.read_parquet(dataset + "/val.parquet")
    test = pd.read_parquet(dataset + "/test.parquet")
    
    X_train = train.drop(columns=['Label'])
    y_train = train['Label']
    X_val = val.drop(columns=['Label'])
    y_val = val['Label']
    X_test = test.drop(columns=['Label'])
    y_test = test['Label']
    
    y_train_bin = (y_train != 'BENIGN').astype(int)
    y_val_bin = (y_val != 'BENIGN').astype(int)
    y_test_bin = (y_test != 'BENIGN').astype(int)

    if tensor:
        import torch

        def _to_tensor(data, reshape=None):
            tensor = torch.as_tensor(data.to_numpy(dtype='float32'))
            return tensor.view(reshape) if reshape else tensor
    
        X_train = _to_tensor(X_train)
        X_val = _to_tensor(X_val)
        X_test = _to_tensor(X_test)

        y_train_bin = _to_tensor(y_train_bin, reshape=(-1, 1))
        y_val_bin = _to_tensor(y_val_bin, reshape=(-1, 1))
        y_test_bin = _to_tensor(y_test_bin, reshape=(-1, 1))

    return X_train, y_train, y_train_bin, X_val, y_val, y_val_bin, X_test, y_test, y_test_bin
