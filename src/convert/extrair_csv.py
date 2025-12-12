import pandas as pd
import numpy as np
import os
from datetime import datetime

arquivo = "tickets_aberto.csv"
base = pd.read_csv(os.path.join("src", "convert", "csv", arquivo), sep=",", encoding="utf-8")  


# extrarir todos os apenas os ID da coluna "ID",s e armazenar em uma lista
lista_ids = base["ID"].tolist()
print(lista_ids)