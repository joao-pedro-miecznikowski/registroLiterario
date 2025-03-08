from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///livros.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(200), nullable=False)
    data_inicio = db.Column(db.String(10))
    data_fim = db.Column(db.String(10))
    valor = db.Column(db.Float)
    nota = db.Column(db.Integer)
    capa = db.Column(db.String(200))
    descricao = db.Column(db.Text)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    livros = Livro.query.all()
    return render_template('index.html', livros=livros)

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        valor = float(request.form['valor'])
        nota = int(request.form['nota'])
        capa = request.files['capa']
        if capa:
            filename = secure_filename(capa.filename)
            capa.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
          filename = "default.jpg"
        descricao = request.form['descricao']
        livro = Livro(titulo=titulo, autor=autor, data_inicio=data_inicio, data_fim=data_fim, valor=valor, nota=nota, capa=filename, descricao=descricao)
        db.session.add(livro)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('adicionar.html')

@app.route('/detalhes/<int:id>')
def detalhes(id):
    livro = Livro.query.get_or_404(id)
    data_inicio = datetime.strptime(livro.data_inicio, '%Y-%m-%d').strftime('%d/%m/%Y') if livro.data_inicio else None
    data_fim = datetime.strptime(livro.data_fim, '%Y-%m-%d').strftime('%d/%m/%Y') if livro.data_fim else None
    return render_template('detalhes.html', livro=livro, data_inicio=data_inicio, data_fim=data_fim)

@app.route('/remover/<int:id>', methods=['POST'])
def remover(id):
    livro = Livro.query.get_or_404(id)
    db.session.delete(livro)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    livro = Livro.query.get_or_404(id)
    if request.method == 'POST':
        livro.titulo = request.form['titulo']
        livro.autor = request.form['autor']
        livro.data_inicio = request.form['data_inicio']
        livro.data_fim = request.form['data_fim']
        livro.valor = float(request.form['valor'])
        livro.nota = int(request.form['nota'])
        capa = request.files['capa']
        if capa:
            filename = secure_filename(capa.filename)
            capa.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            livro.capa = filename

        livro.descricao = request.form['descricao']

        db.session.commit()
        return redirect(url_for('detalhes', id=id))
    return render_template('editar.html', livro=livro)

if __name__ == '__main__':
    app.run(debug=True)