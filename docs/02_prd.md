# 02 - Product Requirements Document (PRD)

**Projeto:** MotorControl  
**Versão:** 1.0  
**Data:** 01 de Julho de 2026  

## 1. Objetivo
O objetivo deste documento é especificar de forma detalhada e granular todos os requisitos funcionais e não funcionais do sistema MotorControl. Ele serve como o guia definitivo do escopo do produto para engenharia de software, garantindo que o comportamento esperado da aplicação esteja perfeitamente mapeado sem ambiguidades.

## 2. Escopo
Este PRD detalha as capacidades do sistema referentes ao controle de cadastros, fluxo de Ordens de Serviço (OS), orçamento, laudos técnicos, prontuário do motor e os critérios de qualidade técnica (requisitos não funcionais), aplicando as diretrizes de simplicidade (KISS) e ausência de desperdício (YAGNI).

---

## 3. Conteúdo Principal

### 3.1. Requisitos Funcionais (RF)

#### Módulo 01: Cadastros Base
* **RF01 - Cadastro de Clientes:**
    * **Descrição:** O sistema deve permitir criar, ler, atualizar e desativar (soft delete) clientes.
    * **Campos Requeridos:** Nome/Razão Social (string, obrigatório), CPF/CNPJ (string, validado, obrigatório), Telefone Principal (string, obrigatório), Email (string, opcional), Endereço Completo (string, opcional).
    * **Regra de Validação:** Não permitir dois clientes ativos com o mesmo CPF/CNPJ.
* **RF02 - Cadastro de Motores:**
    * **Descrição:** O sistema deve registrar os motores elétricos vinculando-os a um cliente proprietário.
    * **Campos Requeridos:** Número de Série (string, obrigatório/chave alternativa), Marca/Fabricante (string, obrigatório), Modelo (string, opcional), Potência (decimal, obrigatório) + Unidade (Enum: CV, kW), RPM (inteiro, opcional), Tensão Nominal (Enum: 220V, 380V, 440V, 220/380V, 380/660V), Corrente Nominal (decimal, opcional), Classe de Isolamento (Enum: B, F, H).
    * **Regra de Domínio:** Um motor sempre deve pertencer a um cliente cadastrado.

#### Módulo 02: Fluxo de Ordens de Serviço (OS)
* **RF03 - Abertura de Ordem de Serviço:**
    * **Descrição:** Iniciar o ciclo de vida de uma manutenção de motor.
    * **Campos Requeridos:** Código da OS (Numérico sequencial auto-incremental automático), Cliente (ID), Motor (ID), Data/Hora de Entrada (automático do sistema), Descrição do Sintoma/Reclamação (texto, obrigatório), Observações Visuais de Entrada (texto, opcional).
    * **Status Inicial:** Toda OS nasce obrigatoriamente com o status `EM_ORCAMENTO`.
* **RF04 - Gestão do Ciclo de Vida (Status):**
    * **Descrição:** Controlar o progresso da OS através de uma máquina de estados finitos bem definida.
    * **Estados Válidos:** `EM_ORCAMENTO` -> `AGUARDANDO_APROVACAO` -> `APROVADA` (ou `REJEITADA`) -> `EM_MANUTENCAO` -> `PRONTA_PARA_TESTE` -> `FINALIZADA_ENTREGUE`.
* **RF05 - Lançamento de Itens e Orçamento:**
    * **Descrição:** Permitir a inserção de Serviços (Mão de Obra) e Peças/Insumos na OS para composição do preço final.
    * **Campos por Item de Serviço:** Descrição do serviço (ex: Rebobinamento Estator, Troca de Rolamentos), Valor (decimal, obrigatório).
    * **Campos por Item de Peça:** Descrição da peça (ex: Rolamento 6205 DDU, Verniz Isolante), Quantidade (inteiro), Valor Unitário (decimal), Valor Total do Item (Calculado automaticamente: Qtd x ValorUnitario).
    * **Cálculo Geral:** O sistema deve somar em tempo real todos os serviços e peças e exibir o Valor Total da OS.

#### Módulo 03: Histórico e Emissão de Documentos
* **RF06 - Prontuário do Motor (Histórico Longitudinal):**
    * **Descrição:** Exibir uma linha do tempo de todas as ordens de serviço associadas a um determinado Número de Série de motor.
    * **Critério de Aceite:** Ao buscar pelo número de série, o sistema lista as datas de entrada, defeitos anteriores e peças substituídas nas manutenções passadas.
* **RF07 - Emissão de Relatórios em PDF:**
    * **Descrição:** Gerar documentos formatados e limpos para impressão local ou exportação.
    * **Modelos de PDF Necessários:** 1. Comprovante de Entrada (Sem valores, apenas dados do motor e reclamação).
        2. Folha de Orçamento (Com discriminação detalhada de peças, serviços e valor total para aprovação do cliente).
        3. Termo de Entrega/Garantia (Dados do fechamento do motor, testes finais e prazo de garantia).

---

### 3.2. Requisitos Não Funcionais (RNF)

| Identificador | Categoria | Descrição do Requisito | Métrica/Critério de Sucesso |
| :--- | :--- | :--- | :--- |
| **RNF01** | Arquitetura | Operação 100% Autônoma e Offline. | Não deve haver nenhuma chamada de rede externa (Internet) para as funções core do app. |
| **RNF02** | Desempenho | Tempo de resposta de consultas locais. | Buscas por número de série ou nome de cliente devem levar menos de 500ms em bases com até 20.000 registros. |
| **RNF03** | Confiabilidade | Resiliência contra quedas de energia (muito comuns em ambientes industriais/oficinas). | Uso obrigatório do mecanismo de Write-Ahead Logging (WAL) do SQLite para garantir transações ACID intactas. |
| **RNF04** | Portabilidade | Distribuição simplificada sem instaladores complexos. | O arquivo compilado pelo PyInstaller deve rodar diretamente via clique duplo em sistemas Windows 10/11 sem dependências externas. |
| **RNF05** | Interface | Adaptabilidade de Tela. | A interface construída em Flet deve se auto-ajustar perfeitamente para a resolução mínima de 1366x768 pixels. |

---

## 4. Boas Práticas
* **Campos Sanitizados:** Todos os campos de texto devem passar por trim automático (remoção de espaços extras no início e fim) antes de salvar no banco de dados.
* **Tratamento de Exceções Base:** Falhas de gravação no banco (ex: disco cheio) devem ser capturadas na camada de persistência e exibidas de forma amigável ao usuário (Snackbar ou Diálogo com mensagem clara), nunca quebrando a aplicação (Crash).

## 5. Observações
* Seguindo o princípio **YAGNI**, os cadastros não terão fotos ou anexos pesados de arquivos nesta primeira fase para evitar o crescimento descontrolado do tamanho do arquivo SQLite e manter backups simples.
* Campos numéricos de moeda devem sempre adotar precisão decimal fixa de duas casas para evitar erros de arredondamento de ponto flutuante comuns em Python puro.

## 6. Possíveis Melhorias Futuras
* Implementação de níveis de permissão de acesso simples (Administrador vs Mecânico) caso a oficina contrate mais funcionários no futuro.
* Mecanismo automático de backup zipado do arquivo `.db` do SQLite ao fechar o sistema.

## 7. Dependências com Outros Documentos
* **Depende de:** `01 - Visão do Produto` (para validação dos módulos base e personas).
* **É pré-requisito para:** `03 - Regras de Negócio` (onde validaremos o comportamento fino de transição de status) e `05 - Modelagem do Banco de Dados` (onde os campos e tipos definidos aqui virarão colunas físicos).
