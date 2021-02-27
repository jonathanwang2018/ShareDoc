from flask import Flask, render_template, request
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SecretKey")


@app.route("/")
def index():
	conn = sqlite3.connect('docs.sql')
	c = conn.cursor()
	results = c.execute(
	    "SELECT title FROM docsInfo WHERE mode='public'").fetchall()
	authors = c.execute(
	    "SELECT author FROM docsInfo WHERE mode='public'").fetchall()
	total = len(results)
	docs_list = []
	for i in range(total):
		results_item = str(results[i])
		authors_item = str(authors[i])
		results_item = results_item[2:]
		results_item = results_item[:-3]

		authors_item = authors_item[2:]
		authors_item = authors_item[:-3]
		docs_list.append(results_item)
		docs_list.append(authors_item)

	preview = c.execute(
	    "SELECT doccontent FROM docsInfo WHERE mode='public'").fetchall()

	conn.commit()
	conn.close()
	docs_list.reverse()


	f = open("docs.md", "w")
	f.write(
	    "# Public Docs Available to View on ShareDoc\nArray | (Author, Title)\n---\n" + "`" + str(docs_list) + "`" +
	    "\n\nP.S. Passwords are not stored here... if that's what you're looking for..."
	)
	f.close()

	return render_template("index.html",
	                       total=total,
	                       docs_list=docs_list,
	                       preview=preview)


@app.route("/find", methods=['GET'])
def search():
	if request.args.get('term').find("\'") != -1 or request.args.get(
	    'term').find("%") != -1:
		error = "Error! Search Term cannot contain single quotes or the percent sign."
		return render_template("system/error-report.html", error=error)
	conn = sqlite3.connect('docs.sql')
	c = conn.cursor()
	results = c.execute(
	    f"SELECT title FROM docsInfo WHERE title LIKE '%{request.args.get('term')}%' AND mode='public'"
	).fetchall()
	conn.commit()
	conn.close()
	total = len(results)
	if total == 1:
		propernumgrammar = "result"
	else:
		propernumgrammar = "results"

	search_results = f"Showing {total} search {propernumgrammar} for "

	search_term = f"{request.args.get('term')}"

	results = list(results)
	conn = sqlite3.connect('docs.sql')
	c = conn.cursor()
	authors = list(
	    c.execute(
	        f"SELECT author FROM docsInfo WHERE title LIKE '%{request.args.get('term')}%' AND mode='public'"
	    ).fetchall())
	conn.commit()
	conn.close()

	conn = sqlite3.connect('docs.sql')
	c = conn.cursor()
	results = c.execute(
	    f"SELECT title FROM docsInfo WHERE title LIKE '%{request.args.get('term')}%' AND mode='public'"
	).fetchall()
	authors = c.execute(
	    f"SELECT author FROM docsInfo WHERE title LIKE '%{request.args.get('term')}%' AND mode='public'"
	).fetchall()
	total = len(results)
	docs_list = []
	for i in range(total):
		results_item = str(results[i])
		authors_item = str(authors[i])
		results_item = results_item[2:]
		results_item = results_item[:-3]

		authors_item = authors_item[2:]
		authors_item = authors_item[:-3]
		docs_list.append(results_item)
		docs_list.append(authors_item)

	conn.commit()
	conn.close()
	docs_list.reverse()

	return render_template("index.html",
	                       search_results=search_results,
	                       search_term=search_term,
	                       squote="\'",
	                       total=total,
	                       docs_list=docs_list)


@app.route("/creation")
def creation():
	return render_template("creation/index.html")


