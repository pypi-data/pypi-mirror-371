from . import Tokenizer, EmbeddingModel, Trainer, Reinforce

def main():
    corpus = [
        "hola mundo",
        "texto simples datos",
        "vector de texto",
        "hola datos de mundo"
    ]

    tok = Tokenizer()
    vocab = tok.build_vocab(corpus)
    print("📖 Vocabulario:", vocab)

    model = EmbeddingModel(len(vocab), embed_dim=4)
    trainer = Trainer(model, tok)
    losses = trainer.train(corpus, epochs=5)
    print("📉 Pérdidas:", losses)

    vec = model.get_vector(vocab["hola"])
    print("🔤 Embedding 'hola':", vec.tolist())

    reinforce = Reinforce(model)
    score = reinforce.reward("hola", "mundo")
    print("🎯 Refuerzo hola-mundo:", score)

if __name__ == "__main__":
    main()
