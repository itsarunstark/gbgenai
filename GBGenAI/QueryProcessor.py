import re
import nltk

nltk.download('popular')

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import sqlite3
from nltk.corpus import wordnet
from nltk import pos_tag

# -------------------- Configuration --------------------

TABLE_MAPPING = {
    "students": "student",
    "student": "student"
}

COLUMN_MAPPING = {
    "name": "first_name",
    "age": "age",
    "department": "dept_name",
    "student_id": "student_id",
    "country": "country",
    "id": "id",
    "firstname": "first_name",
    "lastname": "last_name",
    "joining": "join_date" 
}

OPERATORS = {
    "less": "<",
    "greater": ">",
    "equal": "=",
    "before": "<",
    "after": ">",
    "is": "="
}

FUNCTIONS = {
    "maximum": "MAX",
    "minimum": "MIN",
    "average": "AVG",
    "count": "COUNT",
    "total": "SUM"
}

# -------------------- Helper Functions --------------------

def preprocess(query, explain_vector:dict):
    """
    Tokenizes, removes stop words, and lemmatizes the query.
    Lemmatization is generally preferred over stemming.
    """
    tokens = word_tokenize(query.lower())
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    filtered_tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    explain_vector['tokens'] = tokens
    return filtered_tokens

def get_synonyms(word):
    """Gets synonyms for a word using WordNet."""
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms

def extract_table(tokens, explain_vector):
    """
    Identifies the table from the processed tokens, using synonyms and lemmatization.
    """
    table = None
    for word in tokens:
        # 1. Check for exact matches first
        if word in TABLE_MAPPING:
            table = TABLE_MAPPING[word]
            break
        else:
            # 2. Check synonyms using WordNet
            synonyms = get_synonyms(word)
            for syn in synonyms:
                if syn in TABLE_MAPPING:
                    table = TABLE_MAPPING[syn]
                    break
            if table:
                break

    if not table:
        # 3. Check lemmatized versions
        lemmatizer = WordNetLemmatizer()
        for word in tokens:
            lemmatized_word = lemmatizer.lemmatize(word)
            if lemmatized_word in TABLE_MAPPING:
                table = TABLE_MAPPING[lemmatized_word]
                break
    explain_vector['tables'] = table
    return table

def extract_column(tokens, explain_vector):
    """
    Identifies the column from the processed tokens, using synonyms and lemmatization.
    """
    column = None
    for word in tokens:
        # 1. Check for exact matches first
        if word in COLUMN_MAPPING:
            column = COLUMN_MAPPING[word]
            break
        else:
            # 2. Check synonyms using WordNet
            synonyms = get_synonyms(word)
            for syn in synonyms:
                if syn in COLUMN_MAPPING:
                    column = COLUMN_MAPPING[syn]
                    break
            if column:
                break

    if not column:
        # 3. Check lemmatized versions
        lemmatizer = WordNetLemmatizer()
        for word in tokens:
            lemmatized_word = lemmatizer.lemmatize(word)
            if lemmatized_word in COLUMN_MAPPING:
                column = COLUMN_MAPPING[lemmatized_word]
                break
    explain_vector['columns'] = column
    return column

# -------------------- Core NL to SQL Conversion --------------------

def convert_nl_to_sql(nl_query):
    """Converts a natural language query to an SQL query."""

    explain_vector = {}

    tokens = preprocess(nl_query, explain_vector)
    print("Processed tokens:", tokens)

    table = extract_table(tokens, explain_vector)
    if not table:
        return "Error: No valid table found in the query."

    sql_function = None
    for word in tokens:
        if word in FUNCTIONS:
            sql_function = FUNCTIONS[word]
            break

    column = extract_column(tokens, explain_vector)
    if not column:
        return "Error: No valid column found in the query."

    condition = ""
    # Regex to capture WHERE/whose with various operators and values (numbers or words)
    match = re.search(r"(where|whose)\s+(\w+)\s+(greater|less|equal|before|after|is)\s+([\w\d']+)", nl_query.lower())
    if match:
        where_column = match.group(2)
        operator = OPERATORS.get(match.group(3), None)
        value = match.group(4)
        if operator and where_column in COLUMN_MAPPING:
            condition = f" WHERE {COLUMN_MAPPING[where_column]} {operator} '{value}'"
    elif "in" in tokens:
        try:
            country_index = tokens.index("in") + 1
            country_value = tokens[country_index]
            condition = f" WHERE country = '{country_value.capitalize()}'"
        except IndexError:
            pass

    # Handling COUNT with a column
    if sql_function == "COUNT" and column:
        sql_query = f"SELECT COUNT({column}) FROM {table}{condition};"
    elif sql_function:
        sql_query = f"SELECT {sql_function}({column}) FROM {table}{condition};"
    else:
        sql_query = f"SELECT {column} FROM {table}{condition};"

    return sql_query, explain_vector

# -------------------- Database Interaction --------------------

def execute_query(sql_query):
    """Executes the SQL query against the database and fetches results."""
    try:
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        return results, None
    except sqlite3.Error as e:
        print("Database Error:", e)
        return None, None

# -------------------- Main Function --------------------

def simplified_nlidb(query):
    """Processes the natural language query and returns the database results."""
    sql_query = convert_nl_to_sql(query)[0]
    print("Generated SQL:", sql_query)

    if sql_query.startswith("Error"):
        return sql_query

    results = execute_query(sql_query)
    return results

# -------------------- Test Cases --------------------

if __name__ == "__main__":
    nl_queries = [
        "name of students in india",
        "average age of students",
        "maximum joining of students",
        "name of students",
        "age of students where age greater than 20",
        "list the names of students where age less than 30",
        "count students",
        "show the department of students",
        "what is the students firstname?",
        "what is the students id?",
        "show the students lastname",
        "names of students"
    ]

    for query in nl_queries:
        print(f"\nNL: {query}")
        results = simplified_nlidb(query)
        if isinstance(results, str):
            print(results)
        else:
            print("Results:", results)
