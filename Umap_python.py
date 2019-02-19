import umap
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import fetch_mldata
import plotly.plotly as py

hdd = pd.read_csv("High Dimensionl Data.csv")
hdd_new = hdd.drop(['Desc_00001'], axis=1)
hdd_str_labels = hdd_labels = hdd['Desc_00001']
hdd_labels = hdd['Desc_00001'].str[-2:].astype(int)

embedding = umap.UMAP().fit_transform(hdd_new)

clusterable_embedding = umap.UMAP(
    n_neighbors=30,
    min_dist=0.0,
    n_components=2,
    random_state=42,
).fit_transform(hdd_new)

clusterable_embedding_df= pd.DataFrame(clusterable_embedding, index=hdd_str_labels)
clusterable_embedding_df.to_csv('clusterable_embedding_df.csv')

plt.scatter(clusterable_embedding[:, 0], clusterable_embedding[:, 1],
            c=hdd_labels, cmap='RdYlGn');
plt.colorbar()
plt.show()


p = plot(
  [
    Scatter3d(x=clusterable_embedding[:, 0], y=clusterable_embedding[:, 1], 
    z=skills_df[2], text= skills_df['designation'], mode='markers', marker=Marker(color=skills_df['cluster_number'], size=3, opacity=0.5, colorscale='Viridis'))
  ],
  output_type='div'
#   filename='/dbfs/FileStore/tables/lnkdn_jobroles_viridis.html' turn it on to save the file
)
            
            
            
