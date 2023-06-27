import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
import streamlit as st
import matplotlib as mt


st.title("Bellabeat Wellness Tracker: Usage Insights and Analysis")

# importing tables to pd's df
daily_activity = pd.read_csv("https://raw.githubusercontent.com/aungheinko/bellabeat_streamlit_app/main/dailyActivity_merged.csv")
hourly_steps = pd.read_csv("https://raw.githubusercontent.com/aungheinko/bellabeat_streamlit_app/main/hourlySteps_merged.csv")
daily_sleep = pd.read_csv("https://raw.githubusercontent.com/aungheinko/bellabeat_streamlit_app/main/sleepDay_merged.csv")

# cleaning duplitcates
# print(daily_activity.duplicated().sum(),
# hourly_steps.duplicated().sum(),
# daily_sleep.duplicated().sum())

daily_activity = daily_activity.drop_duplicates().dropna()
hourly_steps = hourly_steps.drop_duplicates().dropna()
daily_sleep = daily_sleep.drop_duplicates().dropna()

daily_activity = daily_activity.rename(columns = str.lower)
hourly_steps = hourly_steps.rename(columns = str.lower)
daily_sleep = daily_sleep.rename(columns = str.lower)

# Renaming date columns
daily_activity.rename(columns = {'activitydate':'date'}, inplace = True)
daily_sleep.rename(columns = {'sleepday':'date_time'}, inplace = True)
hourly_steps.rename(columns = {'activityhour':'date_time'}, inplace = True)

daily_activity['date'] = pd.to_datetime(daily_activity['date'])
daily_sleep['date_time'] = pd.to_datetime(daily_sleep['date_time'])
hourly_steps['date_time'] = pd.to_datetime(hourly_steps['date_time'])

daily_sleep['date_time'] = daily_sleep['date_time'].dt.date
daily_sleep.rename(columns={'date_time':'date'},inplace = True)

daily_sleep['date'] = pd.to_datetime(daily_sleep['date'])
daily_activity_sleep = pd.merge(daily_activity,daily_sleep, on = ['id','date'])

daily_average = daily_activity_sleep.groupby('id').agg(mean_daily_steps = ('totalsteps','mean'),
                                                         mean_daily_calories = ('calories','mean'),
                                                         mean_daily_sleep = ('totalminutesasleep','mean'))

daily_average['user_type'] = pd.cut(daily_average['mean_daily_steps'],
                                   bins=[-float('inf'), 5000, 7499, 9999, float('inf')],
                                   labels=['sedentary', 'lightly active', 'fairly active', 'very active'])
user_type_percent = daily_average.groupby('user_type').size().reset_index(name='count')
total_count = user_type_percent['count'].sum()
user_type_percent['total_percent'] = np.ceil(user_type_percent['count'] / total_count * 100).astype(int)


### fig2
daily_activity_sleep['weekday'] = daily_activity_sleep['date'].dt.day_name()
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
daily_activity_sleep['weekday'] = pd.Categorical(daily_activity_sleep['weekday'], categories=weekday_order, ordered = True)
weekday_steps_sleep = daily_activity_sleep.groupby('weekday').agg(daily_steps = ('totalsteps','mean'),
                                                                  daily_sleep = ('totalminutesasleep','mean')).reset_index()


#tab2 share phase fig 1
daily_use = daily_activity_sleep.groupby('id').size().reset_index(name='days_used')
daily_use['usage'] = pd.cut(daily_use['days_used'], bins=[0, 10, 20, 31], labels=['low use', 'moderate use', 'high use'])
daily_use_percent = daily_use.groupby('usage').size().reset_index(name='total')
daily_use_percent['totals'] = daily_use_percent['total'].sum()
daily_use_percent['total_percent'] = daily_use_percent['total'] / daily_use_percent['totals']
daily_use_percent['labels'] = (daily_use_percent['total_percent'] * 100).map('{:.1f}%'.format)
daily_use_percent['usage'] = pd.Categorical(daily_use_percent['usage'], categories=['high use', 'moderate use', 'low use'], ordered=True)

## Share Phase

daily_use_merged = pd.merge(daily_activity,daily_use,on =['id'])
daily_use_merged['total_minutes_worn'] = daily_use_merged['veryactiveminutes'] + daily_use_merged['fairlyactiveminutes'] + daily_use_merged['lightlyactiveminutes'] + daily_use_merged['sedentaryminutes']

