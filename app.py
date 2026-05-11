from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import bcrypt
import jwt
import datetime
import os
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

JWT_SECRET = os.getenv('JWT_SECRET', 'recarga_inteligente_jwt_secret_2024')
JWT_ALGORITHM = 'HS256'

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Miguel741414@'),
    'database': os.getenv('DB_NAME', 'recarga_inteligente'),
    'charset': 'utf8mb4'
}

LOCATIONS = {
    'Zona Sul': [
        {'id': 1, 'nome': 'Shopping Interlagos', 'endereco': 'Av. Interlagos, 2255'},
        {'id': 2, 'nome': 'Metrô Jabaquara', 'endereco': 'R. Maestro Cardim, 1100'},
        {'id': 3, 'nome': 'Supermercado Extra — Saúde', 'endereco': 'R. Domingos de Morais, 2564'},
    ],
    'Zona Leste': [
        {'id': 4, 'nome': 'Shopping Aricanduva', 'endereco': 'Av. Aricanduva, 5555'},
        {'id': 5, 'nome': 'Metrô Itaquera', 'endereco': 'Praça Pedro Braido, s/n'},
        {'id': 6, 'nome': 'Shopping Anália Franco', 'endereco': 'Av. Regente Feijó, 1739'},
    ],
    'Zona Oeste': [
        {'id': 7, 'nome': 'Shopping Iguatemi', 'endereco': 'Av. Brig. Faria Lima, 2232'},
        {'id': 8, 'nome': 'Metrô Faria Lima', 'endereco': 'Av. Brig. Faria Lima, s/n'},
        {'id': 9, 'nome': 'Shopping West Plaza', 'endereco': 'Av. Antártica, 381'},
    ],
    'Zona Norte': [
        {'id': 10, 'nome': 'Shopping Center Norte', 'endereco': 'Travessa Casalbuono, 120'},
        {'id': 11, 'nome': 'Metrô Santana', 'endereco': 'Av. Cruzeiro do Sul, 1775'},
        {'id': 12, 'nome': 'Shopping Pátio Paulista', 'endereco': 'R. Treze de Maio, 1947'},
    ],
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '').strip()
        if not token:
            return jsonify({'error': 'Token necessário'}), 401
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            current_user_id = data['user_id']
        except Exception:
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated


# ─── TEMPLATE ROUTES ────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/perfil')
def perfil():
    return render_template('perfil.html')

@app.route('/recarga')
def recarga():
    return render_template('recarga.html')

@app.route('/ia')
def ia():
    return render_template('ia.html')


