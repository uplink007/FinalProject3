from flask import Flask, request #import main Flask class and request object

app = Flask(__name__) #create the Flask app


@app.route('/query-example')
def query_example():
    params = [""+k+"="+v for k,v in request.args.items()]
    return 'params '+params.__str__()


@app.route('/form-example', methods=['GET', 'POST']) #allow both GET and POST requests
def form_example():
    if request.method == 'POST': #this block is only entered when the form is submitted
        return request.form.get('language')

    return '''<form method="POST">
                  sentence:<br/> <textarea type="text" name="language" rows="10" cols="100"></textarea><br/>
                  <input type="submit" value="Submit"><br>
              </form>'''


@app.route('/json-example')
def json_example():
    return 'Todo...'


if __name__ == '__main__':
    app.run(debug=True, port=5000)