daily_use_merged['percent_minutes_worn'] = (daily_use_merged['total_minutes_worn']/1440)*100
daily_use_merged['worn'] = daily_use_merged['total_minutes_worn'].apply(lambda x: 'All day' if x == 100 else 'More than half day' if 50 <= x < 100 else 'Less than half day')

minutes_worn  = pd.merge(daily_activity,daily_use,on =['id'])

# Calculate total minutes worn
minutes_worn['total_minutes_worn'] = daily_use_merged['veryactiveminutes'] + daily_use_merged['fairlyactiveminutes'] + daily_use_merged['lightlyactiveminutes'] + daily_use_merged['sedentaryminutes']

# Calculate percentage of minutes worn
minutes_worn['percent_minutes_worn'] = (minutes_worn['total_minutes_worn'] / 1440) * 100

# Define worn category based on percentage of minutes worn
minutes_worn['worn'] = minutes_worn['percent_minutes_worn'].apply(lambda x: 'All day' if x == 100 else 'More than half day' if 50 <= x < 100 else 'Less than half day')

# Calculate percentage of minutes worn for all users
minutes_worn_percent = minutes_worn.groupby('worn').size().reset_index(name='total')
minutes_worn_percent['totals'] = minutes_worn_percent['total'].sum()
minutes_worn_percent['total_percent'] = minutes_worn_percent['total'] / minutes_worn_percent['totals']
minutes_worn_percent['total_percent'] = (minutes_worn_percent['total_percent'] * 100).round()
minutes_worn_percent['labels'] = minutes_worn_percent['total_percent'].astype(int).astype(str) + '%'

# Filter and calculate percentages for high use
minutes_worn_highuse = minutes_worn[minutes_worn['usage'] == 'high use'].groupby('worn').size().reset_index(name='total')
minutes_worn_highuse['totals'] = minutes_worn_highuse['total'].sum()
minutes_worn_highuse['total_percent'] = minutes_worn_highuse['total'] / minutes_worn_highuse['totals']
minutes_worn_highuse['total_percent'] = (minutes_worn_highuse['total_percent'] * 100).round()
minutes_worn_highuse['labels'] = minutes_worn_highuse['total_percent'].astype(int).astype(str) + '%'
minutes_worn_highuse['worn'] = pd.Categorical(minutes_worn_highuse['worn'],
                                              categories=["All day", "More than half day", "Less than half day"],
                                              ordered=True)

# Filter and calculate percentages for moderate use
minutes_worn_moduse = minutes_worn[minutes_worn['usage'] == 'moderate use'].groupby('worn').size().reset_index(name='total')
minutes_worn_moduse['totals'] = minutes_worn_moduse['total'].sum()
minutes_worn_moduse['total_percent'] = minutes_worn_moduse['total'] / minutes_worn_moduse['totals']
minutes_worn_moduse['total_percent'] = (minutes_worn_moduse['total_percent'] * 100).round()
minutes_worn_moduse['labels'] = minutes_worn_moduse['total_percent'].astype(int).astype(str) + '%'
minutes_worn_moduse['worn'] = pd.Categorical(minutes_worn_moduse['worn'],
                                             categories=["All day", "More than half day", "Less than half day"],
                                             ordered=True)

# Filter and calculate percentages for low use
minutes_worn_lowuse = minutes_worn[minutes_worn['usage'] == 'low use'].groupby('worn').size().reset_index(name='total')
minutes_worn_lowuse['totals'] = minutes_worn_lowuse['total'].sum()
minutes_worn_lowuse['total_percent'] = minutes_worn_lowuse['total'] / minutes_worn_lowuse['totals']
minutes_worn_lowuse['total_percent'] = (minutes_worn_lowuse['total_percent'] * 100).round()
minutes_worn_lowuse['labels'] = minutes_worn_lowuse['total_percent'].astype(int).astype(str) + '%'
minutes_worn_lowuse['worn'] = pd.Categorical(minutes_worn_lowuse['worn'],
                                             categories=["All day", "More than half day", "Less than half day"],
                                             ordered=True)


tab1, tab2, tab3, tab4 = st.tabs(["Process Phase","Analyze Phase", "Share Phase", "Act Phase"])

