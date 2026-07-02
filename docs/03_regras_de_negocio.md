# 03 - Regras de Negócio (RN)

**Projeto:** MotorControl  
**Versão:** 1.0  
**Data:** 01 de Julho de 2026  

## 1. Objetivo
Definir as políticas, restrições e cálculos operacionais imperativos da oficina que o software deve obrigatoriamente fazer cumprir.

## 2. Conteúdo Principal
* **RN01 - Máquina de Estados da OS:** `EM_ORCAMENTO` -> `AGUARDANDO_APROVACAO` -> `APROVADA` (ou `REJEITADA`) -> `EM_MANUTENCAO` -> `PRONTA_PARA_TESTE` -> `FINALIZADA_ENTREGUE`. Transições exigem validações (ex: laudo técnico para finalizar).
* **RN02 - Soft Delete:** Clientes e Motores usam flag `is_active`. Nunca são deletados fisicamente para proteger o histórico longitudinal.
* **RN03 - Precificação:** Valor Total = Serviços + Peças - Desconto. Desconto máximo limitado a 15% do valor bruto.
* **RN04 - Ficha de Rebobinamento:** Se a OS incluir serviços de bobinagem, torna-se obrigatório o preenchimento de dados técnicos (fio, espiras, passo) antes de iniciar a manutenção.
