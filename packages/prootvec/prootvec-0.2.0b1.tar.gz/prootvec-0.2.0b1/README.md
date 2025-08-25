# ProotVec 0.2.0b1

🚀 **ProotVec** es una librería **mínima** y **ligera** para vectorización y entrenamiento básico de embeddings en sistemas **ARM64**, ideal para entornos como **Ubuntu** y **Termux**.

Incluye un sistema modular en **6 nanos**:
- `tokenizer.py` → Convierte texto en tokens.
- `losses.py` → Funciones de pérdida básicas.
- `model.py` → Modelo de embeddings con inicialización aleatoria.
- `trainer.py` → Entrenamiento supervisado simple.
- `reinforce.py` → Refuerzo con similitud coseno.
- `utils.py` → Guardar y cargar modelos.

---

## Instalación

Desde PyPI (cuando lo subas):

```bash
pip install prootvec

from prootvec import Tokenizer, EmbeddingModel, Trainer, Reinforce, save_model, load_model

# 1. Tokenizar
tk = Tokenizer()
tk.fit(["hola mundo", "texto de prueba"])
print("Vocabulario:", tk.vocab)

# 2. Modelo
model = EmbeddingModel(vocab_size=len(tk.vocab), embedding_dim=8)

# 3. Entrenador
trainer = Trainer(model)
pairs = [(tk.vocab["hola"], tk.vocab["mundo"])]
trainer.train_epoch(pairs, epochs=5)

# 4. Refuerzo
reinforce = Reinforce(model)
sim = reinforce.reinforce_pair(tk.vocab["hola"], tk.vocab["mundo"])
print("Similitud reforzada:", sim)

# 5. Guardar
save_model("modelo.json", tk.vocab, model.embeddings)

# 6. Cargar
vocab, embeddings = load_model("modelo.json")
print("Vocabulario cargado:", vocab)
