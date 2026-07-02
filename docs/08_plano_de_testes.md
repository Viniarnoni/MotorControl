# 08 - Plano de Testes

**Projeto:** MotorControl  
**Versão:** 1.0  
**Data:** 01 de Julho de 2026  

## 1. Objetivo
O objetivo deste documento é formalizar a estratégia, o escopo, os cenários e os critérios de aceitação para os testes de software do MotorControl. Ele garante que o sistema seja entregue livre de regressões, com cálculos exatos e resiliente a falhas locais de infraestrutura.

## 2. Escopo
Este plano cobre os Testes Unitários da camada de negócio, Testes de Integração com a persistência e relatórios, e os Testes de Caixa Preta/Interface (UI) baseados nas personas descritas.

---

## 3. Conteúdo Principal

### 3.1. Estratégia de Testes

| Nível de Teste | Ferramenta | Foco Principal | Responsável |
| :--- | :--- | :--- | :--- |
| **Unitário** | `pytest` | Validação fina das Regras de Negócio (cálculo de descontos, máquina de estados da OS, travas de campos). | Desenvolvedor |
| **Integração** | `pytest` | Testar se os modelos `SQLModel` geram e mantêm a integridade referencial no arquivo SQLite real e se o módulo `ReportLab` gera PDFs válidos. | Desenvolvedor |
| **Sistema / E2E** | Manual / Flet | Simulação de fluxo completo pelas Personas (Seu Roberto abrindo OS, Lucas preenchendo ficha de rebobinamento). | QA / PO |

### 3.2. Cenários de Teste Críticos (Casos de Teste)

#### CT01: Validação do Limite de Desconto (Regra RN03)
* **Objetivo:** Garantir que o sistema impeça descontos abusivos.
* **Dados de Entrada:** OS com R$ 1.000,00 em serviços. Tentativa de aplicar R$ 160,00 de desconto (16%).
* **Resultado Esperado:** O sistema deve lançar uma exceção `BusinessRuleException` e a interface Flet deve exibir uma mensagem informando que o desconto máximo permitido é de 15%.

#### CT02: Transição Inválida de Status da OS (Regra RN01)
* **Objetivo:** Impedir que uma OS pule etapas do fluxo operacional.
* **Ação:** Tentar alterar diretamente o status de uma OS de `EM_ORCAMENTO` para `EM_MANUTENCAO`, sem passar por `APROVADA`.
* **Resultado Esperado:** A transição deve ser bloqueada na camada de serviço, mantendo o status original intacto.

#### CT03: Resiliência contra Queda Abrupta de Energia (Requisito RNF03)
* **Objetivo:** Validar a eficácia do modo WAL do SQLite em ambiente hostil de oficina.
* **Ação:** Iniciar uma transação pesada de gravação e forçar o encerramento do processo do Python (Kill Process / Simulação de queda de energia).
* **Resultado Esperado:** Ao reabrir o sistema, o arquivo `.db` deve estar íntegro, revertendo a transação incompleta para o último estado estável sem corromper o banco de dados.

---

## 4. Critérios de Aceite para Liberação (Go/No-Go)
* **Cobertura de Código (Coverage):** Mínimo de **80% de cobertura** de testes unitários na camada de serviços (`src/services/`).
* **Bugs Críticos:** Zero bugs de severidade "Blocker" ou "Critical" abertos (ex: erro de cálculo financeiro ou crash que fecha a tela sozinho).
* **Portabilidade:** O executável compilado pelo PyInstaller deve abrir e executar todas as funções core em uma máquina limpa com Windows 10 (sem Python instalado).

## 5. Observações
Por se tratar de um sistema puramente offline, testes de carga com milhares de usuários simultâneos ou testes de latência de rede estão fora do escopo deste projeto (**Princípio YAGNI**).

## 6. Possíveis Melhorias Futuras
* Automatização dos testes de interface (E2E) utilizando ferramentas de automação de GUI como o `PyAutoGUI` ou integração nativa de testes do Flet se disponível.

## 7. Dependências com Outros Documentos
* **Unifica critérios de:** `02 - PRD` (requisitos de qualidade) e `03 - Regras de Negócio` (regras a serem testadas).
* **É pré-requisito para:** `09 - Plano de Implantação` (só implantamos após aprovação nos testes).
