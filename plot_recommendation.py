import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

class Plot_Recommender:
    def __init__(self,df):
        self.df = pd.read_csv(df)

    def generate_vectors_tfidf(self):
        tfidf = TfidfVectorizer(stop_words='english')
        self.df['plot'] = self.df['plot'].fillna('')
        tfidf_matrix = tfidf.fit_transform(self.df['plot'])
        return tfidf_matrix
    
    def cosine_similarity(self,matrix):
        cosine_sim = linear_kernel(matrix,matrix)
        indices = pd.Series(self.df.index,index = self.df['title']).drop_duplicates()
        return cosine_sim,indices
    
    def get_recommendations(self,title,cosine_sim,indices):
        index = indices[title]
        sim_scores = [(i,val) for i,val in enumerate(cosine_sim[index])]
        sim_scores = sorted(sim_scores, key = lambda x:x[1],reverse = True)[1:9]
        movie_index = [tupel[0] for tupel in sim_scores]
        return self.df['title'].iloc[movie_index]

def plot_recommender(title,df = './dataset/final_data.csv'):
    recommender = Plot_Recommender(df = df)
    matrice = recommender.generate_vectors_tfidf()
    cosine,indices = recommender.cosine_similarity(matrice)
    recommendations = recommender.get_recommendations(title,cosine,indices)
    return recommendations
        
    
        
