SQL
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    genre TEXT,
    seasons_watched INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Watching',
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);