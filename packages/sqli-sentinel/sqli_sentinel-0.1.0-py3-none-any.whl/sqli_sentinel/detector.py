import joblib
import os
import re

class Detector:
    """
    A class to detect SQL Injection attacks in strings using a hybrid approach
    (ML model and regular expressions).
    """
    def __init__(self, model_path=None, vectorizer_path=None):
        """
        Initializes the detector by loading the trained model and vectorizer.
        """
        # --- Load ML Model and Vectorizer ---
        if model_path is None or vectorizer_path is None:
            # Construct default paths relative to this file's location
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(script_dir) # Go up one level to the project root
            self.model = joblib.load(os.path.join(base_dir, 'models', 'sqli_model.joblib'))
            self.vectorizer = joblib.load(os.path.join(base_dir, 'models', 'tfidf_vectorizer.joblib'))
        else:
            # Load from specified paths
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)

        # --- Define Regex Patterns for quick checks ---
        # This list is expanded to include more dangerous SQL commands.
        self.regex_patterns = [
            # Classic SQLi patterns
            r"(\'|\")\s*or\s*1\s*=\s*1",
            r"(\'|\")\s*or\s*(\'|\")\w+(\'|\")\s*=\s*(\'|\")\w+(\'|\")",
            
            # Comment-based SQLi
            r"--|\#|/\*|\*/",
            
            # Union-based SQLi
            r"union\s+select",
            
            # Blind SQLi keywords
            r"sleep\(|benchmark\(|pg_sleep\(",
            
            # Dangerous command keywords (kept for defense-in-depth)
            r"drop\s+table|drop\s+database",
            r"delete\s+from",
            r"truncate\s+table",
            r"exec\s*\(",
            r"xp_cmdshell",

            # Query Stacking detection
            r";\s*(drop|delete|truncate|exec|insert|update)\s"
        ]
        # Compile regexes for better performance
        self.compiled_regex = [re.compile(p, re.IGNORECASE) for p in self.regex_patterns]

    def detect(self, input_string: str) -> bool:
        """
        Analyzes an input string to determine if it contains an SQL Injection attack.

        The detection process is two-fold:
        1. A quick scan using a list of common regex patterns.
        2. A deeper analysis using the pre-trained machine learning model.

        Args:
            input_string (str): The string to be analyzed.

        Returns:
            bool: True if an attack is detected, False otherwise.
        """
        # --- Step 1: Quick Regex Scan ---
        for regex in self.compiled_regex:
            if regex.search(input_string):
                return True # Attack detected by regex

        # --- Step 2: ML Model Prediction ---
        # If no regex matched, proceed with the model
        vectorized_input = self.vectorizer.transform([input_string])
        prediction = self.model.predict(vectorized_input)

        return bool(prediction[0])