# ─── AUTH ────────────────────────────────────────────────────────────────────────
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    nome = data.get('nome', '').strip()
    email = data.get('email', '').strip().lower()
    senha = data.get('senha', '')

    if not all([nome, email, senha]):
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
    if len(senha) < 6:
        return jsonify({'error': 'A senha deve ter ao menos 6 caracteres'}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT id FROM usuarios WHERE email = %s', (email,))
        if cursor.fetchone():
            return jsonify({'error': 'Este email já está cadastrado'}), 409

        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
        cursor.execute(
            'INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s, %s, %s)',
            (nome, email, senha_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.execute(
            'INSERT INTO transacoes (usuario_id, tipo, valor, descricao) VALUES (%s, %s, %s, %s)',
            (user_id, 'sistema', 0, 'Conta criada com sucesso')
        )
        conn.commit()

        token = jwt.encode(
            {'user_id': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
            JWT_SECRET, algorithm=JWT_ALGORITHM
        )
        return jsonify({'token': token, 'message': 'Cadastro realizado com sucesso!'})
    finally:
        cursor.close()
        conn.close()


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    email = data.get('email', '').strip().lower()
    senha = data.get('senha', '')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
        user = cursor.fetchone()
        if not user or not bcrypt.checkpw(senha.encode(), user['senha_hash'].encode()):
            return jsonify({'error': 'Email ou senha incorretos'}), 401

        token = jwt.encode(
            {'user_id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)},
            JWT_SECRET, algorithm=JWT_ALGORITHM
        )
        return jsonify({'token': token, 'message': 'Login realizado!'})
    finally:
        cursor.close()
        conn.close()


# ─── PERFIL ───────────────────────────────────────────────────────────────────
@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(uid):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, nome, email, credito, plano, potencia_max, data_cadastro FROM usuarios WHERE id = %s',
            (uid,)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        user['credito'] = float(user['credito'] or 0)
        user['potencia_max'] = float(user['potencia_max']) if user['potencia_max'] else None
        user['data_cadastro'] = user['data_cadastro'].strftime('%d/%m/%Y')
        return jsonify(user)
    finally:
        cursor.close()
        conn.close()


@app.route('/api/profile/plan', methods=['PUT'])
@token_required
def update_plan(uid):
    data = request.json or {}
    plano = data.get('plano', '')
    planos = {'Básico': 7, 'Intermediário': 11, 'Premium': 22}
    if plano not in planos:
        return jsonify({'error': 'Plano inválido'}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE usuarios SET plano = %s, potencia_max = %s WHERE id = %s',
            (plano, planos[plano], uid)
        )
        conn.commit()
        return jsonify({'message': f'Plano {plano} ativado com sucesso!'})
    finally:
        cursor.close()
        conn.close()


@app.route('/api/profile/credits', methods=['POST'])
@token_required
def add_credits(uid):
    data = request.json or {}
    try:
        valor = float(data.get('valor', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Valor inválido'}), 400
    if valor <= 0:
        return jsonify({'error': 'Valor deve ser maior que zero'}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('UPDATE usuarios SET credito = credito + %s WHERE id = %s', (valor, uid))
        cursor.execute(
            'INSERT INTO transacoes (usuario_id, tipo, valor, descricao) VALUES (%s, %s, %s, %s)',
            (uid, 'credito', valor, f'Adição de créditos — R$ {valor:.2f}')
        )
        conn.commit()
        cursor.execute('SELECT credito FROM usuarios WHERE id = %s', (uid,))
        row = cursor.fetchone()
        return jsonify({'message': f'R$ {valor:.2f} adicionados!', 'credito': float(row['credito'])})
    finally:
        cursor.close()
        conn.close()


@app.route('/api/transactions', methods=['GET'])
@token_required
def get_transactions(uid):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT * FROM transacoes WHERE usuario_id = %s ORDER BY data_hora DESC LIMIT 20', (uid,)
        )
        rows = cursor.fetchall()
        for r in rows:
            r['valor'] = float(r['valor'])
            r['data_hora'] = r['data_hora'].strftime('%d/%m/%Y %H:%M')
        return jsonify(rows)
    finally:
        cursor.close()
        conn.close()


# ─── LOCAIS & VAGAS ──────────────────────────────────────────────────────────
@app.route('/api/locations', methods=['GET'])
@token_required
def get_locations(uid):
    return jsonify(LOCATIONS)


@app.route('/api/spots', methods=['GET'])
@token_required
def get_spots(uid):
    import random
    spots = []
    for row in ['A', 'B']:
        for col in range(1, 4):
            weights = ['L', 'L', 'L', 'R', 'O']
            spots.append({
                'id': f'{row}{col}',
                'row': row,
                'col': col,
                'status': random.choice(weights)
            })
    return jsonify(spots)


# ─── RESERVAS ────────────────────────────────────────────────────────────────
@app.route('/api/reservations', methods=['POST'])
@token_required
def create_reservation(uid):
    data = request.json or {}
    regiao = data.get('regiao', '')
    local = data.get('local', '')
    vaga = data.get('vaga', '')
    try:
        tempo_min = int(data.get('tempo_min', 30))
    except (ValueError, TypeError):
        return jsonify({'error': 'Tempo inválido'}), 400

    valor_reserva = round(tempo_min * 0.5, 2)

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT credito FROM usuarios WHERE id = %s', (uid,))
        user = cursor.fetchone()
        if float(user['credito']) < valor_reserva:
            return jsonify({'error': f'Crédito insuficiente. Necessário R$ {valor_reserva:.2f}'}), 400

        cursor.execute('UPDATE usuarios SET credito = credito - %s WHERE id = %s', (valor_reserva, uid))
        cursor.execute(
            'INSERT INTO reservas (usuario_id, regiao, local, vaga, tempo_min, valor, status) VALUES (%s,%s,%s,%s,%s,%s,%s)',
            (uid, regiao, local, vaga, tempo_min, valor_reserva, 'ativa')
        )
        reserva_id = cursor.lastrowid
        cursor.execute(
            'INSERT INTO transacoes (usuario_id, tipo, valor, descricao) VALUES (%s,%s,%s,%s)',
            (uid, 'debito', valor_reserva, f'Reserva vaga {vaga} — {local}')
        )
        conn.commit()
        return jsonify({'message': 'Reserva confirmada!', 'reserva_id': reserva_id,
                        'valor': valor_reserva, 'tempo_min': tempo_min})
    finally:
        cursor.close()
        conn.close()


# ─── RECARGA ─────────────────────────────────────────────────────────────────
@app.route('/api/charging/start', methods=['POST'])
@token_required
def start_charging(uid):
    data = request.json or {}
    regiao = data.get('regiao', '')
    local = data.get('local', '')
    vaga = data.get('vaga', '')
    try:
        tempo_min = int(data.get('tempo_min', 30))
    except (ValueError, TypeError):
        return jsonify({'error': 'Tempo inválido'}), 400

    tensao, corrente, fator = 380, 32, 1.73
    pot_carregador = (tensao * corrente * fator) / 1000
    pot_carro = 22
    pot_rede = 20

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT plano, potencia_max, credito FROM usuarios WHERE id = %s', (uid,))
        user = cursor.fetchone()
        pot_plano = float(user['potencia_max']) if user['potencia_max'] else 7

        pot_real = min(pot_carregador, pot_carro, pot_rede, pot_plano)
        energia_kwh = round((pot_real * tempo_min) / 60, 3)
        custo = round(energia_kwh * 1.8, 2)

        if float(user['credito']) < custo:
            return jsonify({'error': f'Crédito insuficiente. Necessário R$ {custo:.2f}'}), 400

        cursor.execute('UPDATE usuarios SET credito = credito - %s WHERE id = %s', (custo, uid))
        cursor.execute(
            'INSERT INTO recargas (usuario_id, regiao, local, vaga, energia_kwh, custo, potencia_real, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
            (uid, regiao, local, vaga, energia_kwh, custo, round(pot_real, 2), 'concluida')
        )
        recarga_id = cursor.lastrowid
        cursor.execute(
            'INSERT INTO transacoes (usuario_id, tipo, valor, descricao) VALUES (%s,%s,%s,%s)',
            (uid, 'debito', custo, f'Recarga {energia_kwh} kWh — {local}')
        )
        conn.commit()
        cursor.execute('SELECT credito FROM usuarios WHERE id = %s', (uid,))
        novo = cursor.fetchone()

        return jsonify({
            'recarga_id': recarga_id,
            'potencia_real': round(pot_real, 2),
            'potencia_carregador': round(pot_carregador, 2),
            'potencia_rede': pot_rede,
            'potencia_plano': pot_plano,
            'energia_kwh': energia_kwh,
            'custo': custo,
            'tempo_min': tempo_min,
            'credito_restante': float(novo['credito']),
            'plano': user['plano']
        })
    finally:
        cursor.close()
        conn.close()


@app.route('/api/recharges', methods=['GET'])
@token_required
def get_recharges(uid):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT * FROM recargas WHERE usuario_id = %s ORDER BY data_hora DESC LIMIT 10', (uid,)
        )
        rows = cursor.fetchall()
        for r in rows:
            r['energia_kwh'] = float(r['energia_kwh'])
            r['custo'] = float(r['custo'])
            r['potencia_real'] = float(r['potencia_real'])
            r['data_hora'] = r['data_hora'].strftime('%d/%m/%Y %H:%M')
        return jsonify(rows)
    finally:
        cursor.close()
        conn.close()


# ─── IA CHAT ─────────────────────────────────────────────────────────────────
@app.route('/api/ai/chat', methods=['POST'])
@token_required
def ai_chat(uid):
    data = request.json or {}
    msg = data.get('message', '').lower().strip()

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT nome, credito, plano, potencia_max FROM usuarios WHERE id = %s', (uid,))
        user = cursor.fetchone()
        first_name = user['nome'].split()[0]
        response = None

        # Intenção: gasto total
        if any(w in msg for w in ['gastei', 'gasto total', 'quanto eu gastei', 'total em recargas']):
            cursor.execute('SELECT COALESCE(SUM(custo),0) as total FROM recargas WHERE usuario_id=%s', (uid,))
            total = float(cursor.fetchone()['total'])
            response = f"💰 Você gastou um total de **R$ {total:.2f}** em recargas, {first_name}!"

        # Intenção: número de recargas
        elif any(w in msg for w in ['quantas recargas', 'quantas vezes', 'numero de recargas', 'vezes que carreguei', 'sessões']):
            cursor.execute('SELECT COUNT(*) as total FROM recargas WHERE usuario_id=%s', (uid,))
            total = cursor.fetchone()['total']
            response = f"⚡ Você realizou **{total} recarga(s)** até agora, {first_name}!"

        # Intenção: saldo
        elif any(w in msg for w in ['saldo', 'crédito', 'credito', 'quanto tenho', 'meu saldo', 'meu crédito']):
            response = f"💳 Seu saldo atual é **R$ {float(user['credito']):.2f}**, {first_name}!"

        # Intenção: plano
        elif any(w in msg for w in ['plano', 'meu plano', 'qual plano']):
            plano = user['plano'] or 'Nenhum plano ativo'
            pot = f"{float(user['potencia_max']):.0f} kW" if user['potencia_max'] else '—'
            response = f"📋 Seu plano atual é **{plano}** (até {pot}), {first_name}!"

        # Intenção: histórico
        elif any(w in msg for w in ['histórico', 'historico', 'últimas recargas', 'ultimas recargas', 'minhas recargas']):
            cursor.execute(
                'SELECT local, regiao, energia_kwh, custo, data_hora FROM recargas WHERE usuario_id=%s ORDER BY data_hora DESC LIMIT 5',
                (uid,)
            )
            rows = cursor.fetchall()
            if not rows:
                response = f"📊 Você ainda não realizou nenhuma recarga, {first_name}."
            else:
                linhas = [f"📊 Suas últimas {len(rows)} recarga(s), {first_name}:\n"]
                for r in rows:
                    d = r['data_hora'].strftime('%d/%m/%Y %H:%M')
                    linhas.append(f"• {d} — {r['local']} ({r['regiao']}) — {float(r['energia_kwh']):.2f} kWh — R$ {float(r['custo']):.2f}")
                response = '\n'.join(linhas)

        # Intenção: última recarga
        elif any(w in msg for w in ['última recarga', 'ultima recarga', 'última vez', 'ultima vez']):
            cursor.execute(
                'SELECT local, regiao, vaga, energia_kwh, custo, potencia_real, data_hora FROM recargas WHERE usuario_id=%s ORDER BY data_hora DESC LIMIT 1',
                (uid,)
            )
            r = cursor.fetchone()
            if not r:
                response = f"Você ainda não realizou nenhuma recarga, {first_name}."
            else:
                d = r['data_hora'].strftime('%d/%m/%Y %H:%M')
                response = (f"⚡ Última recarga em **{d}**:\n"
                            f"• Local: {r['local']} ({r['regiao']})\n"
                            f"• Vaga: {r['vaga']}\n"
                            f"• Energia: {float(r['energia_kwh']):.2f} kWh\n"
                            f"• Potência: {float(r['potencia_real']):.2f} kW\n"
                            f"• Custo: R$ {float(r['custo']):.2f}")

        # Intenção: energia total carregada
        elif any(w in msg for w in ['energia total', 'total de energia', 'kwh total', 'total kwh', 'energia carregada']):
            cursor.execute('SELECT COALESCE(SUM(energia_kwh),0) as total FROM recargas WHERE usuario_id=%s', (uid,))
            total = float(cursor.fetchone()['total'])
            response = f"⚡ Você carregou um total de **{total:.2f} kWh**, {first_name}!"

        # Intenção: reservas
        elif any(w in msg for w in ['reserva', 'reservas', 'minhas reservas']):
            cursor.execute(
                'SELECT local, regiao, vaga, tempo_min, valor, status, data_hora FROM reservas WHERE usuario_id=%s ORDER BY data_hora DESC LIMIT 5',
                (uid,)
            )
            rows = cursor.fetchall()
            if not rows:
                response = f"📅 Você ainda não realizou nenhuma reserva, {first_name}."
            else:
                linhas = [f"📅 Suas últimas reservas, {first_name}:\n"]
                for r in rows:
                    d = r['data_hora'].strftime('%d/%m/%Y %H:%M')
                    linhas.append(f"• {d} — {r['local']} — Vaga {r['vaga']} — R$ {float(r['valor']):.2f} ({r['status']})")
                response = '\n'.join(linhas)

        # Intenção: resumo / relatório
        elif any(w in msg for w in ['resumo', 'relatório', 'relatorio', 'meu resumo', 'dashboard']):
            cursor.execute('SELECT COALESCE(SUM(custo),0) as gasto, COALESCE(SUM(energia_kwh),0) as energia, COUNT(*) as qtd FROM recargas WHERE usuario_id=%s', (uid,))
            stats = cursor.fetchone()
            response = (f"📊 Resumo da sua conta, {first_name}:\n"
                        f"• Plano: {user['plano'] or 'Nenhum'}\n"
                        f"• Saldo atual: R$ {float(user['credito']):.2f}\n"
                        f"• Total de recargas: {stats['qtd']}\n"
                        f"• Energia total: {float(stats['energia']):.2f} kWh\n"
                        f"• Gasto total: R$ {float(stats['gasto']):.2f}")

        # Intenção: saudação
        elif any(w in msg for w in ['olá', 'ola', 'oi', 'hello', 'hey', 'bom dia', 'boa tarde', 'boa noite', 'tudo bem']):
            response = (f"👋 Olá, {first_name}! Sou o assistente do Sistema de Recarga Inteligente.\n"
                        f"Posso te ajudar com informações sobre seus gastos, recargas, saldo e histórico.\n"
                        f"Digite **ajuda** para ver o que posso responder!")

        # Intenção: ajuda
        elif any(w in msg for w in ['ajuda', 'help', 'comandos', 'o que você sabe', 'o que voce sabe']):
            response = (f"🤖 Aqui está o que posso responder, {first_name}:\n\n"
                        f"• *Quanto eu já gastei?* — Gasto total em recargas\n"
                        f"• *Quantas recargas fiz?* — Número de sessões\n"
                        f"• *Qual meu saldo?* — Crédito disponível\n"
                        f"• *Qual meu plano?* — Plano e potência\n"
                        f"• *Histórico de recargas* — Últimas 5 recargas\n"
                        f"• *Última recarga* — Detalhes da última sessão\n"
                        f"• *Energia total carregada* — kWh acumulados\n"
                        f"• *Minhas reservas* — Histórico de reservas\n"
                        f"• *Resumo* — Relatório geral da conta")

        # Intenção não reconhecida
        else:
            response = (f"🤔 Não entendi sua pergunta, {first_name}. "
                        f"Só consigo responder com dados reais da sua conta.\n"
                        f"Digite **ajuda** para ver o que posso responder!")

        return jsonify({'response': response})
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"\n=== EV CHARGE SP ===")
    print(f"Servidor rodando em http://localhost:{port}")
    print(f"Banco: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    print(f"====================\n")
    app.run(debug=True, port=port)
