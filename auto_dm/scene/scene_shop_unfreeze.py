
from auto_dm.api import api_idata_query, api_idata_task, api_idata_hdfs


def execute_shop_unfreeze():
    """
    解冻场景
    """
    # 下载数据
    sql_val = "select * from dw_lucky_dataplatform.dm_shop_unfreeze_goods_predict where wh_dept_id in (4001,19101) and dt='2023-11-30';"
    file_path = '../data/shop_unfreeze_data.csv'
    api_idata_query.query_to_csv(sql_val, file_path, env="prod")
    # 上传数据
    upload_file = "/user/yuan.bie/dm/test/shop-order/temp/shop_unfreeze_data.csv"
    api_idata_hdfs.batch_upload_hdfs(upload_file, file_path)
    # 执行 idata 任务
    api_idata_task.execute_task(4836)


if __name__ == '__main__':
    execute_shop_unfreeze()
