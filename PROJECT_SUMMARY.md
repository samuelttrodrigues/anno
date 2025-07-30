# Resumo do Projeto: Anno - Aplicativo de Anotações

Este documento resume o estado atual e as funcionalidades do aplicativo "Anno", desenvolvido para Linux Mint XFCE.

## 1. Objetivo do Aplicativo

Um aplicativo leve para anotações que permite:
*   Capturar anotações rapidamente via terminal (usando `nano`).
*   Visualizar anotações em uma interface gráfica (GUI) organizada.
*   Visualizar anotações diretamente no terminal.
*   Manter as anotações persistentes e organizadas por data.

## 2. Estrutura de Arquivos e Localização

*   **Diretório Raiz do Projeto:** `/home/sam/Projects/Annotation/`
*   **Script Principal (Shell):** `/home/sam/Projects/Annotation/anno` (copiado para `/usr/local/bin/` para uso global)
*   **Módulos Python do App:** `/home/sam/Projects/Annotation/anno_app/`
    *   `anno_viewer.py`: Código da interface gráfica (GUI).
    *   `anno_terminal_viewer.py`: Código do visualizador de terminal.
*   **Arquivo de Dados:** `~/.local/share/annotations.json` (armazena todas as anotações).
*   **Arquivo de Configurações:** `~/.config/anno/settings.json` (armazena o tema selecionado e a última nota aberta).
*   **Pacote de Instalação:** `anno_deb_build.deb` (localizado em `/home/sam/Projects/Annotation/`).

## 3. Comandos Principais

Após a instalação do pacote `.deb` (ou cópia manual do script `anno` para `/usr/local/bin/`):

*   `anno`: Abre o editor `nano` para criar uma nova anotação.
    *   **Como usar `nano`:** `Ctrl+X` para sair, `Y` para salvar, `Enter` para confirmar o nome do arquivo.
*   `anno -o`: Abre a interface gráfica (GUI) do aplicativo.
*   `anno -t`: Exibe todas as anotações diretamente no terminal.

## 4. Funcionalidades da Interface Gráfica (`anno -o`)

*   **Layout:** Duas colunas (`PanedWindow` redimensionável).
    *   **Coluna Esquerda:** Visualização em árvore (`ttk.Treeview`) organizada por Ano > Mês > Anotação (Dia, Hora).
    *   **Coluna Direita:** Área de texto para exibir o conteúdo da anotação selecionada.
*   **Edição de Anotações:**
    *   Botão "Edit" para entrar no modo de edição.
    *   Botões "Save" e "Cancel" para gerenciar as alterações.
    *   **Estilização com Tags:** Suporte a tags pseudo-HTML para formatação visual:
        *   `<h>texto</h>`: Texto destacado (highlight).
        *   `<i>texto</i>`: Texto importante (negrito, cor diferente).
        *   `<c>texto</c>`: Texto de código (fonte monoespaçada, fundo diferente).
    *   Barra de ajuda com as tags visível no modo de edição.
*   **Temas Visuais:** Seletor de temas (dropdown) com as seguintes opções:
    *   Pastel (padrão)
    *   Dark
    *   Light
    *   Nord
    *   Solarized Light
    *   Gruvbox
*   **Persistência:**
    *   O tema selecionado é salvo e carregado automaticamente na próxima inicialização.
    *   A última anotação visualizada é salva e reaberta automaticamente na próxima inicialização.

## 5. Funcionalidades do Visualizador de Terminal (`anno -t`)

*   Exibe as anotações de forma hierárquica (Ano > Mês > Dia > Anotação).
*   Aplica cores ANSI e estilos (negrito) para as tags `<h>`, `<i>` e `<c>`, tornando a visualização no terminal organizada e legível.

## 6. Dependências

Para que o aplicativo funcione, as seguintes dependências devem estar instaladas no sistema:

*   `python3`
*   `python3-tk` (para a GUI)
*   `jq` (para processamento JSON no script `anno`)

## 7. Instalação em Outras Máquinas Linux Mint/Ubuntu

Um pacote Debian (`.deb`) foi gerado para facilitar a instalação:

*   **Localização do Pacote:** `/home/sam/Projects/Annotation/anno_deb_build.deb`
*   **Comando de Instalação:**
    ```bash
    sudo dpkg -i /caminho/para/anno_deb_build.deb
    sudo apt-get install -f  # Para resolver dependências, se necessário
    ```

## 8. Próximos Passos (se desejar continuar)

*   **Novas Funcionalidades:** Adicionar mais tags de estilização, funcionalidade de busca, exportação de anotações, etc.
*   **Refinamento Visual:** Embora o Tkinter tenha limitações, pequenos ajustes de padding, fontes e cores podem sempre ser explorados.
*   **Otimização:** Para sistemas extremamente limitados, pode-se investigar otimizações de código Python ou considerar linguagens de menor nível (C/C++), embora com maior complexidade de desenvolvimento.

Este resumo deve ser suficiente para você ou qualquer outro desenvolvedor entender o projeto e continuar trabalhando nele.
