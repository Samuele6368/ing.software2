/*crea la tabella "students" nel caso non esista*/
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricola TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL
);

/*crea la tabella "courses" nel caso non esista*/
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    cfu INTEGER NOT NULL
);

/*crea la tabella "exams" nel caso non esista*/
/*ON DELETE CASCADE garantisce che, se un Corso viene eliminato tutti i relativi Appelli d'esame vengano cancellati automaticamente a cascata. Questo impedisce di avere nel database "esami orfani" che puntano a un corso inesistente.*/
CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    data_appello TEXT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

/*crea la tabella "registrations" nel caso non esista*/
/*"registrations" è stata inserita per eliminare la relazione molti a molti tra students ed exams*/
/* Doppio Vincolo di Integrità (Integrità della Relazione Molti-a-Molti):
       1. Se lo STUDENTE viene cancellato (es. si ritira), eliminiamo tutti i suoi voti/iscrizioni.
       2. Se l'ESAME viene annullato (cancellato), eliminiamo tutte le prenotazioni per quella data.
       
       Il CASCADE ci permette di mantenere il database pulito senza dover cancellare 
       manualmente i voti prima di poter eliminare uno studente o un appello.
    */
CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    voto INTEGER,
    lode INTEGER DEFAULT 0,
    stato TEXT DEFAULT 'iscritto',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
);
