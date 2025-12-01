Com certeza\! Já que você optou por rodar direto pelo código fonte (o que é ótimo para desenvolvimento e aprendizado), o README deve focar em como configurar o ambiente Python e rodar o script.

Aqui está o novo `README.md` limpo e atualizado para o seu repositório:

-----

# Paladin vs Dracula - Final Battle ⚔️🧛‍♂️

Um jogo de aventura e ação estilo *top-down* desenvolvido em Python usando a biblioteca **Pygame Zero**. Enfrente hordas de vampiros, desvie de obstáculos e derrote o Conde Drácula\!

## 📋 Pré-requisitos

Para rodar este jogo, você precisa ter instalado no seu computador:

  * **Python 3.11** (ou superior).
  * **Git** (para clonar o repositório).

## 🚀 Instalação e Configuração

Siga os passos abaixo para configurar o ambiente e rodar o jogo:

### 1\. Clonar o Repositório

Abra o terminal e clone os arquivos do projeto:

```bash
git clone https://github.com/SEU_USUARIO/paladin-vs-dracula.git
cd paladin-vs-dracula
```

### 2\. Criar e Ativar o Ambiente Virtual

É recomendado usar um ambiente virtual (`venv`) para não misturar as bibliotecas do jogo com as do seu sistema.

**No Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

**No Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3\. Instalar Dependências

Com o ambiente virtual ativado, instale a biblioteca **Pygame Zero**:

```powershell
pip install pgzero
```

*(Ou, se houver um arquivo requirements.txt: `pip install -r requirements.txt`)*

-----

## 🎮 Como Jogar

1.  Certifique-se de que o ambiente virtual (`venv`) está ativado.
2.  Execute o comando abaixo para iniciar o jogo:

<!-- end list -->

```powershell
python -X utf8 game.py
```

*(Nota: O `-X utf8` garante que caracteres especiais e acentos não causem erros no Windows).*

### Controles

| Tecla / Ação | Função |
| :--- | :--- |
| **Setas Direcionais** | Mover o Herói |
| **Barra de Espaço** | Atacar |
| **ESC** | Pausar o Jogo |
| **Mouse (Clique)** | Interagir com os botões do Menu |

-----

## 📂 Estrutura do Projeto

  * **`game.py`**: Código fonte principal do jogo.
  * **`images/`**: Contém todos os sprites (Herói, Drácula, Vampiros e Cenário).
  * **`music/`**: Trilhas sonoras (Menu, Jogo e Boss).
  * **`sounds/`**: Efeitos sonoros (Click, Ataque).

-----

## 🛠️ Tecnologias Utilizadas

  * **Linguagem:** Python
  * **Engine:** Pygame Zero (pgzero)
  * **Bibliotecas:** `math`, `random`, `pygame.Rect`

-----

**Desenvolvido por Pedro** 🛡️
