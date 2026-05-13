# ⚡ Sistema de Recarga Inteligente de VEs

Um sistema full-stack completo para gestão e simulação de recarga de veículos elétricos na capital de São Paulo.

## 🚀 Funcionalidades

- **Autenticação:** Sistema de login e cadastro seguro com criptografia de senha.
- **Gestão de Créditos:** Adição de saldo fictício para pagamento de recargas.
- **Planos Customizados:** Escolha entre planos Básico (7kW), Intermediário (11kW) e Premium (22kW).
- **Mapa de Vagas:** Seleção de vagas em tempo real por região de SP.
- **Simulador de Recarga:** Monitoramento visual do progresso da recarga e energia consumida.
## 🤖 Assistente IA (GPT-4o-mini)

O sistema agora conta com uma inteligência artificial real baseada no modelo **GPT-4o-mini** da OpenAI.

### Por que GPT-4o-mini?
- **Eficiência:** Oferece um equilíbrio perfeito entre inteligência e velocidade de resposta.
- **Custo-benefício:** É significativamente mais barato que o GPT-4o padrão, mantendo alta qualidade para tarefas de assistência.
- **Contexto:** Capaz de processar os dados em tempo real da sua conta para fornecer respostas precisas e personalizadas.

### Escopo e Contexto
O assistente foi projetado especificamente para usuários de veículos elétricos na cidade de São Paulo. Ele tem acesso (via prompt injection seguro) aos seus dados de:
- Saldo e transações.
- Histórico de recargas e locais frequentados.
- Detalhes do seu plano atual.
- Reservas de vagas.

*Nota: O assistente está instruído a não responder sobre assuntos fora do ecopo de recarga e gestão de VEs.*

## ⚙️ Configuração da API
Para que a IA funcione, você precisa:
1. Obter uma chave de API na [OpenAI Platform](https://platform.openai.com/).
2. No arquivo `.env`, adicione a linha:
   ```env
   OPENAI_API_KEY=sua_chave_aqui
   ```

## 🛠️ Tecnologias Utilizadas

- **Frontend:** HTML5, CSS3 (Premium Dark Theme), JavaScript Vanilla.
- **Backend:** Python com Flask.
- **IA:** OpenAI GPT-4o-mini API.
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