@app.route("/creation/create", methods=['POST'])
def createDoc():

	password1 = request.form.get("password")
	password2 = request.form.get("password2")

	if password1 == password2:
		title = request.form.get("title")
	
		conn = sqlite3.connect('docs.sql')
		c = conn.cursor()
		results = c.execute("SELECT title FROM docsInfo WHERE title=:title", {
		    "title": title
		}).fetchall()
		conn.commit()
		conn.close()
		if len(results) > 0:
			error = "The title for you Doc is already taken, you will need to modify the name."
			return render_template("system/error-report.html", error=error)
		else:
			pass

		author = request.form.get("author")
		author = f" {author}"
		if title.isspace() or title.find("\'") != -1 or title.find(
		    "%") != -1 or title.find("?") != -1 or title.find("/") != -1 or title.find("+") != -1:
			error = "Invalid title name! Title cannot be just be spaces, contain any single quotes ('), question marks (?), or contain any percent signs (%)."
			return render_template("system/it.html")
		elif password1.isspace():
			error = "Unsecure Password! Your password cannot just be spaces."
			return render_template("system/error-report.html", error=error)
		elif author.isspace() or author.find("\'") != -1:
			error = "Author can't be empty or contain a single quote! We want to give credit to someone."
			return render_template("system/error-report.html", error=error)
		else:
			pass
		crdate = datetime.datetime.now()
		view = request.form.get("view")
		pwhash = generate_password_hash(request.form.get("password"), "sha256")
		doc_content = (request.form.get("doc-content"))

		conn = sqlite3.connect('docs.sql')
		c = conn.cursor()
		c.execute("INSERT INTO docsInfo VALUES (?,?,?,?,?,?,?)",
		          (title, author, crdate, crdate, view, pwhash, doc_content))
		conn.commit()
		conn.close()
		if view == "private":
			view = "Only people with the link or password"
		else:
			view = "Anyone can find and"

		return render_template("creation/create/create.html",
		                       mode=view,
		                       title=title,
		                       pwd=password1)
	else:
		error = "The two passwords you entered do not match. Please re-enter them."
		return render_template("system/error-report.html", error=error)


@app.route("/open/<title>")
def viewDoc(title):
	conn = sqlite3.connect('docs.sql')
	c = conn.cursor()
	title = title.replace("+", " ")
	doc = c.execute("SELECT doccontent FROM docsInfo WHERE title=:title", {
	    "title": title
	}).fetchall()
	if len(doc) == 0:
		error = "404 - That document does not exist!"
		return render_template("system/error-report.html", error=error)
	conn.commit()
	conn.close()

	doc = str(doc)
	doc = doc.replace(r"\r\n", "∇")
	doc = doc[3:]
	doc = doc[:-4]
	utitle = title.replace(" ", "%20")
	return render_template("open/index.html",
	                       title=title,
	                       content=doc,
	                       utitle=utitle)


@app.route("/open/<title>/<pwd>")
def editDoc(title, pwd):
	conn = sqlite3.connect('docs.sql')
	c = conn.cursor()
	stored_pwd = c.execute("SELECT pwhash FROM docsInfo WHERE title=:title", {
	    "title": title
	}).fetchall()
	stored_pwd = str(stored_pwd)
	stored_pwd = stored_pwd[3:]
	stored_pwd = stored_pwd[:-4]
	check_pwd = check_password_hash(stored_pwd, pwd)
	if check_pwd:
		doc = c.execute("SELECT doccontent FROM docsInfo WHERE title=:title", {
		    "title": title
		}).fetchall()

		doc = str(doc)
		doc = doc.replace(r"\r\n", "∇")
		doc = doc[3:]
		doc = doc[:-4]
		lastedate = c.execute("SELECT edate FROM docsInfo WHERE title=:title",
		                      {
		                          "title": title
		                      }).fetchall()
		conn.commit()
		conn.close()
		lastedate = str(lastedate)
		lastedate = lastedate[3:]
		lastedate = lastedate[:-11]
		print(lastedate)
		utitle = title.replace(" ", "%20")
		upwd = pwd.replace(" ", "%20")
		return render_template("open/edit.html",
		                       title=title,
		                       content=doc,
		                       pwd=upwd,
		                       lastedate=lastedate,
		                       utitle=utitle)
	else:
		conn.commit()
		conn.close()
		error = "Password Incorrect"
		return render_template("system/error-report.html", error=error)


@app.route("/submit-edit/<title>/<pwd>", methods=['POST'])
def saveEdits(title, pwd):
	edited = request.form.get("edited")
	conn = sqlite3.connect('docs.sql')
	edate = datetime.datetime.now()
	c = conn.cursor()
	# Checking pwd, to prevent spam and malicious actions
	stored_pwd = c.execute("SELECT pwhash FROM docsInfo WHERE title=:title", {
	    "title": title
	}).fetchall()
	stored_pwd = str(stored_pwd)
	stored_pwd = stored_pwd[3:]
	stored_pwd = stored_pwd[:-4]
	check_pwd = check_password_hash(stored_pwd, pwd)
	if check_pwd:
		c.execute("UPDATE docsInfo SET doccontent=:edited WHERE title=:title",
		          {
		              "title": title,
		              "edited": edited
		          })
		c.execute("UPDATE docsInfo SET edate=:edate WHERE title=:title", {
		    "title": title,
		    "edate": edate
		})
		conn.commit()
		conn.close()
		return render_template("open/cs.html", title=title)
	else:
		conn.commit()
		conn.close()
		error = "Password Incorrect"
		return render_template("system/error-report.html", error=error)
	conn.commit()
	conn.close()
	return render_template("open/cs.html", title=title)


