from workerA import add_nums, get_accuracy, get_predictions

from flask import (
   Flask,
   request,
   jsonify,
   Markup,
   render_template 
)

#app = Flask(__name__, template_folder='./templates',static_folder='./static')
app = Flask(__name__)

@app.route("/")
def index():
    return '<h1>Welcome to the Machine Learning Course11.</h1>'

@app.route("/accuracy", methods=['POST', 'GET'])
def accuracy():
    if request.method == 'POST':
        r = get_accuracy()
        #a = r.get()
        return '<h1>The accuracy is {}</h1>'.format(r)

    return '''<form method="POST">
    <input type="submit">
    </form>'''

@app.route("/predictions", methods=['POST', 'GET'])
def predictions():
    if request.method == 'POST':
        #results = get_predictions()
        #predictions = results.get()

        top5, result1 = get_accuracy()
        #accuracy = results.get()
        print(top5)
        #final_results = predictions

        return render_template('result.html', accuracy=result1 ,final_results=top5) 

    return '''<form method="POST">
    <input type="submit">
    </form>'''

if __name__ == '__main__':
    app.run(host = '0.0.0.0',port=5100,debug=True)


