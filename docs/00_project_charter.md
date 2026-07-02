# 00 - Project Charter

**Projeto:** MotorControl  
**Versão:** 1.0  
**Data:** 01 de Julho de 2026  

## 1. Objetivo
O objetivo deste documento é autorizar formalmente o início do projeto **MotorControl**, estabelecendo sua visão de alto nível, justificativa, principais stakeholders, premissas iniciais e restrições. Ele servirá como a "pedra fundamental" para o alinhamento de expectativas antes do aprofundamento técnico.

## 2. Escopo
### 2.1. O que está INCLUSO (In-Scope)
* Desenvolvimento de uma aplicação Desktop (Windows/Linux/Mac).
* Funcionamento 100% offline, com armazenamento local.
* Gerenciamento completo do ciclo de vida de manutenção de motores elétricos (cadastro, orçamento, execução, entrega).
* Cadastro de clientes, motores, serviços e peças.
* Geração de ordens de serviço.

### 2.2. O que está EXCLUSO (Out-of-Scope)
* Sincronização em nuvem ou acesso web.
* Gestão financeira complexa (fluxo de caixa, emissão de notas fiscais integrais com a SEFAZ).
* Aplicativo mobile.

## 3. Conteúdo Principal
### 3.1. Justificativa do Projeto
Pequenas oficinas de manutenção de motores elétricos frequentemente sofrem com processos manuais, resultando em perda de histórico de manutenções, dificuldade na precificação, atrasos nas entregas e comunicação falha com o cliente. O MotorControl visa digitalizar e padronizar este processo, aumentando a confiabilidade e a organização do negócio.

### 3.2. Stack Tecnológico Base
* **Linguagem:** Python 3.11+
* **Interface Gráfica (UI):** Flet
* **Banco de Dados:** SQLite
* **ORM:** SQLModel
* **Empacotamento:** PyInstaller

### 3.3. Restrições e Premissas
* **Premissa:** O usuário final possui conhecimento básico de informática. O sistema deve ser extremamente intuitivo.
* **Restrição:** O sistema operará em máquinas que podem ter hardware limitado. A performance deve ser otimizada.

## 4. Boas Práticas
* **Transparência:** Todas as limitações do ambiente offline devem ser claras desde o início.
* **Foco no Domínio:** A arquitetura será orientada ao domínio da manutenção de motores.

## 5. Observações
Este é o documento de autorização. Ele não detalha as telas ou as regras de negócio minuciosas. Seu papel é garantir que a equipe técnica e os stakeholders estejam olhando para o mesmo horizonte.

## 6. Possíveis Melhorias Futuras
* Migração do banco SQLite para PostgreSQL em nuvem.
* Implementação de uma arquitetura multi-tenant (SaaS).
* Módulo de sincronização de dados via API REST.

## 7. Dependências com Outros Documentos
* Este documento não possui dependências anteriores.
* Ele é o pré-requisito absoluto para o **00A - Glossário** e **01 - Visão do Produto**.
