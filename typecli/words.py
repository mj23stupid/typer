import random

WORDS = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
    "people", "into", "year", "your", "good", "some", "could", "them", "see",
    "other", "than", "then", "now", "look", "only", "come", "its", "over",
    "think", "also", "back", "after", "use", "two", "how", "our", "work",
    "first", "well", "way", "even", "new", "want", "because", "any", "these",
    "give", "day", "most", "us", "great", "between", "need", "large", "under",
    "never", "each", "right", "last", "keep", "same", "should", "still",
    "around", "much", "every", "tell", "does", "set", "three", "own", "hand",
    "high", "place", "long", "where", "help", "line", "turn", "move", "thing",
    "point", "city", "play", "live", "find", "since", "stand", "both", "run",
    "world", "small", "part", "home", "while", "end", "put", "read", "hold",
    "head", "start", "might", "story", "far", "change", "name", "close",
    "door", "between", "through", "light", "life", "before", "begin", "below",
    "state", "open", "side", "night", "seem", "hard", "house", "system",
    "better", "during", "number", "always", "found", "water", "old", "land",
    "case", "early", "face", "group", "child", "important", "often", "problem",
    "class", "leave", "power", "real", "sure", "question", "along", "true",
    "body", "young", "book", "carry", "develop", "learn", "paper", "letter",
    "program", "social", "second", "enough", "note", "above", "example",
    "river", "local", "pull", "kind", "follow", "show", "money", "serve",
    "voice", "fall", "cover", "word", "less", "late", "clear",
]


def generate(count=80):
    return " ".join(random.choice(WORDS) for _ in range(count))
