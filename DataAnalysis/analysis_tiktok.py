# -*- coding: utf-8 -*-
"""Analysis_Tiktok.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Bf7WYmtzghb747qt49ZtRaUqjjhO5C1d

# **Giới thiệu**

**PHÂN TÍCH VÀ TRỰC QUAN HÓA DỮ LIỆU VIDEO TRENDING TIKTOK BẰNG GOOGLE COLAB**

Nhóm tiến hành phân tích, thống kê, trực quan hóa trên tập dữ liệu đã được định dạng. Các file local mà nhóm sử dụng cần đính kèm là:
1. data_tiktok_10days.json
2. tiktok.jpg
3. vietnamese-stopwords.txt

Dưới đây là source code nhóm đã thực hiện

# **Phần 1: Hiển thị cấu trúc dữ liệu dạng DataFrame**

Cài đặt thư viện
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import init_notebook_mode, iplot, plot
from plotly.subplots import make_subplots

"""Đọc file"""

file = open('data_tiktok_10days.json', encoding="utf8")
raw_data = json.load(file)
file.close()

len(raw_data['collector'])

"""Hiển thị cấu trúc dạng DataFrame"""

trending_videos_list = raw_data['collector']

df_tiktok_dataset = pd.DataFrame(trending_videos_list)
df_tiktok_dataset

def object_to_columns(dfRow, **kwargs):
    '''Function to expand cells containing dictionaries, to columns'''
    for column, prefix in kwargs.items():
        if isinstance(dfRow[column], dict):
            for key, value in dfRow[column].items():
                columnName = '{}.{}'.format(prefix, key)
                dfRow[columnName] = value
    return dfRow

# Mở rộng các ô nhất định chứa từ điển thành các cột
df_tiktok_dataset = df_tiktok_dataset.apply(object_to_columns, 
                            authorMeta='authorMeta',  
                            musicMeta='musicMeta',
                            covers='cover',
                            videoMeta='videoMeta', axis = 1)

# Xóa các cột ban đầu chứa từ điển gốc
df_tiktok_dataset = df_tiktok_dataset.drop(['authorMeta','musicMeta','covers','videoMeta'], axis = 1)
df_tiktok_dataset

"""Trích xuất thông tin dữ liệu"""

df_tiktok_dataset.info()

# Lấy các hàng duy nhất từ ​​tập dữ liệu
df_unique_videos = df_tiktok_dataset.drop_duplicates(subset='id', keep="first")
df_unique_music = df_tiktok_dataset.drop_duplicates(subset='musicMeta.musicId', keep="first")
df_unique_authors = df_tiktok_dataset.drop_duplicates(subset='authorMeta.id', keep="first")

# Hiển thị số lượng hàng trên mỗi tập
{
    'df_tiktok_dataset': df_tiktok_dataset.shape,
    'df_unique_videos': df_unique_videos.shape,
    'df_unique_music': df_unique_music.shape,
    'df_unique_authors': df_unique_authors.shape
}

"""# **Phần 2: Phân tích dữ liệu**

## **I. Phân tích dữ liệu trùng lặp**

Đếm dữ liệu trùng lặp
"""

count_duplicated = pd.crosstab(index=df_tiktok_dataset['id'], columns='duplicates')
count_duplicated

"""Hiển thị 10 video có tần suất xuất hiện nhiều nhất"""

duplicated = pd.crosstab(index=[df_tiktok_dataset['id'],df_tiktok_dataset['text'], df_tiktok_dataset['authorMeta.name'], 
                                df_tiktok_dataset['authorMeta.verified'], df_tiktok_dataset['authorMeta.signature'],
                                df_tiktok_dataset['musicMeta.musicName']], columns='duplicates')
df_duplicate = duplicated.sort_values(by='duplicates', ascending=False)
df_duplicate.head(10)

"""## **II. Phân tích dữ liệu duy nhất**

