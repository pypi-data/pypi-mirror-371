import pandas as pd
import mysql.connector
import decimal

def gerar_df_phoenix(
        db_phoenix: str, 
        request_select: str,
        user_phoenix: str,
        password_phoenix: str,
        host_phoenix: str
    ) -> pd.DataFrame:
    
    config = {
        'user': user_phoenix, 
        'password': password_phoenix, 
        'host': host_phoenix, 
        'database': db_phoenix
        }

    conexao = mysql.connector.connect(**config)

    cursor = conexao.cursor()

    request_name = request_select

    cursor.execute(request_name)

    resultado = cursor.fetchall()
    
    cabecalho = [desc[0] for desc in cursor.description]

    cursor.close()

    conexao.close()

    df = pd.DataFrame(
        resultado, 
        columns=cabecalho
    )

    df = df.applymap(
        lambda x: float(x) 
        if isinstance(x, decimal.Decimal) 
        else (
            x.decode() 
            if isinstance(x, (bytes, bytearray)) 
            else x
        )
    )

    return df
