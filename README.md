# 🚀 LINEARX Engine
### Sistema Híbrido de Álgebra Lineal y Métodos Numéricos

**LINEARX** es una aplicación multiplataforma de alto rendimiento diseñada para resolver operaciones avanzadas de matemáticas aplicadas. 

El proyecto implementa una arquitectura híbrida profesional que separa un motor backend centralizado en Python de dos interfaces independientes: 
* Un cliente de escritorio construido con **Tkinter**.
* Un panel web moderno desarrollado con **Django y Tailwind CSS**.

---

## 🛠️ Arquitectura del Proyecto

El sistema está estructurado modularmente para evitar la duplicación de código y garantizar la reutilización del motor matemático en cualquier interfaz:

```text
LinearX/
├── core/                         # Motor Backend Matemático Independiente
│   ├── __init__.py
│   └── motor.py                  # Algoritmos puros (Gauss-Jordan, LU, Sarrus, Bisección, etc.)
├── web/                          # Aplicación Web (Django)
│   ├── manage.py
│   ├── linearx_project/          # Configuración principal de Django
│   └── app/                      # Módulo de vistas y templates (Tailwind CSS)
│       └── templates/
│           └── index.html        # Dashboard Web Profesional
└── gui.py                        # Aplicación de Escritorio (Tkinter / Custom UI)
