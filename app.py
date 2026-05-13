from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import bcrypt
import jwt
import datetime
import os
from openai import OpenAI, APIError, AuthenticationError
from functools import wraps
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)
CORS(app)

JWT_SECRET = os.getenv('JWT_SECRET', 'recarga_inteligente_jwt_secret_2024')
JWT_ALGORITHM = 'HS256'

key = os.getenv('OPENAI_API_KEY')
if not key:
    print("⚠️ AVISO: OPENAI_API_KEY não encontrada no .env")
else:
    # Mostra apenas o início e fim da chave para confirmar que foi carregada
    print(f"✅ OpenAI API Key carregada: {key[:5]}...{key[-4:] if len(key) > 4 else ''}")

client = OpenAI(api_key=key)

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
    user_msg = data.get('message', '').strip()

    if not user_msg:
        return jsonify({'error': 'Mensagem vazia'}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Buscar Dados do Usuário
        cursor.execute('SELECT nome, email, credito, plano, potencia_max, data_cadastro FROM usuarios WHERE id = %s', (uid,))
        user = cursor.fetchone()
        
        # 2. Buscar Estatísticas Gerais
        cursor.execute('SELECT COALESCE(SUM(custo),0) as gasto_total, COALESCE(SUM(energia_kwh),0) as energia_total, COUNT(*) as qtd_recargas FROM recargas WHERE usuario_id=%s', (uid,))
        stats = cursor.fetchone()

        # 3. Buscar Últimas Recargas
        cursor.execute('SELECT local, regiao, vaga, energia_kwh, custo, potencia_real, data_hora FROM recargas WHERE usuario_id=%s ORDER BY data_hora DESC LIMIT 5', (uid,))
        history = cursor.fetchall()
        for r in history:
            r['data_hora'] = r['data_hora'].strftime('%d/%m/%Y %H:%M')

        # 4. Buscar Últimas Reservas
        cursor.execute('SELECT local, vaga, tempo_min, valor, status, data_hora FROM reservas WHERE usuario_id=%s ORDER BY data_hora DESC LIMIT 3', (uid,))
        reservations = cursor.fetchall()
        for res in reservations:
            res['data_hora'] = res['data_hora'].strftime('%d/%m/%Y %H:%M')

        # Construção do Contexto (Prompt System)
        system_context = f"""
Você é o assistente virtual do "Sistema de Recarga Inteligente de VEs". 
Seu objetivo é ajudar o usuário com dúvidas sobre o sistema, seus gastos, histórico e informações sobre recarga de veículos elétricos.

DIRETRIZES DE RESPOSTA:
1. Seja educado, profissional e use o nome do usuário.
2. Use APENAS os dados fornecidos abaixo para responder sobre a conta do usuário. 
3. Se o usuário perguntar algo que não está nos dados (ex: "quem ganhou o jogo ontem?"), responda educadamente que você só tem acesso a informações do sistema de recargas.
4. Use Markdown para formatar a resposta (negrito, listas, etc.).
5. O escopo do site é a gestão de recargas de veículos elétricos na cidade de São Paulo.

DADOS DO USUÁRIO ATUAL ({user['nome']}):
- Saldo Atual: R$ {float(user['credito']):.2f}
- Plano: {user['plano'] or 'Nenhum'}
- Potência Máxima do Plano: {float(user['potencia_max']) if user['potencia_max'] else '7'} kW
- Data de Cadastro: {user['data_cadastro'].strftime('%d/%m/%Y')}
- Total Gasto em Recargas: R$ {float(stats['gasto_total']):.2f}
- Energia Total Consumida: {float(stats['energia_total']):.2f} kWh
- Total de Sessões de Recarga: {stats['qtd_recargas']}

HISTÓRICO RECENTE DE RECARGAS:
{history if history else 'Nenhuma recarga realizada ainda.'}

RESERVAS RECENTES:
{reservations if reservations else 'Nenhuma reserva realizada ainda.'}

INFORMAÇÕES DO SISTEMA:
- Locais de recarga disponíveis em: Zona Sul, Leste, Oeste e Norte de SP.
- Preço fixo por kWh: R$ 1,80.
- Custo de reserva de vaga: R$ 0,50 por minuto.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_context},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=500
        )

        ai_response = response.choices[0].message.content
        return jsonify({'response': ai_response})

    except AuthenticationError:
        msg = "⚠️ **Erro de Configuração:** A chave da API OpenAI não foi encontrada ou é inválida. Por favor, adicione uma chave válida no arquivo `.env` para usar o assistente."
        print(msg)
        return jsonify({'response': msg})
    except APIError as e:
        msg = f"🔌 **Erro na API:** Tive um problema de conexão com a OpenAI. Detalhes: {e}"
        print(msg)
        return jsonify({'response': msg})
    except Exception as e:
        msg = "🤯 **Erro Inesperado:** Desculpe, tive um problema interno ao processar sua pergunta."
        print(f"{msg} {e}")
        return jsonify({'response': msg})
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
