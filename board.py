import math	
from flask import Flask, render_template, request, url_for, redirect, session
from flaskext.mysql import MySQL

mysql = MySQL() #mysql 인스턴스 생성. 객체.

app=Flask(__name__)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
app.config['MYSQL_DATABASE_DB'] = 'mydb'

app.secret_key = '^U\xe1\x96\xd0F\x9c\x06E\x80\x07\x9c\xd8B~fW"\x952X\'`\x1a.\xed\xad\x92\xc8\x1e\x885\x01\xe5\xf1\x84\x97\x9c\xa8;\t\xe1'

mysql.init_app(app) #flask와 객체 사이의 관계를 초기화시켜줌.

@app.route("/")
def index():
	userid=None
	if 'id' in session:
		userid = session['id']
	return render_template("index.html", userid=userid)

@app.route("/write", methods=['GET','POST'])
def write():
	if request.method =='POST':  #or request.method == 'POST'
		title= request.form['title']
		content = request.form['content']
		id=session['id']
		sql1='SELECT name FROM member WHERE id=%s'
		data1=(id,)
		conn=mysql.connect()
		cursor =conn.cursor()
		sql = 'INSERT INTO board(title, content,id) VALUES(%s, %s,%s)' #제목, 내용, id가 저장되게 하는 것이고 나머지는 자동 입력됨(hit, date)
		data =(title, content, id)
		cursor.execute(sql, data)
		conn.commit()
		conn.close()
		return 'OK'
		# return redirect(url_for('/list/1'))
	else : 
		return render_template("writeform.html")

@app.route("/list")
def list0(): 
	return redirect("/list/1")

@app.route("/list/<int:page>")	#page값인 문자를 숫자로 받는 것.
def list(page):
	size =10
	begin= (page-1)*size
	conn=mysql.connect()
	cursor = conn.cursor()
	sql_count="SELECT count(*) cnt from board"
	cursor.execute(sql_count)
	t1=cursor.fetchone()	#(1490,)
	cnt=t1[0]	#1490
	total_page=math.ceil(cnt/size) #1490이 10으로 나눠지지 않는 값이라면 값을 올림.
	link_size=10 				   #보여줄 게시물 링크의 수
	# a=(page-1)					#10, 20, 30 때문에 미리 1을 뺀다.
	# b=a/10	
	# c=math.floor(b) 			   #소수점 버림
	# d= c*10						#10을 곱하고 1을 더하면 1, 11, 21 이렇게 처음 시작하는 페이지가 나온다.
	# e=d+1
	# print(e)
	start_link=math.floor((page-1)/link_size) * link_size + 1
	end_link=start_link +(link_size - 1) 
	if end_link > total_page:
		end_link = total_page
	sql = """
	SELECT 
		b.num, b.title, b.content, m.name writer, b.hit, b.regdate
	FROM board b, member m
	WHERE b.id = m.id
	ORDER BY b.num DESC LIMIT %s, %s
	"""
	data=(begin, size)
	cursor.execute(sql, data)
	lists= [ dict(num=row[0], title=row[1], content=row[2], writer=row[3], hit=row[4], regdate=row[5]) for row in cursor.fetchall()]
	conn.close()
	max = cnt - ((page-1) * link_size)	#각 페이지별로 가장 큰 숫자.
	datas={ "lists":lists, "page":page, "total_page":total_page, "link_size":link_size, "start_link":start_link, "end_link":end_link, "max":max}
	return render_template("list.html", datas=datas)

''' board 테이블 객체 : num, title, content, hit, regdate, id'''
''' comments 테이블 객체 : no, content, regdate, num, id '''

@app.route("/read/<num>/<page>")
def read(num, page):
	sql1="UPDATE board SET hit=hit+1 WHERE num=%s" 
	data =(num,)
	conn=mysql.connect()
	cursor=conn.cursor()
	cursor.execute(sql1, data)
	conn.commit()
	sql2="SELECT * FROM board WHERE num=%s"
	cursor.execute
	data2=(num,)
	cursor.execute(sql2, data2)
	t=cursor.fetchone()   #웹에서는 주로 구조를 사전으로 쓴다. 그래서 튜플을 t로 받아서 밑에서 사전으로 만들어준다.
	b=dict(num=t[0], title=t[1], content=t[2], writer=t[3],  hit=t[4], regdate=t[5])
	# print(b)
	sql3= "SELECT content, writer, regdate FROM comments WHERE num=%s ORDER BY no DESC"
	data3=(num,)
	cursor.execute(sql3, data3)
	c=[dict(content=row[0], writer=row[1], regdate=row[2]) for row in cursor.fetchall() ]
	datas={'b':b, "c":c, "page":page} 	#b는 board의 글 하나, c는 댓글 여러개를 뜻함.
	conn.close()
	return render_template("read.html", datas=datas)

