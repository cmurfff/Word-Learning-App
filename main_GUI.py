import customtkinter as ctk
import sqlite3

from backend import add_category



ctk.set_appearance_mode("Dark")     
ctk.set_default_color_theme("blue") 

class ExpandableCategoryFrame(ctk.CTkFrame):
    def __init__(self, master, category_id, category_name, **kwargs):

        super().__init__(master, **kwargs)

        self.category_name = category_name  # Теперь плашка запомнит свое имя насовсем!
        
        self.category_id = category_id
        self.is_expanded = False # Переменная-флаг: раскрыта плашка или нет

        
        # 1. Верхняя плашка (Шапка категории)
        self.header_frame = ctk.CTkFrame(self, fg_color="#2c3e50", height=40)
        self.header_frame.pack(fill="x", padx=5, pady=2)

        
        # Название категории
        self.name_lbl = ctk.CTkLabel(self.header_frame, text=f"📁 {category_name}", text_color="white")
        self.name_lbl.pack(side="left", padx=15, pady=5)

        
        # Стрелочка (Юникод символ ▼ / ▲)
        self.arrow_btn = ctk.CTkButton(
            self.header_frame, 
            text="▼", 
            width=30, 
            fg_color="transparent", 
            text_color="white",
            hover_color="#34495e",
            command=self.toggle_expand # При клике вызываем функцию раздвигания
        )
        self.arrow_btn.pack(side="right", padx=10)

        
        # 2. Скрытый фрейм для списка слов (изначально просто создаем, но не упаковываем!)
        self.words_frame = ctk.CTkFrame(self, fg_color="#1a252f")
        
    def toggle_expand(self):


        from backend import get_words_with_stats_by_category
        
        if not self.is_expanded:


            # === РАЗДВИГАЕМ ПЛАШКУ ===
            self.arrow_btn.configure(text="▲") # Меняем стрелочку вверх
            self.words_frame.pack(fill="x", padx=5, pady=(0, 5)) # Показываем фрейм со словами

            
            # Очищаем старые лейблы слов внутри фрейма, если они были
            for widget in self.words_frame.winfo_children():
                widget.destroy()

                
            # Запрашиваем слова из бэкенда
            words = get_words_with_stats_by_category(self.category_name)
            
            if not words:
                no_words_lbl = ctk.CTkLabel(self.words_frame, text="No words in this category yet... 📝", text_color="gray")
                no_words_lbl.pack(pady=10)
            


            else:
                # Выводим каждое слово красивой строчкой со статистикой
                for word, translation, correct, total in words:
                    perc = round((correct / total) * 100) if total > 0 else 0
                    word_text = f"• {word} — {translation}  |  📊 {correct}/{total} ({perc}%)"
                        
                    word_lbl = ctk.CTkLabel(self.words_frame, text=word_text, anchor="w", font=ctk.CTkFont(size=14))
                    word_lbl.pack(fill="x", padx=20, pady=4)
                    
            self.is_expanded = True


        else:
            # === СВОРАЧИВАЕМ ПЛАШКУ ===
            self.arrow_btn.configure(text="▼") # Меняем стрелочку обратно вниз
            self.words_frame.pack_forget() # Полностью скрываем фрейм, интерфейс сам сожмется обратно вверх
            self.is_expanded = False




