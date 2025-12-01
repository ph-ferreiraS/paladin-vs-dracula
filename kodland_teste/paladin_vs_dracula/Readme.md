# Manual de Compilação: Paladin vs Dracula

Este guia explica como transformar o código fonte Python (`game.py`) em um executável Windows (`.exe`) independente, que pode ser jogado em computadores sem Python instalado.

## Pré-requisitos

1.  **Python 3.11** instalado e adicionado ao PATH.
2.  Ambiente virtual (`venv`) ativado no terminal.
3.  Biblioteca **PyInstaller** instalada:
    ```powershell
    pip install pyinstaller
    ```

-----

## Passo 1: Preparar o Arquivo de Lançamento

O Pygame Zero não pode ser compilado diretamente. É necessário criar um pequeno script "lançador" para inicializar o motor corretamente dentro do executável.

1.  Crie um arquivo chamado **`run_game.py`** na mesma pasta do `game.py`.
2.  Cole o seguinte código nele:

<!-- end list -->

```python
import os
import sys
import pgzero.runner
import game  # Importa o seu arquivo game.py

# Garante que o diretório de trabalho é onde o executável está
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

# Inicia o jogo manualmente passando o módulo 'game'
pgzero.runner.PGZeroGame(game).run()
```

3.  **IMPORTANTE:** Abra o seu arquivo **`game.py`** e **remova** (ou comente) a última linha:

    ```python
    # pgzrun.go()  <-- COMENTE ESTA LINHA NO GAME.PY
    ```

4.  Ainda no **`game.py`**, adicione esta importação manual no topo (linha 5) para garantir que o executável encontre os controles:

    ```python
    from pgzero.builtins import keyboard, screen, music, sounds, images, Actor, clock
    ```

-----

## Passo 2: Compilar o Jogo

Abra o terminal na pasta do projeto e execute o comando abaixo (tudo em uma linha só):

```powershell
pyinstaller --noconfirm --onedir --windowed --name "PaladinVsDracula" --collect-all pgzero --add-data "images;images" --add-data "music;music" --add-data "sounds;sounds" run_game.py
```

**Explicação dos parâmetros:**

  * `--onedir`: Cria uma pasta com os arquivos (mais fácil de debugar).
  * `--windowed`: Oculta a tela preta do terminal ao abrir o jogo.
  * `--collect-all pgzero`: Copia os arquivos internos essenciais do Pygame Zero.
  * `--add-data`: Copia suas pastas de mídia automaticamente.

-----

## Passo 3: Organização Final (Crucial)

Após a compilação terminar:

1.  Vá até a nova pasta **`dist/PaladinVsDracula`**.
2.  Verifique se as pastas **`images`**, **`music`** e **`sounds`** estão presentes **ao lado** do arquivo `PaladinVsDracula.exe`.
3.  **Se não estiverem:** Copie-as manualmente da sua pasta de projeto original e cole dentro de `dist/PaladinVsDracula`.

A estrutura final da pasta deve ser:

```text
PaladinVsDracula/
├── _internal/
├── images/       <-- (Copie se faltar)
├── music/        <-- (Copie se faltar)
├── sounds/       <-- (Copie se faltar)
└── PaladinVsDracula.exe
```

## Passo 4: Jogar

Basta clicar duas vezes em **`PaladinVsDracula.exe`** para iniciar o jogo\!

-----

### Solução de Problemas Comuns

  * **O jogo fecha instantaneamente:**

      * Verifique se as pastas de mídia (`images`, `sounds`) estão ao lado do `.exe`.
      * Tente compilar sem `--windowed` (use `--console`) para ver a mensagem de erro.

  * **Erro `NameError: name 'keyboard' is not defined`:**

      * Você esqueceu de adicionar a linha `from pgzero.builtins...` no topo do `game.py`.

  * **Música não toca:**

      * Verifique se os arquivos `.ogg` estão na pasta `music` e se os nomes batem com o código (`menu.ogg`, `game.ogg`).