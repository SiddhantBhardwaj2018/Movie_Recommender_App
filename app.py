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
        #response = requests.get("http://api.themoviedb.org/3/search/person?query={name}&api_key=6dbe3c2b48ba7012390499fe4e59c6a4")
        #response = response.json()
        response_1 = requests.get("https://api.themoviedb.org/3/search/movie?api_key=6dbe3c2b48ba7012390499fe4e59c6a4&query=" + name)
        response_1 = response_1.json()
        if len(response_1['results']) > 0:
            try:
                res = second_recommender.second_recommender(response_1['results'][0]['original_title'])
                if res == "No Movies":
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
                actor = requests.get(f"http://api.themoviedb.org/3/search/person?query={name}&api_key=6dbe3c2b48ba7012390499fe4e59c6a4")
                actor = actor.json()
                if len(actor['results']) > 0:
                    try:
                        return actor_recommender(name)
                    except:
                        return render_template("500.html")
                else:
                    return render_template("500.html")
        else:
            actor = requests.get(f"http://api.themoviedb.org/3/search/person?query={name}&api_key=6dbe3c2b48ba7012390499fe4e59c6a4")
            actor = actor.json()
            if len(actor['results']) > 0:
                try:
                    return actor_recommender(name)
                except:
                    return render_template("500.html")
            else:
                return render_template("index.html",users = "None1",first = "None",upcoming = "None")
    else:
        response = requests.get("https://api.themoviedb.org/3/movie/upcoming?api_key=6dbe3c2b48ba7012390499fe4e59c6a4&language=en-US&page=1")
        response = response.json()
        response = response['results'][:9]
        for i in response:
            i['genre_ids'] = list(set(i['genre_ids']))
            i['genre_ids'] = [genre_d[i['genre_ids'][j]] for j in range(len(i['genre_ids'])) ]
            i['release_date'] = i['release_date'][:4]
        return render_template("index.html",users = "None",first = "None", upcoming = response)
    
def actor_recommender(name):
    google_search = requests.get(f"https://serpapi.com/search.json?engine=google&q={name}&api_key=27957cb0d044df28115a38f0dc6ffc6e2702d76f01f377832762c2ed9774be18")
    google_search = google_search.json()
    option_one = "movies"
    option_two = "movies_and_tv_shows"
    if option_one in google_search['knowledge_graph']:
        movies = [i['name'] for i in google_search['knowledge_graph'][option_one]]
    elif option_two in google_search['knowledge_graph']:
        movies = [i['name'] for i in google_search['knowledge_graph'][option_two]]
    co_actors = [i['name'] for i in google_search['knowledge_graph']['people_also_search_for']]
    for co_actor in co_actors:
        search = requests.get(f"https://serpapi.com/search.json?engine=google&q={co_actor}&api_key=27957cb0d044df28115a38f0dc6ffc6e2702d76f01f377832762c2ed9774be18")
        search = search.json()
        if 'type' in search['knowledge_graph']:
            if 'actor' in search['knowledge_graph']['type'].lower() or 'actress' in search['knowledge_graph']['type'].lower():
                if option_one in search['knowledge_graph']:
                    movies += [j['name'] for j in search['knowledge_graph'][option_one]]
                elif option_two in search['knowledge_graph']:
                    movies += [j['name'] for j in search['knowledge_graph'][option_two]]
        else:
            continue
    arr = []
    for i in movies:
        res_2 = requests.get(f"https://api.themoviedb.org/3/search/movie?api_key=6dbe3c2b48ba7012390499fe4e59c6a4&query={i}")
        res_2 = res_2.json()
        if len(res_2['results']) > 0:
            arr.append(res_2['results'][0])
    print('Gotcha 2')
    for i in arr:
        i['genre_ids'] = list(set(i['genre_ids']))
        i['genre_ids'] = [genre_d[i['genre_ids'][j]] for j in range(len(i['genre_ids'])) ]
        i['release_date'] = i['release_date'][:4]
    movie_name = arr[0]
    arr = arr[1:-1]
    print('Gotcha')
    return render_template("index.html",users = arr,first = movie_name,upcoming = "None")
   

@app.route('/movie',methods=['GET'])
def recommend_movies():
    res = recommendation.results(request.args.get('title'))
    return jsonify(res)

@app.errorhandler(500)
def page_not_found(e):
    render_template("500.html")

if __name__ == "__main__":
    app.run(port = 5000,debug = True)