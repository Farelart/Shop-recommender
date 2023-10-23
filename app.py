import pickle
import numpy as np
import pandas as pd
from flask import request
from flask import jsonify
from flask import Flask
from flask import render_template, url_for

app = Flask(__name__, static_url_path='/static', static_folder='static')

model = pickle.load(open('model.pkl','rb'))
books_name = pickle.load(open('books_name.pkl','rb'))
final_rating = pickle.load(open('final_rating.pkl','rb'))
book_pivot = pickle.load(open('book_pivot.pkl', 'rb'))

def fetch_poster(suggestion):
    book_name = []
    ids_index = []
    poster_url = []
    
    for book_id in suggestion:
        book_name.append(book_pivot.index[book_id])
        
    for name in book_name[0]:
        ids = np.where(final_rating['title'] == name)[0][0]
        ids_index.append(ids)
    
    for idx in ids_index:
        url = final_rating.iloc[idx]['img-url']
        poster_url.append(url)
        
    return poster_url

def recommend_books(book_name):
    books_list =  []
    book_id = np.where(book_pivot.index == book_name)[0][0]
    distance, suggestion = model.kneighbors(book_pivot.iloc[book_id,:].values.reshape(1,-1), n_neighbors=8)
    
    poster_url = fetch_poster(suggestion)
    
    for i in range(len(suggestion)):
        books = book_pivot.index[suggestion[i]]
        for j in books:
            books_list.append(j)
    return books_list , poster_url 


@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/books")
def books():
    # Load the dataset from the CSV file
    books_data = pd.read_csv('books_final.csv')  # Adjust the path to your actual file location

    # Pagination variables
    page = request.args.get('page', 1, type=int)  # Get the current page number from the query parameters
    per_page = 100  # Number of books to display per page
    total_books = len(books_data)  # Total number of books in the dataset

    # Calculate the start and end indices for the current page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    # Retrieve the books for the current page
    books_subset = books_data[start_idx:end_idx]

    # Convert the subset of books to a list of dictionaries for easier access in the template
    books = books_subset.to_dict(orient='records')

    # Render the books.html template, passing the list of books and pagination information to the template context
    return render_template('books.html', books=books, page=page, per_page=per_page, total_books=total_books)

@app.route('/book/<book_id>')
def book_details(book_id):
    # Retrieve the book details based on the book_id
    #book = get_book_details(book_id)# Replace this with your logic to retrieve book details
    books_data = pd.read_csv('books_final.csv')
    book = books_data[books_data['title'] == book_id].to_dict(orient='records')[0]

    # Render the details.html template, passing the book details to the template context
    return render_template('detailsB.html', book=book)

"""@app.route("/products", methods=["POST", "GET"])
def products():
    if request.method == "POST":
        message = request.get_json(force=True)
        name = message['name']

        prediction_book, url_book = recommend_books(name)

        response = {
            'prediction': {
                'book': prediction_book,
                'url': url_book[0]
            }
        }
        return jsonify(response)
    else:
        # Render the products.html template
        return render_template('detailsB.html')"""

@app.route('/cart', methods=['POST'])
def cart():
    if request.method == 'POST':
        book_name = request.form['name']
        prediction_book, url_book = recommend_books(book_name)
        recommendations = zip(prediction_book, url_book)
        return render_template('recommendationsB.html', recommendations=recommendations)


if __name__ == '__main__':
    app.run(debug=True)