from google_play_scraper import app
import pandas as pd
import numpy as np
from google_play_scraper import Sort, reviews_all, reviews
from datetime import datetime
from app_store_scraper import AppStore
# reading a csv file that contains the app id from both app store and google play store
app_data = pd.read_csv('app_data - Sheet1.csv')
# iterate through each app
for index, row in app_data.iterrows():
    app_name = row['app_name']
    app_id = row['app_id']
    google_id = row['google_id']
    # Get the data from the us google play store
    us_reviews, _ = reviews(
        google_id,
        lang='en',
        country='us',
        sort=Sort.NEWEST,
        count=200000
    )
    # Get reviews from App Store 
    after_date = datetime(2020, 1, 1)
    apple = AppStore(
        country='us',
        app_name=str(app_name),
        app_id=str(app_id)
    )
    apple.review(how_many=200000, after=after_date, sleep=1)
    appledf = pd.DataFrame(np.array(apple.reviews), columns=['review'])
    appledf2 = appledf.join(pd.DataFrame(appledf.pop('review').tolist()))
    appledf2 = appledf2.rename(columns={
        'review': 'content',
        'userName': 'userName',
        'rating': 'score',
        'date': 'at',
    })

    # 整合两个数据源的评论数据
    df_total = pd.DataFrame(np.array(us_reviews), columns=['review'])
    df_total = df_total.join(pd.DataFrame(df_total.pop('review').tolist()))
    combined_df = pd.concat([appledf2, df_total])
    combined_df = combined_df.loc[:, ['at', 'content', 'userName', 'score']]

    # 筛选2020年1月1日之后的评论数据
    after_date = pd.to_datetime('2020-01-01')
    filtered_df = combined_df[combined_df['at'] >= after_date]

    # 将结果保存到CSV文件
    file_name = app_name + '_reviews.csv'
    filtered_df.to_csv(file_name, index=False)
