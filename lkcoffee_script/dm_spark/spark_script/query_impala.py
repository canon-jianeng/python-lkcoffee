
from impala.dbapi import connect

# 连接impala
conn = connect(host='10.218.18.85', port=7051, auth_mechanism='PLAIN')
# conn = connect(host='10.218.18.77', port=7051, database='rtdw_dataplatform', auth_mechanism='PLAIN')
# conn = connect(host='10.218.23.112', port=7051, database='rtdw_dataplatform', auth_mechanism='PLAIN')
# conn = connect(host='dataqjdbctest03.lkcoffee.com', port=16666, database='rtdw_dataplatform', auth_mechanism='PLAIN')

# 游标
cur = conn.cursor()

cur.execute("select * from dm_shop_spec_order_data where dt='2023-08-07' and goods_id=4488")
print(cur.fetchall())


# 关闭游标
cur.close()
# 关闭连接
conn.close()