### **1. Lọc dữ liệu duy nhất**
"""

df_filter_dataset = df_tiktok_dataset.drop_duplicates(subset=['id'], keep='last')
df_filter_dataset

"""### **2. Hiển thị một số dữ liệu thống kê**"""

df_filter_dataset.describe()

"""### **3. Biểu thị thời lượng video**"""

plt.figure(figsize=(15, 8))
sns.kdeplot(df_filter_dataset['videoMeta.duration'], fill=True, color='g')
plt.xlabel('Video Length Seconds')
plt.title('Video Length')

max_play=df_filter_dataset[df_filter_dataset['videoMeta.duration'] <= 60 ]['videoMeta.duration'].count() / df_filter_dataset['videoMeta.duration'].count() * 100
min_play=df_filter_dataset[df_filter_dataset['videoMeta.duration'] > 60 ]['videoMeta.duration'].count() / df_filter_dataset['videoMeta.duration'].count() * 100
df_views = df2 = pd.DataFrame([[max_play,min_play]], columns=['max_play','min_play'])

plt.pie(df_views, autopct='%0.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
plt.title("Videos over and under 60 seconds in length")
plt.legend(["<= 60s","> 60s"])

"""### **4. Biểu thị lượt play, like, share và comment theo từng khoảng**

Function trợ giúp về pandas cut()
"""

# Wrapper around pandas cut() method.
def my_cut (x, bins, lower_infinite=False, upper_infinite=False, **kwargs):
    # Quick passthru if no infinite bounds
    if not lower_infinite and not upper_infinite:
        return pd.cut(x, bins, **kwargs)

    # Setup
    num_labels      = len(bins) - 1
    include_lowest  = kwargs.get("include_lowest", False)
    right           = kwargs.get("right", True)

    # Prepend/Append infinities where indiciated
    bins_final = bins.copy()
    if upper_infinite:
        bins_final.insert(len(bins),float("inf"))
        num_labels += 1
    if lower_infinite:
        bins_final.insert(0,float("-inf"))
        num_labels += 1

    # Decide all boundary symbols based on traditional cut() parameters
    symbol_lower  = "<=" if include_lowest and right else "<"
    left_bracket  = "(" if right else "["
    right_bracket = "]" if right else ")"
    symbol_upper  = ">" if right else ">="

    # Inner function reused in multiple clauses for labeling
    def make_label(i, lb=left_bracket, rb=right_bracket):
        return "{0} - {1}".format(bins_final[i], bins_final[i+1])

    # Create custom labels
    labels=[]
    for i in range(0,num_labels):
        new_label = None

        if i == 0:
            if lower_infinite:
                new_label = "{0} {1}".format(symbol_lower, bins_final[i+1])
            elif include_lowest:
                new_label = make_label(i, lb="[")
            else:
                new_label = make_label(i)
        elif upper_infinite and i == (num_labels - 1):
            new_label = "{0} {1}".format(symbol_upper, bins_final[i])
        else:
            new_label = make_label(i)

        labels.append(new_label)

    # Pass thru to pandas cut()
    return pd.cut(x, bins_final, labels=labels, **kwargs)

# Đặt khoảng
buckets = list(range(0,1200000,50000))
# Đếm số lượng video theo lượt like, share, comment, play theo từng khoảng
plays = df_filter_dataset.groupby( my_cut( df_filter_dataset['playCount'], buckets, upper_infinite=True ) ).diggCount.count()
likes = df_filter_dataset.groupby( my_cut( df_filter_dataset['diggCount'], buckets, upper_infinite=True ) ).diggCount.count()
plays = plays.rename('plays').to_frame().reset_index()
likes = likes.rename('likes').to_frame().reset_index()
fig = make_subplots(1,2,subplot_titles=("Distribution of Plays","Distribution of Likes"))
fig.add_trace(
    go.Bar(y = plays['playCount'], x = plays['plays'], name="Plays",text = plays['plays'], 
           orientation='h',texttemplate='%{text:.2s}', textposition='outside', marker_color='rgb(170, 210, 200)'
    ),
    row=1,col=1
)
fig.add_trace(
    go.Bar(y = likes['diggCount'], x = likes['likes'], name="Likes",text = likes['likes'], 
           orientation='h',texttemplate='%{text:.2s}', textposition='outside', marker_color='rgb(162, 210, 255)'
    ),
    row=1,col=2
)
fig.update_xaxes(title_text='Videos')
fig.update_yaxes(title_text='Plays', col=1, row=1, automargin=True)
fig.update_yaxes(title_text='Likes', col=2, row=1, automargin=True)
fig.show(config={'displayModeBar': False})

comments = df_filter_dataset.groupby( my_cut( df_filter_dataset['commentCount'], buckets, upper_infinite=True ) ).diggCount.count()
shares = df_filter_dataset.groupby( my_cut( df_filter_dataset['shareCount'], buckets, upper_infinite=True ) ).diggCount.count()


comments = comments.rename('comments').to_frame().reset_index() 
shares = shares.rename('shares').to_frame().reset_index() 
fig = make_subplots(1,2,subplot_titles=("Distribution of Comments", "Distribution of Shares"))


fig.add_trace(
    go.Bar(y = comments['commentCount'], x = comments['comments'], name="Comments",text = comments['comments'], 
           orientation='h',texttemplate='%{text:.2s}', textposition='outside', marker_color='rgb(205, 180, 219)'
    ),
    row=1,col=1
)
fig.add_trace(
    go.Bar(y = shares['shareCount'], x = shares['shares'], name="Shares",text = shares['shares'], 
           orientation='h',texttemplate='%{text:.2s}', textposition='outside', marker_color='rgb(154, 180, 200)'
    ),
    row=1,col=2
)
fig.update_xaxes(title_text='Videos')
fig.update_yaxes(title_text='Comments', col=1, row=1, automargin=True)
fig.update_yaxes(title_text='Share', col=2, row=1, automargin=True)
fig.show(config={'displayModeBar': False})

"""### **5. Biểu thị lượt play, like, share và comment trong một khoảng xác định**

**Biểu thị lượt play**
"""

df_videos_users_focus = df_filter_dataset[df_filter_dataset['playCount'] <= 50000000 ]
ax = df_videos_users_focus['playCount'].plot(kind='hist', figsize=(16,8))
plt.title("Total Videos and Play < 50M Plays")
ax.set_ylabel('No. of Video')
ax.set_xlabel('Plays')

max_play=df_filter_dataset[df_filter_dataset['playCount'] <= 50000000 ]['playCount'].count() / df_filter_dataset['playCount'].count() * 100
min_play=df_filter_dataset[df_filter_dataset['playCount'] > 50000000 ]['playCount'].count() / df_filter_dataset['playCount'].count() * 100
df_views = df2 = pd.DataFrame([[max_play,min_play]], columns=['max_play','min_play'])

plt.pie(df_views, autopct='%0.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
plt.title("Video above and below 50M plays")
plt.legend(["<= 50M plays","> 50M plays"])

"""**Biểu thị lượt like**"""

df_videos_users_focus = df_filter_dataset[df_filter_dataset['diggCount'] < 10000000 ]
ax = df_videos_users_focus['diggCount'].plot(kind='hist', figsize=(16,8))
plt.title("Total Videos and Like < 10M Likes")
ax.set_ylabel('No. of Video')
ax.set_xlabel('Likes')

max_like=df_filter_dataset[df_filter_dataset['diggCount'] <= 3000000 ]['diggCount'].count() / df_filter_dataset['diggCount'].count() * 100
min_like=df_filter_dataset[df_filter_dataset['diggCount'] > 3000000 ]['diggCount'].count() / df_filter_dataset['diggCount'].count() * 100
df_views = df2 = pd.DataFrame([[max_like,min_like]], columns=['max_like','min_like'])

plt.pie(df_views, autopct='%0.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
plt.title("Video above and below 3M likes")
plt.legend(["<= 3M likes","> 3M likes"])

"""**Biểu thị lượt Share**"""

df_videos_users_focus_share = df_filter_dataset[df_filter_dataset['shareCount'] <= 20000 ]
ax = df_videos_users_focus_share['shareCount'].plot(kind='hist', figsize=(16,8))
plt.title("Total Videos and Share < 20.000 Shares")
ax.set_ylabel('No. of Video')
ax.set_xlabel('Shares')

max_share=df_filter_dataset[df_filter_dataset['shareCount'] <= 10000 ]['shareCount'].count() / df_filter_dataset['shareCount'].count() * 100
min_share=df_filter_dataset[df_filter_dataset['shareCount'] > 10000 ]['shareCount'].count() / df_filter_dataset['shareCount'].count() * 100
df_views_share = df2_share = pd.DataFrame([[max_share,min_share]], columns=['max_share','min_share'])

plt.pie(df_views_share, autopct='%0.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
plt.title("Video above and below 10.000 shares")
plt.legend(["<= 10.000 shares","> 10.000 shares"])

"""**Biểu thị lượt comment**"""

df_videos_users_focus_comment = df_filter_dataset[df_filter_dataset['commentCount'] <= 20000 ]
ax = df_videos_users_focus_comment['commentCount'].plot(kind='hist', figsize=(16,8))
plt.title("Total Videos and Comment < 20.000 Comments")
ax.set_ylabel('No. of Video')
ax.set_xlabel('Comments')

max_cmt=df_filter_dataset[df_filter_dataset['commentCount'] <= 10000 ]['commentCount'].count() / df_filter_dataset['commentCount'].count() * 100
min_cmt=df_filter_dataset[df_filter_dataset['commentCount'] > 10000 ]['commentCount'].count() / df_filter_dataset['commentCount'].count() * 100
df_views_cmt = df2_cmt = pd.DataFrame([[max_cmt,min_cmt]], columns=['max_cmt','min_cmt'])

plt.pie(df_views_cmt, autopct='%0.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
plt.title("Video above and below 10.000 comments")
plt.legend(["<= 10.000 comments","> 10.000 comments"])

"""### **6. Biểu thị sự tương quan giữa lượt like và comment**"""

# Tập trung vào những video trong tập dữ liệu nhỏ hơn 50.000 like
df_videos_users_focus = df_filter_dataset[df_filter_dataset['diggCount'] <= 50000]
# Tạo biểu đồ chấm với trend line
fig = px.scatter(df_videos_users_focus, trendline="ols",
                 x="diggCount", 
                 y="commentCount",
                 labels={
                     "diggCount": "Likes",
                     "commentCount": "Comments"
                 },
                 log_y=True,
                 trendline_color_override="#ff7096", 
                 template='plotly_white')

fig.update_traces(marker=dict(
                     color='#4cc9f0',
                     opacity=0.6,
                 ))
fig.show()

"""### **7. Sự tương quan giữa các biến**"""

df_filter_dataset.corr()

h_labels = [x.replace('_',' ').title() 
            for x in list(df_filter_dataset.select_dtypes(include=['number','bool']).columns.values)]
            
fig, ax = plt.subplots(figsize=(10,6))
_ =sns.heatmap(df_tiktok_dataset.corr(), annot=True, xticklabels=h_labels, yticklabels=h_labels, 
               cmap=sns.cubehelix_palette(as_cmap=True), ax=None)

"""### **8. Người dùng nổi bật trên TikTok**"""

df_users = df_filter_dataset.groupby(['authorMeta.name']).sum()
pal = sns.color_palette("Blues", as_cmap=True)


df_users = df_users.sort_values(by='playCount', ascending=False)
plt.figure(figsize=(15,8))
plt.ticklabel_format(style = 'plain')
plt.title('Most watched Usernames')
g = sns.barplot(df_users.index[:30], df_users.playCount[:30], palette='inferno')
g.set_xticklabels(g.get_xticklabels(),rotation=90)

plt.ylabel('Number of plays')
plt.xlabel('Username')

df_users = df_filter_dataset.groupby(['authorMeta.name']).sum()
pal = sns.color_palette("Blues", as_cmap=True)


df_users = df_users.sort_values(by='diggCount', ascending=False)
plt.figure(figsize=(15,8))
plt.ticklabel_format(style = 'plain')
plt.title('Most liked Usernames')
g = sns.barplot(df_users.index[:30], df_users.diggCount[:30], palette='inferno')
g.set_xticklabels(g.get_xticklabels(),rotation=90)

plt.ylabel('Number of likes')
plt.xlabel('Username')

df_users = df_filter_dataset.groupby(['authorMeta.name']).sum()
pal = sns.color_palette("Blues", as_cmap=True)


df_users = df_users.sort_values(by='commentCount', ascending=False)
plt.figure(figsize=(15,8))
plt.ticklabel_format(style = 'plain')
plt.title('Most commented Usernames')
g = sns.barplot(df_users.index[:30], df_users.commentCount[:30], palette='inferno')
g.set_xticklabels(g.get_xticklabels(),rotation=90)

plt.ylabel('Number of comments')
plt.xlabel('Username')

df_users = df_filter_dataset.groupby(['authorMeta.name']).sum()
pal = sns.color_palette("Blues", as_cmap=True)


df_users = df_users.sort_values(by='shareCount', ascending=False)
plt.figure(figsize=(15,8))
plt.ticklabel_format(style = 'plain')
plt.title('Most shared Usernames')
g = sns.barplot(df_users.index[:30], df_users.shareCount[:30], palette='inferno')
g.set_xticklabels(g.get_xticklabels(),rotation=90)

plt.ylabel('Number of shares')
plt.xlabel('Username')

"""### **9. Trích xuất dữ liệu Music Tiktok**"""

df_filter_dataset = pd.DataFrame(trending_videos_list)

df_filter_dataset = df_filter_dataset.apply(object_to_columns, 
                                        musicMeta='musicMeta', axis = 1)

musicMeta = df_filter_dataset[['musicMeta.musicName']]
musicMeta.info()

"""### **10. Trực quan dữ liệu nhạc Original**"""

# Thêm cột với giá trị mặc định
musicMeta ['count'] = 1

# Đếm tất cả nhạc, nhóm và thay thế giá trị cột đếm bằng tổng
musicMeta = musicMeta.groupby(["musicMeta.musicName"])["count"].count().reset_index()

# Sắp xếp theo các thẻ bắt đầu bằng # phổ biến nhất và giữ vị trí top 15
musicMeta = musicMeta.sort_values(by='count', ascending=False)[:15]

# Đặt màu

# Tạo Biểu đồ hình tròn với tất cả các giá trị
fig = go.Figure(data=[go.Pie(
                        labels=musicMeta["musicMeta.musicName"], 
                        values=musicMeta["count"], 
                        textinfo='label+percent',
                     
                )], 
                layout={"colorway": ["#6699FF","#FFFF66",
                                     "#FF99FF","#FFCC00",
                                     "#339966","#99FFCC",
                                     "#66CC00","#FFCCCC",
                                     "#FF9999","#CC00FF"]})
fig.show()

musicMeta.head(10)

labels= musicMeta["musicMeta.musicName"].head(10)
values= musicMeta["count"].head(10)

plt.plot(values,labels)
plt.xlabel('Count')
plt.ylabel('Music Name')

plt.figure(figsize=(30,10))

plt.show()

"""### **11. Trực quan dữ liệu nhạc trên ứng dụng TikTok**

Thống kê dữ liệu
"""

df_filter_dataset.groupby(['musicMeta.musicName']).describe().head(20)

""" Trích xuất các thông tin có nghĩa của 20 bài hát đầu tiên"""

df_filter_dataset.groupby(['musicMeta.musicName']).mean().head(20)

"""Top 20 bài hát được yêu thích nhất, có số likes nhiều nhất"""

df_music = df_filter_dataset.groupby(['musicMeta.musicName']).mean().head(20)

df_filter_dataset = df_filter_dataset.groupby(['musicMeta.musicName']).sum()
pal = sns.color_palette("Blues", as_cmap=True)
 
 
df_music = df_music.sort_values(by='diggCount', ascending=False)
plt.figure(figsize=(15,8))
plt.ticklabel_format(style = 'plain')
plt.title('Most liked music')
g = sns.barplot(df_music.index[:20], df_music.diggCount[:20], palette='inferno')
g.set_xticklabels(g.get_xticklabels(),rotation=90)

plt.ylabel('Number of likes')
plt.xlabel('Music')

"""**Top 20 bài hát được phát (play) nhiều nhất**"""

df_filter_dataset = df_filter_dataset.groupby(['musicMeta.musicName']).sum()
pal = sns.color_palette("Blues", as_cmap=True)
 
 
df_music = df_music.sort_values(by='playCount', ascending=False)
plt.figure(figsize=(15,8))
plt.ticklabel_format(style = 'plain')
plt.title('Most played music')
g = sns.barplot(df_music.index[:20], df_music.playCount[:20], palette='inferno')
g.set_xticklabels(g.get_xticklabels(),rotation=90)
 
plt.ylabel('Number of plays')
plt.xlabel('Music')

"""**Top 20 video được bình luận nhiều nhất**"""

df_filter_dataset = df_filter_dataset.groupby(['musicMeta.musicName']).sum()
pal = sns.color_palette("Blues", as_cmap=True)
 
 
df_music = df_music.sort_values(by='commentCount', ascending=False)
plt.figure(figsize=(15,8))
plt.ticklabel_format(style = 'plain')
plt.title('Most commented music')
g = sns.barplot(df_music.index[:20], df_music.commentCount[:20], palette='inferno')
g.set_xticklabels(g.get_xticklabels(),rotation=90)
 
plt.ylabel('Number of comments')
plt.xlabel('Music')

"""**Top 20 video được chia sẻ nhiều nhất**"""

df_filter_dataset = df_filter_dataset.groupby(['musicMeta.musicName']).sum()
pal = sns.color_palette("Blues", as_cmap=True)
 
 
df_music = df_music.sort_values(by='shareCount', ascending=False)
plt.figure(figsize=(15,8))
plt.ticklabel_format(style = 'plain')
plt.title('Most shared music')
g = sns.barplot(df_music.index[:20], df_music.shareCount[:20], palette='inferno')
g.set_xticklabels(g.get_xticklabels(),rotation=90)
 
plt.ylabel('Number of shares')
plt.xlabel('Music')

"""### **12. Phân tích Hashtag**"""

df_filter_dataset = df_tiktok_dataset.drop_duplicates(subset=['id'], keep='last')

# expand df.tags into its own dataframe
hashtags = df_filter_dataset['hashtags'].apply(pd.Series)

# rename each variable is tags
hashtags = hashtags.rename(columns = lambda x : 'hashtag_' + str(x))

# view the tags dataframe
hashtags

df_filter_dataset['hashtags'].describe()

hashtags.isnull().sum()

from google.colab import files
uploaded = files.upload()

from matplotlib import rcParams 
rcParams['figure.figsize']=10,8

lst_hashtag=df_filter_dataset['hashtags'].to_list()
print(lst_hashtag)

def read_txt(filename):
  f=open(filename)
  if(f.mode=="r"):
    contents=f.read()
    return contents

stopwords = read_txt("vietnamese-stopwords.txt")

from wordcloud import WordCloud, STOPWORDS
import numpy as np 
from PIL import Image
mask = np.array(Image.open('tiktok.jpg'))
wc = WordCloud(stopwords=STOPWORDS,
               mask=mask, background_color="white",
               max_words=500, max_font_size=256,
               random_state=42, width=mask.shape[1],
               height=mask.shape[0])
wc.generate(str(lst_hashtag))
plt.imshow(wc, interpolation="bilinear")
plt.axis('off')
plt.show()

"""**HẾT**"""