with tab1:
    markdown_text = """
### 1. Summary
Bellabeat is a high-tech company that manufactures health-focused smart products. They offer different smart devices that collect data on activity, sleep, stress, and reproductive health to empower women with knowledge about their own health and habits.

The main focus of this case is to analyze smart device fitness data and determine how it could help unlock new growth opportunities for Bellabeat. We will focus on one of Bellabeat’s products: Bellabeat app.

The Bellabeat app provides users with health data related to their activity, sleep, stress, menstrual cycle, and mindfulness habits. This data can help users better understand their current habits and make healthy decisions. The Bellabeat app connects to their line of smart wellness products.

### 2. Ask Phase
#### 2.1 Business Task
Identify trends in how consumers use non-Bellabeat smart devices to apply insights into Bellabeat’s marketing strategy.

#### Stakeholders
- Urška Sršen - Bellabeat cofounder and Chief Creative Officer
- Sando Mur - Bellabeat cofounder and key member of Bellabeat executive team
- Bellabeat Marketing Analytics team

### 3. Prepare Phase
#### 3.1 Dataset used
The data source used for our case study is FitBit Fitness Tracker Data. This dataset is stored in Kaggle and was made available through Mobius.

#### 3.2 Accessibility and privacy of data
Verifying the metadata of our dataset, we can confirm it is open-source. The owner has dedicated the work to the public domain by waiving all of their rights to the work worldwide under copyright law, including all related and neighboring rights, to the extent allowed by law. You can copy, modify, distribute, and perform the work, even for commercial purposes, all without asking permission.

#### 3.3 Information about our dataset
These datasets were generated by respondents to a distributed survey via Amazon Mechanical Turk between 03.12.2016-05.12.2016. Thirty eligible Fitbit users consented to the submission of personal tracker data, including minute-level output for physical activity, heart rate, and sleep monitoring. Variation between output represents the use of different types of Fitbit trackers and individual tracking behaviors/preferences.

#### 3.4 Data Organization and verification
We have access to 18 CSV documents. Each document represents different quantitative data tracked by Fitbit. The data is considered long since each row is one time point per subject, so each subject will have data in multiple rows. Every user has a unique ID and different rows since data is tracked by day and time.

Due to the small sample size, I sorted and filtered tables by creating Pivot Tables in Excel. I was able to verify the attributes and observations of each table and the relations between tables. I also counted the sample size (users) of each table and verified the time length of the analysis - 31 days.
"""

    st.markdown(markdown_text)

