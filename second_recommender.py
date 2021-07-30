import pandas as pd
import scipy.sparse as sp
from operator import itemgetter
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Second_Recommender:
    def __init__(self,df):
        self.df = pd.read_csv(df)
        
    def count_vectorize(self):
        count = CountVectorizer(stop_words = 'english')
        count_matrix = count.fit_transform(self.df['word_soup'])
        return count_matrix
    
    def cosine_similarities(self,matrix):
        cosine_sim = cosine_similarity(matrix,matrix)
        dataframe = self.df.reset_index()
        index = pd.Series(dataframe.index,index = dataframe['title'])
        return cosine_sim,index

    def get_recommendations(self,title,cosine_sim,indices):
        index = indices[title]
        sim_scores = cosine_sim[index]
        sim_scores = sorted([(idx,val) for idx,val in enumerate(sim_scores)],key = lambda x:x[1],reverse = True)[1:10]
        movie_index = [tupel[0] for tupel in sim_scores]
        return [title for title in self.df['title'].iloc[movie_index]]
    
def second_recommender(title,df = './dataset/second_final_data.csv'):
    recommender = Second_Recommender(df = df)
    matrice = recommender.count_vectorize()
    cosine,indices = recommender.cosine_similarities(matrice)
    recommendations = recommender.get_recommendations(title,cosine,indices)
    return recommendations
        