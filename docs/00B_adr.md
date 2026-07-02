# 00B - Architecture Decision Records (ADR)

**Projeto:** MotorControl  
**Versão:** 1.0  
**Data:** 01 de Julho de 2026  

## 1. Objetivo
O objetivo deste documento é registrar formalmente as decisões arquiteturais de alto impacto tomadas para o projeto MotorControl. Cada registro (ADR) contextualiza o problema, avalia as alternativas, justifica a escolha final e mapeia as consequências técnicas da decisão.

## 2. Escopo
Este documento cobre a definição da stack tecnológica base (Python, Flet, SQLite, SQLModel e PyInstaller), bem como os pilares de design de software (Arquitetura em Camadas, Princípios SOLID/KISS).

---

## 3. Conteúdo Principal (Registros de Decisão)

### ADR 001: Escolha do Framework de Interface Gráfica (UI)
* **Status:** Aprovado
* **Contexto:** O sistema precisa ser Desktop, rodar offline em computadores potencialmente antigos de oficina e possuir uma interface moderna, amigável e de rápido desenvolvimento.
* **Alternativas Consideradas:** 1. *Tkinter:* Nativo do Python, muito leve, mas esteticamente defasado e complexo para criar interfaces modernas/responsivas.
  2. *PyQt / PySide:* Extremamente robusto, mas possui uma curva de aprendizado íngreme e licenças comerciais complexas (LGPL/GPL).
  3. *Electron (JS):* Interfaces lindas, mas consome muita memória RAM e exige uma stack híbrida (NodeJS + Python de fundo).
* **Decisão:** **Flet (Flutter para Python)**.
* **Justificativa:** O Flet permite construir aplicações baseadas no motor do Flutter usando apenas código Python. Entrega uma UI moderna, reativa, com excelente performance e tempo de desenvolvimento reduzido, eliminando a necessidade de gerenciar HTML/CSS/JS.
* **Consequências:** Dependência de um framework em crescimento. O design fica atrelado aos componentes prontos do Flutter/Flet (o que atende perfeitamente ao princípio **KISS**).

### ADR 002: Escolha do Mecanismo de Armazenamento de Dados
* **Status:** Aprovado
* **Contexto:** O sistema funcionará de forma 100% offline em uma única máquina por oficina. Não há infraestrutura de rede ou servidor local dedicada.
* **Alternativas Consideradas:**
  1. *PostgreSQL / MySQL:* Excelentes bancos relacionais, mas exigem a instalação e configuração de um serviço de servidor na máquina do cliente, aumentando o suporte técnico e o risco de falhas no ambiente da oficina.
  2. *Arquivos JSON/CSV locais:* Simples, mas não garantem integridade referencial, transações (ACID) e perdem performance drasticamente com o crescimento dos dados.
* **Decisão:** **SQLite**.
* **Justificativa:** É um banco de dados relacional embutido (serverless). O banco é apenas um arquivo local no disco. Não requer instalação, configuração ou manutenção de servidores. Suporta transações ACID e é extremamente rápido para o volume de dados de uma oficina.
* **Consequências:** Limitação para acessos simultâneos concorrentes (gravações concorrentes bloqueiam o banco), o que não é um problema para o escopo inicial de um sistema Desktop de usuário único.

### ADR 003: Escolha da Camada de Abstração de Banco de Dados (ORM)
* **Status:** Aprovado
* **Contexto:** Precisamos de uma forma produtiva, segura (contra SQL Injection) e tipada para interagir com o SQLite, mantendo o código limpo e de fácil manutenção.
* **Alternativas Consideradas:**
  1. *SQLite3 nativo (Raw SQL):* Escrever queries SQL na mão dentro de strings Python. Alta performance, mas difícil manutenção, sem tipagem e propenso a erros de sintaxe em tempo de execução.
  2. *SQLAlchemy Puro:* O ORM mais robusto do ecossistema Python. No entanto, exige duplicar definições de tipos se quisermos validação de dados rigorosa.
* **Decisão:** **SQLModel**.
* **Justificativa:** Desenvolvido pelo mesmo criador do FastAPI, o SQLModel une o poder do SQLAlchemy com a validação de tipos do Pydantic. Ele elimina a duplicidade de código: a mesma classe que define a tabela no banco valida os dados que entram na UI (**DRY** - Don't Repeat Yourself). Oferece suporte total a autocompletar nas IDEs.
* **Consequências:** O projeto fica acoplado à biblioteca SQLModel, mas como ela é construída sobre o SQLAlchemy, o risco de descontinuação é mitigado pela compatibilidade direta com a engine clássica.

### ADR 004: Estratégia de Distribuição e Implantação (Deployment)
* **Status:** Aprovado
* **Contexto:** O dono da oficina não deve precisar instalar o interpretador Python, pip ou dependências para rodar o software. A instalação deve ser um clique único.
* **Decisão:** **PyInstaller**.
* **Justificativa:** Transforma o código Python e todas as suas dependências (incluindo o runtime do Flet) em um único arquivo executável executável (`.exe` no Windows).
* **Consequências:** O tamanho do executável final será consideravelmente maior (frequentemente acima de 60MB) porque inclui todo o motor gráfico e o interpretador Python embutido.

---

## 4. Boas Práticas
* **Imutabilidade:** Uma ADR aprovada e implementada não deve ser editada. Se mudarmos de ideia no futuro, criamos uma nova ADR (ex: *ADR 005: Migração para PostgreSQL*) que revoga ou modifica a ADR anterior.
* **Foco no 'Porquê':** O foco principal deve ser sempre a justificativa e os trade-offs (perdas e ganhos).

## 5. Observações
Estas escolhas foram guiadas pelo princípio **YAGNI**. Não escolhemos arquiteturas complexas de microsserviços ou bancos em nuvem porque a necessidade real e imediata é resolver o problema de uma oficina offline de forma robusta e barata.

## 6. Possíveis Melhorias Futuras
* Criação de uma ADR para definir a estratégia de Backup automatizado do arquivo `.db` do SQLite.

## 7. Dependências com Outros Documentos
* **Depende de:** `00 - Project Charter` (que dita a stack base).
* **É pré-requisito para:** `04 - Arquitetura do Sistema` e `05 - Modelagem do Banco de Dados`.