class WordApp(ctk.CTk):
    
    def __init__(self):
        super().__init__()
        
     
        self.title("Word Learning App")
        self.geometry("800x600")
        self.minsize(600, 450)

        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

       
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1e1e1e")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False) 

        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        self.sidebar_frame.grid_rowconfigure(0, minsize=49) 

        sidebar_font = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        sidebar_btn_font = ctk.CTkFont(family="Segoe UI", size=14, weight="normal")

        self.sidebar_label = ctk.CTkLabel(self.sidebar_frame, text="Control panel", font=sidebar_font)
        self.sidebar_label.grid(row=0, column=0, sticky="w", padx=20)

        
        self.sidebar_line = ctk.CTkFrame(self.sidebar_frame, height=2, corner_radius=0, fg_color="#2d2d2d")
        self.sidebar_line.grid(row=1, column=0, sticky="ew", padx=0)

       
        
        self.btn_add_cat = ctk.CTkButton(
            self.sidebar_frame, 
            text="📂 Create a new category", 
            height=40, 
            font=sidebar_btn_font,
            corner_radius=6, 
            command=self.open_add_category_screen  
        )
        self.btn_add_cat.grid(row=2, column=0, sticky="ew", padx=15, pady=(10, 0))


        self.btn_add_words = ctk.CTkButton(
            self.sidebar_frame, 
            text="📝 Add Words", 
            height=40, 
            font=sidebar_btn_font,
            corner_radius=6, 
            command=self.open_add_words_screen  
        )
        self.btn_add_words.grid(row=3, column=0, sticky="ew", padx=15, pady=(10, 0))

         
        self.btn_train = ctk.CTkButton(
            self.sidebar_frame,
            text="training",
            height=40,
            font=sidebar_btn_font,
            corner_radius=6,
            command=self.open_training_menu
        )
        self.btn_train.grid(row=4,column=0, sticky="ew", padx = 15, pady=(10, 0))


        self.btn_manage = ctk.CTkButton(
            self.sidebar_frame, 
            text="🗑️ manage dictionary ", 
            height=40, 
            font=sidebar_btn_font,
            corner_radius=6, 
            command=self.open_manage_dictionary_screen  
        )
        self.btn_manage.grid(row=5, column=0, sticky="ew", padx=15, pady=10)

        
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew")
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_rowconfigure(0, minsize=50, weight=0) 
        self.right_container.grid_rowconfigure(1, weight=1) 

        
        self.top_bar_frame = ctk.CTkFrame(self.right_container, height=50, corner_radius=0, fg_color="#252526")
        self.top_bar_frame.grid(row=0, column=0, sticky="nsew")

        
        self.settings_btn = ctk.CTkButton(
            self.top_bar_frame, text="⚙️", 
            width=38, 
            height=38, 
            font=ctk.CTkFont(size=16),
            command=self.open_settings
        )
        self.settings_btn.pack(side="right", padx=10, pady=8)

        self.statik_btn = ctk.CTkButton(
            self.top_bar_frame, text="📊", 
            width=38, 
            height=38, 
            font=ctk.CTkFont(size=22),
            command=self.open_stats_menu    
        

        )
        self.statik_btn.pack(side="right", padx=10, pady=8)



        self.main_content_frame = ctk.CTkFrame(self.right_container, corner_radius=0, fg_color="#121212")
        self.main_content_frame.grid(row=1, column=0, sticky="nsew")

        self.main_content_font = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")

        
        self.main_label = ctk.CTkLabel(self.main_content_frame, text="Welcome 👋 \nSelect an action from the menu\nand you can view the guide in the settings⚙️", font=self.main_content_font)
        self.main_label.pack(expand=True)


   
    def open_settings(self):
        self.clear_center()


        self.main_content_frame.grid_columnconfigure(0, weight=1)

        help_title = ctk.CTkLabel(
            self.main_content_frame,
            text="📖 User Manual ",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        )
        help_title.grid(row=0, column=0,pady=(30,20))

        help_text=(
            "ENG:\n"
            "    How to use the app:\n"
            "    1. Select a training mode or add new words from the menu on the left.\n"
            "    2. Enter your data into the text fields and click the confirmation buttons.\n\n"
            "    👥 How to share your words with a friend:\n"
            "    All your categories and added words are saved\n"
            "    into one small database file: 'all_categories.db'.\n\n"
            "    To share your word lists, simply\n"
            "    copy this file and send it to your friend.\n"
            "    They just need to place your file into their app\n"
            "    folder, replacing their old database file!\n\n\n"
            "RU:"
            "\n   Как пользоваться приложением:\n"
            "   1. Выберите режим тренировки или добавления в меню слева.\n"
            "   2. Вводите данные в текстовые поля и нажимайте кнопки подтверждения.\n\n"
            "   👥 Как передать свои слова другу:\n"
            "   Все ваши категории и добавленные слова сохраняются\n"
            "   в один небольшой файл базы данных: 'all_categories.db'.\n\n"
            "   Чтобы поделиться своими списками слов, просто\n"
            "   скопируйте этот файл и отправьте его другу.\n"
            "   Ему достаточно положить ваш файл в папку со своей\n"
            "   программой, заменив свой старый файл базы данных!")

        help_label = ctk.CTkLabel(
            self.main_content_frame, 
            text=help_text, 
            font=ctk.CTkFont(family="Segoe UI", size=20), 
            justify="left"
        )
      
        help_label.grid(row=1, column=0, padx=40, pady=10)





    def clear_center(self):
       
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()


   
    def open_add_category_screen(self):
       
        self.clear_center() 
        
       
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            self.main_content_frame, 
            text="Create a new category ", 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        )
        title.grid(row=0, column=0, pady=(40, 20))

       
        self.new_cat_input = ctk.CTkEntry(
            self.main_content_frame, 
            placeholder_text="input category name...", 
            width=300, 
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=15)
        )
        self.new_cat_input.grid(row=1, column=0, pady=10)

    
        self.cat_status_lbl = ctk.CTkLabel(
            self.main_content_frame, 
            text="", 
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.cat_status_lbl.grid(row=2, column=0, pady=10)

        
        btn_save_cat = ctk.CTkButton(
            self.main_content_frame, 
            text="Save category", 
            width=200, 
            height=40, 
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            command=self.save_new_category  
        )
        btn_save_cat.grid(row=3, column=0, pady=10)

    

    def save_new_category(self):
       
        
        name = self.new_cat_input.get().strip()
        
        
        if not name:
            self.cat_status_lbl.configure(text="name category  cant empty! ❌", text_color="#e74c3c")
            return
        
        
        success = add_category(name)
        
        
        if success:
            
            self.cat_status_lbl.configure(text=f"category '{name}' create! 🎉", text_color="#2ecc71")
            self.new_cat_input.delete(0, 'end') 
        else:
            
            self.cat_status_lbl.configure(text="error: Such a category already exists! ❌", text_color="#e74c3c")


    def open_add_words_screen(self):
        
        self.clear_center() 
                
                
        self.main_content_frame.grid_columnconfigure(0, weight=1)
                
                
        title = ctk.CTkLabel(
            self.main_content_frame, 
            text="add a new words ", 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        )
        title.grid(row=0, column=0, pady=(30, 20))

        from backend import get_all_categories
        db_categories = get_all_categories()
        if not db_categories:
            db_categories=[f'first, create a new category']

        self.add_words_cat_select = ctk.CTkOptionMenu(
            self.main_content_frame,
            values=db_categories,
            width=300,
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=15)
        )
        self.add_words_cat_select.grid(row=1, column=0, pady=10)

                
        hint_lbl = ctk.CTkLabel(
            self.main_content_frame,
            text="Enter words in the format: word : translation (each word on a new line)",
            font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic"),
            text_color="gray"
        )
        hint_lbl.grid(row=2, column=0, pady=(10, 5))


        self.bulk_words_textbox = ctk.CTkTextbox(
            self.main_content_frame,
            width=450,
            height=200,
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.bulk_words_textbox.grid(row=3, column=0, pady=10)

        self.bulk_words_textbox.insert("1.0", "apple : яблоко\ncat : кот\ndog : собака")

        self.bulk_words_textbox.bind(
            "<FocusIn>",
            lambda event: self.clear_placeholder()

        )

    def clear_placeholder(self):
        
        try:
            
            current_text = self.bulk_words_textbox.get("1.0", "end-1c").strip()
            
            
            placeholder = "apple : яблоко\ncat : кот\ndog : собака"
            
            
            if current_text.replace(" ", "") == placeholder.replace(" ", ""):
                
                self.bulk_words_textbox.delete("1.0", "end")
        except Exception:
            pass 
        

        self.words_status_lbl = ctk.CTkLabel(
            self.main_content_frame, 
            text="", 
            font=ctk.CTkFont(family="Segoe UI", size=14)
            )
        self.words_status_lbl.grid(row=4, column=0, pady=10)
        
               
        btn_save = ctk.CTkButton(
            self.main_content_frame, 
            text="add words", 
            width=200, 
            height=40, 
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            command=self.save_new_words 
        )
        btn_save.grid(row=5, column=0, pady=15)


    def save_new_words(self):

        from backend import add_words

        selected_cat = self.add_words_cat_select.get()

        if selected_cat == "First, create a new category! 📂" :
            self.word_status_lbl.configure(text="Please choose a valid category! ⚠️", text_color="#f39c12")
            return
        raw_text = self.bulk_words_textbox.get("1.0", "end").strip()

        if not raw_text:
            self.bulk_words_textbox(text="Input field is empty! ⚠️", text_color='#ff0000')
            return

        words_dictonary = {}
        error_lines = 0

        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                parts = line.split(":", 1)
                word = parts[0].strip()
                translation = parts[1].strip()

                if word and translation:
                    words_dictonary[word] = translation
                else:
                    error_lines += 1
            else:
                error_lines += 1

        if not words_dictonary:
            self.words_status_lbl.configure(text="Not a single correct line found! ❌", text_color="#ff0000")
            self.bulk_words_textbox.delete("2.0", "end")
            return

        success = add_words(selected_cat, words_dictonary)


        if success:
            count = len(words_dictonary)
            msg = f"{count} words successfully added"

            if error_lines > 0:
                msg += f"Missing lines with errors: {error_lines} ⚠️)"
            self.words_status_lbl.configure(text=msg,text_color="#2ecc71")

            self.bulk_words_textbox.delete("1.0", "end")

        else:
            self.words_status_lbl.configure(text="Error saving the list to the database ❌", text_color="#e74c3c")

        self.after(1500, self.clear_status_message)

    def clear_status_message(self):
        """Clears the status text after the timer ends to prevent text overlapping"""
        if self.words_status_lbl.winfo_exists():
            self.words_status_lbl.configure(text="") 



   
        
    def open_training_menu(self):
        from backend import reset_session
        reset_session()

        self.clear_center() 
                
       
        title = ctk.CTkLabel(
            self.main_content_frame, 
            text="Select a Category to Start", 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        )
        title.pack(pady=(60, 20))

       
        from backend import get_all_categories
        categories = get_all_categories()

        if not categories:
            categories = ["First, create a category! 📂"]

       
        self.select_category = ctk.CTkOptionMenu(
            self.main_content_frame,
            values=categories,
            width=300,
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=15)
        )
        self.select_category.pack(pady=20)

      
        btn_start = ctk.CTkButton(
            self.main_content_frame,
            text="Start Training 🚀",
            width=250,
            height=45,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            corner_radius=6,
            command=self.start_training_session  
        )
        btn_start.pack(pady=0)

    
    def start_training_session(self):
   
        self.selected_category = self.select_category.get()
        
        if self.selected_category == "First, create a category! 📂":
            return
            
        
        from backend import reset_session
        reset_session()
        self.temporary_word=0  #переменная дял удаления из использованых слов временые слова
        
        
        self.show_next_word()

    def show_next_word(self):
        
        self.clear_center() # Clear center frame
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        
        
        from backend import pick_word
        


        
        current_cat = self.selected_category.strip()
        if "First, create a category!" in current_cat:
            current_cat = "food" 

        
       
        word_row = pick_word(current_cat)
        
            
        if word_row:
            self.current_word_id = word_row[0]       # ТЕПЕРЬ ПРОГРАММА ЗНАЕТ ID СЛОВА!
            self.current_word = word_row[1]
            self.correct_translation = word_row[2]
            self.weight=word_row[3]
            self.current_category_id = word_row[4] # Запоминаем числовой ID категории для статистики
        else:
            self.current_word_id, self.current_word, self.correct_translation, self.current_category_id = None, None, None, None
            
       

        
        
        if self.current_word is None:
            end_lbl = ctk.CTkLabel(
                self.main_content_frame, 
                text="Perfect! You've learned all words in this category! 🎉", 
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                text_color="#2ecc71"
            )
            end_lbl.grid(row=0, column=0, pady=50)
            return

        
        self.word_display = ctk.CTkLabel(
            self.main_content_frame, 
            text=self.current_word, 
            font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold")
        )
        self.word_display.grid(row=0, column=0, pady=(50, 20))

       
        self.user_input = ctk.CTkEntry(
            self.main_content_frame, 
            placeholder_text="Type  translation here...", 
            width=300, 
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=15)
        )
        self.user_input.grid(row=1, column=0, pady=10)

        self.user_input.bind("<Return>", lambda event: self.check_training_answer())

        # 3. Скрытая строка статуса ответа (row=2)
        self.train_status_lbl = ctk.CTkLabel(
            self.main_content_frame, 
            text="", 
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        )
        self.train_status_lbl.grid(row=2, column=0, pady=10)

        
        btn_check = ctk.CTkButton(
            self.main_content_frame,
            text="Check Answer",
            width=200,
            height=40,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            command=self.check_training_answer
        )
        btn_check.grid(row=3, column=0, pady=15)



   
    def check_training_answer(self):
        from backend import check_answer, used_words_in_session,redact_weight
        
        
        user_text = self.user_input.get()
        
        
        is_correct  = check_answer(
            user_text, 
            self.correct_translation,
            self.current_word_id,       # Передаем ID слова
            self.current_category_id    # Передаем ID категории
            
        )
        redact_weight(self.current_word_id,self.weight,is_correct)
        if self.temporary_word!=0 and len(used_words_in_session) >=1:
            if self.temporary_word==1:
                del used_words_in_session[-1]
        

        if is_correct:
           
            if self.current_word not in used_words_in_session:
                used_words_in_session.append(self.current_word)

            self.temporary_word=2   # для того чтобы слово которое должно быть в used_words_in_session  не удалялось 

            self.train_status_lbl.configure(text="Correct! Excellent job! ✨", text_color="#2ecc71")
            
            self.after(1500, self.show_next_word)
            

        else:
            if self.current_word not in used_words_in_session:
                used_words_in_session.append(self.current_word)
            

            self.temporary_word=1   # для удаления временого слова

            self.train_status_lbl.configure(
                text=f"Wrong answer! Try again ❌\n(Hint: {self.correct_translation})", 
                text_color="#e74c3c"
            )
            self.after(2000, self.show_next_word)


    def open_manage_dictionary_screen(self):

        

        self.clear_center()

        self.main_content_frame.grid_columnconfigure(0, weight=1)

        title= ctk.CTkLabel(
            self.main_content_frame,
            text="Dictonary managment ",
            font=ctk.CTkFont(family="Segoe UI", size=20,weight="bold")
        )
        title.grid(row=0,column=0, pady=(30,20))

        from backend import get_all_categories

        categories=get_all_categories()

        if not categories:
            no_category_lbl= ctk.CTkLabel(
                self.main_content_frame,
                text="Your dictionary is empty. Create a category first 📂 ",
                font=ctk.CTkFont(family="Segoe UI",size=15,slant="italic"),
                text_color="gray"
            )
            no_category_lbl.grid(row=1,column=0,pady=30)
            return


        self.scroll_container = ctk.CTkScrollableFrame(
            self.main_content_frame,
            width=500,
            height=350,
            fg_color="transparent"
        )
        self.scroll_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)


        self.category_dropdowns = {}


        for index, name in enumerate(categories):
            row_frame = ctk.CTkFrame(self.scroll_container, height=30, fg_color="#2c3e50", corner_radius=6)
            row_frame.grid(row=index * 2, column=0, sticky="ew", padx=10, pady=5)
            row_frame.grid_columnconfigure(0, weight=1) 

            cat_lbl = ctk.CTkLabel(
                row_frame, 
                text=f"📂 {name}", 
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
            )
            cat_lbl.grid(row=0, column=0,  padx=15, pady=(16,5), sticky="w")

            btn_del_cat = ctk.CTkButton(
                row_frame,
                text="🗑️",
                width=40,
                height=30,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                hover_color="#750c00", 
                text_color="#e74c3c",
                command=lambda name=name: self.delete_entire_category(name)  
            )
            btn_del_cat.grid(row=0,column=1, padx=(5, 0), pady=10, sticky="e")


            btn_toggle = ctk.CTkButton(
                row_frame,
                text="▶", 
                width=40,
                height=30,
                font=ctk.CTkFont(size=20, weight="bold"),
                fg_color="transparent",
                hover_color="#34495e",
                command=lambda name=name: self.toggle_category_words(name)
            )
            btn_toggle.grid(row=0, column=2, padx=15, pady=10, sticky="e")

            words_sub_frame = ctk.CTkFrame(self.scroll_container, fg_color="#1a252f", corner_radius=4)

            self.category_dropdowns[name] = {
                "frame": words_sub_frame,
                "button": btn_toggle,
                "is_open": False,
                "row_index": index * 2 + 1
            }






    def toggle_category_words(self, cat_name):
        
        data = self.category_dropdowns[cat_name]
        sub_frame = data["frame"]
        btn = data["button"]
        
        if data["is_open"]:
            
            sub_frame.grid_forget()
            btn.configure(text="▶")
            data["is_open"] = False
        else:
            
            btn.configure(text="▼")
            sub_frame.grid(row=data["row_index"], column=0, sticky="ew", padx=20, pady=(0, 5))
            sub_frame.grid_columnconfigure(0, weight=1)
            
            
            for child in sub_frame.winfo_children():
                child.destroy()
                
            
            import sqlite3
            from backend import DB_NAME
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            
            cursor.execute("SELECT id FROM categories WHERE name = ?", (cat_name.strip(),))
            cat_row = cursor.fetchone()
            
            if cat_row:
                
                category_id = cat_row[0]
                
                
                cursor.execute("SELECT id, word, translation FROM words WHERE category_id = ?", (category_id,))
                words = cursor.fetchall()
                
                if not words:
                    empty_lbl = ctk.CTkLabel(sub_frame, text="   No words in this category yet... 📝", font=ctk.CTkFont(slant="italic"), text_color="gray")
                    empty_lbl.grid(row=0, column=0, pady=10, sticky="w")
                else:
                    
                    for w_idx, (w_id, word, trans) in enumerate(words):
                        word_line = ctk.CTkFrame(sub_frame, fg_color="transparent")
                        word_line.grid(row=w_idx, column=0, sticky="ew", padx=10, pady=2)
                        word_line.grid_columnconfigure(0, weight=1)
                        
                        
                        text_display = f"• {word}  :  {trans}"
                        w_lbl = ctk.CTkLabel(word_line, text=text_display, font=ctk.CTkFont(family="Segoe UI", size=13))
                        w_lbl.grid(row=0, column=0, sticky="w", padx=5, pady=2)
                        
                        
                        btn_del_word = ctk.CTkButton(
                            word_line,
                            text="❌",
                            width=25,
                            height=25,
                            fg_color="transparent",
                            hover_color="#e74c3c",
                            text_color="#e74c3c",
                            font=ctk.CTkFont(size=11, weight="bold"),
                            command=lambda wid=w_id, cname=cat_name: self.delete_word_by_id(wid, cname)
                        )
                        btn_del_word.grid(row=0, column=1, sticky="e", padx=5, pady=2)
            
            conn.close()
            data["is_open"] = True




    def delete_word_by_id(self, word_id, cat_name):
        
        import sqlite3
        from backend import DB_NAME
        
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM words WHERE id = ?", (word_id,))
            conn.commit()
            conn.close()
            
            
            self.category_dropdowns[cat_name]["is_open"] = False
            self.toggle_category_words(cat_name)
            
        except sqlite3.Error as e:
            print(f"Error deleting word: {e}")

    def delete_entire_category(self, name):
       
        import sqlite3
        from backend import DB_NAME

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            
            cursor.execute("SELECT id FROM categories WHERE name = ?", (name.strip(),))
            category_row = cursor.fetchone()

            if category_row:
                category_id = category_row[0]

                
                cursor.execute("DELETE FROM words WHERE category_id = ?", (category_id,))
                
               
                cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))

                
                conn.commit()
            
           
            conn.close()

           
            self.open_manage_dictionary_screen()

        except sqlite3.Error as e:
            print(f"Error deleting category: {e}")


    def open_stats_menu(self):
        self.clear_center()
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        
        from backend import get_all_categories
        categories = get_all_categories() # Твой бэкенд возвращает список кортежей [(id, name), ...]
        
                # Используем enumerate, чтобы автоматом получить числа 0, 1, 2... как ID
        for index, row in enumerate(categories):
            # Так как row — это чистая строка с именем, берем её целиком!
            cat_id = index
            cat_name = row  # Берем всё слово целиком (например, "food")
            
            item = ExpandableCategoryFrame(
                self.main_content_frame,
                category_id=cat_id,
                category_name=cat_name
            )
            item.pack(fill="x", padx=10, pady=5)




      

if __name__ == "__main__":
    app = WordApp()
    app.mainloop()

