import sqlite3, json
from datetime import datetime
DB = "campusmate.db"
def init_db():
    with sqlite3.connect(DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, time TEXT, status TEXT, tool TEXT, args TEXT, result TEXT)")
def add_log(status, tool, args, result):
    with sqlite3.connect(DB) as c:
        c.execute("INSERT INTO logs(time,status,tool,args,result) VALUES(?,?,?,?,?)",
                  (datetime.now().isoformat(timespec="seconds"), status, tool, json.dumps(args), json.dumps(result)))
def get_logs():
    with sqlite3.connect(DB) as c:
        rows=c.execute("SELECT id,time,status,tool,args,result FROM logs ORDER BY id DESC").fetchall()
    return [{"ID":r[0],"Time":r[1],"Status":r[2],"Tool":r[3],"Arguments":r[4],"Result":r[5]} for r in rows]
def clear_logs():
    with sqlite3.connect(DB) as c: c.execute("DELETE FROM logs")
