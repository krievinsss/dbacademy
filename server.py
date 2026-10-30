import csv, hashlib, hmac, io, json, os, re, secrets, sqlite3, time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from curriculum import make_lessons, QUIZ_BANK, SECTION_NOTES

ROOT=Path(__file__).resolve().parent
DB=ROOT/'data'/'academy.sqlite3'
DB.parent.mkdir(exist_ok=True)
HOST=os.environ.get('HOST','127.0.0.1')
PORT=int(os.environ.get('PORT','8765'))

def db():
 c=sqlite3.connect(DB,timeout=10)
 c.row_factory=sqlite3.Row
 c.execute('PRAGMA foreign_keys=ON')
 return c

def pw_hash(pw,salt=None):
 salt=salt or secrets.token_hex(16)
 digest=hashlib.pbkdf2_hmac('sha256',pw.encode(),bytes.fromhex(salt),240000).hex()
 return salt+':'+digest

def pw_valid(pw,stored):
 try:
  salt,_=stored.split(':'); return hmac.compare_digest(pw_hash(pw,salt),stored)
 except Exception:return False

def setup():
 with db() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE NOT NULL,name TEXT NOT NULL,role TEXT NOT NULL,password_hash TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id),expires INTEGER NOT NULL);
  CREATE TABLE IF NOT EXISTS lessons(id INTEGER PRIMARY KEY,section TEXT NOT NULL,section_title TEXT NOT NULL,number INTEGER NOT NULL,title TEXT NOT NULL,hours INTEGER NOT NULL,opened INTEGER NOT NULL DEFAULT 0);
  CREATE TABLE IF NOT EXISTS quiz_attempts(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id),lesson_id INTEGER NOT NULL REFERENCES lessons(id),score INTEGER NOT NULL,total INTEGER NOT NULL,answers_json TEXT NOT NULL,created TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS sql_attempts(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id),lesson_id INTEGER NOT NULL REFERENCES lessons(id),query TEXT NOT NULL,passed INTEGER NOT NULL,message TEXT NOT NULL,created TEXT NOT NULL);
  CREATE INDEX IF NOT EXISTS idx_quiz_lookup ON quiz_attempts(user_id,lesson_id);
  CREATE INDEX IF NOT EXISTS idx_sql_lookup ON sql_attempts(user_id,lesson_id);''')
  if not c.execute('SELECT 1 FROM users LIMIT 1').fetchone():
   c.execute('INSERT INTO users(username,name,role,password_hash) VALUES(?,?,?,?)',('teacher','Demo skolotājs','teacher',pw_hash('DemoTeacher123!')))
   for i in range(1,9):c.execute('INSERT INTO users(username,name,role,password_hash) VALUES(?,?,?,?)',(f'student{i}',f'Skolēns {i}','student',pw_hash('DemoStudent123!')))
  if not c.execute('SELECT 1 FROM lessons LIMIT 1').fetchone():
   c.executemany('INSERT INTO lessons(section,section_title,number,title,hours,opened) VALUES(?,?,?,?,?,?)',[(l['section'],l['section_title'],l['number'],l['title'],l['hours'],1 if i<2 else 0) for i,l in enumerate(make_lessons())])

def now(): return datetime.now(timezone.utc).isoformat(timespec='seconds')

def quiz_for(lesson):
 section=lesson['section']
 slots={'5.1':[0,1,2,3,4,5,6,8], '5.2':[1,4,5,6,7,10,11,0], '6.1':[8,9,10,11,6,0,1,7], 'FIN':[0,1,4,5,8,9,10,11]}[section]
 start=(lesson['number']-1)%len(slots)
 return [(slots[(start+i)%len(slots)],QUIZ_BANK[slots[(start+i)%len(slots)]]) for i in range(5)]

# Vienmēr tīra, izolēta demonstrācijas datubāze. SQLite, nevis reālās lietotnes DB.
def sql_demo():
 c=sqlite3.connect(':memory:')
 c.executescript('''CREATE TABLE groups (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
 CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL, group_id INTEGER REFERENCES groups(id));
 CREATE TABLE grades (id INTEGER PRIMARY KEY, student_id INTEGER REFERENCES students(id), score INTEGER);
 INSERT INTO groups VALUES (1,'IPa23'),(2,'IPb23');
 INSERT INTO students VALUES (1,'Anna',1),(2,'Jānis',1),(3,'Līga',2),(4,'Mārtiņš',2);
 INSERT INTO grades VALUES (1,1,9),(2,1,8),(3,2,6),(4,3,10),(5,4,7);''')
 c.execute('PRAGMA query_only=ON')
 return c

def run_sql(query):
 query=query.strip()
 if len(query)>2500 or not re.match(r'(?is)^(SELECT|WITH)\b',query): return None,'Atļauts tikai SELECT vai WITH ... SELECT vaicājums (līdz 2500 rakstzīmēm).'
 if ';' in query.rstrip(';'):return None,'Atļauts tikai viens vaicājums.'
 c=sql_demo();started=time.monotonic()
 def guard(): return 1 if time.monotonic()-started>.25 else 0
 c.set_progress_handler(guard,1000)
 try:
  cur=c.execute(query);columns=[x[0] for x in cur.description or []];rows=cur.fetchmany(51)
  if len(rows)>50:return None,'Vaicājums atgrieza vairāk nekā 50 rindas.'
  return {'columns':columns,'rows':[list(row) for row in rows]},None
 except sqlite3.Error as e:return None,str(e)
 finally:c.close()

SQL_TASKS={
 '5.1':('Atlasi skolēnu vārdus un grupu nosaukumus, savienojot tabulas students un groups.','SELECT students.name, groups.name FROM students JOIN groups ON students.group_id = groups.id'),
 '5.2':('Aprēķini katram skolēnam vidējo atzīmi, atgriežot skolēna vārdu un AVG(score).','SELECT students.name, AVG(grades.score) FROM students JOIN grades ON students.id = grades.student_id GROUP BY students.id, students.name'),
 '6.1':('Atlasi skolēnus ar vārdu un group_id, sakārtojot tos pēc vārda alfabētiskā secībā.','SELECT name, group_id FROM students ORDER BY name'),
 'FIN':('Aprēķini katrai grupai skolēnu skaitu, atgriežot grupas nosaukumu un COUNT(students.id).','SELECT groups.name, COUNT(students.id) FROM groups LEFT JOIN students ON groups.id=students.group_id GROUP BY groups.id, groups.name')
}

def sql_check(q,section):
 actual,err=run_sql(q)
 if err:return False,err,actual
 expected,_=run_sql(SQL_TASKS[section][1]); assert expected
 # Vērtē saturu un rezultātu, nevis vaicājuma teksta sakritību.
 def norm(result):return sorted([tuple(str(v) for v in row) for row in result['rows']])
 if norm(actual)==norm(expected) and len(actual['columns'])==len(expected['columns']):return True,'Pareizi! Rezultātu rindas atbilst sagaidāmajam.',actual
 return False,'Vaicājums izpildījās, bet rezultāts neatbilst sagaidāmajam. Pārbaudi kolonnas, savienojumus un kārtošanu.',actual

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args): pass
 def send_json(self,obj,status=200,headers=None):
  data=json.dumps(obj,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('X-Frame-Options','DENY');self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'")
  for k,v in (headers or {}).items():self.send_header(k,v)
  self.end_headers();self.wfile.write(data)
 def fail(self,msg,status=400):self.send_json({'error':msg},status)
 def body(self):
  length=int(self.headers.get('Content-Length','0'))
  if length>30000:raise ValueError('Pārāk liels pieprasījums')
  return json.loads(self.rfile.read(length) or b'{}')
 def user(self):
  cookie=self.headers.get('Cookie','')
  token=next((p.strip().split('=',1)[1] for p in cookie.split(';') if p.strip().startswith('academy_session=')),None)
  if not token:return None
  with db() as c:
   return c.execute('SELECT u.id,u.username,u.name,u.role FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=? AND s.expires>?',(hashlib.sha256(token.encode()).hexdigest(),int(time.time()))).fetchone()
 def require(self,role=None):
  u=self.user()
  if not u:self.fail('Lūdzu, pieslēdzies.',401);return None
  if role and u['role']!=role:self.fail('Nav piekļuves tiesību.',403);return None
  return u
 def do_GET(self):
  path=urlparse(self.path).path
  if path in ('/','/static/app.js','/static/style.css'):
   file=ROOT/('static/index.html' if path=='/' else path.lstrip('/'))
   if not file.is_file():self.send_error(404);return
   data=file.read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8' if path=='/' else 'application/javascript; charset=utf-8' if path.endswith('js') else 'text/css; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(data);return
  if path=='/api/me':
   u=self.user();self.send_json({'user':dict(u) if u else None});return
  u=self.require()
  if not u:return
  with db() as c:
   if path=='/api/lessons':
    lessons=[dict(r) for r in c.execute('SELECT * FROM lessons ORDER BY id')]
    attempts=c.execute('SELECT lesson_id, MAX(score*100/total) AS best FROM quiz_attempts WHERE user_id=? GROUP BY lesson_id',(u['id'],)).fetchall()
    sql=c.execute('SELECT lesson_id, MAX(passed) AS passed FROM sql_attempts WHERE user_id=? GROUP BY lesson_id',(u['id'],)).fetchall()
    b={r['lesson_id']:r['best'] for r in attempts};s={r['lesson_id']:r['passed'] for r in sql}
    for l in lessons:
     l['best_quiz']=b.get(l['id']);l['sql_passed']=s.get(l['id'],0)
    self.send_json({'lessons':lessons,'total_hours':sum(l['hours'] for l in lessons)});return
   if path.startswith('/api/lesson/'):
    try:lid=int(path.rsplit('/',1)[1])
    except ValueError:self.fail('Nepareizs ID');return
    lesson=c.execute('SELECT * FROM lessons WHERE id=?',(lid,)).fetchone()
    if not lesson:self.fail('Nodarbība nav atrasta',404);return
    if u['role']!='teacher' and not lesson['opened']:self.fail('Nodarbība nav atvērta',403);return
    lesson=dict(lesson);quiz=[{'id':i,'question':q[0],'choices':q[1]} for i,q in quiz_for(lesson)]
    prompt,example=SQL_TASKS[lesson['section']]
    self.send_json({'lesson':lesson,'theory':SECTION_NOTES[lesson['section']],'quiz':quiz,'sql_task':prompt,'schema':'groups(id, name)\nstudents(id, name, group_id)\ngrades(id, student_id, score)','example_data':{'groups':[['1','IPa23'],['2','IPb23']],'students':[['1','Anna','1'],['2','Jānis','1'],['3','Līga','2'],['4','Mārtiņš','2']]}});return
   if path=='/api/dashboard':
    if u['role']!='teacher':self.fail('Nav piekļuves tiesību',403);return
    students=[dict(r) for r in c.execute("SELECT id,username,name FROM users WHERE role='student' ORDER BY id")]
    lessons=c.execute('SELECT COUNT(*) n,SUM(opened) opened,SUM(hours) h FROM lessons').fetchone()
    for s in students:
     scores=c.execute('SELECT lesson_id,MAX(score*100.0/total) best FROM quiz_attempts WHERE user_id=? GROUP BY lesson_id',(s['id'],)).fetchall()
     passed=c.execute('SELECT COUNT(DISTINCT lesson_id) n FROM sql_attempts WHERE user_id=? AND passed=1',(s['id'],)).fetchone()['n']
     s['quizzes']=len(scores);s['mean_score']=round(sum(x['best'] for x in scores)/len(scores)) if scores else None;s['sql_passed']=passed
     s['completed']=c.execute('''SELECT COUNT(*) n FROM (SELECT lesson_id,MAX(score*100.0/total) score FROM quiz_attempts WHERE user_id=? GROUP BY lesson_id) q WHERE q.score>=70 AND EXISTS(SELECT 1 FROM sql_attempts x WHERE x.user_id=? AND x.lesson_id=q.lesson_id AND x.passed=1)''',(s['id'],s['id'])).fetchone()['n']
    self.send_json({'students':students,'lessons':dict(lessons),'recent':[dict(x) for x in c.execute('''SELECT u.name,l.title,q.score,q.total,q.created FROM quiz_attempts q JOIN users u ON u.id=q.user_id JOIN lessons l ON l.id=q.lesson_id ORDER BY q.id DESC LIMIT 12''')]});return
   if path=='/api/export.csv':
    if u['role']!='teacher':self.fail('Nav piekļuves tiesību',403);return
    out=io.StringIO();writer=csv.writer(out);writer.writerow(['Lietotājs','Jaunietis','Nodarbība','Tēma','Labākais tests (%)','SQL izpildīts'])
    for row in c.execute('''SELECT u.username,u.name,l.id,l.title,MAX(q.score*100.0/q.total) best,(SELECT MAX(passed) FROM sql_attempts x WHERE x.user_id=u.id AND x.lesson_id=l.id) passed FROM users u CROSS JOIN lessons l LEFT JOIN quiz_attempts q ON q.user_id=u.id AND q.lesson_id=l.id WHERE u.role='student' GROUP BY u.id,l.id ORDER BY u.id,l.id'''):
     writer.writerow([row[0],row[1],row[2],row[3],round(row[4],1) if row[4] is not None else '',row[5] or 0])
    data=out.getvalue().encode('utf-8-sig');self.send_response(200);self.send_header('Content-Type','text/csv; charset=utf-8');self.send_header('Content-Disposition','attachment; filename="db_academy_progress.csv"');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
  self.fail('Nezināms resurss',404)
 def do_POST(self):
  path=urlparse(self.path).path
  try:payload=self.body()
  except (ValueError,json.JSONDecodeError) as e:self.fail(str(e));return
  if path=='/api/login':
   name=str(payload.get('username','')).strip();pw=str(payload.get('password',''))
   with db() as c:
    person=c.execute('SELECT * FROM users WHERE username=?',(name,)).fetchone()
    if not person or not pw_valid(pw,person['password_hash']):self.fail('Nepareizs lietotājvārds vai parole',401);return
    token=secrets.token_urlsafe(36);c.execute('INSERT INTO sessions(token_hash,user_id,expires) VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),person['id'],int(time.time())+86400))
   self.send_json({'ok':True,'user':{'name':person['name'],'role':person['role']}},headers={'Set-Cookie':f'academy_session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=86400'});return
  if path=='/api/logout':
   cookie=self.headers.get('Cookie','')
   token=next((p.strip().split('=',1)[1] for p in cookie.split(';') if p.strip().startswith('academy_session=')),None)
   if token:
    with db() as c:c.execute('DELETE FROM sessions WHERE token_hash=?',(hashlib.sha256(token.encode()).hexdigest(),))
   self.send_json({'ok':True},headers={'Set-Cookie':'academy_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0'});return
  u=self.require()
  if not u:return
  if path=='/api/open':
   if u['role']!='teacher':self.fail('Tikai skolotājam',403);return
   try:lid=int(payload['lesson_id']);opened=1 if payload['opened'] is True else 0
   except (KeyError,ValueError,TypeError):self.fail('Nepareizi dati');return
   with db() as c:
    cur=c.execute('UPDATE lessons SET opened=? WHERE id=?',(opened,lid))
    if not cur.rowcount:self.fail('Nodarbība nav atrasta',404);return
   self.send_json({'ok':True});return
  if path=='/api/quiz':
   try:lid=int(payload['lesson_id']);answers=payload['answers']
   except (KeyError,TypeError,ValueError):self.fail('Nepareizi dati');return
   with db() as c:
    lesson=c.execute('SELECT * FROM lessons WHERE id=?',(lid,)).fetchone()
    if not lesson:self.fail('Nodarbība nav atrasta',404);return
    if not lesson['opened'] and u['role']!='teacher':self.fail('Nodarbība nav atvērta',403);return
    quiz=quiz_for(lesson);score=sum(1 for i,q in quiz if str(answers.get(str(i),'-1'))==str(q[2]))
    feedback=[{'id':i,'correct':q[2],'explanation':q[3]} for i,q in quiz]
    c.execute('INSERT INTO quiz_attempts(user_id,lesson_id,score,total,answers_json,created) VALUES(?,?,?,?,?,?)',(u['id'],lid,score,len(quiz),json.dumps(answers),now()))
   self.send_json({'score':score,'total':len(quiz),'feedback':feedback});return
  if path=='/api/sql':
   try:lid=int(payload['lesson_id']);query=str(payload['query'])
   except (KeyError,ValueError,TypeError):self.fail('Nepareizi dati');return
   with db() as c:
    lesson=c.execute('SELECT * FROM lessons WHERE id=?',(lid,)).fetchone()
    if not lesson:self.fail('Nodarbība nav atrasta',404);return
    if not lesson['opened'] and u['role']!='teacher':self.fail('Nodarbība nav atvērta',403);return
    passed,message,result=sql_check(query,lesson['section'])
    c.execute('INSERT INTO sql_attempts(user_id,lesson_id,query,passed,message,created) VALUES(?,?,?,?,?,?)',(u['id'],lid,query,int(passed),message,now()))
   self.send_json({'passed':passed,'message':message,'result':result});return
  self.fail('Nezināma darbība',404)

if __name__=='__main__':
 setup();print(f'DB Academy: http://{HOST}:{PORT}',flush=True)
 ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
