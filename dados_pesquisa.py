import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


# Crie uma conexão com o banco de dados
engine = create_engine('sqlite:///users.db')
with engine.connect() as connection:
    result = connection.execute("SELECT * FROM df")
    result2 = connection.execute("SELECT * FROM df_original")
    # Carregue os dados do resultado em um DataFrame do Pandas
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
    df_original = pd.DataFrame(result2.fetchall(), columns=result2.keys())


# Selecionar as variáveis numéricas que serão utilizadas na clusterização
vars_num = ['Sexo_F', 'Sexo_M','nivel_escolaridade_sem_escolaridade','nivel_escolaridade_fundamental_incompleto',
'nivel_escolaridade_fundamental_completo','nivel_escolaridade_médio_incompleto',
'nivel_escolaridade_médio_completo','nivel_escolaridade_superior_incompleto','nivel_escolaridade_superior_completo',
'redes_sociais_whatsapp','redes_sociais_facebook','redes_sociais_instagram','horario_manha','horario_tarde',
'horario_noite', 'idade', 'renda']

# Criar uma cópia do dataframe com apenas as variáveis selecionadas
df_num = df[vars_num].copy()

# Padronizar as variáveis numéricas
scaler = StandardScaler()
df_num_scaled = scaler.fit_transform(df_num)

# Definir o modelo DBSCAN
dbscan = DBSCAN(eps=2.5, min_samples=3)

# Treinar o modelo DBSCAN com o conjunto de dados padronizado
dbscan.fit(df_num_scaled)

# Adicionar a coluna de rótulos de cluster ao dataframe original
df['cluster'] = dbscan.labels_


