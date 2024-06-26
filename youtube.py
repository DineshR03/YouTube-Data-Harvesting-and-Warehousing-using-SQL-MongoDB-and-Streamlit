# libraries

from googleapiclient.discovery import build
import pymongo
import psycopg2
import pandas as pd
import streamlit as st


# API key connection

def Apiconnect():
    Api_Id="AIzaSyCFKKRjVR40azXx7Kanj4Ng15qeSVKoApQ"
    
    api_service_name = "youtube"
    api_version = "v3"
    
    youtube = build(api_service_name,api_version,developerKey=Api_Id)
    return youtube

youtube=Apiconnect()

# collecting channel details

def get_channel_info(channel_id):
    
    request = youtube.channels().list(
                part = "snippet,contentDetails,Statistics",
                id = channel_id)
            
    response1=request.execute()

    for i in range(0,len(response1["items"])):
        data = dict(
                    Channel_Name = response1["items"][i]["snippet"]["title"],
                    Channel_Id = response1["items"][i]["id"],
                    Subscription_Count= response1["items"][i]["statistics"]["subscriberCount"],
                    Views = response1["items"][i]["statistics"]["viewCount"],
                    Total_Videos = response1["items"][i]["statistics"]["videoCount"],
                    Channel_Description = response1["items"][i]["snippet"]["description"],
                    Playlist_Id = response1["items"][i]["contentDetails"]["relatedPlaylists"]["uploads"],
                    )
        return data


# Collecting Video Ids

def get_channel_videos(channel_id):
    Video_Ids = []
    # Collecting Uploads playlist id
    res = youtube.channels().list(id=channel_id, 
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    
    while True:
        res = youtube.playlistItems().list( 
                                           part = 'snippet',
                                           playlistId = playlist_id, 
                                           maxResults = 50,
                                           pageToken = next_page_token).execute()
        
        for i in range(len(res['items'])):
            Video_Ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break
    return Video_Ids

# Collecting Video details

def get_video_info(video_ids):

    video_data = []

    for video_id in video_ids:
        request = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id= video_id)
        response = request.execute()

        for item in response["items"]:
            video_information = dict(Channel_Name = item['snippet']['channelTitle'],
                        Channel_Id = item['snippet']['channelId'],
                        Video_Id = item['id'],
                        Title = item['snippet']['title'],
                        Tags = item['snippet'].get('tags'),
                        Thumbnail = item['snippet']['thumbnails']['default']['url'],
                        Description = item['snippet']['description'],
                        Published_Date = item['snippet']['publishedAt'],
                        Duration = item['contentDetails']['duration'],
                        Views = item['statistics']['viewCount'],
                        Likes = item['statistics'].get('likeCount'),
                        Comments = item['statistics'].get('commentCount'),
                        Favorite_Count = item['statistics']['favoriteCount'],
                        Definition = item['contentDetails']['definition'],
                        Caption_Status = item['contentDetails']['caption']
                        )
            video_data.append(video_information)
    return video_data


# Collecting Comment details

