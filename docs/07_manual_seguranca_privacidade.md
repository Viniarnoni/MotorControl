# 07 - Manual de Segurança e Privacidade

**Projeto:** MotorControl  
**Versão:** 1.0  
**Data:** 01 de Julho de 2026  

## 1. Objetivo
Estabelecer as diretrizes de segurança da informação e privacidade de dados para o MotorControl, mitigando riscos de perda, corrupção ou vazamento de dados em um ambiente desktop offline local.

## 2. Conteúdo Principal

### 2.1. Segurança do Banco de Dados Local
Como o banco de dados é um arquivo SQLite local, ele fica exposto a usuários mal-intencionados com acesso físico à máquina.
* **Diretriz:** O arquivo `.db` deve ser armazenado na pasta oculta de dados de aplicativos do usuário (`AppData` no Windows) ou protegido por permissões de leitura do Sistema Operacional ao nível do usuário que instalou o software.

### 2.2. Mitigação de Corrupção de Dados
O maior risco de segurança operacional em oficinas mecânicas é o desligamento abrupto do computador por quedas de energia.
* **Mecanismo:** Ativação obrigatória do modo **WAL (Write-Ahead Logging)** no SQLite através do SQLModel na inicialização do sistema. Isso garante que as transações de Ordens de Serviço em andamento não corrompam a base de dados em caso de queda de energia.

### 2.3. Privacidade de Dados (LGPD Compliance Local)
Mesmo sendo um software local, o sistema armazena dados pessoais (Nome, CPF/CNPJ, Telefone e E-mail de clientes).
* **Anonimização no Descarte:** Ao acionar o recurso futuro de "Limpeza de Base", o sistema deve sobrescrever os campos de texto identificáveis (`name`, `email`, `phone`) com hashes ou strings vazias, em vez de manter dados mortos expostos.
* **Acesso Local:** O software não transmitirá nenhuma informação para servidores externos, garantindo privacidade total aos clientes da oficina.

---

## 3. Dependências com Outros Documentos
* **Depende de:** `02 - PRD` (requisitos não-funcionais de confiabilidade RNF03) e `05 - Modelagem do Banco de Dados`.
* **É pré-requisito para:** `08 - Plano de Testes` (testes de estresse de queda de energia e integridade).
