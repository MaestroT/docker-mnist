import logging

log = logging.getLogger()
log.setLevel('INFO')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)
# 引入Cluster模块
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
# 循环负载平衡策略，以循环方式查询节点
from cassandra.policies import RoundRobinPolicy

KEYSPACE = "mnist"


def createKeySpace():
    # 默认本机数据库集群
    cluster = Cluster(contact_points=['cassandra'], load_balancing_policy=RoundRobinPolicy(),port=9042,)
    # 连接并创建一个会话
    session = cluster.connect()

    log.info("Creating keyspace...")
    try:
        # 创建KeySpace；使用第一个副本放置策略，即简单策略；选择复制因子为2个副本。
        session.execute("""
            CREATE KEYSPACE %s
            WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
            """ % KEYSPACE)

        log.info("Setting keyspace...")
        session.set_keyspace(KEYSPACE)

        log.info("Creating table...")
        session.execute("""
            CREATE TABLE History (
                IP_Address text,
                access_time timestamp,
                image_path text,
                mnist_result text,
                PRIMARY KEY (IP_Address, access_time)
            )
            """)
            
        
    except Exception as e:
        log.error("Unable to create keyspace")
        log.error(e)

def insertData(ip_addr, access_time, image_path, mnist_result):
    cluster = Cluster(contact_points=['cassandra'],load_balancing_policy=None, port=9042,)
    session = cluster.connect()
    log.info("Inserting data...")
    try:
        session.execute(""" 
            INSERT INTO mnist.History (IP_Address, access_time, image_path, mnist_result)
            VALUES(%s, %s, %s, %s);
            """,
            (ip_addr, access_time, image_path, mnist_result)
        )
    except Exception as e:
        log.error("Unable to insert data")
        log.error(e)
        
def readRows():
    cluster = Cluster(contact_points=['cassandra'],load_balancing_policy=None, port=9042,)
    session = cluster.connect()
    log.info("Selecting data...")
    try:
        rows = session.execute("SELECT * FROM mnist.History")
        log.info("IP_Address text \t access_time \t image_path \t mnist_result")
        log.info("---------\t-----\t-----\t-----")
        count=0
        for row in rows:
            if(count%100==0):
                log.info('\t'.join(row))
            count=count+1
        log.info("Total")
        log.info("-----")
        log.info("rows %d" %(count))
    except Exception as e:
        log.error("Unable to read data")
        log.error(e)