def get_comment_info(video_ids):
        comment_data = []
        try:
                for video_id in video_ids:

                        request = youtube.commentThreads().list(
                                part = "snippet",
                                videoId = video_id,
                                maxResults = 50
                                )
                        response5 = request.execute()
                        
                        for item in response5["items"]:
                                comment_information = dict(
                                        Comment_Id = item["snippet"]["topLevelComment"]["id"],
                                        Video_Id = item["snippet"]["videoId"],
                                        Comment_Text = item["snippet"]["topLevelComment"]["snippet"]["textOriginal"],
                                        Comment_Author = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"],
                                        Comment_Published = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"])

                                comment_data.append(comment_information)
        except:
                pass
                
        return comment_data
    

# Collecting Playlist_Ids

def get_playlist_info(channel_id):
    All_data = []
    next_page_token = None
    next_page = True
    while next_page:

        request = youtube.playlists().list(
            part="snippet,contentDetails",
            channelId=channel_id,
            maxResults=50,
            pageToken=next_page_token
            )
        response = request.execute()

        for item in response['items']: 
            data={'PlaylistId':item['id'],
                    'Title':item['snippet']['title'],
                    'ChannelId':item['snippet']['channelId'],
                    'ChannelName':item['snippet']['channelTitle'],
                    'PublishedAt':item['snippet']['publishedAt'],
                    'VideoCount':item['contentDetails']['itemCount']}
            All_data.append(data)
        next_page_token = response.get('nextPageToken')
        if next_page_token is None:
            next_page=False
    return All_data

# Mongodb Connection

client = pymongo.MongoClient("mongodb://Dinesh:9095888616@ac-e2itoov-shard-00-00.zlq2lfo.mongodb.net:27017,ac-e2itoov-shard-00-01.zlq2lfo.mongodb.net:27017,ac-e2itoov-shard-00-02.zlq2lfo.mongodb.net:27017/?ssl=true&replicaSet=atlas-3n8yuz-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0")
db = client["Youtube_data"]

# Uploading to Mongodb

def channel_details(channel_id):
    ch_details = get_channel_info(channel_id)
    pl_details = get_playlist_info(channel_id)
    vi_ids = get_channel_videos(channel_id)
    vi_details = get_video_info(vi_ids)
    com_details = get_comment_info(vi_ids)

    collection1 = db["channel_details"]
    collection1.insert_one({"channel_information":ch_details,"playlist_information":pl_details,"video_information":vi_details,
                     "comment_information":com_details})
    
    return "upload completed successfully"


#Table creation for channnels

def channels_table(channel_name_s):
    mydb = psycopg2.connect(host="localhost",
            user="postgres",
            password="dineshr",
            database= "youtube_data",
            port = "5432"
            )
    cursor = mydb.cursor()
    
    
    
    create_query = '''create table if not exists channels(Channel_Name varchar(100),
                    Channel_Id varchar(80) primary key, 
                    Subscription_Count bigint, 
                    Views bigint,
                    Total_Videos int,
                    Channel_Description text,
                    Playlist_Id varchar(50))'''
    cursor.execute(create_query)
    mydb.commit()
    

    single_channel_details=[]
    db = client["Youtube_data"]
    collection1 = db["channel_details"]
    for ch_data in collection1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}):
        single_channel_details.append(ch_data["channel_information"])

        df_single_channel= pd.DataFrame(single_channel_details)

    for index,row in df_single_channel.iterrows():
        insert_query = '''INSERT into channels(Channel_Name,
                                                    Channel_Id,
                                                    Subscription_Count,
                                                    Views,
                                                    Total_Videos,
                                                    Channel_Description,
                                                    Playlist_Id)
                                        VALUES(%s,%s,%s,%s,%s,%s,%s)'''
            

        values =(
                row['Channel_Name'],
                row['Channel_Id'],
                row['Subscription_Count'],
                row['Views'],
                row['Total_Videos'],
                row['Channel_Description'],
                row['Playlist_Id'])
        try:
                                 
            cursor.execute(insert_query,values)
            mydb.commit()
                
        except:
            
            news = f"Selected channel '{channel_name_s}' is already exists"
            
            return news

#Table creation for playlists

def playlists_table(channel_name_s):
    
    mydb = psycopg2.connect(host="localhost",
            user="postgres",
            password="dineshr",
            database= "youtube_data",
            port = "5432"
            )
    cursor = mydb.cursor()  
  

    create_query = '''create table if not exists playlists(PlaylistId varchar(100) primary key,
                    Title varchar(80), 
                    ChannelId varchar(100), 
                    ChannelName varchar(100),
                    PublishedAt timestamp,
                    VideoCount int
                    )'''
    cursor.execute(create_query)
    mydb.commit()
      


    single_playlist_details=[]
    db = client["Youtube_data"]
    collection1 = db["channel_details"]
    for ch_data in collection1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}):
        single_playlist_details.append(ch_data["playlist_information"])

    df_single_playlist_details= pd.DataFrame(single_playlist_details[0])
        
    for index,row in df_single_playlist_details.iterrows():
        insert_query = '''INSERT into playlists(PlaylistId,
                                                    Title,
                                                    ChannelId,
                                                    ChannelName,
                                                    PublishedAt,
                                                    VideoCount)
                                        VALUES(%s,%s,%s,%s,%s,%s)'''            
        values =(
                row['PlaylistId'],
                row['Title'],
                row['ChannelId'],
                row['ChannelName'],
                row['PublishedAt'],
                row['VideoCount'])
                
                           
        cursor.execute(insert_query,values)
        mydb.commit()    
            
            
