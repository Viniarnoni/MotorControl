# 09 - Plano de Implantação (Deployment)

**Projeto:** MotorControl
**Versão:** 1.0

## 1. Objetivo
Definir a estratégia de empacotamento e distribuição offline do sistema para o ambiente de produção.

## 2. Conteúdo Principal
* **Empacotamento:** Uso do PyInstaller para compilar o código em um executável (.exe) standalone e monolítico.
* **Comando de Build:** pyinstaller --noconsole --onefile --name=MotorControl src/main.py
* **Distribuição:** Transferência direta via Pendrive USB ou rede local para as máquinas da oficina.
* **Banco de Dados:** Criação automática do arquivo SQLite local (motorcontrol.db) na primeira execução do sistema.