@app.route("/update/<num>/<page>")	#num, page번호를 같이 받겠다.
def updateform(num, page):
	conn=mysql.connect()
	cursor=conn.cursor()
	sql="SELECT num, title, content, id FROM board WHERE num =%s"
	data=(num,)
	cursor.execute(sql, data)
	t=cursor.fetchone()
	print(t)
	b=dict(num=t[0], title=t[1], content=t[2], writer=t[3])
	print(b)
	datas={ 'b':b, 'page':page }
	conn.close()
	return render_template("updateform.html", datas=datas)

@app.route('/update', methods=['POST'])
def update():
	num=request.form['num']
	title= request.form['title']
	content = request.form['content']
	writer = request.form['writer']
	pwd = request.form['pwd']
	page=request.form['page'] 	#POST라서 /update/page수 안해줘도 되지만, page를 받아야 하기 때문에 넣어줘야 한다.
	sql = '''UPDATE board SET title=%s, content=%s, writer=%s WHERE num=%s AND pwd=%s''' #비밀번호는 고치는 범위에 포함 안시킴.
	data=(title, content, writer, num, pwd)
	conn=mysql.connect()
	cursor=conn.cursor()
	cursor.execute(sql, data)
	conn.commit()
	conn.close()
	return redirect('/list/' + page)	#request.form은 무조건 문자이기 때문에 int<page> 이렇게 해주지 않아도 된다.

@app.route("/delete/<num>/<page>") #변수를 쓸 때는 <> 이걸 쓴다.
def deleteform(num, page):
	datas={'num':num, 'page':page} 	#받아야 될 인자가 2개이므로 datas로 묶어버림.
	return render_template('deleteform.html', datas=datas) #{'num':num} num이라는 키에 번호가 매칭되는 것이다.

@app.route('/delete', methods=['POST'])
def delete():
	num=request.form['num']
	pwd=request.form['pwd']
	page=request.form['page']
	sql='DELETE FROM board WHERE num=%s AND pwd=%s'
	data = (num, pwd)
	conn=mysql.connect()
	cursor=conn.cursor()
	cursor.execute(sql, data)
	conn.commit()
	conn.close()
	return redirect('list/' + page)  	#/list/2

@app.route("/write300")
def write300():
	conn=mysql.connect()
	cursor =conn.cursor()
	for i in range(1,301):
		writer = '타잔' + str(i)
		title= writer +"이 " + str(i)+'원짜리 팬티를'
		content = writer +'이 ' + str(i) +"원짜리 칼을 차고..."
		pwd = '1234'
		sql = 'INSERT INTO board(title, content, writer, pwd) VALUES(%s, %s,%s,%s)'
		data =(title, content, writer, pwd)
		cursor.execute(sql, data)
		conn.commit()
	conn.close()
	return "OK"

@app.route('/comment/<int:num>/<page>')	#입력하는 쪽
def comment(num, page):
	datas={'num':num, 'page':page }
	return render_template('comment_writeform.html', datas=datas)	#num이 hidden으로 들어가야 한다.
	
@app.route('/comment/write', methods=['POST'])	#받는 쪽
def comment_write():
	writer = request.form['writer']
	pwd = request.form['pwd']
	content=request.form['content']
	num=request.form['num']
	page=request.form['page']
	# 위의 4개의 값들을 입력받는다.
	sql='INSERT INTO comments(content, pwd, writer, num) VALUES(%s,%s,%s,%s)'
	data=(content, pwd, writer, num)
	conn=mysql.connect()
	cursor=conn.cursor()
	cursor.execute(sql, data)
	conn.commit()
	conn.close()
	return redirect('/read/{0}/{1}' .format(num, page))
	# return redirect('/')

