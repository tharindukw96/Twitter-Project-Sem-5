from flask import Flask,jsonify,request,render_template,send_from_directory
from bokeh.io import show, output_file
from bokeh.plotting import figure
import pyodbc 
from bokeh.embed import components
import bokeh.layouts 
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import _thread

server = 'tcp:twitter-emotion.database.windows.net' 
database = 'tweet_collection' 
username = 'tharindukw96' 
password = 'cpktnwt@GMA2012' 
cnxn = pyodbc.connect('Driver={ODBC Driver 13 for SQL Server};Server=tcp:twitter-emotion.database.windows.net,1433;Database=tweet_collection;Uid=tharindukw96@twitter-emotion;Pwd=cpktnwt@GMA2012;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
cursor = cnxn.cursor()

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('index.html')


def getWordCloud(cnxn,keyword,frmDate,toDate):
    texts = []
    
    fNames = ['sad.png','joy.png','fear.png','angry.png']
    for i in range(0,4):
        cursor = cnxn.cursor()
        query = "SELECT TEXT FROM TWEET_INFO WHERE TEXT LIKE '%"+keyword+"%' and Emotion ='"+str(i)+"' and created_at between '"+frmDate+"' and '"+toDate+"'";
        cursor.execute(query)
        txt=[]
        for row in cursor:
            txt.append(row[0])
        texts.append(txt)
    for i in range(0,4):
        words = ''
        for w in texts[i]:
            words += ' '.join(w.split(' '))
        txt.append(words)
        wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(words)
        wordcloud.to_file(fNames[i])


@app.route("/analyze/", methods=['POST'])
def analyze():
    global cnxn
    keyword = request.form.get('keyword')
    frmDate = request.form.get('frmDate')
    toDate = request.form.get('toDate')
    data = {}
    dates = {}

    for i in range(0,4):
        cursor = cnxn.cursor()
        query = "SELECT created_at,count(*) * (abs(cast(newid() as binary(6)) % 10)) FROM TWEET_INFO WHERE TEXT LIKE '%"+keyword+"%' and Emotion ='"+str(i)+"' and created_at between '"+frmDate+"' and '"+toDate+"' group by created_at";
        cursor.execute(query)
        date = []
        count = []
        for row in cursor:
            date.append(row[0].strftime("%Y-%m-%d, %H:%M:%S"))
            count.append(row[1])
        data[str(i)] = count
        dates[str(i)] = date
    graphs = []
    Emotions = ['Joy','Sad','Fear','Angry']
    for i in range(0,4):
        p1 = figure(x_range=dates[str(i)], plot_height=350,plot_width=3000 ,title=Emotions[i]+" Emotion Count Timeline",toolbar_location='below', tools="")
        p1.xaxis.major_label_orientation = 'horizontal'
        p1.vbar(x=dates[str(i)], top=data[str(i)], width=0.4)
        p1.xaxis.major_label_orientation = 'vertical'
        p1.xgrid.grid_line_color = None
        p1.y_range.start = 0
        graphs.append(p1)

    try:
        _thread.start_new_thread( getWordCloud, (cnxn,keyword,frmDate,toDate, ) )
        
    except:
        print ("Error: unable to start thread")
    #getWordCloud(cnxn,keyword,frmDate,toDate)
    show(bokeh.layouts.column(graphs[0],graphs[1],graphs[2],graphs[3]))
    base = 'http://127.0.0.1:5000/image/'
    filename1 = base + 'joy.png'
    filename2 = base + 'sad.png'
    filename3 = base + 'fear.png'
    filename4 = base + 'angry.png'
    return render_template("index.html",filename1=filename1,filename2=filename2,filename3=filename3,filename4=filename4)

@app.route('/image/<path:filename>')
def image(filename):
    try:
        w = int(request.args['w'])
        h = int(request.args['h'])
    except (KeyError, ValueError):
        return send_from_directory('.', filename)

    try:
        im = Image.open(filename)
        im.thumbnail((w, h), Image.ANTIALIAS)
        io = StringIO.StringIO()
        im.save(io, format='JPEG')
        return Response(io.getvalue(), mimetype='image/jpeg')

    except IOError:
        abort(404)

    return send_from_directory('.', filename)

