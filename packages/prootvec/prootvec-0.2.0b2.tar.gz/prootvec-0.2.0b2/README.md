# prootvec 🚀

**prootvec** es una mini-biblioteca para entrenar *word embeddings* en Python usando [micrograd](https://github.com/karpathy/micrograd).  
Ideal para aprender cómo funcionan los modelos tipo *skip-gram* sin frameworks pesados.

## ✨ Features
- Tokenizador propio con `<PAD>`, `<UNK>`, `<BOS>`, `<EOS>`
- Entrenadores:
  - `MicroTrainer` → entrenamiento minimalista masivo con MLP
  - `Trainer` → versión simple para pruebas rápidas
- Backend ligero basado en `micrograd`
- Utilidades: similitud coseno, guardar/cargar embeddings

## 📦 Instalación

```bash
pip install prootvec
