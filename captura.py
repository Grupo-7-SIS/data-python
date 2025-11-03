
import mysql.connector
from mysql.connector import Error
import datetime
import psutil
import time

DB_CONFIG = {
    'host': '100.27.60.224',
    'user': 'cyberbeef',
    'password': 'admin123@',
    'database': 'cyberbeef',
    'port': 3306
}

ID_MAQUINA = 1
INTERVALO = 5  # segundos

def conectar():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Erro na conexão com o banco: {e}")
        return None

def obter_ou_criar_componente(tipo, unidade, id_maquina):
    db = conectar()
    if db is None:
        return None
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT idComponente FROM componente
            WHERE tipoComponente = %s AND idMaquina = %s
        """, (tipo, id_maquina))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]

        cursor.execute("""
            INSERT INTO componente (tipoComponente, unidadeMedida, idMaquina)
            VALUES (%s, %s, %s)
        """, (tipo, unidade, id_maquina))
        db.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Erro ao obter ou criar componente '{tipo}': {e}")
        return None
    finally:
        cursor.close()
        db.close()

def inserir_leitura(id_componente, id_maquina, valor, tipo, unidade):
    db = conectar()
    if db is None:
        return
    try:
        cursor = db.cursor()
        agora = datetime.datetime.now()
        cursor.execute("""
            INSERT INTO leitura (idComponente, idMaquina, dado, dthCaptura)
            VALUES (%s, %s, %s, %s)
        """, (id_componente, id_maquina, valor, agora))
        db.commit()
        print(f"[{agora.strftime('%Y-%m-%d %H:%M:%S')}] Componente: {tipo:<7} | Unidade: {unidade:<3} | Valor: {valor:.2f}")
    except Error as e:
        print(f"Erro ao inserir leitura: {e}")
    finally:
        cursor.close()
        db.close()

def capturar_metricas():
    cpu_percent = psutil.cpu_percent(interval=1)
    ram_uso_gb = psutil.virtual_memory().used / (1024 ** 3)
    disco_uso_gb = psutil.disk_usage('/').used / (1024 ** 3)

    return {
        ("CPU", "%"): cpu_percent,
        ("MEMORIA", "GB"): ram_uso_gb,
        ("DISCO", "GB"): disco_uso_gb
    }

def iniciar_monitoramento():
    print("Iniciando monitoramento em tempo real... (Ctrl + C para parar)\n")
    while True:
        metricas = capturar_metricas()
        for (tipo, unidade), valor in metricas.items():
            id_comp = obter_ou_criar_componente(tipo, unidade, ID_MAQUINA)
            if id_comp:
                inserir_leitura(id_comp, ID_MAQUINA, valor, tipo, unidade)
        time.sleep(INTERVALO)

if __name__ == "__main__":
    iniciar_monitoramento()


