import psycopg2

# conn = psycopg2.connect(
#     database="shopdb",
#     user="kendyiand",
#     password="xoRH1B0lyXET",
#     host="ep-winter-haze-16199232.eu-central-1.aws.neon.tech",
#     port="5432"
# )


def get_connection():
    return psycopg2.connect(
        database="shopdb",
        user="kendyiand",
        password="xoRH1B0lyXET",
        host="ep-winter-haze-16199232.eu-central-1.aws.neon.tech",
        port="5432"
    )


def db_init():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS product (
        id SERIAL PRIMARY KEY,
        name VARCHAR(30),
        price FLOAT,
        count INT,  
        sku VARCHAR(9),
        file_id VARCHAR,
        is_sale BOOLEAN DEFAULT FALSE,
        sale_price NUMERIC(10, 2) DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id BIGINT,
        first_name VARCHAR(64),
        last_name VARCHAR(64),
        username VARCHAR(32),
        user_role VARCHAR(64) DEFAULT 'user'
    )
    """)

    conn.commit()


def user_exists(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone() is not None


def create_user(id, first_name, last_name, username):
    conn = get_connection()
    cursor = conn.cursor()

    if not user_exists(id):
        cursor.execute("INSERT INTO users (id, first_name, last_name, username) VALUES (%s, %s, %s, %s)",
                       (id, first_name, last_name, username))
        conn.commit()


def get_user_role(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_role FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        return result[0]

    return None
