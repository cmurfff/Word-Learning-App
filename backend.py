import os
import random
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))



used_words_in_session = []
choose_another_category=None
DB_NAME = os.path.join(BASE_DIR, "all_categories.db")
FILEPATH = DB_NAME

def log_word_attempt(word_id, category_id, is_correct):
    # Используем твой правильный путь к базе (переменная DB_NAME)
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # 1. Если этого слова ещё нет в таблице статистики — создаем для него строку
        # и сразу привязываем его к числовому ID категории
        cursor.execute("""
            INSERT OR IGNORE INTO stats (word_id, category_id) 
            VALUES (?, ?)
        """, (word_id, category_id))
        
        # 2. Обновляем счётчики в зависимости от флага (True/False)
        if is_correct:
            # Если True: +1 ко всем попыткам и +1 к правильным
            cursor.execute("""
                UPDATE stats 
                SET total_attempts = total_attempts + 1,
                    correct_attempts = correct_attempts + 1
                WHERE word_id = ?
            """, (word_id,))
        else:
            # Если False: только +1 ко всем попыткам (правильные не трогаем)
            cursor.execute("""
                UPDATE stats 
                SET total_attempts = total_attempts + 1
                WHERE word_id = ?
            """, (word_id,))
    finally:
        conn.commit()
        conn.close()





def prepare_session_table(category_name):
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))


    row=cursor.fetchone()
    if row is  None:
        conn.close()
        return False
    category_id=row[0]
    cursor.execute('''
    CREATE TEMP TABLE IF NOT EXISTS temp_session_words(
    word TEXT,
    translation TEXT
    )
    ''')

    cursor.execute("DELETE FROM temp_session_words")

    cursor.execute('''
    INSERT INTO temp_session_words(word, translation)
    SELECT word,translation  FROM words WHERE category_id=?
''', (category_id,))
    conn.commit()
    return conn
 

