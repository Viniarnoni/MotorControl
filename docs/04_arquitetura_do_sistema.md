# 04 - Arquitetura do Sistema

**Projeto:** MotorControl  
**Versão:** 1.0  
**Data:** 01 de Julho de 2026  

## 1. Objetivo
Definir a divisão de responsabilidades em 3 camadas claras para garantir um sistema testável e manutenível.

## 2. Conteúdo Principal
* **Camada de Apresentação (UI):** Desenvolvida em Flet, captura eventos e renderiza as telas sem conter lógica SQL.
* **Camada de Negócio (Domain/Service):** Python puro, valida as Regras de Negócio de forma isolada.
* **Camada de Dados (Data/Repository):** SQLModel gerencia o arquivo local SQLite.
* **Estrutura de Código:** Organizado em `src/ui`, `src/services`, `src/models` e `src/repositories`.