#Table creation for videos
            
def videos_table(channel_name_s):

    mydb = psycopg2.connect(host="localhost",
                user="postgres",
                password="dineshr",
                database= "youtube_data",
                port = "5432"
                )
    cursor = mydb.cursor()


    create_query = '''create table if not exists videos(
                    Channel_Name varchar(150),
                    Channel_Id varchar(100),
                    Video_Id varchar(50) primary key, 
                    Title varchar(150), 
                    Tags text,
                    Thumbnail varchar(225),
                    Description text, 
                    Published_Date timestamp,
                    Duration interval, 
                    Views bigint, 
                    Likes bigint,
                    Comments int,
                    Favorite_Count int, 
                    Definition varchar(10), 
                    Caption_Status varchar(50) 
                    )''' 
                    
    cursor.execute(create_query)             
    mydb.commit()
    
    single_videos_details=[]
    db = client["Youtube_data"]
    collection1 = db["channel_details"]
    for ch_data in collection1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}):
        single_videos_details.append(ch_data["video_information"])

    df_single_videos_details= pd.DataFrame(single_videos_details[0])
        
    
    for index, row in df_single_videos_details.iterrows():
        insert_query = '''
                    INSERT INTO videos (Channel_Name,
                        Channel_Id,
                        Video_Id, 
                        Title, 
                        Tags,
                        Thumbnail,
                        Description, 
                        Published_Date,
                        Duration, 
                        Views, 
                        Likes,
                        Comments,
                        Favorite_Count, 
                        Definition, 
                        Caption_Status 
                        )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

                '''
        values = (
                    row['Channel_Name'],
                    row['Channel_Id'],
                    row['Video_Id'],
                    row['Title'],
                    row['Tags'],
                    row['Thumbnail'],
                    row['Description'],
                    row['Published_Date'],
                    row['Duration'],
                    row['Views'],
                    row['Likes'],
                    row['Comments'],
                    row['Favorite_Count'],
                    row['Definition'],
                    row['Caption_Status'])
                                
            
        cursor.execute(insert_query,values)
        mydb.commit()
            
#Table creation for comments
            
def comments_table(channel_name_s):
    
    mydb = psycopg2.connect(host="localhost",
                user="postgres",
                password="dineshr",
                database= "youtube_data",
                port = "5432"
                )
    cursor = mydb.cursor()


    create_query = '''CREATE TABLE if not exists comments(Comment_Id varchar(100) primary key,
                    Video_Id varchar(80),
                    Comment_Text text, 
                    Comment_Author varchar(150),
                    Comment_Published timestamp)'''
    cursor.execute(create_query)
    mydb.commit()
        

    single_comments_details=[]
    db = client["Youtube_data"]
    collection1 = db["channel_details"]
    for ch_data in collection1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}):
        single_comments_details.append(ch_data["comment_information"])

    df_single_comments_details= pd.DataFrame(single_comments_details[0])

    for index, row in df_single_comments_details.iterrows():
            insert_query = '''
                INSERT INTO comments (Comment_Id,
                                      Video_Id ,
                                      Comment_Text,
                                      Comment_Author,
                                      Comment_Published)
                VALUES (%s, %s, %s, %s, %s)

            '''
            values = (
                row['Comment_Id'],
                row['Video_Id'],
                row['Comment_Text'],
                row['Comment_Author'],
                row['Comment_Published']
            )
            
            cursor.execute(insert_query,values)
            mydb.commit()
               
               
