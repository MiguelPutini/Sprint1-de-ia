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

## 🔍 o Porque das tecnlogias?
1. Frontend: HTML5, CSS3 e JavaScript Vanilla
Performance Extrema: Por não usarmos frameworks pesados (como React ou Angular), o site carrega instantaneamente. O "Vanilla JS" (JavaScript puro) garante que o navegador processe as interações sem camadas extras de complexidade.
Controle Estético (Premium Dark Theme): O uso de CSS3 puro permitiu a criação de um design exclusivo com efeitos de glassmorphism (efeito de vidro), gradientes dinâmicos e animações sutis que dão o aspecto "Premium" exigido, algo que seria mais difícil de customizar em bibliotecas de componentes prontos.
2. Backend: Python com Flask
Agilidade e Leveza: O Flask é um "micro-framework", o que significa que ele é minimalista e muito rápido. Ele nos deu a liberdade de estruturar o projeto exatamente como precisávamos, sem o "excesso de bagagem" de frameworks maiores.
Ecossistema Python: Python é a linguagem líder em integração de serviços modernos. Isso facilitou enormemente a conexão entre o banco de dados, o sistema de tokens e a comunicação com APIs externas.
3. Banco de Dados: MySQL
Confiabilidade Relacional: Como lidamos com dinheiro (créditos), usuários e transações, um banco de dados SQL é essencial. O MySQL garante a Integridade Referencial (ex: você não pode ter uma recarga de um usuário que não existe).
Padrão de Indústria: É um dos bancos mais robustos e utilizados no mundo, o que garante que o sistema suporte um grande volume de dados de histórico e reservas sem perder performance.
4. Segurança: JWT (JSON Web Tokens)
Autenticação Stateless: Diferente das sessões antigas que sobrecarregavam o servidor, o JWT armazena as informações de login de forma criptografada no próprio navegador do usuário.
Segurança em APIs: Cada requisição (como iniciar uma recarga) exige que o token seja enviado e validado, garantindo que um usuário nunca consiga interferir nos dados de outro.
5. Segurança: Bcrypt (Hash de Senhas)
Proteção contra Invasões: O Bcrypt é o padrão ouro para salvar senhas. Ele não apenas criptografa, mas aplica um "sal" (salt) aleatório e executa milhares de iterações de processamento.
Segurança Irreversível: Mesmo que alguém tivesse acesso ao banco de dados, seria virtualmente impossível descobrir as senhas reais dos usuários, protegendo-os contra ataques de força bruta.
Resumo da Arquitetura: Essa combinação cria um sistema robusto no backend e extremamente ágil no frontend, focado em uma experiência de usuário moderna e segura.

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

Miguel Putini 571624
Julia Junqueira Konishi 569506
João Victor Scheren de Freitas 568883
João Vitor Neves Fernandes Giadans 571608
