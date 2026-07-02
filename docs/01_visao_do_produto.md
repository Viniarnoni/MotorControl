# 01 - Visão do Produto

**Projeto:** MotorControl  
**Versão:** 1.0  
**Data:** 01 de Julho de 2026  

## 1. Objetivo
O objetivo deste documento é definir o direcionamento estratégico, a proposta de valor e o posicionamento de mercado do MotorControl. Ele alinha a visão técnica com os objetivos de negócio, garantindo que o software resolva problemas reais dos usuários finais de forma eficiente.

## 2. Escopo
Este documento detalha o perfil dos usuários (personas), os problemas que o produto resolve, a declaração de posicionamento do produto e os principais recursos de alto nível (recursos macro), sem entrar em especificações técnicas de código.

---

## 3. Conteúdo Principal

### 3.1. Declaração de Posicionamento do Produto
Para pequenas oficinas de manutenção de motores elétricos, que sofrem com a desorganização de ordens de serviço em papel e perda de histórico de manutenções, o **MotorControl** é um software de gestão desktop que centraliza todo o ciclo de vida do motor (da entrada à entrega). Ao contrário de planilhas complexas ou sistemas ERP genéricos e caros baseados na nuvem, nosso produto oferece uma interface simples, funcionamento 100% offline e campos específicos para o ecossistema de motores elétricos.

### 3.2. Personas (Usuários-Alvo)

#### Persona 1: Seu Roberto (Dono da Oficina / Gestor)
* **Perfil:** 52 anos, técnico eletromecânico veterano e proprietário do negócio.
* **Comportamento:** Passa o dia atendendo clientes, precificando serviços e cobrando prazos dos mecânicos. Prefere ferramentas visuais rápidas e não gosta de digitar textos longos.
* **Dores:** Perde dinheiro por esquecer de cobrar peças usadas; não sabe o histórico de um motor que já quebrou três vezes; tem dificuldade em dar prazos assertivos aos clientes.

#### Persona 2: Lucas (Mecânico / Rebobinador)
* **Perfil:** 26 anos, focado no trabalho manual na bancada de testes e rebobinamento.
* **Comportamento:** Pragmático, trabalha com as mãos sujas de graxa/verniz. Quer apenas ver o que precisa ser feito e registrar que terminou.
* **Dores:** Perde tempo procurando o papel da Ordem de Serviço na oficina; esquece quais os dados nominais da placa do motor e precisa ir até o motor coletar as informações várias vezes.

### 3.3. Matriz de Problemas e Soluções

| Problema do Cliente | Solução do MotorControl | Princípio Aplicado |
| :--- | :--- | :--- |
| Perda de Ordens de Serviço físicas ou rasuras por graxa. | Centralização digital de todas as OS com busca rápida por cliente ou placa do motor. | **KISS** (Fácil substituição do papel). |
| Esquecimento de dados de fechamento e rebobinamento (fios, espiras). | Banco de dados estruturado que armazena os dados técnicos de cada motor atendido. | **DRY** (Não repetir a coleta de dados de um motor recorrente). |
| Falta de clareza no status do motor para o cliente que liga cobrando. | Painel visual rápido indicando se o motor está "Em Orçamento", "Em Manutenção" ou "Pronto". | Alta Coesão (Interface focada no fluxo real da oficina). |

### 3.4. Recursos Macro (Épicos)
* **EP01 - Gestão de Cadastros:** Clientes, Motores e Fornecedores.
* **EP02 - Fluxo de Ordens de Serviço (OS):** Criação, alteração de status, inserção de laudos técnicos e precificação.
* **EP03 - Histórico do Motor (Prontuário):** Linha do tempo de todas as vezes que um motor específico deu entrada na oficina.
* **EP04 - Relatórios e Fechamento:** Geração de termos de entrega e resumo de OS finalizadas para acerto com o cliente.

---

## 4. Boas Práticas
* **Foco na Usabilidade:** Como a Persona 2 (Lucas) trabalha em ambiente fabril/oficina, a interface do Flet deve ter fontes legíveis, botões grandes e inputs fáceis de navegar via teclado.
* **Garantia de Evolução:** Manter as entidades separadas por contexto comercial para facilitar se, no futuro, o cadastro de motores precisar virar um microsserviço ou API externa.

## 5. Observações
O foco inicial do produto é **sanar a dor operacional**. Não tentaremos criar módulos complexos de emissão de NF-e ou integrações contábeis nesta fase (Respeitando estritamente o princípio **YAGNI**).

## 6. Possíveis Melhorias Futuras
* Módulo de envio automático de alertas de "Motor Pronto" via WhatsApp (quando houver conexão à internet disponível).
* Banco de dados global compartilhado de esquemas de bobinagem (uma biblioteca de dados de motores de fábrica).

## 7. Dependências com Outros Documentos
* **Depende de:** `00 - Project Charter` (validação de escopo) e `00A - Glossário` (uso dos termos corretos).
* **É pré-requisito para:** `02 - Product Requirements Document (PRD)` (onde os Épicos virarão requisitos funcionais detalhados).
