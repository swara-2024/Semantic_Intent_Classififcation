def ml_predict(query, classifier, semantic_model, preprocess_fn):
    processed = preprocess_fn(query)

    embedding = semantic_model.encode(
        [processed],
        normalize_embeddings=True,
        convert_to_numpy=True
    )

    intent = classifier.predict(embedding)[0]

    confidence = (
        classifier.predict_proba(embedding).max()
        if hasattr(classifier, "predict_proba")
        else None
    )

    return intent, confidence