@app.route("/postpwd/<title>", methods=['POST'])
def postPwd(title):
	pwd = request.form.get("enter-pwd")
	conn = sqlite3.connect("docs.sql")
	c = conn.cursor()
	stored_pwd = c.execute("SELECT pwhash FROM docsInfo WHERE title=:title", {
	    "title": title
	}).fetchall()
	conn.commit()
	conn.close()
	stored_pwd = str(stored_pwd)
	stored_pwd = stored_pwd[3:]
	stored_pwd = stored_pwd[:-4]
	check_pwd = check_password_hash(stored_pwd, pwd)
	if check_pwd:
		conn = sqlite3.connect('docs.sql')
		c = conn.cursor()
		doc = c.execute("SELECT doccontent FROM docsInfo WHERE title=:title", {
		    "title": title
		}).fetchall()
		doc = str(doc)
		doc = doc.replace(r"\r\n", "∇")
		doc = doc[3:]
		doc = doc[:-4]
		lastedate = c.execute("SELECT edate FROM docsInfo WHERE title=:title",
		                      {
		                          "title": title
		                      }).fetchall()
		lastedate = str(lastedate)
		lastedate = lastedate[3:]
		lastedate = lastedate[:-11]
		conn.commit()
		conn.close()
		utitle = title.replace(" ", "%20")
		return render_template("open/edit.html",
		                       title=title,
		                       pwd=pwd,
		                       content=doc,
		                       lastedate=lastedate,
		                       utitle=utitle)
	else:
		error = "Password Incorrect"
		return render_template("system/error-report.html", error=error)


@app.route("/delete-doc/<title>", methods=['POST'])
def delete(title):
	pwd = request.form.get("delete-doc")
	print(pwd)
	conn = sqlite3.connect("docs.sql")
	c = conn.cursor()
	stored_pwd = c.execute("SELECT pwhash FROM docsInfo WHERE title=:title", {
	    "title": title
	}).fetchall()
	conn.commit()
	conn.close()
	stored_pwd = str(stored_pwd)
	stored_pwd = stored_pwd[3:]
	stored_pwd = stored_pwd[:-4]
	check_pwd = check_password_hash(stored_pwd, pwd)
	if check_pwd:
		conn = sqlite3.connect('docs.sql')
		c = conn.cursor()
		c.execute("DELETE FROM docsInfo WHERE title=:title", {"title": title})
		conn.commit()
		conn.close()
		return render_template("system/deleted.html", title=title)
	else:
		error = "Cannot delete doc because password is incorrect or Doc doesn't exist anymore!"
		return render_template("system/error-report.html", error=error)


@app.route("/changePass/<title>", methods=['POST'])
def change(title):
	oldpass = request.form.get("oldpass")
	newpass = request.form.get("newpass")
	newpassc = request.form.get("newpassc")

	conn = sqlite3.connect("docs.sql")
	c = conn.cursor()
	stored_pwd = c.execute("SELECT pwhash FROM docsInfo WHERE title=:title", {
	    "title": title
	}).fetchall()
	stored_pwd = str(stored_pwd)
	stored_pwd = stored_pwd[3:]
	stored_pwd = stored_pwd[:-4]
	check_pwd = check_password_hash(stored_pwd, oldpass)
	#print(stored_pwd)
	#print(oldpass)
	#print(check_pwd)
	if check_pwd:
		if newpass == newpassc:
			newpwhash = generate_password_hash(newpass)
			c.execute(
			    "UPDATE docsInfo SET pwhash=:newpwhash WHERE title=:title", {
			        "title": title,
			        "newpwhash": newpwhash
			    })
			conn.commit()
			conn.close()
			return render_template("system/pwdchanged.html", title=title)
		else:
			error = "New passwords do not match!"
			return render_template("system/error-report.html", error=error)

	else:
		error = "Cannot change to new password because current password is incorrect."
		return render_template("system/error-report.html", error=error)


app.run(host='0.0.0.0', port=8080, debug=True)

# Original Creator: @Jonathan2018