def init_db(db_path=DB_NAME):
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id integer primary key AUTOINCREMENT ,
            name text unique not null
    )''')
    cursor.execute(''' 
        CREATE  TABLE IF NOT EXISTS words(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            word TEXT NOT NULL,
            translation TEXT NOT NULL,
            weight INTEGER DEFAULT 1,
            FOREIGN KEY (category_id) REFERENCES categories(id)
            
            )
        ''')
    


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stats (
        word_id INTEGER PRIMARY KEY,
        category_id INTEGER,
        total_attempts INTEGER DEFAULT 0,
        correct_attempts INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def get_random_word(category_name):
    conn= sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    category_row= cursor.fetchone()

    if category_row is None:
        conn.close()
        return None,None
    
    category_id = category_row[0]

    cursor.execute(
        "SELECT word, translation FROM words WHERE category_id = ? ORDER BY RANDOM() LIMIT 1",
        (category_id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None, None
    
    return row[0], row[1]

def get_session_word(category_name):

    global used_words_in_session

    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))

    category_row = cursor.fetchone()

    if category_row is None :
        conn.close()
        return None,None

    category_id = category_row[0]
    cursor.execute("SELECT COUNT(*) FROM words WHERE category_id = ?", (category_id,))
    count_row = cursor.fetchone()
    total_words = count_row[0] if count_row else 0
    
    

    if used_words_in_session:
        placeholders = ', '.join('?' for _ in used_words_in_session)
        query = f'''
            SELECT word, translation FROM words
            WHERE category_id = ? AND word NOT IN ({placeholders})
            ORDER BY RANDOM() LIMIT 1

        '''
        cursor.execute(query, (category_id, *used_words_in_session))
    else:
        cursor.execute(
            "SELECT word, translation FROM words WHERE category_id = ? ORDER BY RANDOM() LIMIT 1",
            (category_id,)
        )
    row= cursor.fetchone()
    conn.close()

    if row is None:
        return None,None

    used_words_in_session.append(row[0])

    return row[0], row[1]

def reset_session():
    global used_words_in_session
    used_words_in_session.clear()
    

def add_category(category_name):

    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()
    
    try:
        cursor.execute("INSERT INTO categories (name) VALUES(?)",(category_name,))
        conn.commit()
    
        return True
            
    except sqlite3.IntegrityError:
        return False
            
    finally:
        conn.close()


def add_words(category_name, words_dict):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Сначала пытаемся найти ID категории по имени
    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name.strip(),))
    row = cursor.fetchone()
    
    # 🌟 АВТОМАТИЧЕСКАЯ ПОДСТРАХОВКА:
    # Если в ЭТОМ файле базы данных темы нет, мы её тут же САМИ создаём!
    if row is None:
        try:
            # Создаем категорию прямо в текущем активном файле базы
            cursor.execute("INSERT INTO categories (name) VALUES(?)", (category_name.strip(),))
            conn.commit() # Сохраняем категорию на диск
            
            # Сразу же берём её новенький ID
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name.strip(),))
            row = cursor.fetchone()
        except sqlite3.Error as e:
            print(f"🔴 Auto-create category failed: {e}")
            conn.close()
            return False
       
    category_id = row[0] # Теперь здесь ЖЕЛЕЗНО будет лежать правильный числовой ID
    saved_counter = 0    

    # 2. Спокойно бежим циклом по нашему словарю
    for word, translation in words_dict.items():
        try:
            # Проверяем, нет ли уже такого слова именно в этой теме
            cursor.execute(
                "SELECT id FROM words WHERE category_id = ? AND word = ?", 
                (category_id, word.strip())
            )
            if cursor.fetchone() is not None:
                continue # Дубликат слова просто пропускаем
                
            # Добавляем уникальное новое слово
            cursor.execute(
                "INSERT INTO words (category_id, word, translation) VALUES (?,?,?)",
                (category_id, word.strip(), translation.strip())
            )
            saved_counter += 1 
            
        except sqlite3.Error as error:
            print(f"🔴 Word '{word}' skipped due to error: {error}")
            continue 

    conn.commit()
    conn.close()

    # Если мы успешно записали хотя бы одно новое слово — это победа!
    if saved_counter > 0:
        return True
    else:
        return False








def get_all_categories():
    conn = sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    cursor.execute("SELECT name FROM categories")
    rows = cursor.fetchall()
    conn.close()

    categories_list = []
    for row in rows:
        categories_list.append(f"{row[0]}\n")

    return categories_list

def check_answer(user_translation, correct_translation, word_id, category_id):

    user_clean = user_translation.lower().strip()
    correct_clean = correct_translation.lower().strip()

    if user_clean==correct_clean:

        message = "Правильный ответ! ✨"
        is_correct=True
    else:
        message = f"Неправильно. Правильный перевод: {correct_translation}"
        is_correct=False
    log_word_attempt(word_id, category_id, is_correct)
    return is_correct
    
        


def remove_words(category_name, words):
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    row=cursor.fetchone()

    if row is None:
        
        conn.close()
        return False

    try:
        category_id = row[0]

        for word in words:
            cursor.execute(
                "DELETE FROM words WHERE category_id = ? AND word = ?",
                (category_id, word)
            )
        
            
        conn.commit()
        return True

    except sqlite3.Error as error:
        return False
        
    finally:
        conn.close()


def remove_category(category_name):
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return False
    
    try:
        category_id=row[0]
        cursor.execute("DELETE FROM words WHERE category_id = ?", (category_id,))
        cursor.execute("DELETE FROM categories WHERE id=?", (category_id,))
        conn.commit()
        return True

    except sqlite3.Error as error:
        return False
        
    finally:
        conn.close()


def list_all_categories():
    conn=sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    result_dict={}

    cursor.execute("SELECT id,name FROM categories")
    categories=cursor.fetchall()

    for category_id, category_name in categories:
        
        cursor.execute("SELECT word,translation FROM words WHERE category_id=?", (category_id,))
        words=cursor.fetchall()

        result_dict[category_name] =  words
        
    conn.close()
    return result_dict


def list_all_categories_formatted():
    conn = sqlite3.connect(DB_NAME)
    cursor=conn.cursor()

    result_dict = {}

    cursor.execute("SELECT id, name FROM categories ")
    categories = cursor.fetchall()

    for category_id,category_name in categories:
        cursor.execute("SELECT word, translation FROM words WHERE category_id = ? ", (category_id,))
        words=cursor.fetchall()

        formatted_words = []
        
        for word,translation in words:
            line = f"{word} : {translation}"
            formatted_words.append(line)

        result_dict[category_name] = formatted_words

    conn.close()
    return result_dict

"""
def get_words_with_stats_by_category(category_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Используем LEFT JOIN, чтобы вытащить даже те слова, 
        # которые пользователь еще ни разу не тренировал (у них в статистике будут нули)
        cursor.execute(
            SELECT w.word, w.translation, 
                IFNULL(s.correct_attempts, 0), 
                IFNULL(s.total_attempts, 0)
            FROM words w
            LEFT JOIN stats s ON w.id = s.word_id
            WHERE w.category_id = (SELECT id FROM categories WHERE name = ?)
        , (category_id,))
        
        rows = cursor.fetchall()
    finally:
        conn.close()
    return rows 
"""
def get_words_with_stats_by_category(category_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Срезаем невидимый \n, превращая "food\n" в "food"
    clean_name = category_name.strip()
    
    # Идеальный и простой JOIN: связываем слова с категориями, 
    # а в конце ищем строго по текстовому имени clean_name
    cursor.execute("""
        SELECT w.word, w.translation, 
               IFNULL(s.correct_attempts, 0), 
               IFNULL(s.total_attempts, 0)
        FROM words w
        JOIN categories c ON w.category_id = c.id
        LEFT JOIN stats s ON w.id = s.word_id
        WHERE c.name = ?
    """, (clean_name,))
    
    rows = cursor.fetchall()
    conn.close()
    return rows


def redact_weight(word_id,weight,is_correct): # берет текущий вес,статус ответа,айди слова  для изменения веса 


    #проверяет вес чтобы он не взлетел вв верх или не упал ниже 1
    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        if is_correct==False and weight <20:     
                weight+=1
                cursor.execute("UPDATE words SET weight = ? WHERE id = ?",(weight, word_id))


        elif is_correct==True and weight >=3:   #если статус ответа правильный и вес больше 3 (объяснение почему выше)  уменьшает вес на 2
            weight-=2
            cursor.execute("UPDATE words SET weight = ? WHERE id=?",
                (weight,word_id)
            )


        conn.commit()

    finally:
        
        conn.close()
def pick_word(current_cat):
    conn=sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM categories WHERE name = ?", (current_cat,))
    cat_row = cursor.fetchone()
                
    if cat_row is None:
                    
        cursor.execute("INSERT INTO categories (name) VALUES(?)", (current_cat,))
        conn.commit()
        cursor.execute("SELECT id FROM categories WHERE name = ?", (current_cat,))
        cat_row = cursor.fetchone()
        
    category_id = cat_row[0] # Чистое число ID
                
                
    if used_words_in_session:
        placeholders = ', '.join('?' for _ in used_words_in_session)
        query = f"""
            SELECT id , word, translation, weight FROM words 
            WHERE category_id = ? AND word NOT IN ({placeholders}) 
            
        """
        cursor.execute(query, (category_id, *used_words_in_session))
    else:
        cursor.execute(
            "SELECT id,word, translation,weight FROM words WHERE category_id = ? ",
        (category_id,))
                
        
       
                    
    words=cursor.fetchall()
    if not words:
        return None

    weights=[w[3] for w in words]
    chosen = random.choices(words, weights=weights, k=1)[0]

    conn.close()
    return chosen[0], chosen[1], chosen[2], chosen[3], category_id

    





init_db()
