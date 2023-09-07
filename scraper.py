from google_play_scraper import app
import pandas as pd
import numpy as np
from google_play_scraper import Sort, reviews_all, reviews
from datetime import datetime
from app_store_scraper import AppStore
# 读取包含多个app信息的CSV文件
app_data = pd.read_csv('app_data - Sheet1.csv')
# 循环处理每个app
for index, row in app_data.iterrows():
    app_name = row['app_name']
    app_id = row['app_id']
    google_id = row['google_id']
    # 获取Google Play Store的评论数据
    us_reviews, _ = reviews(
        google_id,
        lang='en',
        country='us',
        sort=Sort.NEWEST,
        count=200000
    )
    # 获取App Store的评论数据
    after_date = datetime(2020, 1, 1)
    slack = AppStore(
        country='us',
        app_name=str(app_name),
        app_id=str(app_id)
    )
    slack.review(how_many=200000, after=after_date, sleep=1)
    slackdf = pd.DataFrame(np.array(slack.reviews), columns=['review'])
    slackdf2 = slackdf.join(pd.DataFrame(slackdf.pop('review').tolist()))
    slackdf2 = slackdf2.rename(columns={
        'review': 'content',
        'userName': 'userName',
        'rating': 'score',
        'date': 'at',
    })

    # 整合两个数据源的评论数据
    df_busu = pd.DataFrame(np.array(us_reviews), columns=['review'])
    df_busu = df_busu.join(pd.DataFrame(df_busu.pop('review').tolist()))
    combined_df = pd.concat([slackdf2, df_busu])
    combined_df = combined_df.loc[:, ['at', 'content', 'userName', 'score']]

    # 筛选2020年1月1日之后的评论数据
    after_date = pd.to_datetime('2020-01-01')
    filtered_df = combined_df[combined_df['at'] >= after_date]

    # 将结果保存到CSV文件
    file_name = app_name + '_reviews.csv'
    filtered_df.to_csv(file_name, index=False)
