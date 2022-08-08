import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
from PIL import Image


# Set Page Details
st.set_page_config(page_title='NotifyAnalytics', page_icon='statistics.png', layout="wide", initial_sidebar_state="collapsed", menu_items=None)
st.title("NotifyAnalytics")



with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.sidebar.header("NotifyAnalytics")
st.sidebar.subheader("Upload Notification Data and have them visualised")
file_upload = st.sidebar.file_uploader(label="Upload Notification Data from The NotificationLog App as a CSV File")

DATE_COLUMN = ['postTime']


def load_data(DATA_URL):
    data = pd.read_csv(DATA_URL)
    return data

def clean_data(df):
    # drop irrelevant columns from the Notification Logs dataset
    drop_list = ['offset', 'version', 'sdk', 'sortKey', 'textLines', 'category', 'style', 'key', 'textSummary', 'textSub', 'textInfo', 'textBig', 'titleBig', 'tickerText',
                'ringerMode', 'packageName', 'defaults', 'flags', 'listenerHints', 'color', 'visibility',
                'people', 'number', 'nid', 'matchesInterruptionFilter', 'hasAppointment', 'ledARGB', 'ledOn', 'ledOff',
                'isClearable', 'tag', 'interruptionFilter', 'group', 'isGroupSummary']

    df.drop(drop_list, axis=1, inplace=True)

    # Converting appropriate columns to datetime
    df['postTime'] = pd.to_datetime(df['postTime'], unit='ms')
    df['systemTime'] = pd.to_datetime(df['systemTime'], unit='ms')
    df['when'] = pd.to_datetime(df['when'], unit='ms')

    # I also created a new column to hold the hour value of the notification post times
    # within a 24 hour cycle For Analysing Peak Times
    notifications['Time_inHours'] = pd.to_datetime(notifications['postTime']).dt.hour


