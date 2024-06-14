import streamlit as st
import calendar
import pandas as pd
from datetime import date, timedelta, datetime
import requests
import json

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
def save_post(details):
    st.session_state["scheduled_posts"].append(details)
    st.success("Post scheduled successfully!")

# Function to update an existing post
def update_post(index, details):
    st.session_state["scheduled_posts"][index] = details
    st.success("Post updated successfully!")

# Function to generate a social media post using Ollama API
def generate_post(prompt):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {"model": "llama3", "prompt": prompt}
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json().get("generated_text", "")
    else:
        st.error(f"Failed to generate post: {response.text}")
        return ""

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
    post_content = st.text_area("Write your social media post content here or generate a post using Ollama")
    post_time = st.time_input("Select time for the post")
    link = st.text_input("Enter link for the post")
    image_url = st.text_input("Enter image URL for the post")
    video_url = st.text_input("Enter video URL for the post")
    post_month = st.number_input("Enter Month (1-12)", min_value=1, max_value=12, step=1)
    post_day = st.number_input("Enter Day (1-31)", min_value=1, max_value=31, step=1)
    post_year = st.number_input("Enter Year", min_value=1900, max_value=2100, step=1, value=date.today().year)
    post_hour = st.number_input("Enter Hour (1-24)", min_value=1, max_value=24, step=1)
    post_minute = st.number_input("Enter Minute (0-59)", min_value=0, max_value=59, step=1)
    pin_title = st.text_input("Enter Pin Title")
    category = st.text_input("Enter Category")
    watermark = st.text_input("Enter Watermark")
    hashtag_group = st.text_input("Enter Hashtag Group (comma-separated)")
    video_thumbnail_url = st.text_input("Enter Video Thumbnail URL")
    cta_group = st.text_input("Enter CTA Group")

    post_datetime = datetime(post_year, post_month, post_day, post_hour, post_minute)

    post_details = {
        "platform": selected_platform,
        "content": post_content,
        "datetime": post_datetime,
        "link": link,
        "image_url": image_url,
        "video_url": video_url,
        "pin_title": pin_title,
        "category": category,
        "watermark": watermark,
        "hashtag_group": hashtag_group,
        "video_thumbnail_url": video_thumbnail_url,
        "cta_group": cta_group
    }

    if "scheduled_posts" not in st.session_state:
        st.session_state["scheduled_posts"] = []

    if st.button("Generate Post with Ollama"):
        prompt = st.text_area("Enter prompt for post generation")
        if prompt:
            generated_post = generate_post(prompt)
            st.session_state["generated_post"] = generated_post
            st.write(generated_post)

    if st.button("Save Post"):
        save_post(post_details)

    if st.session_state["scheduled_posts"]:
        st.subheader("Scheduled Posts")
        for i, post in enumerate(st.session_state["scheduled_posts"]):
            st.write(f"**Platform:** {post['platform']}")
            st.write(f"**Date and Time:** {post['datetime']}")
            st.write(f"**Content:**\n{post['content']}")
            st.write(f"**Link:** {post['link']}")
            st.write(f"**Image URL:** {post['image_url']}")
            st.write(f"**Video URL:** {post['video_url']}")
            st.write(f"**Pin Title:** {post['pin_title']}")
            st.write(f"**Category:** {post['category']}")
            st.write(f"**Watermark:** {post['watermark']}")
            st.write(f"**Hashtag Group:** {post['hashtag_group']}")
            st.write(f"**Video Thumbnail URL:** {post['video_thumbnail_url']}")
            st.write(f"**CTA Group:** {post['cta_group']}")
            if st.button(f"Edit Post {i + 1}"):
                st.session_state["edit_mode"] = i

        if "edit_mode" in st.session_state:
            edit_index = st.session_state["edit_mode"]
            post = st.session_state["scheduled_posts"][edit_index]
            edited_platform = st.selectbox("Edit Social Media Platform", social_platforms, index=social_platforms.index(post["platform"]))
            edited_weekday = st.selectbox("Edit Day of the Week", weekdays, index=weekdays.index(post["datetime"].strftime('%A')))
            edited_content = st.text_area("Edit your social media post content here", post["content"])
            edited_time = st.time_input("Edit time for the post", post["datetime"].time())
            edited_link = st.text_input("Edit link for the post", post["link"])
            edited_image_url = st.text_input("Edit image URL for the post", post["image_url"])
            edited_video_url = st.text_input("Edit video URL for the post", post["video_url"])
            edited_month = st.number_input("Edit Month (1-12)", min_value=1, max_value=12, step=1, value=post["datetime"].month)
            edited_day = st.number_input("Edit Day (1-31)", min_value=1, max_value=31, step=1, value=post["datetime"].day)
            edited_year = st.number_input("Edit Year", min_value=1900, max_value=2100, step=1, value=post["datetime"].year)
            edited_hour = st.number_input("Edit Hour (1-24)", min_value=1, max_value=24, step=1, value=post["datetime"].hour)
            edited_minute = st.number_input("Edit Minute (0-59)", min_value=0, max_value=59, step=1, value=post["datetime"].minute)
            edited_pin_title = st.text_input("Edit Pin Title", post["pin_title"])
            edited_category = st.text_input("Edit Category", post["category"])
            edited_watermark = st.text_input("Edit Watermark", post["watermark"])
            edited_hashtag_group = st.text_input("Edit Hashtag Group (comma-separated)", post["hashtag_group"])
            edited_video_thumbnail_url = st.text_input("Edit Video Thumbnail URL", post["video_thumbnail_url"])
            edited_cta_group = st.text_input("Edit CTA Group", post["cta_group"])

            edited_datetime = datetime(edited_year, edited_month, edited_day, edited_hour, edited_minute)

            edited_post_details = {
                "platform": edited_platform,
                "content": edited_content,
                "datetime": edited_datetime,
                "link": edited_link,
                "image_url": edited_image_url,
                "video_url": edited_video_url,
                "pin_title": edited_pin_title,
                "category": edited_category,
                "watermark": edited_watermark,
                "hashtag_group": edited_hashtag_group,
                "video_thumbnail_url": edited_video_thumbnail_url,
                "cta_group": edited_cta_group
            }

            if st.button("Update Post"):
                update_post(edit_index, edited_post_details)
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
            post_details = {
                "platform": row["platform"],
                "content": row["content"],
                "datetime": datetime.strptime(row["datetime"], '%Y-%m-%d %H:%M:%S'),
                "link": row["link"],
                "image_url": row["image_url"],
                "video_url": row["video_url"],
                "pin_title": row["pin_title"],
                "category": row["category"],
                "watermark": row["watermark"],
                "hashtag_group": row["hashtag_group"],
                "video_thumbnail_url": row["video_thumbnail_url"],
                "cta_group": row["cta_group"]
            }
            st.session_state["scheduled_posts"].append(post_details)
        st.success("Posts imported successfully!")

if __name__ == "__main__":
    main()
