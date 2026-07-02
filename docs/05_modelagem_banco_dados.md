# 05 - Modelagem do Banco de Dados (DER)

**Projeto:** MotorControl  
**Versão:** 1.0  
**Data:** 01 de Julho de 2026  

## 1. Dicionário de Tabelas (SQLite)
* **`clients`:** id (PK), name, gov_id (Unique), phone, email, is_active.
* **`motors`:** id (PK), client_id (FK), serial_number (Unique), brand, model, hp_kw, power_unit, rpm, voltage, is_active.
* **`order_services`:** id (PK), motor_id (FK), status, opened_at, symptom, execution_report, discount, total_value, test_voltage, test_current, test_insulation.
* **`item_services` / `item_pieces`:** Itens vinculados à OS com exclusão em cascata.
