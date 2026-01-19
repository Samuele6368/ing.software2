from __future__ import annotations  # Permette la valutazione ritardata delle annotazioni

import tkinter as tk                # Libreria tkinter per l'interfaccia grafica
from tkinter import messagebox, ttk

from api import api                 # Importa l'API per la gestione degli studenti e degli esami
from db.database import init_db     # Importa la funzione di inizializzazione del database


# Classe principale per l'interfaccia grafica dell'applicazione
class StudentExamGUI:

    # Inizializza la finestra principale
    def __init__(self, root: tk.Tk):  
        self.root = root
        self.root.title("StudentExamManager")
        self.root.geometry("1200x720")

        # Inizializza liste vuote per tenere traccia dei menu a tendina (Combobox)
        self.student_selectors: list[ttk.Combobox] = []
        self.course_selectors: list[ttk.Combobox] = []
        self.exam_selectors: list[ttk.Combobox] = []
        self.exam_value_map: dict[str, tuple[str, str]] = {}
        self._student_cache: list[dict] = []

        # Crea il layout principale diviso in due: menu a sinistra e contenuti a destra
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        self.menu_frame = ttk.Frame(self.main_frame)
        self.menu_frame.pack(side="left", fill="y")
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Inizializza il dizionario delle diverse schermate
        self.views: dict[str, ttk.Frame] = {}
        self._build_menu()
        self._build_student_view()
        self._build_course_view()
        self._build_enrollment_view()
        self._build_grades_view()
        self.show_view("studenti")

    # NAVIGAZIONE NEL MENU
    def _build_menu(self) -> None:
        buttons = [     # Crea i pulsanti del menu tramite un elenco di tuple (bottone, comando)
            ("Studenti", lambda: self.show_view("studenti")), # "lambda" ritarda l'esecuzione di "show.view" fino al click
            ("Corsi & Appelli", lambda: self.show_view("corsi")),
            ("Iscrizioni", lambda: self.show_view("iscrizioni")),
            ("Voti & Libretto", lambda: self.show_view("voti")),
            ("Chiudi", self.root.destroy),
        ]
        for text, command in buttons:
            ttk.Button(self.menu_frame, text=text, command=command).pack(fill="x", pady=5)


    def show_view(self, name: str) -> None:
        for frame in self.views.values():
            frame.pack_forget()  # "pack_forget" nasconde tutte le schermate
        frame = self.views[name] # "self.views" mostra la schermata selezionata
        frame.pack(fill="both", expand=True)
        if name == "studenti":
            self._refresh_students() # Aggiorna i dati nel database
        elif name == "corsi":
            self._refresh_courses()
        elif name == "iscrizioni":
            self._refresh_enrollment_data()
        elif name == "voti":
            self._refresh_grade_view()

    # SCHERMATA "STUDENTI"
    def _build_student_view(self) -> None:
        frame = ttk.Frame(self.content_frame, padding=10)
        self.views["studenti"] = frame

        form = ttk.LabelFrame(frame, text="Nuovo studente", padding=10) 
        form.pack(fill="x", pady=10)
        self.var_matricola = tk.StringVar() # "tk.StringVar" = variabili Tkinter per memorizzare i 
        self.var_nome = tk.StringVar()      # dati del form quando l'utente li inserisce
        self.var_cognome = tk.StringVar()
        ttk.Label(form, text="Matricola").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_matricola).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(form, text="Nome").grid(row=1, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_nome).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(form, text="Cognome").grid(row=2, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.var_cognome).grid(row=2, column=1, padx=5, pady=2)
        ttk.Button(form, text="Aggiungi", command=self._add_student).grid(row=0, column=2, rowspan=3, padx=10)

        table_frame = ttk.LabelFrame(frame, text="Elenco studenti", padding=10)
        table_frame.pack(fill="both", expand=True)

        # Creazione della tabella per l'elenco studenti con "Treeview"
        columns = ("matricola", "nome", "cognome")
        self.student_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.student_tree.heading(col, text=col.capitalize())
            self.student_tree.column(col, width=180)
        self.student_tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Modifica selezionato", command=self._edit_student).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Elimina selezionato", command=self._delete_student).pack(side="left", padx=5)

    # SCHERMATA "CORSI"
    # Vado a gestire due entità: Corsi e Appelli
    def _build_course_view(self) -> None:
        frame = ttk.Frame(self.content_frame, padding=10)
        self.views["corsi"] = frame

        course_form = ttk.LabelFrame(frame, text="Nuovo corso", padding=10)
        course_form.pack(fill="x", pady=10)
        self.var_course_code = tk.StringVar()
        self.var_course_name = tk.StringVar()
        self.var_course_cfu = tk.StringVar()
        ttk.Label(course_form, text="Codice").grid(row=0, column=0, sticky="w")
        ttk.Entry(course_form, textvariable=self.var_course_code).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(course_form, text="Nome").grid(row=1, column=0, sticky="w")
        ttk.Entry(course_form, textvariable=self.var_course_name).grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(course_form, text="CFU").grid(row=2, column=0, sticky="w")
        ttk.Entry(course_form, textvariable=self.var_course_cfu).grid(row=2, column=1, padx=5, pady=2)
        ttk.Button(course_form, text="Crea corso", command=self._add_course).grid(row=0, column=2, rowspan=3, padx=10)

        exam_form = ttk.LabelFrame(frame, text="Nuovo appello", padding=10)
        exam_form.pack(fill="x", pady=10)
        self.var_exam_course = tk.StringVar()
        self.var_exam_date = tk.StringVar()
        ttk.Label(exam_form, text="Codice corso").grid(row=0, column=0, sticky="w")
        course_combo = ttk.Combobox(exam_form, textvariable=self.var_exam_course, state="readonly")
        course_combo.grid(row=0, column=1, padx=5, pady=2)
        self.course_selectors.append(course_combo) 
        ttk.Label(exam_form, text="Data (YYYY-MM-DD)").grid(row=1, column=0, sticky="w")
        ttk.Entry(exam_form, textvariable=self.var_exam_date).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(exam_form, text="Crea appello", command=self._add_exam).grid(row=0, column=2, rowspan=2, padx=10)

        tables = ttk.Frame(frame)
        tables.pack(fill="both", expand=True)

        courses_frame = ttk.LabelFrame(tables, text="Corsi", padding=10)
        courses_frame.pack(side="left", fill="both", expand=True, padx=5)
        self.courses_tree = ttk.Treeview(courses_frame, columns=("codice", "nome", "cfu"), show="headings")
        for col in ("codice", "nome", "cfu"):
            self.courses_tree.heading(col, text=col.capitalize())
            self.courses_tree.column(col, width=100) # Larghezza colonne corsi
        self.courses_tree.pack(fill="both", expand=True)
        course_btns = ttk.Frame(courses_frame)
        course_btns.pack(fill="x", pady=5)
        ttk.Button(course_btns, text="Elimina corso", command=self._delete_course).pack(side="left")

        exams_frame = ttk.LabelFrame(tables, text="Appelli", padding=10)
        exams_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        # --- TABELLA APPELLI CON DATA ---
        self.exams_tree = ttk.Treeview(exams_frame, columns=("codice", "nome", "data"), show="headings")
        self.exams_tree.heading("codice", text="Codice")
        self.exams_tree.heading("nome", text="Corso")
        self.exams_tree.heading("data", text="Data")
        
        # Impostiamo la larghezza per assicurare che si vedano
        self.exams_tree.column("codice", width=100)
        self.exams_tree.column("nome", width=150)
        self.exams_tree.column("data", width=120)
        
        self.exams_tree.pack(fill="both", expand=True)
        exam_btns = ttk.Frame(exams_frame)
        exam_btns.pack(fill="x", pady=5)
        ttk.Button(exam_btns, text="Elimina appello", command=self._delete_exam).pack(side="left")

    # SCHERMATA "ISCRIZIONI"
    def _build_enrollment_view(self) -> None:
        frame = ttk.Frame(self.content_frame, padding=10)
        self.views["iscrizioni"] = frame

        enroll_box = ttk.LabelFrame(frame, text="Iscrivi studente", padding=10)
        enroll_box.pack(fill="x", pady=20)
        self.var_enroll_student = tk.StringVar()
        self.var_enroll_exam = tk.StringVar()
        ttk.Label(enroll_box, text="Matricola").grid(row=0, column=0, sticky="w")
        student_combo = ttk.Combobox(enroll_box, textvariable=self.var_enroll_student, state="readonly")
        student_combo.grid(row=0, column=1, padx=5, pady=2)
        self.student_selectors.append(student_combo)
        ttk.Label(enroll_box, text="Appello").grid(row=1, column=0, sticky="w")
        exam_combo = ttk.Combobox(enroll_box, textvariable=self.var_enroll_exam, state="readonly", width=40)
        exam_combo.grid(row=1, column=1, padx=5, pady=2)
        self.exam_selectors.append(exam_combo)
        ttk.Button(enroll_box, text="Iscrivi", command=self._enroll_student).grid(row=0, column=2, rowspan=2, padx=10)

        list_box = ttk.LabelFrame(frame, text="Iscrizioni correnti", padding=10)
        list_box.pack(fill="both", expand=True)
        columns = ("matricola", "studente", "codice", "corso", "data", "stato")
        self.enrollments_tree = ttk.Treeview(list_box, columns=columns, show="headings", height=12)
        headers = {
            "matricola": "Matricola",
            "studente": "Studente",
            "codice": "Codice",
            "corso": "Corso",
            "data": "Data",
            "stato": "Stato",
        }
        for col in columns:
            self.enrollments_tree.heading(col, text=headers[col])
            width = 140 if col in ("matricola", "codice", "data") else 200
            self.enrollments_tree.column(col, width=width)
        self.enrollments_tree.pack(side="left", fill="both", expand=True)
        enroll_scroll = ttk.Scrollbar(list_box, orient="vertical", command=self.enrollments_tree.yview)
        self.enrollments_tree.configure(yscrollcommand=enroll_scroll.set)
        enroll_scroll.pack(side="right", fill="y")
        ttk.Button(frame, text="Rimuovi iscrizione selezionata", command=self._delete_enrollment).pack(pady=10)

    # SCHERMATA "VOTI"
    def _build_grades_view(self) -> None:
        frame = ttk.Frame(self.content_frame, padding=10)
        self.views["voti"] = frame

        selector = ttk.LabelFrame(frame, text="Libretto studente", padding=10)
        selector.pack(fill="x", pady=10)
        self.var_grade_student = tk.StringVar()
        ttk.Label(selector, text="Matricola").grid(row=0, column=0, sticky="w")
        grade_combo = ttk.Combobox(selector, textvariable=self.var_grade_student, state="readonly")
        grade_combo.grid(row=0, column=1, padx=5, pady=2)
        self.student_selectors.append(grade_combo)
        ttk.Button(selector, text="Carica libretto", command=self._refresh_grade_view).grid(row=0, column=2, padx=10)

        columns = ("corso", "data", "voto", "lode", "stato", "codice", "appello")
        self.grades_tree = ttk.Treeview(frame, columns=columns, show="headings", height=14)
        headings = {
            "corso": "Corso",
            "data": "Data",
            "voto": "Voto",
            "lode": "Lode",
            "stato": "Stato",
        }
        for col in columns:
            title = headings.get(col, "")
            self.grades_tree.heading(col, text=title)
            width = 200 if col == "corso" else 120
            if col in ("codice", "appello"):
                width = 0
            self.grades_tree.column(col, width=width, stretch=col not in ("codice", "appello"))
        self.grades_tree.pack(fill="both", expand=True, pady=10)

        grade_form = ttk.LabelFrame(frame, text="Registra voto", padding=10)
        grade_form.pack(fill="x")
        self.var_grade_value = tk.StringVar()
        self.var_grade_lode = tk.BooleanVar()
        ttk.Label(grade_form, text="Voto (18-31)").grid(row=0, column=0, sticky="w")
        ttk.Entry(grade_form, textvariable=self.var_grade_value, width=10).grid(row=0, column=1, padx=5)
        ttk.Checkbutton(grade_form, text="Lode", variable=self.var_grade_lode).grid(row=0, column=2, padx=5)
        ttk.Button(grade_form, text="Salva voto", command=self._record_grade).grid(row=0, column=3, padx=10)
        ttk.Button(grade_form, text="Reset voto", command=self._reset_grade).grid(row=0, column=4, padx=10)

        self.average_label = ttk.Label(frame, text="Media: - | CFU totali: 0")
        self.average_label.pack(pady=10)

    # REFRESH:
    # Prende una lista di menu a tendina e aggiorna le opzioni disponibili.
    def _set_combobox_values(self, combos: list[ttk.Combobox], values: list[str]) -> None:
        for combo in combos:
            combo["values"] = values

    # AGGIUNTA STUDENTE
    def _add_student(self) -> None:
        matricola = self.var_matricola.get()
        # Validazione locale della matricola prima di chiamare l'API
        matricola_stripped = matricola.strip()
        if not matricola_stripped:
            messagebox.showerror("Errore", "Formato non valido: la matricola deve essere un numero intero.")
            return
        if not matricola_stripped.isdigit():
            messagebox.showerror("Errore", "Formato non valido: la matricola deve essere un numero intero.")
            return
        if int(matricola_stripped) <= 0:
            messagebox.showerror("Errore", "Formato non valido: la matricola deve essere un numero intero.")
            return
        # Chiamo l'API per aggiungere lo studente nel database
        try:
            api.add_student(matricola, self.var_nome.get(), self.var_cognome.get())
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return
        messagebox.showinfo("Successo", "Studente aggiunto con successo.")
        self.var_matricola.set("")
        self.var_nome.set("")
        self.var_cognome.set("")
        self._refresh_students()

    # MODIFICA STUDENTE
    def _edit_student(self) -> None:
        selection = self.student_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona uno studente.")
            return
        matricola, nome, cognome = self.student_tree.item(selection[0], "values")
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Modifica studente")
        tk.Label(edit_window, text="Nome").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(edit_window, text="Cognome").grid(row=1, column=0, padx=5, pady=5)
        nome_var = tk.StringVar(value=nome)
        cognome_var = tk.StringVar(value=cognome)
        tk.Entry(edit_window, textvariable=nome_var).grid(row=0, column=1, padx=5, pady=5)
        tk.Entry(edit_window, textvariable=cognome_var).grid(row=1, column=1, padx=5, pady=5)

        # salva le modifiche
        def save_changes() -> None:
            try:
                api.edit_student(matricola, nome_var.get(), cognome_var.get())
            except ValueError as exc:
                messagebox.showerror("Errore", str(exc))
                return
            messagebox.showinfo("Successo", "Studente aggiornato.")
            edit_window.destroy()
            self._refresh_students()

        ttk.Button(edit_window, text="Salva", command=save_changes).grid(row=2, column=0, columnspan=2, pady=10)

    # ELIMINA STUDENTE
    def _delete_student(self) -> None:
        selection = self.student_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona uno studente.")
            return
        matricola = self.student_tree.item(selection[0], "values")[0]
        if not messagebox.askyesno("Conferma", "Eliminare lo studente selezionato?"):
            return
        try:
            api.remove_student(matricola)
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return
        messagebox.showinfo("Successo", "Studente eliminato.")
        self._refresh_students()

    # AGGIUNTA CORSO
    def _add_course(self) -> None:
        try:
            cfu = int(self.var_course_cfu.get())
        except ValueError:
            messagebox.showerror("Errore", "I CFU devono essere numerici.")
            return
        try:
            api.add_course(self.var_course_code.get(), self.var_course_name.get(), cfu)
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return
        messagebox.showinfo("Successo", "Corso creato correttamente.")
        self.var_course_code.set("")
        self.var_course_name.set("")
        self.var_course_cfu.set("")
        self._refresh_courses()

    # AGGIUNTA ESAME
    def _add_exam(self) -> None:
        try:
            api.create_exam(self.var_exam_course.get(), self.var_exam_date.get())
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return
        messagebox.showinfo("Successo", "Appello creato.")
        self.var_exam_date.set("")
        self._refresh_exams()
        self._refresh_enrollments()

    # ELIMINA CORSO 
    def _delete_course(self) -> None:
        selection = self.courses_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un corso.")
            return
        codice = self.courses_tree.item(selection[0], "values")[0]
        if not messagebox.askyesno("Conferma", f"Eliminare il corso {codice}?"):
            return
        try:
            api.remove_course(codice)
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return
        messagebox.showinfo("Successo", "Corso eliminato.")
        self._refresh_courses()
        self._refresh_enrollments()

    # ELIMINA ESAME
    def _delete_exam(self) -> None:
        selection = self.exams_tree.selection()
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona un appello.")
            return
        course_codice, _, data_appello = self.exams_tree.item(selection[0], "values")
        if not messagebox.askyesno("Conferma", f"Eliminare l'appello {course_codice} - {data_appello}?"):
            return
        try:
            api.remove_exam(course_codice, data_appello)
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return
        messagebox.showinfo("Successo", "Appello eliminato.")
        self._refresh_exams()
        self._refresh_enrollments()

    # ISCRIZIONE STUDENTE
    def _enroll_student(self) -> None:
        matricola = self.var_enroll_student.get()
        exam_label = self.var_enroll_exam.get()
        if not matricola or not exam_label:
            messagebox.showwarning("Attenzione", "Seleziona studente e appello.")
            return
        course_codice, data_appello = self.exam_value_map.get(exam_label, ("", ""))
        try:
            api.enroll_student(matricola, course_codice, data_appello)
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return
        messagebox.showinfo("Successo", "Studente iscritto all'appello.")
        self.var_enroll_exam.set("")
        self._refresh_enrollments()

    # ELIMINA ISCRIZIONE
    def _delete_enrollment(self) -> None:
        selection = getattr(self, "enrollments_tree", None)
        if selection is None:
            return
        chosen = self.enrollments_tree.selection()
        if not chosen:
            messagebox.showwarning("Attenzione", "Seleziona un'iscrizione.")
            return
        values = self.enrollments_tree.item(chosen[0], "values")
        matricola, _, course_codice, _, data_appello, _ = values
        if not messagebox.askyesno(
            "Conferma", f"Rimuovere l'iscrizione di {matricola} a {course_codice} ({data_appello})?"
        ):
            return
        try:
            api.remove_enrollment(matricola, course_codice, data_appello)
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return
        messagebox.showinfo("Successo", "Iscrizione rimossa.")
        self._refresh_enrollments()
        self._refresh_grade_view()

    # REGISTRA VOTO
    def _record_grade(self) -> None:
        matricola = self.var_grade_student.get()
        selection = self.grades_tree.selection()
        if not matricola:
            messagebox.showwarning("Attenzione", "Seleziona una matricola.")
            return
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una registrazione.")
            return
        try:
            voto = int(self.var_grade_value.get())
        except ValueError:
            messagebox.showerror("Errore", "Il voto deve essere numerico.")
            return
        values = self.grades_tree.item(selection[0], "values")
        course_codice, data_appello = values[5], values[6]
        try:
            api.record_grade(matricola, course_codice, data_appello, voto, self.var_grade_lode.get())
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return
        messagebox.showinfo("Successo", "Voto registrato.")
        self.var_grade_value.set("")
        self.var_grade_lode.set(False)
        self._refresh_grade_view()

    # RESET VOTO
    def _reset_grade(self) -> None:
        matricola = self.var_grade_student.get()
        selection = self.grades_tree.selection()
        if not matricola:
            messagebox.showwarning("Attenzione", "Seleziona una matricola.")
            return
        if not selection:
            messagebox.showwarning("Attenzione", "Seleziona una registrazione.")
            return
        values = self.grades_tree.item(selection[0], "values")
        course_codice, data_appello = values[5], values[6]
        if not messagebox.askyesno(
            "Conferma", f"Reset del voto per {course_codice} ({data_appello}) per lo studente {matricola}?"
        ):
            return
        try:
            api.reset_grade(matricola, course_codice, data_appello)
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return
        messagebox.showinfo("Successo", "Voto ripristinato.")
        self._refresh_grade_view()

    # REFRESH STUDENTI
    def _refresh_students(self) -> None:
        students = self._fetch_students()
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for student in students:
            self.student_tree.insert("", "end", values=(student["matricola"], student["nome"], student["cognome"]))

    # RECUPERA STUDENTI
    def _fetch_students(self) -> list[dict]:
        try:
            students = api.list_students()
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return []
        self._student_cache = students
        self._set_combobox_values(self.student_selectors, [s["matricola"] for s in students])
        return students

    # REFFRESH CORSI
    def _refresh_courses(self) -> None:
        self._refresh_course_list()
        self._refresh_exams()

    # REFRESH LISTA CORSI
    def _refresh_course_list(self) -> None:
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)
        try:
            courses = api.list_courses()
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return
        for course in courses:
            self.courses_tree.insert("", "end", values=(course["codice"], course["nome"], course["cfu"]))
        self._set_combobox_values(self.course_selectors, [c["codice"] for c in courses])

    # REFRESH ESAMI
    def _refresh_exams(self) -> None:
        for item in self.exams_tree.get_children():
            self.exams_tree.delete(item)
        try:
            exams = api.list_exams()
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            exams = []
        exam_values: list[str] = []
        self.exam_value_map.clear()
        for exam in exams:
            self.exams_tree.insert("", "end", values=(exam["course_codice"], exam["course_nome"], exam["data_appello"]))
            label = f"{exam['course_codice']} | {exam['data_appello']}"
            exam_values.append(label)
            self.exam_value_map[label] = (exam["course_codice"], exam["data_appello"])
        self._set_combobox_values(self.exam_selectors, exam_values)

    # REFRESH DATI D'ISCRIZIONE
    def _refresh_enrollment_data(self) -> None:
        self._fetch_students()
        self._refresh_exams()
        self._refresh_enrollments()

    # REFRESH ISCRIZIONI
    def _refresh_enrollments(self) -> None:
        tree = getattr(self, "enrollments_tree", None)
        if tree is None:
            return
        for item in tree.get_children():
            tree.delete(item)
        try:
            registrations = api.list_registrations()
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            registrations = []
        for reg in registrations:
            tree.insert(
                "",
                "end",
                values=(
                    reg["matricola"],
                    reg["studente"],
                    reg["course_codice"],
                    reg["course_nome"],
                    reg["data_appello"],
                    reg["stato"],
                ),
            )

    # REFRESH VOTI
    def _refresh_grade_view(self) -> None:
        students = self._fetch_students()
        matricola = self.var_grade_student.get()
        if not matricola and students:
            self.var_grade_student.set(students[0]["matricola"])
            matricola = students[0]["matricola"]
        for item in self.grades_tree.get_children():
            self.grades_tree.delete(item)
        if not matricola:
            self.average_label.config(text="Media: - | CFU totali: 0")
            return
        try:
            transcript = api.get_transcript(matricola)
        except ValueError as exc:
            messagebox.showerror("Errore", str(exc))
            return
        for record in transcript["exams"]:
            self.grades_tree.insert(
                "",
                "end",
                values=(
                    record["course"],
                    record["data_appello"],
                    record["voto"] if record["voto"] is not None else "-",
                    "Si" if record["lode"] else "No",
                    record["stato"],
                    record["course_codice"],
                    record["data_appello"],
                ),
            )
        avg = transcript["average"] if transcript["average"] is not None else "-"
        self.average_label.config(text=f"Media: {avg} | CFU totali: {transcript['total_cfu']}")


def run_app() -> None:
    init_db()               # Crea le tabelle nel database se non esistono
    root = tk.Tk()          # Crea la finestra principale
    StudentExamGUI(root)    # Inizializza l'interfaccia grafica
    root.mainloop()         # Avvia il loop principale di Tkinter per gestire gli eventi dell'interfaccia grafica