def tables(single_channel):
    news = channels_table(single_channel)
    if news:
        return news
    else:    
        playlists_table(single_channel)
        videos_table(single_channel)
        comments_table(single_channel)
        
        return "Tables Created successfully"

def show_channels_table():
    ch_list = []
    db = client["Youtube_data"]
    collection1 = db["channel_details"] 
    for ch_data in collection1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    channels_table = st.dataframe(ch_list)
    return channels_table

def show_playlists_table():
    db = client["Youtube_data"]
    collection1 =db["channel_details"]
    pl_list = []
    for pl_data in collection1.find({},{"_id":0,"playlist_information":1}):
        for i in range(len(pl_data["playlist_information"])):
                pl_list.append(pl_data["playlist_information"][i])
    playlists_table = st.dataframe(pl_list)
    return playlists_table

def show_videos_table():
    vi_list = []
    db = client["Youtube_data"]
    collection2 = db["channel_details"]
    for vi_data in collection2.find({},{"_id":0,"video_information":1}):
        for i in range(len(vi_data["video_information"])):
            vi_list.append(vi_data["video_information"][i])
    videos_table = st.dataframe(vi_list)
    return videos_table

def show_comments_table():
    com_list = []
    db = client["Youtube_data"]
    collection3 = db["channel_details"]
    for com_data in collection3.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    comments_table = st.dataframe(com_list)
    return comments_table

def data_collection():
    channel_id = st.text_input("Enter the Channel id")
    channels = channel_id.split(',')
    channels = [ch.strip() for ch in channels if ch]

    if st.button("Collect and Store data"):
        for channel in channels:
            ch_ids = []
            db = client["Youtube_data"]
            coll1 = db["channel_details"]
            for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
                ch_ids.append(ch_data["channel_information"]["Channel_Id"])
            if channel in ch_ids:
                st.success("Channel details of the given channel id: " + channel + " already exists")
            else:
                output = channel_details(channel)
                st.success(output)
            

    all_channels=[]
    db = client["Youtube_data"]
    collection1 = db["channel_details"]
    for ch_data in collection1.find({},{"_id":0,"channel_information":1}):
        all_channels.append(ch_data["channel_information"]["Channel_Name"])
        
    unique_channel= st.selectbox("Select the Channel",all_channels)

    if st.button("Migrate to SQL"):
        display = tables(unique_channel)
        st.success(display)
        
