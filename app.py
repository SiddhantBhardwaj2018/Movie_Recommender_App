from os import abort
from flask import Flask,request,jsonify
from flask.templating import render_template
from flask_cors import CORS
import urllib
import requests
import json

from werkzeug.wrappers import response
import recommendation
import plot_recommendation
import second_recommender

app = Flask(__name__)
CORS(app)

global genre_d 
genre_d = {28: 'Action', 12 : 'Adventure', 16: 'Animation', 35: 'Comedy', 80: 'Crime', 99: 'Documentary',18: 'Drama', 10751: 'Family', 
           14: 'Fantasy', 36: 'History', 27: 'Horror', 10402: 'Music', 9648: 'Mystery', 10749: 'Romance', 878: 'Science Fiction', 53: 'Thriller',
           10770: 'TV Movie', 10752: 'War', 37: 'Western'}

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == "POST":
        movie_name = request.form["movie_name"]
        movie = movie_name
        name = movie_name.lstrip().rstrip().split(' ')
        for i,val in enumerate(name):
            name[i] = val[0].upper() + val[1:].lower()
        name = '+'.join(name)
        print(name)
        response = requests.get("http://api.themoviedb.org/3/search/person?query={name}e&api_key=6dbe3c2b48ba7012390499fe4e59c6a4")
        response = response.json()
        if response:
            print(response)
            return render_template("500.html")
        else:
            response_1 = requests.get("https://api.themoviedb.org/3/search/movie?api_key=6dbe3c2b48ba7012390499fe4e59c6a4&query=" + name)
            response_1 = response_1.json()
            if len(response_1['results']) > 0:
                try:
                    res = second_recommender.second_recommender(response_1['results'][0]['original_title'])
                    if res == "Movie not":
                        movie_name = response_1['results'][0]
                        movie_name['release_date'] = movie_name['release_date'][:4]
                        movie_name['genre_ids'] = list(set(movie_name['genre_ids']))
                        movie_name['genre_ids'] = [genre_d[movie_name['genre_ids'][j]] for j in range(len(movie_name['genre_ids'])) ]
                        movie_id = movie_name['id']
                        recommend = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key=6dbe3c2b48ba7012390499fe4e59c6a4&language=en-US&page=1")
                        recommend = recommend.json()
                        arr = recommend['results'][:9]
                        for i in arr:
                            i['genre_ids'] = list(set(i['genre_ids']))
                            i['genre_ids'] = [genre_d[i['genre_ids'][j]] for j in range(len(i['genre_ids'])) ]
                            i['release_date'] = i['release_date'][:4]
                        return render_template("index.html",users = "None",arr = arr,first = movie_name,upcoming = "None")
                    else:
                        response = res
                        arr = []
                        for name in response:
                            request1 = requests.get("https://api.themoviedb.org/3/search/movie?api_key=6dbe3c2b48ba7012390499fe4e59c6a4&query=" + name)
                            request1 = request1.json()
                            arr.append(request1['results'][0])
                        movie_name = response_1['results'][0]
                        movie_name['release_date'] = movie_name['release_date'][:4]
                        movie_name['genre_ids'] = list(set(movie_name['genre_ids']))
                        movie_name['genre_ids'] = [genre_d[movie_name['genre_ids'][j]] for j in range(len(movie_name['genre_ids'])) ]
                        for i in arr:
                            i['genre_ids'] = list(set(i['genre_ids']))
                            i['genre_ids'] = [genre_d[i['genre_ids'][j]] for j in range(len(i['genre_ids'])) ]
                            i['release_date'] = i['release_date'][:4]
                        return render_template("index.html",users = arr,first = movie_name, upcoming = "None")
                except:
                    return render_template("500.html")
            else:
                return render_template("index.html",users = "None1",first = "None",upcoming = "None")
    response = requests.get("https://api.themoviedb.org/3/movie/upcoming?api_key=6dbe3c2b48ba7012390499fe4e59c6a4&language=en-US&page=1")
    response = response.json()
    response = response['results'][:9]
    for i in response:
        i['genre_ids'] = list(set(i['genre_ids']))
        i['genre_ids'] = [genre_d[i['genre_ids'][j]] for j in range(len(i['genre_ids'])) ]
        i['release_date'] = i['release_date'][:4]
    return render_template("index.html",users = "None",first = "None", upcoming = response)

@app.route('/movie',methods=['GET'])
def recommend_movies():
    res = recommendation.results(request.args.get('title'))
    return jsonify(res)

@app.errorhandler(500)
def page_not_found(e):
    render_template("500.html")

if __name__ == "__main__":
    app.run(port = 5000,debug = True)