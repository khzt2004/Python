# http://www.awesomestats.in/python-cluster-validation/

import umap
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import fetch_mldata
import plotly.plotly as py
from sklearn.cluster import KMeans
import sklearn.cluster as cluster
from sklearn.metrics import silhouette_score
import numpy as np
from scipy.spatial.distance import cdist,pdist
from sklearn.metrics import adjusted_rand_score, adjusted_mutual_info_score
from scipy.cluster.vq import kmeans
from matplotlib import cm

hdd = pd.read_csv("C:\\Users\\User\\Documents\\High Dimensionl Data.csv")
hdd_new = hdd.drop(['Desc_00001'], axis=1)
hdd_str_labels = hdd_labels = hdd['Desc_00001']
hdd_labels = hdd['Desc_00001'].str[-2:].astype(int)

embedding = umap.UMAP().fit_transform(hdd_new)


# use a scree plot to determine clusters

standard_embedding = umap.UMAP(random_state=42).fit_transform(hdd_new)

# Scree plots
def scree_plot(x):
   K = range(1,21)
   KM = [KMeans(n_clusters=k).fit(x) for k in K]
   centroids = [k.cluster_centers_ for k in KM]
   D_k = [cdist(x, cent, 'euclidean') for cent in centroids]
   cIdx = [np.argmin(D,axis=1) for D in D_k]
   dist = [np.min(D,axis=1) for D in D_k]
   avgWithinSS = [sum(d)/x.shape[0] for d in dist]
   
   wcss = [sum(d**2) for d in dist]
   tss = sum(pdist(x)**2)/x.shape[0]
   bss = tss-wcss
   return K, avgWithinSS, tss, bss;

K, avgWithinSS, tss, bss = scree_plot(standard_embedding)

# elbow curve
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(K, avgWithinSS, 'b*-')
plt.grid(True)
plt.xlabel('Number of clusters')
plt.ylabel('Average within-cluster sum of squares')
plt.title('Elbow for KMeans clustering')
plt.show()

plt.clf()
plt.cla()
plt.close()

# percentage of variance explained
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(K, bss/tss*100, 'b*-')
plt.grid(True)
plt.xlabel('Number of clusters')
plt.ylabel('Percentage of variance explained')
plt.title('Elbow for KMeans clustering')
plt.show()

plt.clf()
plt.cla()
plt.close()


# perform K means clustering 
kmeans = KMeans(n_clusters=3)
kmeans.fit(standard_embedding)
y_kmeans = kmeans.predict(standard_embedding)

plt.scatter(standard_embedding[:, 0], standard_embedding[:, 1], 
c=y_kmeans, s=30, cmap='Spectral');
plt.show()

plt.clf()
plt.cla()
plt.close()


centers = kmeans.cluster_centers_
plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5);
plt.show()

plt.clf()
plt.cla()
plt.close()

# Map clusters back to standard embedding

hdd['cluster'] = y_kmeans

# cluster aggregation and exploration
hdd_cluster_aggregate = hdd.groupby('cluster')['Desc_00002', 
               'Desc_00003',
               'Desc_00013',
               'Prop_001'].mean()


# use clusterable embeddings

clusterable_embedding = umap.UMAP(
    n_neighbors=30,
    min_dist=0.0,
    n_components=2,
    random_state=42,
).fit_transform(hdd_new)


# plot dimensionality reduction of clusterable embeddings
clusterable_embedding_df= pd.DataFrame(clusterable_embedding, index=hdd_str_labels)
clusterable_embedding_df.to_csv('clusterable_embedding_df.csv')

plt.scatter(clusterable_embedding[:, 0], clusterable_embedding[:, 1],
            c=hdd_labels, cmap='RdYlGn');
plt.colorbar()
plt.show()