@app.route('/join', methods=['GET', 'POST'])
def join():
	if request.method =='POST':
		# print(request.form)
		id=request.form['id']
		pwd=request.form['pwd']
		name=request.form['name']
		phone=request.form['phone']
		gender=request.form['gender']
		addr=request.form['addr']
		birth=request.form['birth']	#
		conn=mysql.connect() #db 연결
		cursor=conn.cursor() #cursor객체. 커서
		sql1=' INSERT INTO member(id, pwd, name, phone, gender, addr, birth) VALUES (%s, %s, %s, %s,%s, %s,%s)'
		data=(id, pwd, name, phone, gender, addr, birth)
		cursor.execute(sql1, data)
		conn.commit()
		conn.close()
		return redirect('/login')
	else:
		return render_template('member/join.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method=='POST':
		id=request.form['id']
		pwd=request.form['pwd']
		sql='SELECT count(*) cnt FROM member WHERE id=%s AND pwd=%s'
		data=(id, pwd)
		conn=mysql.connect()
		cursor=conn.cursor()
		cursor.execute(sql, data)
		t=cursor.fetchone()
		cnt=t[0] #위에서 튜플로 묶인 값의 첫번째가 카운트 된 회원수이기 때문.
		conn.close()
		if cnt== 0:
			return "<script>alert('비밀번호를 확인해주세요.');history.back()</script>"
		else :
			session['id'] =id 	
			#정상적으로 id, pwd가 맞았을 때 id값을 내보낸다. 즉, 값이 있으면 로그인이 정상적으로 된 상태라는거.
			return redirect('/')
	else:
		return render_template('member/login.html')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')
	



''' member 테이블 객체 : id, pwd, name, phone, gender, addr, birth'''
''' board 테이블 객체 : num, title, content, hit, regdate, id'''
''' comments 테이블 객체 : no, content, regdate, num, id '''

if __name__=="__main__":
	app.debug = True
	app.run() 
#입력하는쪽에서는 return render_template, 받는쪽에서는 주로 redirect를 사용한다.







'''

CREATE TABLE board (
	num     INT           NOT NULL AUTO_INCREMENT,
	title   VARCHAR(50)   NOT NULL, 
	content VARCHAR(1000) NOT NULL,
	writer  VARCHAR(10)   NOT NULL,
	pwd     VARCHAR(12)   NOT NULL,
	hit     INT           NOT NULL DEFAULT 0,
	regdate DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
	constraint PK_board PRIMARY KEY(num)
	)

CREATE TABLE comments (
	no      INT          AUTO_INCREMENT NOT NULL, 
	content VARCHAR(200) NOT NULL,
	pwd     VARCHAR(12)  NOT NULL, 
	writer  VARCHAR(10)  NOT NULL,
	regdate DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	num     INT          NULL,
	CONSTRAINT PK_comments PRIMARY KEY(no), -- comments 테이블의 no를 PK로 설정했다.
	CONSTRAINT PK_board_TO_comments FOREIGN KEY (num) REFERENCES board (num)
	   -- board에서  num이 comments 테이블의 FK의 num이 된다는  의미.
)

select * from board		전체 내용 보기.

update board set hit=+1 where num =2 	hit추가해보기.

select * from board order by num DESC limit 0,10  가장 최신순으로 10개 출력
select * from board order by num DESC limit 10,10	가장 최신순으로 나열했을 때 10번째부터 10개 출력.
paging 처리 = (페이지 -1) *10

'''




"""
CREATE TABLE member (
	id     VARCHAR(12)  NOT NULL ,
	pwd    VARCHAR(12)  NOT NULL ,
	name   VARCHAR(10)  NOT NULL ,
	phone  VARCHAR(13)  NOT NULL ,
	gender VARCHAR(1)   NOT NULL ,
	addr   VARCHAR(200) NOT NULL ,
	birth  DATE         NOT NULL ,
	CONSTRAINT PK_member PRIMARY KEY (id) 
);

CREATE TABLE board (
	num     INT           NOT NULL AUTO_INCREMENT ,
	title   VARCHAR(50)   NOT NULL ,
	content VARCHAR(1000) NOT NULL ,
	hit     INT           NOT NULL DEFAULT 0 ,
	regdate DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ,
	id      VARCHAR(12)   ,
	CONSTRAINT PK_board PRIMARY KEY (num) ,
	CONSTRAINT FK_member_TO_board FOREIGN KEY (id) REFERENCES member (id)
);

CREATE TABLE comments (
	no      INT          NOT NULL AUTO_INCREMENT ,
	content VARCHAR(200) NOT NULL ,
	regdate DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ,
	num     INT          ,
	id      VARCHAR(12)  ,
	CONSTRAINT PK_comments PRIMARY KEY (no) ,
	CONSTRAINT FK_board_TO_comments FOREIGN KEY (num) REFERENCES board (num) ,
	CONSTRAINT FK_member_TO_comments FOREIGN KEY (id) REFERENCES member (id)
);
"""