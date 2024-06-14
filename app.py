import streamlit as st
import calendar
import pandas as pd
from datetime import date, timedelta, datetime

# Function to determine the next specified weekday from a given date
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + timedelta(days_ahead)

# Function to display the calendar
def display_calendar(year):
    cal = calendar.Calendar(calendar.SUNDAY)
    all_months = []

    for month in range(1, 13):
        month_cal = cal.monthdayscalendar(year, month)
        month_name = calendar.month_name[month]

        month_title = f"### {month_name} {year}"
        days_header = "|".join(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        separator = "|".join(["---"] * 7)
        header_row = f"|{days_header}|\n|{separator}|"

        month_table = month_title + "\n" + header_row + "\n"
        for week in month_cal:
            week_str = "|".join(f"{day:2}" if day != 0 else "  " for day in week)
            month_table += f"|{week_str}|\n"

        all_months.append(month_table)

    st.markdown("\n\n".join(all_months), unsafe_allow_html=True)

# Function to save a new post
def save_post(platform, content, post_datetime, email, notes, hashtags):
    st.session_state["scheduled_posts"].append({
        "platform": platform,
        "content": content,
        "datetime": post_datetime,
        "email": email,
        "notes": notes,
        "hashtags": hashtags
    })
    st.success("Post scheduled successfully!")

# Function to update an existing post
def update_post(index, platform, content, post_datetime, email, notes, hashtags):
    st.session_state["scheduled_posts"][index] = {
        "platform": platform,
        "content": content,
        "datetime": post_datetime,
        "email": email,
        "notes": notes,
        "hashtags": hashtags
    }
    st.success("Post updated successfully!")

def main():
    st.title("GalvanMoto Calendar and Social Media Scheduler")

    # Get user input for the year
    year = st.number_input("Enter a year", min_value=0, max_value=9999, value=date.today().year)
    display_calendar(year)

    # Social Media Scheduler Section
    st.subheader("Social Media Scheduler")

    social_platforms = ["Twitter", "Facebook", "LinkedIn", "Instagram"]
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    selected_platform = st.selectbox("Select Social Media Platform", social_platforms)
    selected_weekday = st.selectbox("Select Day of the Week", weekdays)
    post_content = st.text_area("Write your social media post content here")
    post_time = st.time_input("Select time for the post")
    hashtags = st.text_input("Enter hashtags (comma-separated)")
    notes = st.text_area("Add notes for this post")
    email = st.text_input("Enter your email for notifications")

    today = date.today()
    next_post_day = next_weekday(today, weekdays.index(selected_weekday))
    post_datetime = datetime.combine(next_post_day, post_time)
    st.write(f"Your next scheduled post will be on: {post_datetime}")

    if "scheduled_posts" not in st.session_state:
        st.session_state["scheduled_posts"] = []

    if st.button("Save Post"):
        save_post(selected_platform, post_content, post_datetime, email, notes, hashtags)

    if st.session_state["scheduled_posts"]:
        st.subheader("Scheduled Posts")
        for i, post in enumerate(st.session_state["scheduled_posts"]):
            st.write(f"**Platform:** {post['platform']}")
            st.write(f"**Date and Time:** {post['datetime']}")
            st.write(f"**Content:**\n{post['content']}")
            st.write(f"**Notes:**\n{post['notes']}")
            st.write(f"**Hashtags:**\n{post['hashtags']}")
            if st.button(f"Edit Post {i + 1}"):
                st.session_state["edit_mode"] = i

        if "edit_mode" in st.session_state:
            edit_index = st.session_state["edit_mode"]
            edited_platform = st.selectbox("Edit Social Media Platform", social_platforms, index=social_platforms.index(st.session_state["scheduled_posts"][edit_index]["platform"]))
            edited_weekday = st.selectbox("Edit Day of the Week", weekdays, index=weekdays.index(st.session_state["scheduled_posts"][edit_index]["datetime"].strftime('%A')))
            edited_content = st.text_area("Edit your social media post content here", st.session_state["scheduled_posts"][edit_index]["content"])
            edited_time = st.time_input("Edit time for the post", st.session_state["scheduled_posts"][edit_index]["datetime"].time())
            edited_hashtags = st.text_input("Edit hashtags (comma-separated)", st.session_state["scheduled_posts"][edit_index]["hashtags"])
            edited_notes = st.text_area("Edit your notes for this post", st.session_state["scheduled_posts"][edit_index]["notes"])
            edited_email = st.text_input("Edit your email for notifications", st.session_state["scheduled_posts"][edit_index]["email"])
            if st.button("Update Post"):
                edited_date = next_weekday(today, weekdays.index(edited_weekday))
                edited_datetime = datetime.combine(edited_date, edited_time)
                update_post(edit_index, edited_platform, edited_content, edited_datetime, edited_email, edited_notes, edited_hashtags)
                del st.session_state["edit_mode"]

    if st.session_state["scheduled_posts"] and st.button("Export to CSV"):
        df = pd.DataFrame(st.session_state["scheduled_posts"])
        csv_file = "scheduled_posts.csv"
        df.to_csv(csv_file, index=False)
        st.success(f"Scheduled posts exported to {csv_file} successfully!")
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False),
            file_name=csv_file,
            mime='text/csv',
        )

    st.subheader("Import Scheduled Posts from CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        imported_posts = pd.read_csv(uploaded_file)
        for _, row in imported_posts.iterrows():
            st.session_state["scheduled_posts"].append({
                "platform": row["platform"],
                "content": row["content"],
                "datetime": datetime.strptime(row["datetime"], '%Y-%m-%d %H:%M:%S'),
                "email": row["email"],
                "notes": row["notes"],
                "hashtags": row["hashtags"]
            })
        st.success("Posts imported successfully!")

if __name__ == "__main__":
    main()
