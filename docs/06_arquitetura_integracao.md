# 06 - Arquitetura de Integração (API/Módulos)

**Projeto:** MotorControl  
**Versão:** 1.0  
**Data:** 01 de Julho de 2026  

## 1. Integrações Locais (In-Process)
* **Módulo PDF (ReportLab):** Recebe DTOs da camada de negócio e renderiza os relatórios/comprovantes locais em formato PDF.
* **Módulo de Sistema de Arquivos (Pathlib):** Gerencia de forma dinâmica e relativa a gravação dos documentos e backups na pasta raiz do executável, tratando exceções de falta de permissão em disco (I/O).
