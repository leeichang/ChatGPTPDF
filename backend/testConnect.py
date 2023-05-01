import psycopg2

def test_connection():
    try:
        connection = psycopg2.connect(
            dbname="chatgptpdf",
            user="ichang",
            password="",
            host="localhost",
            port="5432"
        )

        cursor = connection.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        if result and result[0] == 1:
            print("連接成功，psycopg2-binary正常運行！")
        else:
            print("連接失敗，請檢查您的連接設定。")

    except psycopg2.Error as e:
        print(f"連接失敗，原因：{e}")
    
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    test_connection()