if __name__ == "__main__":
    notifications = load_data('notification_data.csv')

    # Check or Uploads
    if file_upload is not None:
        print(file_upload)
        try:
            notifications = pd.read_csv(file_upload)
        except Exception as e:
            print(e)
            notifications = pd.read_excel(file_upload)
    else:
        notifications = load_data('notification_data.csv') 


    clean_data(notifications)

    collection_start_time = notifications.postTime.head(1)
    collection_end_time = notifications.postTime.tail(1)
    time_diff = (notifications['postTime'].values[-1]-notifications['postTime'][0])

    

    # Row A
    a1,a2, a3 = st.columns(3)
    a1.metric("Notifications Analysed", f"{notifications.shape[0]}")
    a2.metric("Number of Applications Analysed", f"{len(notifications.appName.unique())}")
    a3.metric("Data Collection Period", f"{time_diff.days} Dys {time_diff.seconds//3600} Hrs", f"{(time_diff.days*24) + (time_diff.seconds//3600)} Hours of Notification Data Collected")



    # Row B
    b1, b2, b3 = st.columns(3)
    b1.metric("App with most Notifications", f"{notifications.appName.value_counts().reset_index(name='Notification_Count')['index'][0]}", f"{notifications.appName.value_counts().reset_index(name='Notification_Count')['Notification_Count'][0]} Notifications Sent")
    b2.metric("Hour of Day Notifications Peaked", f"{notifications['Time_inHours'].value_counts().rename_axis('Time_in_Hours').reset_index(name='Number of Notifications')['Time_in_Hours'][0]}:00H")
    b3.metric('Most Frequent Notification Title ',f"{notifications['title'].mode()[0]}")

    # st.table(notifications)

    # Plot Graphs
    g1,g2 = st.columns((5,5))
    with g1:
        st.markdown('##### Top 20 Mobile Apps by Notifications Sent')
        # Visualise plot for Top 20 Mobile Apps to send notifications within data scraping period
        top_10_app_triggers = notifications.appName.value_counts().head(10)
        # Visualise plot for Top 20 Mobile Apps to send notifications within data scraping period
        sns.set(font_scale=0.75)
        top_10_app_triggers.plot(kind='bar', rot=0, color='navy')
        plt.xlabel("Mobile Applications")
        plt.ylabel("Number of Notifications Sent",)
        plt.xticks(rotation = 90) 
        # plt.title("Top 10 Apps by Notifications Sent", y=1.02);
        st.pyplot(plt)


    with g2:
        st.markdown('##### Notification Distribution by Internet Connection Type')
        connection_types = notifications.groupby('connectionType')['connectionType'].count()
        # Visualising Observations on a Pie Chart
        connection_types.plot.pie(autopct='%.1f %%', colors = ['darkgreen', 'maroon', 'navy']);
        
        labels = notifications.connectionType.unique()
        sizes = notifications.groupby('connectionType')['connectionType'].count()
        plt.rcParams['font.size']=12
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', textprops={"color":"black", 'family':'sans-serif'}, colors = ['gold', 'tomato', 'royalblue'],
                shadow=False, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        st.pyplot(fig1)
    
     # Row C
    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown('##### Local Notifications vs Push Notifications')
        st.subheader('Local Notifications')
        st.write('Local Notifications are directly triggered by the mobile app, locally (ie: not coming from a remote server but coming from your own device).')
        st.subheader('Push Notifications')
        st.write("Push Notifications come from a remote server and is pushed/sent directly to a user's device in real-time.")
        # Get Normalised Value Count proportions of Notification Type 
        # (True = Local Notification, False = Push Notification)
        distribution = notifications.isLocalOnly.value_counts(normalize=True)

        # Visualising Observations on a Pie Chart
        connection_types.plot.pie(autopct='%.1f %%', colors = ['darkgreen', 'maroon', 'navy']);
        
        labels = notifications.isLocalOnly.unique()
        fig2, ax2 = plt.subplots()
        plt.rcParams['font.size']=12
        plt.legend("True", "False")

        ax2.pie(distribution, labels=labels, autopct='%1.1f%%', textprops={"color":"black", 'family':'sans-serif'}, colors = ['turquoise', 'plum'],
                shadow=False, startangle=90)
        ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig2)  


    # Evaluate User Behaviour / Apps that Triggered User Action
    # Group Notifications by their appNames & Find mean of actionCount
    top10_engaging_apps = notifications.groupby(['appName'])['actionCount'].mean().round(2).reset_index()
    # Sort top 15 most engaging apps that triggered notification user action 
    top10_apps = top10_engaging_apps.sort_values(by="actionCount", ascending=False)
    d2.markdown("##### Top 5 Apps that Triggered User's Action")
    d2.metric(f"01", f"{top10_apps.iat[0,0]}", f"{top10_apps.iat[0,1]} Average User Actions Taken")
    d2.metric(f"02", f"{top10_apps.iat[1,0]}", f"{top10_apps.iat[1,1]} Average User Actions Taken")
    d2.metric(f"03", f"{top10_apps.iat[2,0]}", f"{top10_apps.iat[2,1]} Average User Actions Taken")
    d2.metric(f"04", f"{top10_apps.iat[3,0]}", f"{top10_apps.iat[3,1]} Average User Actions Taken")
    d2.metric(f"05", f"{top10_apps.iat[4,0]}", f"{top10_apps.iat[4,1]} Average User Actions Taken")



    # Evaluate top 5 Apps that send the highest volume of high priority data
    top_priority = notifications[notifications['priority']>0]
    top_priority_notifiers = top_priority.groupby(['appName', 'priority'])['priority'].count()
    top_priority_notifiers = top_priority_notifiers.sort_values(ascending=False).head(11)
    d3.markdown('##### Applications with highest volume of High Priority Data')
    d3.write('Identifying the mobile applications responsible for sending the highest volume of high priority notifications i.e Notifications with __priority__ of +1 and +2.')
    d3.table(top_priority_notifiers)

    
    # Plot
    # Row D
    # connection_types = notifications.groupby('connectionType')['connectionType'].count()
    st.markdown('##### Sample Dataset Notifications')
    st.table(notifications[['appName', 'postTime', 'title','priority']].sample(20))


