import threading
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .semantic_validator_base import SemanticValidatorBase
from ...exception import SemanticValidationError
from ...models.result import Result


class TFIDFSemanticValidator(SemanticValidatorBase):
    """TF-IDF based semantic similarity validator."""
    _instances = {}
    _lock = threading.RLock()

    def __init__(self):
        super().__init__()
        self.vectorizer = TfidfVectorizer()

    def validate(self, text1: str, text2: str, threshold: float = 0.8) -> Result:
        if not (0 <= threshold <= 1):
            raise SemanticValidationError("Threshold must be between 0 and 1")

        tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
        similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        if similarity_score < threshold:
            raise SemanticValidationError(
                f"TF-IDF similarity score: {similarity_score} is lesser than threshold: {threshold}")

        return Result(self.validator_name, True,
                      f"TF-IDF similarity score: {similarity_score}, Threshold: {threshold}")

    @classmethod
    def get_instance(cls, **kwargs):
        with cls._lock:
            if "tfidf" not in cls._instances:
                cls._instances["tfidf"] = cls()
            return cls._instances["tfidf"]


class HuggingFaceSemanticValidator(SemanticValidatorBase):
    """HuggingFace API based semantic similarity validator."""
    _instances = {}
    _lock = threading.RLock()

    def __init__(self, model_name: str):
        super().__init__()
        self.model_name = model_name

    def validate(self, text1: str, text2: str, threshold: float = 0.8) -> Result:
        try:
            from huggingface_hub import InferenceClient
        except ImportError:
            raise SemanticValidationError(
                "huggingface_hub not installed. Install with: pip install aisert[huggingface]"
            )
        from sklearn.metrics.pairwise import cosine_similarity

        if not (0 <= threshold <= 1):
            raise SemanticValidationError("Threshold must be between 0 and 1")

        client = InferenceClient()
        embeddings = client.feature_extraction([text1, text2], model=self.model_name)
        similarity_score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

        if similarity_score < threshold:
            raise SemanticValidationError(
                f"HuggingFace similarity score: {similarity_score} is lesser than threshold: {threshold}")

        return Result(self.validator_name, True,
                      f"HuggingFace similarity score: {similarity_score}, Threshold: {threshold}")

    @classmethod
    def get_instance(cls, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", **kwargs):
        key = f"{model_name}"
        with cls._lock:
            if key not in cls._instances:
                cls._instances[key] = cls(model_name)
            return cls._instances[key]


class OpenAISemanticValidator(SemanticValidatorBase):
    """OpenAI API based semantic similarity validator."""
    _instances = {}
    _lock = threading.RLock()

    def __init__(self, model_name: str):
        super().__init__()
        self.model_name = model_name

    def validate(self, text1: str, text2: str, threshold: float = 0.8) -> Result:
        import openai
        from sklearn.metrics.pairwise import cosine_similarity

        if not (0 <= threshold <= 1):
            raise SemanticValidationError("Threshold must be between 0 and 1")

        client = openai.OpenAI()
        response = client.embeddings.create(model=self.model_name, input=[text1, text2])
        embeddings = [data.embedding for data in response.data]
        similarity_score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

        if similarity_score < threshold:
            raise SemanticValidationError(
                f"OpenAI similarity score: {similarity_score} is lesser than threshold: {threshold}")

        return Result(self.validator_name, True,
                      f"OpenAI similarity score: {similarity_score}, Threshold: {threshold}")

    @classmethod
    def get_instance(cls, model_name: str = "text-embedding-3-small", **kwargs):
        key = f"{model_name}"
        with cls._lock:
            if key not in cls._instances:
                cls._instances[key] = cls(model_name)
            return cls._instances[key]


class SentenceTransformersSemanticValidator(SemanticValidatorBase):
    """Sentence Transformers based semantic similarity validator."""
    _instances = {}
    _lock = threading.RLock()

    def __init__(self, model_name: str):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise SemanticValidationError(
                "sentence-transformers not installed. Install with: pip install aisert[sentence-transformers]"
            )
        super().__init__()
        self.model = SentenceTransformer(model_name)

    def validate(self, text1: str, text2: str, threshold: float = 0.8) -> Result:
        try:
            from sentence_transformers import util
        except ImportError:
            raise SemanticValidationError(
                "sentence-transformers not installed. Install with: pip install aisert[sentence-transformers]"
            )

        if not (0 <= threshold <= 1):
            raise SemanticValidationError("Threshold must be between 0 and 1")

        embeddings1 = self.model.encode(text1, convert_to_tensor=True)
        embeddings2 = self.model.encode(text2, convert_to_tensor=True)
        similarity_score = util.pytorch_cos_sim(embeddings1, embeddings2).item()

        if similarity_score < threshold:
            raise SemanticValidationError(
                f"Semantic similarity score: {similarity_score} is lesser than threshold: {threshold}")

        return Result(self.validator_name, True,
                      f"Semantic similarity score: {similarity_score}, Threshold: {threshold}")

    @classmethod
    def get_instance(cls, model_name: str = "all-MiniLM-L6-v2", **kwargs):
        with cls._lock:
            if model_name not in cls._instances:
                cls._instances[model_name] = cls(model_name)
            return cls._instances[model_name]