with tab2:
    st.subheader("4.1 Type of users per activity level")
    st.write("""Since we don't have any demographic variables from our sample,
        we want to determine the type of users with the data we have.
        We can classify the users by activity considering the daily amount of steps.
        We can categorize users as follows:

    - Sedentary: Less than 5000 steps a day.
    - Lightly active: Between 5000 and 7499 steps a day.
    - Fairly active: Between 7500 and 9999 steps a day.
    - Very active: More than 10000 steps a day.
    """)

    labels = user_type_percent['user_type']
    sizes = user_type_percent['total_percent']
    explode = (0, 0, 0, 0.1)
    fig1_colors = ['#3AA6B9','#F6FA70','#FF9EAA','#C1ECE4']

    # Create a pie chart
    fig1, ax1 = plt.subplots(figsize=(8,3))
    ax1.pie(sizes, explode=explode, colors=fig1_colors, autopct='%1.1f%%', textprops={'fontsize': 10})
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

    # Add a legend with color-coded labels
    ax1.legend(labels, loc='upper right',prop={'size': 8})
    ax1.set_title("User type distribution")

    # Display the chart in Streamlit
    st.pyplot(fig1)
    st.markdown("""Above we can see that users are fairly distributed by their activity considering the daily amount of steps.
                **_We can determine that based on users activity all kind of users wear smart-devices._**""")
    print()
    st.subheader("4.2 Steps and minutes asleep per weekday")
    st.write("We want to know now what days of the week are the users more active and also what days of the week users sleep more. We will also verify if the users walk the recommended amount of steps and have the recommended amount of sleep.")

    fig2, ax2 = plt.subplots(1, 2, figsize=(8, 5))
    ax2[0].bar(weekday_steps_sleep['weekday'], weekday_steps_sleep['daily_steps'], color="#30E3DF")
    ax2[0].axhline(y=7500, color='red', linestyle='--')
    ax2[0].set_title('Daily Steps per Weekday')
    ax2[0].set_xlabel('')
    ax2[0].set_ylabel('')
    ax2[0].tick_params(axis='x', rotation=90)

    # Create the second plot for minutes asleep per weekday
    ax2[1].bar(weekday_steps_sleep['weekday'], weekday_steps_sleep['daily_sleep'], color="#FF90BB")
    ax2[1].axhline(y=480, color='red', linestyle='--')
    ax2[1].set_title('Minutes Asleep per Weekday')
    ax2[1].set_xlabel('')
    ax2[1].set_ylabel('')
    ax2[1].tick_params(axis='x', rotation=90)

    st.pyplot(fig2)
    st.markdown("""In the graphs above we can determine the following:

* Users walk daily the recommended amount of steps of 7500 besides Sunday's.

* Users don't sleep the recommended amount of minutes/ hours - 8 hours.""")

    st.subheader("4.3 Hourly steps throughout the day")
    st.write("Getting deeper into our analysis we want to know when exactly are users more active in a day.")
    hourly_steps[['date', 'time']] = hourly_steps['date_time'].astype(str).str.split(' ', expand=True)
    hourly_steps['date'] = pd.to_datetime(hourly_steps['date'])

    # Assuming hourly_steps is a pandas DataFrame
    hourly_steps_grouped = hourly_steps.groupby('time').mean(numeric_only=True).reset_index()

    # Set the colormap
    cmap = mt.colormaps.get_cmap('RdYlGn')
    norm = plt.Normalize(vmin=100, vmax=600)

    fig3, ax3 = plt.subplots(figsize = (8,5))
    # Plotting the bar chart
    bars = ax3.bar(hourly_steps_grouped['time'], hourly_steps_grouped['steptotal'], color=cmap(norm(hourly_steps_grouped['steptotal'])))

    # Customize the plot
    plt.xticks(rotation=90)
    ax3.set_title("Hourly steps throughout the day")
    ax3.set_xlabel("Hours")
    ax3.set_ylabel("Steps")

    # Create a colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax3, label='Average Steps')

    # Show the plot
    st.pyplot(fig3)

    st.markdown("We can see that users are more active between **8am** and **7pm**. Walking more steps during lunch time from 12pm to 2pm and evenings from 5pm and 7pm.")

    st.subheader('4.4 Correlations')
    st.markdown("""
We will now determine if there is any correlation between different variables:

* Daily steps and daily sleep
* Daily steps and calories
""")
    steps = daily_activity_sleep['totalsteps']
    minutes_asleep = daily_activity_sleep['totalminutesasleep']
    calories = daily_activity_sleep['calories']
    trend_minutes_asleep = np.poly1d(np.polyfit(steps, minutes_asleep, 1))(steps)
    trend_calories = np.poly1d(np.polyfit(steps, calories, 1))(steps)

    # Create a scatter plot with trend lines
    fig4, ax4 = plt.subplots(1,2, figsize = (12,8))
    ax4[0].scatter(steps, minutes_asleep, alpha=0.5)
    ax4[1].scatter(steps, calories, alpha=0.5, label='Calories burned')
    ax4[0].plot(steps, trend_minutes_asleep, color='red')
    ax4[1].plot(steps, trend_calories, color='blue', label='Trend (Calories burned)')

    ax4[0].set_xlabel('Daily steps')
    ax4[0].set_ylabel('Minutes')

    ax4[1].set_xlabel('Daily steps')
    ax4[1].set_ylabel('Calories')
    # Render the plot using Streamlit
    st.pyplot(fig4)
    st.markdown("""Per our plots:

* There is no correlation between daily activity level based on steps and the amount of minutes users sleep a day.

* Otherwise we can see a positive correlation between steps and calories burned. As assumed the more steps walked the more calories may be burned.""")



