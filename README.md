# ⚡ Sistema de Recarga Inteligente de VEs

Um sistema full-stack completo para gestão e simulação de recarga de veículos elétricos na capital de São Paulo.

## 🚀 Funcionalidades

- **Autenticação:** Sistema de login e cadastro seguro com criptografia de senha.
- **Gestão de Créditos:** Adição de saldo fictício para pagamento de recargas.
- **Planos Customizados:** Escolha entre planos Básico (7kW), Intermediário (11kW) e Premium (22kW).
- **Mapa de Vagas:** Seleção de vagas em tempo real por região de SP.
- **Simulador de Recarga:** Monitoramento visual do progresso da recarga e energia consumida.
- **🤖 Assistente IA:** Chat integrado que consulta o banco de dados do usuário para responder sobre gastos e histórico (Sem alucinações!).

## 🛠️ Tecnologias Utilizadas

- **Frontend:** HTML5, CSS3 (Premium Dark Theme), JavaScript Vanilla.
- **Backend:** Python com Flask.
- **Banco de Dados:** MySQL.
- **Segurança:** JWT para sessões e Bcrypt para senhas.

## 📦 Como rodar o projeto

1. **Requisitos:** Python 3.10+ e MySQL instalado.
2. **Banco de Dados:** Importe o arquivo `/database/schema.sql` no seu MySQL Workbench.
3. **Configuração:** Renomeie o arquivo `.env.example` para `.env` e preencha com suas credenciais do banco.
4. **Instalação:** 
   ```bash
   pip install -r requirements.txt
   ```
5. **Execução:**
   ```bash
   python app.py
   ```
6. Acesse: `http://localhost:5000`

---
Desenvolvido para o Sprint de IA.