def show_queries():
    mydb = psycopg2.connect(host="localhost",
                user="postgres",
                password="dineshr",
                database= "youtube_data",
                port = "5432"
                )
    cursor = mydb.cursor()


    question = st.selectbox(
        'Please Select Your Question',
        ('select your question',
        '1. What are the names of all the videos and their corresponding channels?',
        '2. Which channels have the most number of videos, and how many videos do they have?',
        '3. What are the top 10 most viewed videos and their respective channels?',
        '4. How many comments were made on each video, and what are their corresponding video names?',
        '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
        '6. What is the total number of likes for each video, and what are their corresponding video names?',
        '7. What is the total number of views for each channel, and what are their corresponding channel names?',
        '8. What are the names of all the channels that have published videos in the year 2022?',
        '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
        '10. Which videos have the highest number of comments, and what are their corresponding channel names?'))

        
    if question == '1. What are the names of all the videos and their corresponding channels?':
        query1 = "select Title as videos, Channel_Name as ChannelName from videos;"
        cursor.execute(query1)
        mydb.commit()
        t1=cursor.fetchall()
        st.write(pd.DataFrame(t1, columns=["Video Title","Channel Name"]))

    elif question == '2. Which channels have the most number of videos, and how many videos do they have?':
        query2 = "select Channel_Name as ChannelName,Total_Videos as NO_Videos from channels order by Total_Videos desc;"
        cursor.execute(query2)
        mydb.commit()
        t2=cursor.fetchall()
        st.write(pd.DataFrame(t2, columns=["Channel Name","No Of Videos"]))

    elif question == '3. What are the top 10 most viewed videos and their respective channels?':
        query3 = '''select Views as views , Channel_Name as ChannelName,Title as VideoTitle from videos 
                            where Views is not null order by Views desc limit 10;'''
        cursor.execute(query3)
        mydb.commit()
        t3 = cursor.fetchall()
        st.write(pd.DataFrame(t3, columns = ["Views","Channel Name","Video title"]))

    elif question == '4. How many comments were made on each video, and what are their corresponding video names?':
        query4 = "select Comments as No_comments ,Title as VideoTitle from videos where Comments is not null;"
        cursor.execute(query4)
        mydb.commit()
        t4=cursor.fetchall()
        st.write(pd.DataFrame(t4, columns=["No Of Comments", "Video Title"]))

    elif question == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        query5 = '''select Title as VideoTitle, Channel_Name as ChannelName, Likes as LikesCount from videos 
                        where Likes is not null order by Likes desc;'''
        cursor.execute(query5)
        mydb.commit()
        t5 = cursor.fetchall()
        st.write(pd.DataFrame(t5, columns=["Video Title","Channel Name","Like count"]))

    elif question == '6. What is the total number of likes for each video, and what are their corresponding video names?':
        query6 = '''select Likes as likeCount,Title as VideoTitle from videos;'''
        cursor.execute(query6)
        mydb.commit()
        t6 = cursor.fetchall()
        st.write(pd.DataFrame(t6, columns=["Like count","video title"]))

    elif question == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        query7 = "select Channel_Name as ChannelName, Views as Channelviews from channels;"
        cursor.execute(query7)
        mydb.commit()
        t7=cursor.fetchall()
        st.write(pd.DataFrame(t7, columns=["Channel name","Total views"]))

    elif question == '8. What are the names of all the channels that have published videos in the year 2022?':
        query8 = '''select Title as Video_Title, Published_Date as VideoRelease, Channel_Name as ChannelName from videos 
                    where extract(year from Published_Date) = 2022;'''
        cursor.execute(query8)
        mydb.commit()
        t8=cursor.fetchall()
        st.write(pd.DataFrame(t8,columns=["Name", "Video Publised On", "Channel Name"]))

    elif question == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        query9 =  "SELECT Channel_Name as ChannelName, AVG(Duration) AS average_duration FROM videos GROUP BY Channel_Name;"
        cursor.execute(query9)
        mydb.commit()
        t9=cursor.fetchall()
        t9 = pd.DataFrame(t9, columns=['ChannelTitle', 'Average Duration'])
        T9=[]
        for index, row in t9.iterrows():
            channel_title = row['ChannelTitle']
            average_duration = row['Average Duration']
            average_duration_str = str(average_duration)
            T9.append({"Channel Title": channel_title ,  "Average Duration": average_duration_str})
        st.write(pd.DataFrame(T9))

    elif question == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        query10 = '''select Title as VideoTitle, Channel_Name as ChannelName, Comments as Comments from videos 
                        where Comments is not null order by Comments desc;'''
        cursor.execute(query10)
        mydb.commit()
        t10=cursor.fetchall()
        st.write(pd.DataFrame(t10, columns=['Video Title', 'Channel Name', 'No Of Comments']))
    

# Streamlit Creation
st.title(":red[YOUTUBE] :green[DATA HARVESTING] AND :blue[WAREHOUSING] :clapper:")

with st.sidebar:
    st.title(":blue[PROJECT RESULTS]")
    show_table = st.radio("SELECT THE OPTION TO VIEW",(":green[**Data Collection**]",":red[Channels]",":orange[Playlists]",":violet[Videos]",":blue[Comments]",":rainbow[**Questions**]"))
    
if show_table == ":red[Channels]":
    show_channels_table()
elif show_table == ":orange[Playlists]":
    show_playlists_table()
elif show_table ==":violet[Videos]":
    show_videos_table()
elif show_table == ":blue[Comments]":
    show_comments_table()    
elif show_table == ":green[**Data Collection**]":
    data_collection()
elif show_table == ":rainbow[**Questions**]":
    show_queries()


