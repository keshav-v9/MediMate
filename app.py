#📌inspired by https://github.com/Azure-Samples/simple-flask-server-appservice
from flask import Flask, render_template, request, jsonify  
from openai import AzureOpenAI  
import os  
import dotenv  
  
# Load environment variables  
dotenv.load_dotenv()  
AOAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  
AOAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")  
MODEL_NAME = "gpt-35-turbo"  
  
# Set up the client for AI Chat  
client = AzureOpenAI(api_key=AOAI_KEY,azure_endpoint=AOAI_ENDPOINT,api_version="2024-05-01-preview")  
  
SCHEDULE_PROMPT = "You are a helpful schedule creator that creates schedules based on tasks. List out these schedules with bullet points. Make sure to write each task on a new line with the time slot preceeding the task. Makse sure that the schedule reduces stress and overworking. "
THERAPY_PROMPT = "You are a mental health support chatbot that provides support to users. You should provide empathetic responses to users and help them feel better. You should also provide resources to help them get the support they need. "



# Function to get AI response with context  
def get_schedule(question, chat_history):  
    # Create the message history  
    messages = [{"role": "system", "content": SCHEDULE_PROMPT}]  
    messages.extend(chat_history)  
    messages.append({"role": "user", "content": question})  
  
    response = client.chat.completions.create(  
        model=MODEL_NAME,  
        temperature=0.7,  
        n=1,  
        messages=messages,  
    )  
    answer = response.choices[0].message.content  
    return answer  
  

app = Flask(__name__, template_folder='templates', static_folder='static')  
  
# Routes  
@app.get('/')  
def index():  
    # Return a page that links to these three pages /test-ai, /ask, /chat
    return render_template("index.html") 


  
@app.route('/status', methods=['GET'])  
def a_live():  
    return "Alive!"  
  

@app.route('/schedule-message', methods=['POST'])  
def schedule_message():  
    data = request.json  
    question = data['message']  
    chat_history = data.get('context', [])  
    resp = get_schedule(question, chat_history)  
    return jsonify({"resp": resp})  
    #return {"resp": resp}
  
@app.route('/therapy-message', methods=['POST'])  
def therapy_message():  
    data = request.json  
    question = data['message']  
    chat_history = data.get('context', [])  
    resp = get_support(question, chat_history)  
    return jsonify({"resp": resp})  
    #return {"resp": resp}


@app.route('/schedule', methods=['GET', 'POST'])  
def chat():  
    if request.method == 'POST':  
        question = request.form.get("question")  
        chat_history = request.form.get("chat_history", [])  
        return get_schedule(question, chat_history)  
    else:  
        return render_template("schedule.html")  


def get_support(thoughts, chat_history):  
    # Create the message history  
    messages = [{"role": "system", "content": THERAPY_PROMPT }]  
    messages.extend(chat_history)  
    messages.append({"role": "user", "content": thoughts })  
  
    response = client.chat.completions.create(  
        model=MODEL_NAME,  
        temperature=0.2,  
        n=1,  
        messages=messages,  
    )  
    answer = response.choices[0].message.content  
    return answer  
  

@app.route('/mental-health-support',methods=['GET', 'POST'])  
def mhsupport():  
    if request.method == 'POST':  
        thoughts = request.form.get("thoughts")  
        chat_history = request.form.get("chat_history", [])  
        return get_support(thoughts, chat_history)  
    else:  
        return render_template("mhs.html")  
  
@app.errorhandler(404)  
def handle_404(e):  
    return '<h1>404</h1><p>File not found!</p><img src="https://httpcats.com/404.jpg" alt="cat in box" width=400>', 404  
  
if __name__ == '__main__':  
    app.run(debug=True)  