with tab3:
    st.header("Use of smart device")

    st.subheader('5.1 Days used smart device')
    st.markdown("""Now that we have seen some trends in activity, sleep and calories burned,
        we want to see how often do the users in our sample use their device.
        That way we can plan our marketing strategy and see what features would benefit the use of smart devices.

* high use - users who use their device between 21 and 31 days.

* moderate use - users who use their device between 10 and 20 days.

* low use - users who use their device between 1 and 10 days.""")

    labels = daily_use_percent['usage']
    sizes = daily_use_percent['total_percent']
    colors = ["#FF0060","#F6FA70","#00DFA2"]

    fig5, ax5 = plt.subplots(figsize = (8, 3))
    ax5.pie(sizes, autopct='%1.1f%%', colors = colors, startangle=90,  textprops={'fontsize': 10})
    ax5.axis('equal')
    ax5.set_title("Daily use of smart device")
    ax5.legend(labels,loc='upper right',prop={'size': 8})
    st.pyplot(fig5)
    st.markdown("""Analyzing our results we can see that

* 50% of the users of our sample use their device frequently - between 21 to 31 days.
* 12% use their device 11 to 20 days.
* 38% of our sample use really rarely their device.""")

    st.subheader('5.2 Time worn per day')

    labels = minutes_worn_percent['worn']
    sizes = minutes_worn_percent['total_percent']
    colors = ['#00DFA2', '#FF0060','#F6FA70']
    fig7, ax7 = plt.subplots(figsize = (8,3))
    ax7.pie(sizes, startangle= 90 ,textprops={'fontsize':10}, colors = colors, autopct='%1.0f%%')
    ax7.axis('equal')
    ax7.legend(labels, loc = 'upper right', prop={'size': 10})
    ax7.set_title("Total Users")
    st.pyplot(fig7)


    labels = minutes_worn_percent['worn']
    colors = ['#00DFA2', '#FF0060','#F6FA70']

    fig8, ax8 = plt.subplots(1,3,figsize = (8,3))

    ax8[0].pie(minutes_worn_highuse['total_percent'], startangle= 90 ,textprops={'fontsize':8}, colors = colors, autopct='%1.0f%%')
    ax8[0].axis('equal')
    ax8[0].set_title("High Use - Users")

    ax8[1].pie(minutes_worn_moduse['total_percent'], startangle= 90 ,textprops={'fontsize':8}, colors = colors, autopct='%1.0f%%')
    ax8[1].axis('equal')
    ax8[1].set_title("Moderate Use - Users")

    ax8[2].pie(minutes_worn_lowuse['total_percent'], startangle= 90 ,textprops={'fontsize':8}, colors = colors, autopct='%1.0f%%')
    ax8[2].axis('equal')
    ax8[2].set_title("Low Use - Users")

    st.pyplot(fig8)

    st.markdown("""
        Per our plots we can see that 36% of the total of users wear the device all day long, 60% more than half day long and just 4% less than half day.

If we filter the total users considering the days they have used the device and also check each day how long they have worn the device, we have the following results:

* High users - Just 7% of the users that have used their device between 21 and 31 days wear it all day.
89% wear the device more than half day but not all day.

* Moderate users are the ones who wear the device less on a daily basis.

* Being low users who wear more time their device the day they use it.
        """)

with tab4:

    st.header("Conclusion")
    st.markdown("**Bellabeat's mission is to empower women by providing them with the data to discover themselves.**")
    st.markdown("""In order for us to respond to our business task and help Bellabeat on their mission, based on our results, I would advice to use own tracking data for further analysis. Datasets used have a small sample and can be biased since we didn't have any demographic details of users. Knowing that our main target are young and adult women I would encourage to continue finding trends to be able to create a marketing stragety focused on them.

That being said, after our analysis we have found different trends that may help our online campaign and improve Bellabeat app""")
    table_content = """
| Recommendation                                 | Description                                                                                                                                                                                                                             |
|--------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1. Daily notification on steps and posts on app**    | We classified users into 4 categories and found that the average number of steps walked by users is more than 7,500 daily, except on Sundays. To encourage customers to reach the daily recommended steps (8,000 as per CDC), we can send them notifications if they haven't reached their steps goal. We can also create posts on our app explaining the benefits of reaching that goal, as walking more steps has been shown to reduce mortality rate. Additionally, there is a positive correlation between steps and calories burned. |
| **2. Notification and sleep techniques**               | Based on our findings, users are sleeping less than 8 hours a day. We can offer a sleep feature where users can set a desired bedtime and receive a notification a few minutes before to prepare for sleep. We can also provide helpful resources such as breathing exercises, podcasts with relaxing music, and sleep techniques to improve their sleep quality. |
| **3. Reward system**                                  | We understand that some users may not be motivated by notifications alone. To engage and motivate users, we can introduce a limited-time game within our app. Users can progress through different levels based on the number of steps they walk daily. To advance to the next level, they would need to maintain their activity level for a certain period (e.g., a month). Each level achieved would earn them a certain number of stars, which can be redeemed for merchandise or discounts on other Bellabeat products. |
"""
    st.markdown(table_content)
    st.markdown("""
        On our analysis we didn't just check trends on daily users habits we also realized that just 50% of the users use their device on a daily basis and that just 36% of the users wear the device all time the day they used it. We can continue promote Bellabeat's products features:

* Water-resistant
* Long-lasting batteries
* Fashion/ elegant products

""")
