# 00A - Glossário do Projeto

**Projeto:** MotorControl  
**Versão:** 1.0  
**Data:** 01 de Julho de 2026  

## 1. Objetivo
O objetivo deste documento é estabelecer uma linguagem ubíqua (comum a todos) entre a equipe de desenvolvimento de software e os especialistas do negócio (donos de oficina e mecânicos). Isso evita ambiguidades onde termos técnicos do negócio possam ser interpretados erroneamente pelos desenvolvedores.

## 2. Escopo
Este glossário cobre termos técnicos do domínio de manutenção de motores elétricos e termos da arquitetura de software que serão utilizados em todas as etapas de modelagem, código e documentação.

## 3. Conteúdo Principal

### 3.1. Termos do Domínio (Negócio)

| Termo | Definição | Exemplo de Uso no Sistema |
| :--- | :--- | :--- |
| **Ordem de Serviço (OS)** | Documento que registra a abertura, execução e encerramento de uma manutenção. É a entidade central do sistema. | Uma OS possui status: "Em Orçamento", "Aprovada", "Em Manutenção", "Pronta", "Entregue". |
| **Estator** | A parte fixa do motor elétrico que contém as bobinas de fio de cobre onde o campo magnético é gerado. | O mecânico reportou que o "estator está em curto". |
| **Rotor** | A parte giratória do motor que se move devido ao campo magnético do estator. | Substituição de rolamentos do rotor. |
| **Rebobinamento** | Processo de retirar a fiação queimada do estator, isolar as ranhuras e inserir uma nova fiação de cobre. | O serviço principal desta OS será o "rebobinamento completo". |
| **Placa de Identificação** | Placa metálica presa ao motor com seus dados nominais (Potência, Tensão, Corrente, RPM, Esquema de Ligação). | Os dados da placa de identificação devem ser digitados no cadastro do motor. |
| **Fechamento** | A configuração de conexão dos terminais do motor (ex: Estrela ou Triângulo) para se adequar à tensão da rede elétrica. | Registrar se o motor foi testado com fechamento em 220V ou 380V. |

### 3.2. Termos Técnicos (Software)

| Termo | Definição | Contexto no MotorControl |
| :--- | :--- | :--- |
| **UI Reativa** | Interface que se atualiza automaticamente quando os dados subjacentes mudam, sem recarga total da tela. | O framework Flet gerencia o estado da tela de forma reativa. |
| **Entidade / Model** | Classe que representa uma tabela do banco de dados no código orientada a objetos. | A classe `Motor` será um modelo do SQLModel. |
| **Migrations** | Histórico de alterações estruturais do banco de dados (criar tabelas, adicionar colunas) controlado por código. | Usado se precisarmos alterar o banco sem perder os dados do cliente. |
| **Stand-alone Executable** | Um arquivo `.exe` que roda de forma independente, contendo o interpretador Python e as bibliotecas embutidas. | Gerado pelo PyInstaller para que o cliente não precise instalar o Python na máquina dele. |

## 4. Boas Práticas
* **Linguagem Ubíqua:** Sempre utilize os termos deste glossário no código. Por exemplo, use a palavra `Rewinding` ou `Rebobinamento` em vez de termos genéricos como `ServiceTypeX`.
* **Consistência:** Telas do sistema devem usar exatamente os mesmos termos que o banco de dados e os relatórios usam.

## 5. Observações
Este documento impede o fenômeno conhecido como "telefone sem fio", onde o desenvolvedor chama de "Produto" o que o cliente chama de "Peça", gerando confusão no código e na interface.

## 6. Possíveis Melhorias Futuras
* Adicionar imagens esquemáticas de componentes do motor caso novos desenvolvedores entrem na equipe sem nenhum conhecimento de elétrica.

## 7. Dependências com Outros Documentos
* **Depende de:** `00 - Project Charter` (para contexto).
* **É pré-requisito para:** `02 - Product Requirements Document (PRD)` e `05 - Modelagem do Banco de Dados` (onde as tabelas usarão estes nomes).
