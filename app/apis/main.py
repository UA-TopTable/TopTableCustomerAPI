from flask import Flask, render_template, request

app = Flask(__name__, template_folder='../templates', static_folder='../static')

class Restaurant:
    def __init__(self, id, name, address, description, photo):
        self.id = id
        self.name = name
        self.address = address
        self.description = description
        self.photo = photo


# Dummy restaurants data, will be replaced by database data
restaurants = []
restaurants.append(Restaurant(0, 'Restaurant 1', 'Address 1', 'Example description 1', 'img/restaurant1.png'))
restaurants.append(Restaurant(1, 'Restaurant 2', 'Address 2', 'Example description 2', 'img/restaurant2.jpg'))
restaurants.append(Restaurant(2, 'Restaurant 3', 'Address 3', 'Example description 3', 'img/restaurant3.jpg'))
restaurants.append(Restaurant(3, 'Restaurant 4', 'Address 4', 'Example description 4', 'img/restaurant4.jpg'))
restaurants.append(Restaurant(4, 'Restaurant 5', 'Address 5', 'Example description 5', 'img/restaurant5.jpg'))


@app.route('/')
def home():

    return render_template('index.html', restaurants=restaurants)

@app.route('/book_restaurant/')
def restaurant():
    id = request.args.get('id')
    if id is None:
        return 'No restaurant id provided'
    

    restaurant = restaurants[int(id)]
    return render_template('book_restaurant.html', restaurant=restaurant)

if __name__ == '__main__':
    app.run(debug=True)