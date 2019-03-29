import pyodbc 

class DB:
    def __init__(self):
        self.server = 'tcp:twitter-emotion.database.windows.net' 
        self.database = 'tweet_collection' 
        self.username = 'tharindukw96' 
        self.password = 'cpktnwt@GMA2012' 
        self.cnxn = pyodbc.connect('Driver={ODBC Driver 13 for SQL Server};Server=tcp:twitter-emotion.database.windows.net,1433;Database=tweet_collection;Uid=tharindukw96@twitter-emotion;Pwd=cpktnwt@GMA2012;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
        self.cursor = self.cnxn.cursor()

    def getConnection(self):
        return self.cursor

    def execute(self,query):
        self.cursor.execute(query)
        return self.cursor

    def insert(self,query):
        self.cursor.execute(query)
        self.cnxn.commit()
        return self.cursor
#Create the DB connection
db = DB()

#Get the all keywords
output = db.execute("Select keyword from key_words")
items = [r[0].lower() for r in output]
query = "select count(*) from tweet_info where lower(text) like '%{0}%'"
count= []
for keyword in items:
    result = db.execute(query.format(keyword))
    for k in result:
        count.append(k[0])
        print(keyword)

for i in  range(0,len(count)):
    query = "Update key_words set tweet_count = {0} where keyword = '{1}' "
    db.insert(query.format(count[i],items[i]))


